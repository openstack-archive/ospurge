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
import itertools
import logging
import os
from requests.exceptions import ConnectionError
import sys
import time

from ceilometerclient.v2 import client as ceilometer_client
import cinderclient.exceptions
from cinderclient.v1 import client as cinder_client
from glanceclient.v1 import client as glance_client
from keystoneclient.apiclient import exceptions as api_exceptions
from keystoneclient.v2_0 import client as keystone_client
import neutronclient.common.exceptions
from neutronclient.v2_0 import client as neutron_client
import novaclient.exceptions
from novaclient.v1_1 import client as nova_client
from swiftclient import client as swift_client

RETRIES = 3
TIMEOUT = 5 # 5 seconds timeout between retries

class EndpointNotFound(Exception):
    pass

class NoSuchProject(Exception):
    ERROR_CODE = 2

AUTHENTICATION_FAILED_ERROR_CODE = 3

class DeletionFailed(Exception):
    ERROR_CODE = 4

CONNECTION_ERROR_CODE = 5

NOT_AUTHORIZED = 6


# Available resources classes

RESOURCES_CLASSES = ['CinderSnapshots',
                     'NovaServers',
                     'NeutronFloatingIps',
                     'NeutronInterfaces',
                     'NeutronRouters',
                     'NeutronNetworks',
                     'NeutronSecgroups',
                     'GlanceImages',
                     'SwiftObjects',
                     'SwiftContainers',
                     'CinderVolumes',
                     'CeilometerAlarms']


### Decorators

def retry(service_name):
    def factory(func):
        """Decorator allowing to retry in case of failure"""
        def wrapper(*args, **kwargs):
            n = 0
            while True :
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if n == RETRIES:
                        raise DeletionFailed(service_name)
                    n += 1
                    logging.info("* Deletion failed - "
                                 "Retrying in {} seconds - "
                                 "Retry count {}".format(TIMEOUT, n))
                    time.sleep(TIMEOUT)
        return wrapper
    return factory



### Classes

class Session(object):
    """
    A Session stores information that can be user by the different
    Openstack Clients. The most important data is:
    * self.token - The Openstack token to be used accross services;
    * self.catalog - Allowing to retrieve services' endpoints.
    """

    def __init__(self, username, password, project_id,
                 auth_url, endpoint_type="publicURL"):
        client = keystone_client.Client(
            username=username, password=password,
            tenant_id=project_id, auth_url=auth_url)
        # Storing username, password, project_id and auth_url for
        # use by clients libraries that cannot use an existing token.
        self.username = username
        self.password = password
        self.project_id = project_id
        self.auth_url = auth_url
        # Session variables to be used by clients when possible
        self.token = client.auth_token
        self.user_id = client.user_id
        self.project_name = client.project_name
        self.endpoint_type = endpoint_type
        self.catalog = client.service_catalog.get_endpoints()

    def get_endpoint(self, service_type):
        try:
            return self.catalog[service_type][0][self.endpoint_type]
        except KeyError:
            # Endpoint could not be found
            raise EndpointNotFound(service_type)


class Resources(object):
    """
    Abstract base class for all resources to be removed.
    """
    def __init__(self, session):
        self.session = session

    def list(self):
        pass

    def delete(self, resource):
        """
        Displays informational message about a resource deletion.
        """
        logging.info("* Deleting {}.".format(self.resource_str(resource)))

    def purge(self):
        "Delete all resources."
        c_name = self.__class__.__name__
        logging.info("* Purging {}".format(c_name))
        for resource in self.list():
            retry(c_name)(self.delete)(resource)

    def dump(self):
        "Display all available resources."
        c_name = self.__class__.__name__
        print "* Resources type: {}".format(c_name)
        for resource in self.list():
            print self.resource_str(resource)
        print ""


class SwiftResources(Resources):

    def __init__(self, session):
        super(SwiftResources, self).__init__(session)
        self.endpoint = self.session.get_endpoint("object-store")
        self.token = self.session.token

    # This method is used to retrieve Objects as well as Containers.
    def list_containers(self):
        containers = swift_client.get_account(self.endpoint, self.token)[1]
        return (cont['name'] for cont in containers)

