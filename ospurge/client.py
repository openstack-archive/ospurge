#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# This software is released under the MIT License.
#
# Copyright (c) 2014 Cloudwatt
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
from distutils import version
import logging
import os
import sys

import os_client_config

from ceilometerclient import client as ceilometer_client
import ceilometerclient.exc
import cinderclient
import glanceclient.exc
import heatclient.openstack.common.apiclient.exceptions
from keystoneclient.apiclient import exceptions as api_exceptions
import keystoneclient.openstack.common.apiclient.exceptions
import neutronclient.common.exceptions
import novaclient.exceptions
import requests

from ospurge import base
from ospurge import constants
from ospurge import exceptions


class SwiftResources(base.Resources):

    def __init__(self, cloud):
        super(SwiftResources, self).__init__(cloud)
        self.swift_client = self.cloud.get_legacy_client('object-store')

    # This method is used to retrieve Objects as well as Containers.
    def list_containers(self):
        containers = self.swift_client.get_account()
        return (cont['name'] for cont in containers)


class SwiftObjects(SwiftResources):

    def list(self):
        swift_objects = []
        for cont in self.list_containers():
            objs = [{'container': cont, 'name': obj['name']} for obj in
                    self.swift_client.get_container(cont)[1]]
            swift_objects.extend(objs)
        return swift_objects

    def delete(self, obj):
        super(SwiftObjects, self).delete(obj)
        self.swift_client.delete_object(
            container=obj['container'], name=obj['name'])

    def resource_str(self, obj):
        return "object {} in container {}".format(obj['name'], obj['container'])


class SwiftContainers(SwiftResources):

    def list(self):
        return self.list_containers()

    def delete(self, container):
        """Container must be empty for deletion to succeed."""
        super(SwiftContainers, self).delete(container)
        self.swift_client.delete_container(container)

    def resource_str(self, obj):
        return "container {}".format(obj)


class CinderResources(base.Resources):

    def __init__(self, cloud):
        super(CinderResources, self).__init__(cloud)
        # Cinder client library can't use an existing token. When
        # using this library, we have to reauthenticate.
        self.client = self.cloud.get_legacy_client('volume')


class CinderSnapshots(CinderResources):

    def list(self):
        return self.client.volume_snapshots.list()

    def delete(self, snap):
        super(CinderSnapshots, self).delete(snap)
        self.client.volume_snapshots.delete(snap)

    def resource_str(self, snap):
        return "snapshot {} (id {})".format(snap.display_name, snap.id)


class CinderVolumes(CinderResources):

    def list(self):
        return self.client.volumes.list()

    def delete(self, vol):
        """Snapshots created from the volume must be deleted first."""
        super(CinderVolumes, self).delete(vol)
        self.client.volumes.delete(vol)

    def resource_str(self, vol):
        return "volume {} (id {})".format(vol.display_name, vol.id)


class CinderBackups(CinderResources):

    def list(self):
        if self.session.is_admin and version.LooseVersion(
                cinderclient.version_info.version_string()) < '1.4.0':
            logging.warning('cinder volume-backups are ignored when ospurge is '
                            'launched with admin credentials because of the '
                            'following bug: '
                            'https://bugs.launchpad.net/python-cinderclient/+bug/1422046')
            return []
        return self.client.backups.list()

    def delete(self, backup):
        super(CinderBackups, self).delete(backup)
        self.client.backups.delete(backup)

    def resource_str(self, backup):
        return "backup {} (id {}) of volume {}".format(backup.name, backup.id, backup.volume_id)


class NeutronResources(base.Resources):

    def __init__(self, cloud):
        super(NeutronResources, self).__init__(cloud)
        self.client = self.cloud.get_legacy_client('network')

    # This method is used for routers and interfaces removal
    def list_routers(self):
        return filter(
            self._owned_resource,
            self.client.list_routers(tenant_id=self.project_id)['routers'])

    def _owned_resource(self, res):
        # Only considering resources owned by project
        # We try to filter directly in the client.list() commands, but some 3rd
        # party Neutron plugins may ignore the "tenant_id=self.project_id"
        # keyword filtering parameter. An extra check does not cost much and
        # keeps us on the safe side.
        return res['tenant_id'] == self.project_id


