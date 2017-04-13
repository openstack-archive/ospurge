#!/usr/bin/env python3
#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.
import argparse
import concurrent.futures
import logging
import operator
import sys
import threading
import typing

import os_client_config
import shade

from ospurge import exceptions
from ospurge.resources.base import ServiceResource
from ospurge import utils

if typing.TYPE_CHECKING:  # pragma: no cover
    from typing import Optional  # noqa: F401


def configure_logging(verbose: bool) -> None:
    log_level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        format='%(levelname)s:%(name)s:%(asctime)s:%(message)s',
        level=log_level
    )
    logging.getLogger(
        'requests.packages.urllib3.connectionpool').setLevel(logging.WARNING)


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Purge resources from an Openstack project."
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Make output verbose"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="List project's resources"
    )
    parser.add_argument(
        "--delete-shared-resources", action="store_true",
        help="Whether to delete shared resources (public images and external "
             "networks)"
    )
    parser.add_argument(
        "--admin-role-name", default="admin",
        help="Name of admin role. Defaults to 'admin'. This role will be "
             "temporarily granted on the project to purge to the "
             "authenticated user."
    )
    parser.add_argument(
        "--resource", choices=["Networks", "Ports", "SecurityGroups",
                               "FloatingIPs", "Routers", "RouterInterfaces",
                               "Servers", "Images", "Backups", "Snapshots",
                               "Volumes"],
        help="Name of Resource type to be checked, instead of all resources "
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--purge-project", metavar="ID_OR_NAME",
        help="ID or Name of project to purge. This option requires "
             "to authenticate with admin credentials."
    )
    group.add_argument(
        "--purge-own-project", action="store_true",
        help="Purge resources of the project used to authenticate. Useful "
             "if you don't have the admin credentials of the cloud."
    )
    return parser


class CredentialsManager(object):
    def __init__(self, options: argparse.Namespace) -> None:
        self.options = options

        self.revoke_role_after_purge = False
        self.disable_project_after_purge = False

        self.cloud = None  # type: Optional[shade.OpenStackCloud]
        self.operator_cloud = None  # type: Optional[shade.OperatorCloud]

        if options.purge_own_project:
            self.cloud = shade.openstack_cloud(argparse=options)
            self.user_id = self.cloud.keystone_session.get_user_id()
            self.project_id = self.cloud.keystone_session.get_project_id()
        else:
            self.operator_cloud = shade.operator_cloud(argparse=options)
            self.user_id = self.operator_cloud.keystone_session.get_user_id()

            project = self.operator_cloud.get_project(options.purge_project)
            if not project:
                raise exceptions.OSProjectNotFound(
                    "Unable to find project '{}'".format(options.purge_project)
                )
            self.project_id = project['id']

            # If project is not enabled, we must disable it after purge.
            self.disable_project_after_purge = not project.enabled

            # Reuse the information passed to get the `OperatorCloud` but
            # change the project. This way we bind/re-scope to the project
            # we want to purge, not the project we authenticated to.
            self.cloud = shade.openstack_cloud(
                **utils.replace_project_info(
                    self.operator_cloud.cloud_config.config,
                    self.project_id
                )
            )

        auth_args = self.cloud.cloud_config.get_auth_args()
        logging.warning(
            "Going to list and/or delete resources from project '%s'",
            options.purge_project or auth_args.get('project_name')
            or auth_args.get('project_id')
        )

    def ensure_role_on_project(self) -> None:
        if self.operator_cloud and self.operator_cloud.grant_role(
                self.options.admin_role_name,
                project=self.options.purge_project, user=self.user_id
        ):
            logging.warning(
                "Role 'Member' granted to user '%s' on project '%s'",
                self.user_id, self.options.purge_project
            )
            self.revoke_role_after_purge = True

    def revoke_role_on_project(self) -> None:
        self.operator_cloud.revoke_role(
            self.options.admin_role_name, user=self.user_id,
            project=self.options.purge_project)
        logging.warning(
            "Role 'Member' revoked from user '%s' on project '%s'",
            self.user_id, self.options.purge_project
        )

    def ensure_enabled_project(self) -> None:
        if self.operator_cloud and self.disable_project_after_purge:
            self.operator_cloud.update_project(self.project_id, enabled=True)
            logging.warning("Project '%s' was disabled before purge and it is "
                            "now enabled", self.options.purge_project)

    def disable_project(self) -> None:
        self.operator_cloud.update_project(self.project_id, enabled=False)
        logging.warning("Project '%s' was disabled before purge and it is "
                        "now also disabled", self.options.purge_project)


def runner(
        resource_mngr: ServiceResource, options: argparse.Namespace,
        exit: threading.Event
) -> None:
    try:

        if not (options.dry_run or options.resource):
            resource_mngr.wait_for_check_prerequisite(exit)

        for resource in resource_mngr.list():
            # No need to continue if requested to exit.
            if exit.is_set():
                return

            if resource_mngr.should_delete(resource):
                logging.info("Going to delete %s",
                             resource_mngr.to_str(resource))

                if options.dry_run:
                    continue

                if options.resource:
                    utils.call_and_ignore_all(resource_mngr.delete, resource)
                else:
                    utils.call_and_ignore_notfound(resource_mngr.delete,
                                                   resource)

    except Exception as exc:
        log = logging.error
        recoverable = False

        def is_exception_recoverable(exc):
            if exc.__class__.__name__.lower().endswith('endpointnotfound'):
                return True
            elif hasattr(exc, 'inner_exception'):
                # inner_exception is a tuple (type, value, traceback)
                # mypy complains: "Exception" has no attribute
                # "inner_exception"
                exc_info = exc.inner_exception  # type: ignore
                if exc_info[0].__name__.lower().endswith('endpointnotfound'):
                    return True
            return False

        if is_exception_recoverable(exc):
            log = logging.info
            recoverable = True
        log("Can't deal with %s: %r", resource_mngr.__class__.__name__, exc)
        if not recoverable:
            exit.set()


@utils.monkeypatch_oscc_logging_warning
def main() -> None:
    parser = create_argument_parser()

    cloud_config = os_client_config.OpenStackConfig()
    cloud_config.register_argparse_arguments(parser, sys.argv)

    options = parser.parse_args()
    configure_logging(options.verbose)

    creds_manager = CredentialsManager(options=options)
    creds_manager.ensure_enabled_project()
    creds_manager.ensure_role_on_project()

    if options.resource:
        resource_managers = sorted(
            [cls(creds_manager)
             for cls in utils.get_resource_classes(options.resource)],
            key=operator.methodcaller('order')
        )
    else:
        resource_managers = sorted(
            [cls(creds_manager) for cls in utils.get_all_resource_classes()],
            key=operator.methodcaller('order')
        )

    # This is an `Event` used to signal whether one of the threads encountered
    # an unrecoverable error, at which point all threads should exit because
    # otherwise there's a chance the cleanup process never finishes.
    exit = threading.Event()

    # Dummy function to work around `ThreadPoolExecutor.map()` not accepting
    # a callable with arguments.
    def partial_runner(resource_manager: ServiceResource) -> None:
        runner(resource_manager, options=options,
               exit=exit)  # pragma: no cover

    try:
        with concurrent.futures.ThreadPoolExecutor(8) as executor:
            executor.map(partial_runner, resource_managers)
    except KeyboardInterrupt:
        exit.set()

    if creds_manager.revoke_role_after_purge:
        creds_manager.revoke_role_on_project()

    if creds_manager.disable_project_after_purge:
        creds_manager.disable_project()

    sys.exit(int(exit.is_set()))


if __name__ == "__main__":  # pragma: no cover
    main()
