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

import itertools
import json as jsonutils

import httpretty
import testtools

import cinderclient

from ospurge import base
from ospurge import client
from ospurge.tests import client_fixtures

# Disable InsecurePlatformWarning which is irrelevant in unittests with
# mocked https requests and only clutters the results.
import requests
requests.packages.urllib3.disable_warnings()


USERNAME = "username"
PASSWORD = "password"
PROJECT_NAME = "project"
AUTH_URL = client_fixtures.AUTH_URL


class HttpTest(testtools.TestCase):

    def stub_url(self, method, parts=None, base_url=None, json=None, **kwargs):
        if not base_url:
            base_url = self.TEST_URL
        if json is not None:
            kwargs['body'] = jsonutils.dumps(json)
            kwargs['content_type'] = 'application/json'
        if parts:
            url = '/'.join([p.strip('/') for p in [base_url] + parts])
        else:
            url = base_url
        httpretty.register_uri(method, url, **kwargs)

    def stub_auth(self):
        self.stub_url('GET', base_url=AUTH_URL,
                      json=client_fixtures.AUTH_URL_RESPONSE)
        self.stub_url('POST', parts=['tokens'], base_url=AUTH_URL,
                      json=client_fixtures.PROJECT_SCOPED_TOKEN)
        self.stub_url('GET', parts=['roles'],
                      base_url=client_fixtures.ROLE_URL,
                      json=client_fixtures.ROLE_LIST)


class SessionTest(HttpTest):

    @httpretty.activate
    def test_init(self):
        self.stub_auth()
        session = base.Session(USERNAME, PASSWORD,
                               client_fixtures.PROJECT_ID, AUTH_URL,
                               region_name="RegionOne")
        self.assertEqual(session.token, client_fixtures.TOKEN_ID)
        self.assertEqual(session.user_id, client_fixtures.USER_ID)
        self.assertEqual(session.project_id, client_fixtures.PROJECT_ID)
        self.assertTrue(session.is_admin)

    @httpretty.activate
    def test_get_public_endpoint(self):
        self.stub_auth()
        session = base.Session(USERNAME, PASSWORD,
                               client_fixtures.PROJECT_ID, AUTH_URL,
                               region_name="RegionOne")
        endpoint = session.get_endpoint('volume')
        self.assertEqual(endpoint, client_fixtures.VOLUME_PUBLIC_ENDPOINT)
        endpoint = session.get_endpoint('image')
        self.assertEqual(endpoint, client_fixtures.IMAGE_PUBLIC_ENDPOINT)

    @httpretty.activate
    def test_get_internal_endpoint(self):
        self.stub_auth()
        session = base.Session(USERNAME, PASSWORD,
                               client_fixtures.PROJECT_ID, AUTH_URL,
                               region_name="RegionOne",
                               endpoint_type='internalURL')
        endpoint = session.get_endpoint('volume')
        self.assertEqual(endpoint, client_fixtures.VOLUME_INTERNAL_ENDPOINT)
        endpoint = session.get_endpoint('image')
        self.assertEqual(endpoint, client_fixtures.IMAGE_INTERNAL_ENDPOINT)

# Abstract class


class TestResourcesBase(HttpTest):

    """Creates a session object that can be used to test any service."""
    @httpretty.activate
    def setUp(self):
        super(TestResourcesBase, self).setUp()
        self.stub_auth()
        self.session = base.Session(USERNAME, PASSWORD,
                                    client_fixtures.PROJECT_ID, AUTH_URL,
                                    region_name="RegionOne")
        # We can't add other stubs in subclasses setUp because
        # httpretty.dactivate() is called after this set_up (so during the
        # super call to this method in subclasses). and extra stubs will not
        # work. if you need extra stubs to be done during setUp, write them
        # in an 'extra_set_up' method. instead of in the subclasses setUp
        if hasattr(self, 'extra_set_up'):
            self.extra_set_up()

    @httpretty.activate
    def _test_list(self):
        self.stub_auth()
        self.stub_list()
        elts = list(self.resources.list())
        # Some Openstack resources use attributes, while others use dicts
        try:
            ids = [elt.id for elt in elts]
        except AttributeError:
            ids = [elt['id'] for elt in elts]
        self.assertEqual(self.IDS, ids)

    @httpretty.activate
    def _test_delete(self):
        self.stub_auth()
        self.stub_list()
        self.stub_delete()
        elts = self.resources.list()
        # List() must return an iterable
        res = itertools.islice(elts, 1).next()
        self.resources.delete(res)  # Checks this doesn't raise an exception