class NeutronRouters(NeutronResources):

    def list(self):
        return self.list_routers()

    def delete(self, router):
        """Interfaces must be deleted first."""
        super(NeutronRouters, self).delete(router)
        # Remove router gateway prior to remove the router itself
        self.client.remove_gateway_router(router['id'])
        self.client.delete_router(router['id'])

    @staticmethod
    def resource_str(router):
        return "router {} (id {})".format(router['name'], router['id'])


class NeutronInterfaces(NeutronResources):

    def list(self):
        # Only considering "router_interface" ports
        # (not gateways, neither unbound ports)
        all_ports = [
            port for port in self.client.list_ports(
                tenant_id=self.project_id)['ports']
            if port["device_owner"] == "network:router_interface"
        ]
        return filter(self._owned_resource, all_ports)

    def delete(self, interface):
        super(NeutronInterfaces, self).delete(interface)
        self.client.remove_interface_router(interface['device_id'],
                                            {'port_id': interface['id']})

    @staticmethod
    def resource_str(interface):
        return "interface {} (id {})".format(interface['name'],
                                             interface['id'])


class NeutronPorts(NeutronResources):

    # When created, unbound ports' device_owner are "". device_owner
    # is of the form" compute:*" if it has been bound to some vm in
    # the past.
    def list(self):
        all_ports = [
            port for port in self.client.list_ports(
                tenant_id=self.project_id)['ports']
            if port["device_owner"] == ""
            or port["device_owner"].startswith("compute:")
        ]
        return filter(self._owned_resource, all_ports)

    def delete(self, port):
        super(NeutronPorts, self).delete(port)
        self.client.delete_port(port['id'])

    @staticmethod
    def resource_str(port):
        return "port {} (id {})".format(port['name'], port['id'])


class NeutronNetworks(NeutronResources):

    def list(self):
        return filter(self._owned_resource,
                      self.client.list_networks(
                          tenant_id=self.project_id)['networks'])

    def delete(self, net):
        """Delete a Neutron network

        Interfaces connected to the network must be deleted first.
        Implying there must not be any VM on the network.
        """
        super(NeutronNetworks, self).delete(net)
        self.client.delete_network(net['id'])

    @staticmethod
    def resource_str(net):
        return "network {} (id {})".format(net['name'], net['id'])


class NeutronSecgroups(NeutronResources):

    def list(self):
        # filtering out default security group (cannot be removed)
        def secgroup_filter(secgroup):
            if secgroup['name'] == 'default':
                return False
            return self._owned_resource(secgroup)

        try:
            sgs = self.client.list_security_groups(
                tenant_id=self.project_id)['security_groups']
            return filter(secgroup_filter, sgs)
        except neutronclient.common.exceptions.NeutronClientException as err:
            if getattr(err, "status_code", None) == 404:
                raise exceptions.ResourceNotEnabled
            raise

    def delete(self, secgroup):
        """VMs using the security group should be deleted first."""
        super(NeutronSecgroups, self).delete(secgroup)
        self.client.delete_security_group(secgroup['id'])

    @staticmethod
    def resource_str(secgroup):
        return "security group {} (id {})".format(
            secgroup['name'], secgroup['id'])


class NeutronFloatingIps(NeutronResources):

    def list(self):
        return filter(self._owned_resource,
                      self.client.list_floatingips(
                          tenant_id=self.project_id)['floatingips'])

    def delete(self, floating_ip):
        super(NeutronFloatingIps, self).delete(floating_ip)
        self.client.delete_floatingip(floating_ip['id'])

    @staticmethod
    def resource_str(floating_ip):
        return "floating ip {} (id {})".format(
            floating_ip['floating_ip_address'], floating_ip['id'])