class SwiftObjects(SwiftResources):

    def list(self):
        swift_objects = []
        for cont in self.list_containers():
            objs = [{'container': cont, 'name': obj['name']} for obj in
                    swift_client.get_container(self.endpoint, self.token, cont)[1]]
            swift_objects.extend(objs)
        return swift_objects

    def delete(self, obj):
        super(SwiftObjects, self).delete(obj)
        swift_client.delete_object(self.endpoint, token=self.token,
                                   container=obj['container'], name=obj['name'])

    def resource_str(self, obj):
        return "object {} in container {}".format(obj['name'], obj['container'])


class SwiftContainers(SwiftResources):

    def list(self):
        return self.list_containers()

    def delete(self, container):
        """Container must be empty for deletion to succeed."""
        super(SwiftContainers, self).delete(container)
        swift_client.delete_container(self.endpoint, self.token, container)

    def resource_str(self, obj):
        return "container {}".format(obj)


class CinderResources(Resources):
    def __init__(self, session):
        super(CinderResources, self).__init__(session)
        # Cinder client library can't use an existing token. When
        # using this library, we have to reauthenticate.
        self.client = cinder_client.Client(
            session.username, session.password,
            session.project_name, session.auth_url,
            endpoint_type=session.endpoint_type)


class CinderSnapshots(CinderResources):
    def list(self):
        return self.client.volume_snapshots.list()

    def delete(self, snap):
        super(CinderResources, self).delete(snap)
        self.client.volume_snapshots.delete(snap)

    def resource_str(self, snap):
        return "snapshot {} (id {})".format(snap.display_name, snap.id)


class CinderVolumes(CinderResources):
    def list(self):
        return self.client.volumes.list()

    def delete(self, vol):
        """Snapshots created from the volume must be deleted first"""
        super(CinderVolumes, self).delete(vol)
        self.client.volumes.delete(vol)

    def resource_str(self, vol):
        return "volume {} (id {})".format(vol.display_name, vol.id)


class NeutronResources(Resources):
    def __init__(self, session):
        super(NeutronResources, self).__init__(session)
        self.client = neutron_client.Client(
            username=session.username, password=session.password,
            tenant_id=session.project_id, auth_url=session.auth_url,
            endpoint_type=session.endpoint_type)
        self.project_id = session.project_id

    # This method is used for routers and interfaces removal
    def list_routers(self):
        return filter(self._owned_resource, self.client.list_routers()['routers'])

    def _owned_resource(self, res):
        # Only considering resources owned by project
        return res['tenant_id'] == self.project_id


class NeutronRouters(NeutronResources):

    def list(self):
        return self.list_routers()

    def delete(self, router):
        """interfaces must be deleted first"""
        super(NeutronRouters, self).delete(router)
        # Remove router gateway prior to remove the router itself
        self.client.remove_gateway_router(router['id'])
        self.client.delete_router(router['id'])

    def resource_str(self, router):
        return "router {} (id {})".format(router['name'], router['id'])


class NeutronInterfaces(NeutronResources):

    def list(self):
        def get_ports(router):
            # Only considering "router_interface" ports (not gateways)
            ports = [port for port in
                     self.client.list_ports(device_id=router['id'])['ports']
                     if port["device_owner"] == "network:router_interface"]
            return [{'router_id': router['id'], 'interface_id': port['id']}
                    for port in ports ]
        interfaces = [get_ports(rout) for rout in self.list_routers()]
        return itertools.chain(*interfaces)

    def delete(self, interface):
        super(NeutronInterfaces, self).delete(interface)
        self.client.remove_interface_router(interface['router_id'],
                                            {'port_id':interface['interface_id']})

    def resource_str(self, interface):
        return "interfaces {} (id)".format(interface['interface_id'])

class NeutronNetworks(NeutronResources):

    def list(self):
        return filter(self._owned_resource,
                      self.client.list_networks()['networks'])

    def delete(self, net):
        """
        Interfaces connected to the network must be deleted first.
        Implying there must not be any VM on the network.
        """
        super(NeutronNetworks, self).delete(net)
        self.client.delete_network(net['id'])

    def resource_str(self, net):
        return "network {} (id {})".format(net['name'], net['id'])