class TestSwiftBase(TestResourcesBase):
    TEST_URL = client_fixtures.STORAGE_PUBLIC_ENDPOINT


class TestSwiftResources(TestSwiftBase):

    @httpretty.activate
    def test_list_containers(self):
        self.stub_url('GET', json=client_fixtures.STORAGE_CONTAINERS_LIST)
        swift = client.SwiftResources(self.session)
        conts = list(swift.list_containers())
        self.assertEqual(conts, client_fixtures.STORAGE_CONTAINERS)


class TestSwiftObjects(TestSwiftBase):

    def stub_list(self):
        self.stub_url('GET', json=client_fixtures.STORAGE_CONTAINERS_LIST)
        self.stub_url('GET', parts=[client_fixtures.STORAGE_CONTAINERS[0]],
                      json=client_fixtures.STORAGE_OBJECTS_LIST_0),
        self.stub_url('GET', parts=[client_fixtures.STORAGE_CONTAINERS[1]],
                      json=client_fixtures.STORAGE_OBJECTS_LIST_1)

    def stub_delete(self):
        for obj in client_fixtures.STORAGE_OBJECTS:
            self.stub_url('DELETE', parts=[obj['container'], obj['name']])

    def setUp(self):
        super(TestSwiftObjects, self).setUp()
        self.resources = client.SwiftObjects(self.session)

    @httpretty.activate
    def test_list(self):
        self.stub_list()
        objs = list(self.resources.list())
        self.assertEqual(client_fixtures.STORAGE_OBJECTS, objs)

    def test_delete(self):
        self._test_delete()


class TestSwiftContainers(TestSwiftBase):

    def stub_list(self):
        self.stub_url('GET', json=client_fixtures.STORAGE_CONTAINERS_LIST)

    def stub_delete(self):
        self.stub_url('DELETE', parts=[client_fixtures.STORAGE_CONTAINERS[0]])

    def setUp(self):
        super(TestSwiftContainers, self).setUp()
        self.resources = client.SwiftContainers(self.session)

    @httpretty.activate
    def test_list(self):
        self.stub_list()
        conts = list(self.resources.list())
        self.assertEqual(conts, client_fixtures.STORAGE_CONTAINERS)

    def test_delete(self):
        self._test_delete()


class TestCinderBase(TestResourcesBase):
    TEST_URL = client_fixtures.VOLUME_PUBLIC_ENDPOINT