class NeutronLbMembers(NeutronResources):

    def list(self):
        return filter(self._owned_resource, self.client.list_members(
            tenant_id=self.project_id)['members'])

    def delete(self, member):
        super(NeutronLbMembers, self).delete(member)
        self.client.delete_member(member['id'])

    @staticmethod
    def resource_str(member):
        return "lb-member {} (id {})".format(member['address'], member['id'])


class NeutronLbPool(NeutronResources):

    def list(self):
        return filter(self._owned_resource, self.client.list_pools(
            tenant_id=self.project_id)['pools'])

    def delete(self, pool):
        super(NeutronLbPool, self).delete(pool)
        self.client.delete_pool(pool['id'])

    @staticmethod
    def resource_str(pool):
        return "lb-pool {} (id {})".format(pool['name'], pool['id'])


class NeutronLbVip(NeutronResources):

    def list(self):
        return filter(self._owned_resource, self.client.list_vips(
            tenant_id=self.project_id)['vips'])

    def delete(self, vip):
        super(NeutronLbVip, self).delete(vip)
        self.client.delete_vip(vip['id'])

    @staticmethod
    def resource_str(vip):
        return "lb-vip {} (id {})".format(vip['name'], vip['id'])


class NeutronLbHealthMonitor(NeutronResources):

    def list(self):
        return filter(self._owned_resource, self.client.list_health_monitors(
            tenant_id=self.project_id)['health_monitors'])

    def delete(self, health_monitor):
        super(NeutronLbHealthMonitor, self).delete(health_monitor)
        self.client.delete_health_monitor(health_monitor['id'])

    @staticmethod
    def resource_str(health_monitor):
        return "lb-health_monotor type {} (id {})".format(
            health_monitor['type'], health_monitor['id'])


class NeutronMeteringLabel(NeutronResources):

    def list(self):
        return filter(self._owned_resource, self.client.list_metering_labels(
            tenant_id=self.project_id)['metering_labels'])

    def delete(self, metering_label):
        super(NeutronMeteringLabel, self).delete(metering_label)
        self.client.delete_metering_label(metering_label['id'])

    @staticmethod
    def resource_str(metering_label):
        return "meter-label {} (id {})".format(
            metering_label['name'], metering_label['id'])


class NeutronFireWallPolicy(NeutronResources):

    def list(self):
        return filter(self._owned_resource, self.client.list_firewall_policies(
            tenant_id=self.project_id)['firewall_policies'])

    def delete(self, firewall_policy):
        super(NeutronFireWallPolicy, self).delete(firewall_policy)
        self.client.delete_firewall_policy(firewall_policy['id'])

    @staticmethod
    def resource_str(firewall_policy):
        return "Firewall policy {} (id {})".format(
            firewall_policy['name'], firewall_policy['id'])


class NeutronFireWallRule(NeutronResources):

    def list(self):
        return filter(self._owned_resource, self.client.list_firewall_rules(
            tenant_id=self.project_id)['firewall_rules'])

    def delete(self, firewall_rule):
        super(NeutronFireWallRule, self).delete(firewall_rule)
        self.client.delete_firewall_rule(firewall_rule['id'])

    @staticmethod
    def resource_str(firewall_rule):
        return "Firewall rule {} (id {})".format(
            firewall_rule['name'], firewall_rule['id'])


class NeutronFireWall(NeutronResources):

    def list(self):
        return filter(self._owned_resource, self.client.list_firewalls(
            tenant_id=self.project_id)['firewalls'])

    def delete(self, firewall):
        super(NeutronFireWall, self).delete(firewall)
        self.client.delete_firewall(firewall['id'])

    @staticmethod
    def resource_str(firewall):
        return "Firewall {} (id {})".format(firewall['name'], firewall['id'])


class NovaServers(base.Resources):

    def __init__(self, cloud):
        super(NovaServers, self).__init__(cloud)
        self.client = self.cloud.get_legacy_client('compute')

    """Manage nova resources"""

    def list(self):
        return self.client.servers.list()

    def delete(self, server):
        super(NovaServers, self).delete(server)
        self.client.servers.delete(server)

    def resource_str(self, server):
        return "server {} (id {})".format(server.name, server.id)