class NeutronSecgroups(NeutronResources):

    def list(self):
        # filtering out default security group (cannot be removed)
        def secgroup_filter(secgroup):
            if secgroup['name'] == 'default':
                return False
            return self._owned_resource(secgroup)

        return filter(secgroup_filter,
                      self.client.list_security_groups()['security_groups'])

    def delete(self, secgroup):
        """VMs using the security group should be deleted first"""
        super(NeutronSecgroups, self).delete(secgroup)
        self.client.delete_security_group(secgroup['id'])

    def resource_str(self, secgroup):
        return "security group {} (id {})".format(
            secgroup['name'], secgroup['id'])


class NeutronFloatingIps(NeutronResources):
    def list(self):
        return filter(self._owned_resource,
                      self.client.list_floatingips()['floatingips'])

    def delete(self, floating_ip):
        super(NeutronFloatingIps, self).delete(floating_ip)
        self.client.delete_floatingip(floating_ip['id'])

    def resource_str(self, floating_ip):
        return "floating ip {} (id {})".format(
            floating_ip['floating_ip_address'], floating_ip['id'])


class NovaServers(Resources):
    def __init__(self, session):
        super(NovaServers, self).__init__(session)
        self.client = nova_client.Client(
            session.username, session.password,
            session.project_name, auth_url=session.auth_url,
            endpoint_type=session.endpoint_type)
        self.project_id = session.project_id

    """Manage nova resources"""
    def list(self):
        return self.client.servers.list()

    def delete(self, server):
        super(NovaServers, self).delete(server)
        self.client.servers.delete(server)

    def resource_str(self, server):
        return "server {} (id {})".format(server.name, server.id)


class GlanceImages(Resources):
    def __init__(self, session):
        self.client = glance_client.Client(
            endpoint=session.get_endpoint("image"),
            token=session.token)
        self.project_id = session.project_id

    def list(self):
        return filter(self._owned_resource, self.client.images.list())

    def delete(self, image):
        super(GlanceImages, self).delete(image)
        self.client.images.delete(image.id)

    def resource_str(self, image):
        return "image {} (id {})".format(image.name, image.id)

    def _owned_resource(self, res):
        # Only considering resources owned by project
        return res.owner == self.project_id


class CeilometerAlarms(Resources):

    def __init__(self, session):
        # Ceilometer Client needs a method that returns the token
        def get_token():
            return session.token
        self.client = ceilometer_client.Client(
            endpoint=session.get_endpoint("metering"),
            token=get_token)
        self.project_id = session.project_id

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
    """Manages Keystone queries"""

    def __init__(self, username, password, project, auth_url):
        self.client = keystone_client.Client(
            username=username, password=password,
            tenant_name=project, auth_url=auth_url)

    def get_project_id(self, project_name_or_id):
        try:
            self.client.tenants.get(project_name_or_id)
            # If it doesn't raise an 404, project_name_or_id is
            # already the project's id
            project_id = project_name_or_id
        except api_exceptions.NotFound:
            try:
                tenants = self.client.tenants.list() # Can raise api_exceptions.Forbidden:
                project_id = filter(lambda x : x.name==project_name_or_id, tenants)[0].id
            except IndexError:
                raise NoSuchProject(project_name_or_id)
        return project_id

    def become_project_admin(self, project_id):
        user_id = self.client.user_id
        logging.info("* Granting role admin to user {} on project {}.".format(
                user_id, project_id))

        roles = self.client.roles.list()
        role_id = filter(lambda x : x.name=="admin", roles)[0].id
        try:
            return self.client.roles.add_user_role(user_id, role_id, project_id)
        except api_exceptions.Conflict:
            # user is already admin on the target project
            pass

    def delete_project(self, project_id):
        logging.info("* Deleting project {}.".format(project_id))
        self.client.tenants.delete(project_id)