class TestCinderSnapshots(TestCinderBase):
    IDS = client_fixtures.SNAPSHOTS_IDS

    def stub_list(self):
        self.stub_url('GET', parts=['snapshots', 'detail'],
                      json=client_fixtures.SNAPSHOTS_LIST)

    def stub_delete(self):
        self.stub_url(
            'DELETE', parts=['snapshots', client_fixtures.SNAPSHOTS_IDS[0]])

    def setUp(self):
        super(TestCinderSnapshots, self).setUp()
        self.resources = client.CinderSnapshots(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestCinderVolumes(TestCinderBase):
    IDS = client_fixtures.VOLUMES_IDS

    def stub_list(self):
        self.stub_url('GET', parts=['volumes', 'detail'],
                      json=client_fixtures.VOLUMES_LIST)

    def stub_delete(self):
        self.stub_url(
            'DELETE', parts=['volumes', client_fixtures.VOLUMES_IDS[0]])

    def setUp(self):
        super(TestCinderVolumes, self).setUp()
        self.resources = client.CinderVolumes(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestCinderBackups(TestCinderBase):
    IDS = client_fixtures.VOLUME_BACKUP_IDS

    def stub_list(self):
        self.stub_url('GET', parts=['backups', 'detail'],
                      json=client_fixtures.VOLUME_BACKUPS_LIST)

    def stub_delete(self):
        self.stub_url(
            'DELETE', parts=['backups', self.IDS[0]])

    def setUp(self):
        super(TestCinderBackups, self).setUp()
        # Make sure tests work whatever version of cinderclient
        self.versionstring_bak = cinderclient.version_info.version_string
        cinderclient.version_info.version_string = lambda: '1.4.0'
        self.session.is_admin = True
        self.resources = client.CinderBackups(self.session)

    def tearDown(self):
        super(TestCinderBackups, self).tearDown()
        cinderclient.version_info.version_string = self.versionstring_bak

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()

    def test_empty_list(self):
        self.stub_auth()
        versionstring_bak = cinderclient.version_info.version_string
        cinderclient.version_info.version_string = lambda: '1.1.1'
        self.assertEqual(self.resources.list(), [])
        cinderclient.version_info.version_string = versionstring_bak


class TestNeutronBase(TestResourcesBase):
    TEST_URL = client_fixtures.NETWORK_PUBLIC_ENDPOINT

    # Used both in TestNeutronRouters and TestNeutronInterfaces
    def stub_list_routers(self):
        self.stub_url(
            'GET',
            parts=[
                'v2.0',
                'routers.json?tenant_id=%s' % client_fixtures.PROJECT_ID
            ],
            json=client_fixtures.ROUTERS_LIST
        )


class TestNeutronRouters(TestNeutronBase):
    IDS = client_fixtures.ROUTERS_IDS

    def stub_list(self):
        self.stub_list_routers()

    def stub_delete(self):
        routid = client_fixtures.ROUTERS_IDS[0]
        self.stub_url('PUT', parts=['v2.0', 'routers', "%s.json" % routid],
                      json=client_fixtures.ROUTER_CLEAR_GATEWAY)
        self.stub_url('DELETE', parts=['v2.0', 'routers', "%s.json" % routid],
                      json={})

    def setUp(self):
        super(TestNeutronRouters, self).setUp()
        self.resources = client.NeutronRouters(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestNeutronInterfaces(TestNeutronBase):
    IDS = client_fixtures.PORTS_IDS

    def stub_list(self):
        self.stub_list_routers()
        self.stub_url('GET', parts=['v2.0', "ports.json?device_id={}".format(client_fixtures.ROUTERS_IDS[0])],
                      json=client_fixtures.ROUTER0_PORTS)
        self.stub_url('GET', parts=['v2.0', "ports.json?device_id={}".format(client_fixtures.ROUTERS_IDS[1])],
                      json=client_fixtures.ROUTER1_PORTS)

    def stub_delete(self):
        for rout_id in client_fixtures.ROUTERS_IDS:
            self.stub_url('PUT', parts=['v2.0', 'routers', rout_id,
                                        'remove_router_interface.json'],
                          json=client_fixtures.REMOVE_ROUTER_INTERFACE)

    def setUp(self):
        super(TestNeutronInterfaces, self).setUp()
        self.resources = client.NeutronInterfaces(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestNeutronPorts(TestNeutronBase):
    IDS = [client_fixtures.UNBOUND_PORT_ID]

    def stub_list(self):
        self.stub_url(
            'GET',
            parts=[
                'v2.0',
                'ports.json?tenant_id=%s' % client_fixtures.PROJECT_ID
            ],
            json=client_fixtures.NEUTRON_PORTS)

    def stub_delete(self):
        port_id = client_fixtures.UNBOUND_PORT_ID
        self.stub_url('DELETE', parts=['v2.0', 'ports', "{}.json".format(port_id)],
                      json={})

    def setUp(self):
        super(TestNeutronPorts, self).setUp()
        self.resources = client.NeutronPorts(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestNeutronNetworks(TestNeutronBase):
    IDS = client_fixtures.NETWORKS_IDS

    def stub_list(self):
        self.stub_url(
            'GET',
            parts=[
                'v2.0',
                'networks.json?tenant_id=%s' % client_fixtures.PROJECT_ID
            ],
            json=client_fixtures.NETWORKS_LIST
        )

    def stub_delete(self):
        for net_id in client_fixtures.NETWORKS_IDS:
            self.stub_url('DELETE', parts=['v2.0', 'networks',
                                           "{}.json".format(net_id)], json={})

    def setUp(self):
        super(TestNeutronNetworks, self).setUp()
        self.resources = client.NeutronNetworks(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestNeutronSecgroups(TestNeutronBase):
    IDS = client_fixtures.SECGROUPS_IDS

    def stub_list(self):
        self.stub_url(
            'GET',
            parts=[
                'v2.0',
                'security-groups.json?tenant_id=%s' % client_fixtures.PROJECT_ID
            ],
            json=client_fixtures.SECGROUPS_LIST)

    def stub_delete(self):
        for secgroup_id in client_fixtures.SECGROUPS_IDS:
            self.stub_url('DELETE', parts=['v2.0', 'security-groups',
                                           "{}.json".format(secgroup_id)], json={})

    def setUp(self):
        super(TestNeutronSecgroups, self).setUp()
        self.resources = client.NeutronSecgroups(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestNeutronFloatingIps(TestNeutronBase):
    IDS = client_fixtures.FLOATING_IPS_IDS

    def stub_list(self):
        self.stub_url(
            'GET',
            parts=[
                'v2.0',
                'floatingips.json?tenant_id=%s' % client_fixtures.PROJECT_ID
            ],
            json=client_fixtures.FLOATING_IPS_LIST)

    def stub_delete(self):
        ip_id = client_fixtures.FLOATING_IPS_IDS[0]
        self.stub_url('DELETE', parts=['v2.0', 'floatingips', "{}.json".format(ip_id)], json={})

    def setUp(self):
        super(TestNeutronFloatingIps, self).setUp()
        self.resources = client.NeutronFloatingIps(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestNeutronFireWallRule(TestNeutronBase):
    IDS = client_fixtures.FIREWALL_RULE_IDS

    def stub_list(self):
        self.stub_url(
            'GET',
            parts=[
                'v2.0',
                'fw/firewall_rules.json?tenant_id=%s' % client_fixtures.PROJECT_ID
            ],
            json=client_fixtures.FIREWALL_RULE_LIST)

    def stub_delete(self):
        firewall_rule_id = client_fixtures.FIREWALL_RULE_IDS[0]
        self.stub_url('DELETE', parts=['v2.0', 'fw/firewall_rules', "{}.json".format(firewall_rule_id)], json={})

    def setUp(self):
        super(TestNeutronFireWallRule, self).setUp()
        self.resources = client.NeutronFireWallRule(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestNeutronFireWallPolicy(TestNeutronBase):
    IDS = client_fixtures.FIREWALL_POLICY_IDS

    def stub_list(self):
        self.stub_url(
            'GET',
            parts=[
                'v2.0',
                'fw/firewall_policies.json?tenant_id=%s' % client_fixtures.PROJECT_ID
            ],
            json=client_fixtures.FIREWALL_POLICY_LIST)

    def stub_delete(self):
        firewall_policy_id = client_fixtures.FIREWALL_POLICY_IDS[0]
        self.stub_url('DELETE', parts=['v2.0', 'fw/firewall_policies', "{}.json".format(firewall_policy_id)], json={})

    def setUp(self):
        super(TestNeutronFireWallPolicy, self).setUp()
        self.resources = client.NeutronFireWallPolicy(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestNeutronFireWall(TestNeutronBase):
    IDS = client_fixtures.FIREWALL_IDS

    def stub_list(self):
        self.stub_url(
            'GET',
            parts=[
                'v2.0',
                'fw/firewalls.json?tenant_id=%s' % client_fixtures.PROJECT_ID
            ],
            json=client_fixtures.FIREWALL_LIST)

    def stub_delete(self):
        firewall_id = client_fixtures.FIREWALL_IDS[0]
        self.stub_url('DELETE', parts=['v2.0', 'fw/firewalls', "{}.json".format(firewall_id)], json={})

    def setUp(self):
        super(TestNeutronFireWall, self).setUp()
        self.resources = client.NeutronFireWall(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestNeutronMeteringLabel(TestNeutronBase):
    IDS = client_fixtures.METERING_LABEL_IDS

    def stub_list(self):
        self.stub_url(
            'GET',
            parts=[
                'v2.0',
                'metering/metering-labels.json?tenant_id=%s' % client_fixtures.PROJECT_ID
            ],
            json=client_fixtures.METERING_LABEL_LIST)

    def stub_delete(self):
        firewall_id = client_fixtures.METERING_LABEL_IDS[0]
        self.stub_url('DELETE', parts=['v2.0', 'metering/metering-labels', "{}.json".format(firewall_id)], json={})

    def setUp(self):
        super(TestNeutronMeteringLabel, self).setUp()
        self.resources = client.NeutronMeteringLabel(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestNeutronLbMembers(TestNeutronBase):
    IDS = client_fixtures.LBAAS_MEMBER_IDS

    def stub_list(self):
        self.stub_url(
            'GET',
            parts=[
                'v2.0',
                'lb/members.json?tenant_id=%s' % client_fixtures.PROJECT_ID
            ],
            json=client_fixtures.LBAAS_MEMBER_LIST)

    def stub_delete(self):
        lb_member_id = client_fixtures.LBAAS_MEMBER_IDS[0]
        self.stub_url('DELETE', parts=['v2.0', 'lb/members', "{}.json".format(lb_member_id)], json={})

    def setUp(self):
        super(TestNeutronLbMembers, self).setUp()
        self.resources = client.NeutronLbMembers(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestNeutronLbVip(TestNeutronBase):
    IDS = client_fixtures.LBAAS_VIP_IDS

    def stub_list(self):
        self.stub_url(
            'GET',
            parts=[
                'v2.0',
                'lb/vips.json?tenant_id=%s' % client_fixtures.PROJECT_ID
            ],
            json=client_fixtures.LBAAS_VIP_LIST)

    def stub_delete(self):
        lb_vip_id = client_fixtures.LBAAS_VIP_IDS[0]
        self.stub_url('DELETE', parts=['v2.0', 'lb/vips', "{}.json".format(lb_vip_id)], json={})

    def setUp(self):
        super(TestNeutronLbVip, self).setUp()
        self.resources = client.NeutronLbVip(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestNeutronLbHealthMonitor(TestNeutronBase):
    IDS = client_fixtures.LBAAS_HEALTHMONITOR_IDS

    def stub_list(self):
        self.stub_url(
            'GET',
            parts=[
                'v2.0',
                'lb/health_monitors.json?tenant_id=%s' % client_fixtures.PROJECT_ID
            ],
            json=client_fixtures.LBAAS_HEALTHMONITOR_LIST)

    def stub_delete(self):
        lb_healthmonitor_id = client_fixtures.LBAAS_HEALTHMONITOR_IDS[0]
        self.stub_url('DELETE', parts=['v2.0', 'lb/health_monitors', "{}.json".format(lb_healthmonitor_id)], json={})

    def setUp(self):
        super(TestNeutronLbHealthMonitor, self).setUp()
        self.resources = client.NeutronLbHealthMonitor(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestNeutronLbPool(TestNeutronBase):
    IDS = client_fixtures.LBAAS_POOL_IDS

    def stub_list(self):
        self.stub_url(
            'GET',
            parts=[
                'v2.0',
                'lb/pools.json?tenant_id=%s' % client_fixtures.PROJECT_ID
            ],
            json=client_fixtures.LBAAS_POOL_LIST)

    def stub_delete(self):
        lb_pool_id = client_fixtures.LBAAS_POOL_IDS[0]
        self.stub_url('DELETE', parts=['v2.0', 'lb/pools', "{}.json".format(lb_pool_id)], json={})

    def setUp(self):
        super(TestNeutronLbPool, self).setUp()
        self.resources = client.NeutronLbPool(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestNovaServers(TestResourcesBase):
    TEST_URL = client_fixtures.COMPUTE_PUBLIC_ENDPOINT
    IDS = client_fixtures.SERVERS_IDS

    def stub_list(self):
        self.stub_url('GET', parts=['servers', 'detail'],
                      json=client_fixtures.SERVERS_LIST)

    def stub_delete(self):
        self.stub_url(
            'DELETE', parts=['servers', client_fixtures.SERVERS_IDS[0]])

    def setUp(self):
        super(TestNovaServers, self).setUp()
        self.resources = client.NovaServers(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestGlanceImages(TestResourcesBase):
    TEST_URL = client_fixtures.IMAGE_PUBLIC_ENDPOINT
    IDS = client_fixtures.IMAGES_IDS

    def stub_list(self):
        self.stub_url('GET', parts=['v2', 'images?limit=20', 'detail'],
                      json=client_fixtures.IMAGES_LIST)
        self.stub_url('GET', parts=['v2', 'schemas', 'image'],
                      json=client_fixtures.IMAGES_LIST)

    def stub_delete(self):
        self.stub_url(
            'DELETE', parts=['v2', 'images', client_fixtures.IMAGES_IDS[0]])

    def setUp(self):
        super(TestGlanceImages, self).setUp()
        self.resources = client.GlanceImages(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestCeilometerAlarms(TestResourcesBase):
    TEST_URL = client_fixtures.METERING_PUBLIC_ENDPOINT

    def extra_set_up(self):
        self.stub_url(
            'GET', base_url=AUTH_URL, json=client_fixtures.AUTH_URL_RESPONSE)
        self.resources = client.CeilometerAlarms(self.session)

    def stub_list(self):
        self.stub_url('GET', parts=['v2', 'alarms'],
                      json=client_fixtures.ALARMS_LIST)

    def stub_delete(self):
        self.stub_url(
            'DELETE', parts=['v2', 'alarms', client_fixtures.ALARMS_IDS[0]])

    def setUp(self):
        super(TestCeilometerAlarms, self).setUp()

    @httpretty.activate
    def test_list(self):
        self.stub_auth()
        self.stub_list()
        elts = list(self.resources.list())
        ids = [elt.alarm_id for elt in elts]
        self.assertEqual(client_fixtures.ALARMS_IDS, ids)

    def test_delete(self):
        self._test_delete()


class TestHeatStacks(TestResourcesBase):
    TEST_URL = client_fixtures.ORCHESTRATION_PUBLIC_ENDPOINT
    IDS = client_fixtures.STACKS_IDS

    def stub_list(self):
        self.stub_url('GET', parts=['stacks?'],
                      json=client_fixtures.STACKS_LIST)

    def stub_delete(self):
        self.stub_url(
            'DELETE', parts=['stacks', client_fixtures.STACKS_IDS[0]])

    def setUp(self):
        super(TestHeatStacks, self).setUp()
        self.resources = client.HeatStacks(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()

    @httpretty.activate
    def test_abandon(self):
        self.stub_auth()
        self.stub_list()
        get_result = {'stack': client_fixtures.STACKS_LIST['stacks'][1]}
        location = '%s/stacks/stack2/%s' % (self.TEST_URL,
                                            client_fixtures.STACKS_IDS[1])
        self.stub_url(
            'GET', parts=['stacks', client_fixtures.STACKS_IDS[1]],
            json=get_result, location=location)
        self.stub_url(
            'DELETE',
            parts=['stacks', 'stack2', client_fixtures.STACKS_IDS[1],
                   'abandon'])
        elts = list(self.resources.list())
        self.resources.delete(elts[1])