class GlanceImages(base.Resources):

    def __init__(self, cloud):
        super(GlanceImages, self).__init__(cloud)
        self.client = self.cloud.get_legacy_client('image')

    def list(self):
        return filter(self._owned_resource, self.client.images.list(
            owner=self.project_id))

    def delete(self, image):
        super(GlanceImages, self).delete(image)
        self.client.images.delete(image.id)

    def resource_str(self, image):
        return "image {} (id {})".format(image.name, image.id)

    def _owned_resource(self, res):
        # Only considering resources owned by project
        return res.owner == self.project_id


class HeatStacks(base.Resources):

    def __init__(self, cloud):
        super(HeatStacks, self).__init__(cloud)
        self.client = self.cloud.get_legacy_client('orchestration')

    def list(self):
        return self.client.stacks.list()

    def delete(self, stack):
        super(HeatStacks, self).delete(stack)
        if stack.stack_status == "DELETE_FAILED":
            self.client.stacks.abandon(stack.id)
        else:
            self.client.stacks.delete(stack.id)

    def resource_str(self, stack):
        return "stack {})".format(stack.id)


class CeilometerAlarms(base.Resources):

    def __init__(self, cloud):
        super(CeilometerAlarms, self).__init__(cloud)
        self.client = self.cloud.get_legacy_client(
            'metering', ceilometer_client)

    def list(self):
        query = [{'field': 'project_id',
                  'op': 'eq',
                  'value': self.project_id}]
        return self.client.alarms.list(q=query)

    def delete(self, alarm):
        super(CeilometerAlarms, self).delete(alarm)
        self.client.alarms.delete(alarm.alarm_id)

    def resource_str(self, alarm):
        return "alarm {}".format(alarm.name)


class KeystoneManager(object):

    """Manages Keystone queries."""

    def __init__(self, cloud, admin_role_name):
        self.cloud = cloud
        self.client = cloud.get_legacy_client('identity')
        self.admin_role_name = admin_role_name
        self.admin_role_id = None
        self.tenant_info = None

    def get_project_id(self, project_name_or_id=None):
        """Get a project by its id

        Returns:
        * ID of current project if called without parameter,
        * ID of project given as parameter if one is given.
        """

        if project_name_or_id is None:
            return self.client.tenant_id

        try:
            self.tenant_info = self.client.tenants.get(project_name_or_id)
            # If it doesn't raise an 404, project_name_or_id is
            # already the project's id
            project_id = project_name_or_id
        except api_exceptions.NotFound:
            try:
                # Can raise api_exceptions.Forbidden:
                tenants = self.client.tenants.list()
                project_id = filter(
                    lambda x: x.name == project_name_or_id, tenants)[0].id
            except IndexError:
                raise exceptions.NoSuchProject(project_name_or_id)

        if not self.tenant_info:
            self.tenant_info = self.client.tenants.get(project_id)
        return project_id

    def enable_project(self, project_id):
        logging.info("* Enabling project {}.".format(project_id))
        self.tenant_info = self.client.tenants.update(project_id, enabled=True)

    def disable_project(self, project_id):
        logging.info("* Disabling project {}.".format(project_id))
        self.tenant_info = self.client.tenants.update(project_id, enabled=False)

    def get_admin_role_id(self):
        if not self.admin_role_id:
            roles = self.client.roles.list()
            self.admin_role_id = filter(lambda x: x.name == self.admin_role_name, roles)[0].id
        return self.admin_role_id

    def become_project_admin(self, project_id):
        user_id = self.cloud.get_session().get_user_id()
        admin_role_id = self.get_admin_role_id()
        logging.info("* Granting role admin to user {} on project {}.".format(
            user_id, project_id))

        return self.client.roles.add_user_role(user_id, admin_role_id, project_id)

    def undo_become_project_admin(self, project_id):
        user_id = self.client.user_id
        admin_role_id = self.get_admin_role_id()
        logging.info("* Removing role admin to user {} on project {}.".format(
            user_id, project_id))

        return self.client.roles.remove_user_role(user_id, admin_role_id, project_id)

    def delete_project(self, project_id):
        logging.info("* Deleting project {}.".format(project_id))
        self.client.tenants.delete(project_id)