def _perform_on_project(admin_name, password, project, auth_url,
                        endpoint_type='publicURL', action='dump'):
    """
    Perform provided action on all resources of project.
    action can be: 'purge' or 'dump'
    """
    session = Session(admin_name, password, project,
                      auth_url, endpoint_type)
    for rc in RESOURCES_CLASSES:
        try:
            resources = globals()[rc](session)
            res_actions = { 'purge': resources.purge,
                            'dump': resources.dump }
            res_actions[action]()
        except (EndpointNotFound,
                neutronclient.common.exceptions.EndpointNotFound,
                cinderclient.exceptions.EndpointNotFound,
                novaclient.exceptions.EndpointNotFound):
            # If service is not in Keystone's services catalog, ignoring it
            pass


def purge_project(admin_name, password, project, auth_url,
                  endpoint_type='publicURL'):
    """
    project is the project that will be purged.

    Warning: admin must have access to the project.
    """
    _perform_on_project(admin_name, password, project, auth_url,
                        endpoint_type, "purge")


def list_resources(admin_name, password, project, auth_url,
                   endpoint_type='publicURL'):
    """
    Listing resources of given project.
    """
    _perform_on_project(admin_name, password, project, auth_url,
                        endpoint_type, "dump")


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
                        help="Executes cleanup script without removing the project. "\
                             "Warning: all project resources will still be deleted.")
    parser.add_argument("--endpoint-type", action=EnvDefault,
                        envvar='OS_ENDPOINT_TYPE', default="publicURL",
                        help="Endpoint type to use. Defaults to " \
                             "env[OS_ENDPOINT_TYPE] or publicURL")
    parser.add_argument("--username", action=EnvDefault,
                        envvar='OS_USERNAME', required=True,
                        help="A user name with access to the " \
                             "project being purged. Defaults " \
                             "to env[OS_USERNAME]")
    parser.add_argument("--password", action=EnvDefault,
                        envvar='OS_PASSWORD', required=True,
                        help="The user's password. Defaults "
                             "to env[OS_PASSWORD].")
    parser.add_argument("--admin-project", action=EnvDefault,
                        envvar='OS_TENANT_NAME', required=True,
                        help="Name of a project the user is admin on. "\
                             "Defaults to env[OS_TENANT_NAME].")
    parser.add_argument("--auth-url", action=EnvDefault,
                        envvar='OS_AUTH_URL', required=True,
                        help="Authentication URL. Defaults to " \
                             "env[OS_AUTH_URL].")
    parser.add_argument("--cleanup-project", required=True,
                        help="ID or Name of project to purge")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        # Set default log level to Warning
        logging.basicConfig(level=logging.WARNING)

    try:
        keystone_manager = KeystoneManager(args.username, args.password,
                                           args.admin_project, args.auth_url)
    except api_exceptions.Unauthorized as exc:
        print "Authentication failed: {}".format(str(exc))
        sys.exit(AUTHENTICATION_FAILED_ERROR_CODE)

    try:
        cleanup_project_id = keystone_manager.get_project_id(args.cleanup_project)
        keystone_manager.become_project_admin(cleanup_project_id)
    except api_exceptions.Forbidden as exc:
        print "Not authorized: {}".format(str(exc))
        sys.exit(NOT_AUTHORIZED)
    except NoSuchProject as exc:
        print "Project {} doesn't exist".format(str(exc))
        sys.exit(NoSuchProject.ERROR_CODE)

    try:
        if args.dry_run:
            list_resources(args.username, args.password, cleanup_project_id,
                           args.auth_url, args.endpoint_type)
        else:
            purge_project(args.username, args.password, cleanup_project_id,
                          args.auth_url, args.endpoint_type)
    except ConnectionError as exc:
        print "Connection error: {}".format(str(exc))
        sys.exit(CONNECTION_ERROR_CODE)
    except DeletionFailed as exc:
        print "Deletion of {} failed".format(str(exc))
        sys.exit(DeletionFailed.ERROR_CODE)

    if (not args.dry_run) and (not args.dont_delete_project):
        keystone_manager.delete_project(cleanup_project_id)
    sys.exit(0)

if __name__ == "__main__":
    main()