def perform_on_project(cloud, action='dump'):
    """Perform provided action on all resources of project.

    action can be: 'purge' or 'dump'
    """
    error = None
    for rc in constants.RESOURCES_CLASSES:
        try:
            resources = globals()[rc](cloud)
            res_actions = {'purge': resources.purge,
                           'dump': resources.dump}
            res_actions[action]()
        except (exceptions.EndpointNotFound,
                keystoneclient.openstack.common.apiclient.exceptions.EndpointNotFound,
                neutronclient.common.exceptions.EndpointNotFound,
                cinderclient.exceptions.EndpointNotFound,
                novaclient.exceptions.EndpointNotFound,
                heatclient.openstack.common.apiclient.exceptions.EndpointNotFound,
                exceptions.ResourceNotEnabled):
            # If service is not in Keystone's services catalog, ignoring it
            pass
        except requests.exceptions.MissingSchema as e:
            logging.warning(
                'Some resources may not have been deleted, "{!s}" is '
                'improperly configured and returned: {!r}\n'.format(rc, e))
        except (ceilometerclient.exc.InvalidEndpoint, glanceclient.exc.InvalidEndpoint) as e:
            logging.warning(
                "Unable to connect to {} endpoint : {}".format(rc, e.message))
            error = exceptions.InvalidEndpoint(rc)
        except (neutronclient.common.exceptions.NeutronClientException):
            # If service is not configured, ignoring it
            pass
    if error:
        raise error


# From Russell Heilling
# http://stackoverflow.com/questions/10551117/setting-options-from-environment-variables-when-using-argparse
class EnvDefault(argparse.Action):

    def __init__(self, envvar, required=True, default=None, **kwargs):
        # Overriding default with environment variable if available
        if envvar in os.environ:
            default = os.environ[envvar]
        if required and default:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required,
                                         **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


def parse_args():
    desc = "Purge resources from an Openstack project."
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("--verbose", action="store_true",
                        help="Makes output verbose")
    parser.add_argument("--dry-run", action="store_true",
                        help="List project's resources")
    parser.add_argument("--dont-delete-project", action="store_true",
                        help="Executes cleanup script without removing the project. "
                             "Warning: all project resources will still be deleted.")
    parser.add_argument("--region-name", action=EnvDefault, required=False,
                        envvar='OS_REGION_NAME', default=None,
                        help="Region to use. Defaults to env[OS_REGION_NAME] "
                             "or None")
    parser.add_argument("--endpoint-type", action=EnvDefault,
                        envvar='OS_ENDPOINT_TYPE', default="publicURL",
                        help="Endpoint type to use. Defaults to "
                             "env[OS_ENDPOINT_TYPE] or publicURL")
    parser.add_argument("--username", action=EnvDefault,
                        envvar='OS_USERNAME', required=True,
                        help="If --own-project is set : a user name with access to the "
                             "project being purged. If --cleanup-project is set : "
                             "a user name with admin role in project specified in --admin-project. "
                             "Defaults to env[OS_USERNAME]")
    parser.add_argument("--password", action=EnvDefault,
                        envvar='OS_PASSWORD', required=True,
                        help="The user's password. Defaults "
                             "to env[OS_PASSWORD].")
    parser.add_argument("--admin-project", action=EnvDefault,
                        envvar='OS_TENANT_NAME', required=True,
                        help="Project name used for authentication. This project "
                             "will be purged if --own-project is set. "
                             "Defaults to env[OS_TENANT_NAME].")
    parser.add_argument("--admin-role-name", required=False, default="admin",
                        help="Name of admin role. Defaults to 'admin'.")
    parser.add_argument("--auth-url", action=EnvDefault,
                        envvar='OS_AUTH_URL', required=True,
                        help="Authentication URL. Defaults to "
                             "env[OS_AUTH_URL].")
    parser.add_argument("--cleanup-project", required=False, default=None,
                        help="ID or Name of project to purge. Not required "
                             "if --own-project has been set. Using --cleanup-project "
                             "requires to authenticate with admin credentials.")
    parser.add_argument("--own-project", action="store_true",
                        help="Delete resources of the project used to "
                             "authenticate. Useful if you don't have the "
                             "admin credentials of the platform.")
    parser.add_argument("--insecure", action="store_true",
                        help="Explicitly allow all OpenStack clients to perform "
                             "insecure SSL (https) requests. The server's "
                             "certificate will not be verified against any "
                             "certificate authorities. This option should be "
                             "used with caution.")

    args = parser.parse_args()
    if not (args.cleanup_project or args.own_project):
        parser.error('Either --cleanup-project '
                     'or --own-project has to be set')
    if args.cleanup_project and args.own_project:
        parser.error('Both --cleanup-project '
                     'and --own-project can not be set')
    return args


def main():
    args = parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        # Set default log level to Warning
        logging.basicConfig(level=logging.WARNING)

    admin_cloud = os_client_config.OpenStackConfig().get_one_cloud(
        username=args.username, password=args.password,
        project_id=args.admin_project, auth_url=args.auth_url,
        endpoint_type=args.endpoint_type,
        os_metering_api_version='2',
        verify=not args.insecure, region_name=args.region_name)
    try:
        keystone_manager = KeystoneManager(
            admin_cloud, admin_role_name=args.admin_role_name)
    except api_exceptions.Unauthorized as exc:
        print("Authentication failed: {}".format(str(exc)))
        sys.exit(constants.AUTHENTICATION_FAILED_ERROR_CODE)

    remove_admin_role_after_purge = False
    disable_project_after_purge = False
    try:
        cleanup_project_id = keystone_manager.get_project_id(
            args.cleanup_project)
        if not args.own_project:
            try:
                keystone_manager.become_project_admin(cleanup_project_id)
            except api_exceptions.Conflict:
                # user was already admin on the target project.
                pass
            else:
                remove_admin_role_after_purge = True

            # If the project was enabled before the purge, do not disable it after the purge
            disable_project_after_purge = not keystone_manager.tenant_info.enabled
            if disable_project_after_purge:
                # The project is currently disabled so we need to enable it
                # in order to delete resources of the project
                keystone_manager.enable_project(cleanup_project_id)

    except api_exceptions.Forbidden as exc:
        print("Not authorized: {}".format(str(exc)))
        sys.exit(constants.NOT_AUTHORIZED_ERROR_CODE)
    except exceptions.NoSuchProject as exc:
        print("Project {} doesn't exist".format(str(exc)))
        sys.exit(constants.NO_SUCH_PROJECT_ERROR_CODE)

    # Proper cleanup
    try:
        action = "dump" if args.dry_run else "purge"
        purge_cloud = os_client_config.OpenStackConfig().get_one_cloud(
            username=args.username, password=args.password,
            project_id=cleanup_project_id, auth_url=args.auth_url,
            endpoint_type=args.endpoint_type,
            verify=not args.insecure, region_name=args.region_name)
        perform_on_project(purge_cloud, action)
    except requests.exceptions.ConnectionError as exc:
        print("Connection error: {}".format(str(exc)))
        sys.exit(constants.CONNECTION_ERROR_CODE)
    except (exceptions.DeletionFailed, exceptions.InvalidEndpoint) as exc:
        print("Deletion of {} failed".format(str(exc)))
        print("*Warning* Some resources may not have been cleaned up")
        sys.exit(constants.DELETION_FAILED_ERROR_CODE)

    if (not args.dry_run) and (not args.dont_delete_project) and (not args.own_project):
        keystone_manager.delete_project(cleanup_project_id)
    else:
        # Project is not deleted, we may want to disable the project
        # this must happen before we remove the admin role
        if disable_project_after_purge:
            keystone_manager.disable_project(cleanup_project_id)
        # We may also want to remove ourself from the purged project
        if remove_admin_role_after_purge:
            keystone_manager.undo_become_project_admin(cleanup_project_id)
    sys.exit(0)

if __name__ == "__main__":
    main()
