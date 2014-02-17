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

import client_fixtures
from ospurge import ospurge

USERNAME = "username"
PASSWORD = "password"
PROJECT_NAME = "project"
AUTH_URL = "http://localhost:5000/v2.0"

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
        self.stub_url('POST', parts=['tokens'], base_url=AUTH_URL,
                      json=client_fixtures.PROJECT_SCOPED_TOKEN)


class SessionTest(HttpTest):
    @httpretty.activate
    def test_init(self):
        self.stub_auth()
        session = ospurge.Session(USERNAME, PASSWORD,
                                   client_fixtures.PROJECT_ID, AUTH_URL)
        self.assertEqual(session.token, client_fixtures.TOKEN_ID)
        self.assertEqual(session.user_id, client_fixtures.USER_ID)
        self.assertEqual(session.project_id, client_fixtures.PROJECT_ID)

    @httpretty.activate
    def test_get_public_endpoint(self):
        self.stub_auth()
        session = ospurge.Session(USERNAME, PASSWORD,
                                   client_fixtures.PROJECT_ID, AUTH_URL)
        endpoint = session.get_endpoint('volume')
        self.assertEqual(endpoint, client_fixtures.VOLUME_PUBLIC_ENDPOINT)
        endpoint = session.get_endpoint('image')
        self.assertEqual(endpoint, client_fixtures.IMAGE_PUBLIC_ENDPOINT)

    @httpretty.activate
    def test_get_internal_endpoint(self):
        self.stub_auth()
        session = ospurge.Session(USERNAME, PASSWORD, client_fixtures.PROJECT_ID,
                                   AUTH_URL, endpoint_type='internalURL')
        endpoint = session.get_endpoint('volume')
        self.assertEqual(endpoint, client_fixtures.VOLUME_INTERNAL_ENDPOINT)
        endpoint = session.get_endpoint('image')
        self.assertEqual(endpoint, client_fixtures.IMAGE_INTERNAL_ENDPOINT)

# Abstract class
class TestResourcesBase(HttpTest):
    """
    Creates a session object that can be used to test any service.
    """
    @httpretty.activate
    def setUp(self):
        super(TestResourcesBase, self).setUp()
        self.stub_auth()
        self.session = ospurge.Session(USERNAME, PASSWORD,
                                   client_fixtures.PROJECT_ID, AUTH_URL)

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
        self.resources.delete(res) # Checks this doesn't raise an exception


class TestSwiftBase(TestResourcesBase):
    TEST_URL = client_fixtures.STORAGE_PUBLIC_ENDPOINT


class TestSwiftResources(TestSwiftBase):

    @httpretty.activate
    def test_list_containers(self):
        self.stub_url('GET', json=client_fixtures.STORAGE_CONTAINERS_LIST)
        swift = ospurge.SwiftResources(self.session)
        conts = list(swift.list_containers())
        self.assertEqual(conts, client_fixtures.STORAGE_CONTAINERS)


class  TestSwiftObjects(TestSwiftBase):
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
        self.resources = ospurge.SwiftObjects(self.session)

    @httpretty.activate
    def test_list(self):
        self.stub_list()
        objs = list(self.resources.list())
        self.assertEqual(client_fixtures.STORAGE_OBJECTS, objs)

    def test_delete(self):
        self._test_delete()


class  TestSwiftContainers(TestSwiftBase):
    def stub_list(self):
        self.stub_url('GET', json=client_fixtures.STORAGE_CONTAINERS_LIST)

    def stub_delete(self):
        self.stub_url('DELETE', parts=[client_fixtures.STORAGE_CONTAINERS[0]])

    def setUp(self):
        super(TestSwiftContainers, self).setUp()
        self.resources = ospurge.SwiftContainers(self.session)

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
        self.stub_url('DELETE', parts=['snapshots', client_fixtures.SNAPSHOTS_IDS[0]])

    def setUp(self):
        super(TestCinderSnapshots, self).setUp()
        self.resources = ospurge.CinderSnapshots(self.session)

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
        self.stub_url('DELETE', parts=['volumes', client_fixtures.VOLUMES_IDS[0]])

    def setUp(self):
        super(TestCinderVolumes, self).setUp()
        self.resources = ospurge.CinderVolumes(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestNeutronBase(TestResourcesBase):
    TEST_URL = client_fixtures.NETWORK_PUBLIC_ENDPOINT

    # Used both in TestNeutronRouters and TestNeutronInterfaces
    def stub_list_routers(self):
        self.stub_url('GET', parts=['v2.0', 'routers.json'],
                      json=client_fixtures.ROUTERS_LIST)


class TestNeutronRouters(TestNeutronBase):
    IDS = client_fixtures.ROUTERS_IDS

    def stub_list(self):
        self.stub_list_routers()

    def stub_delete(self):
        routid = client_fixtures.ROUTERS_IDS[0]
        self.stub_url('PUT', parts=['v2.0', 'routers', "%s.json"%routid],
                      json=client_fixtures.ROUTER_CLEAR_GATEWAY)
        self.stub_url('DELETE', parts=['v2.0', 'routers', "%s.json"%routid],
                      json={})

    def setUp(self):
        super(TestNeutronRouters, self).setUp()
        self.resources = ospurge.NeutronRouters(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestNeutronInterfaces(TestNeutronBase):
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
        self.resources = ospurge.NeutronInterfaces(self.session)

    # Special case there, interfaces ids can be accessed through
    # port['interface_id']['id']
    @httpretty.activate
    def test_list(self):
        self.stub_auth()
        self.stub_list()
        ids = [port['interface_id'] for port in self.resources.list()]
        # Converting lists to sets, because order of element may have change
        self.assertEqual(set(ids), set(client_fixtures.PORTS_IDS))

    def test_delete(self):
        self._test_delete()


class TestNeutronNetworks(TestNeutronBase):
    IDS = client_fixtures.NETWORKS_IDS

    def stub_list(self):
        self.stub_url('GET', parts=['v2.0', 'networks.json'],
                      json=client_fixtures.NETWORKS_LIST)

    def stub_delete(self):
        for net_id in client_fixtures.NETWORKS_IDS:
            self.stub_url('DELETE', parts=['v2.0', 'networks',
                                           "{}.json".format(net_id)], json={})

    def setUp(self):
        super(TestNeutronNetworks, self).setUp()
        self.resources = ospurge.NeutronNetworks(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestNeutronSecgroups(TestNeutronBase):
    IDS = client_fixtures.SECGROUPS_IDS

    def stub_list(self):
        self.stub_url('GET', parts=['v2.0', 'security-groups.json'],
                      json=client_fixtures.SECGROUPS_LIST)

    def stub_delete(self):
        for secgroup_id in client_fixtures.SECGROUPS_IDS:
            self.stub_url('DELETE', parts=['v2.0', 'security-groups',
                                           "{}.json".format(secgroup_id)], json={})

    def setUp(self):
        super(TestNeutronSecgroups, self).setUp()
        self.resources = ospurge.NeutronSecgroups(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestNeutronFloatingIps(TestNeutronBase):
    IDS = client_fixtures.FLOATING_IPS_IDS

    def stub_list(self):
        self.stub_url('GET', parts=['v2.0', 'floatingips.json'],
                      json=client_fixtures.FLOATING_IPS_LIST)

    def stub_delete(self):
        ip_id = client_fixtures.FLOATING_IPS_IDS[0]
        self.stub_url('DELETE', parts=['v2.0', 'floatingips',
                                       "{}.json".format(ip_id)], json={})

    def setUp(self):
        super(TestNeutronFloatingIps, self).setUp()
        self.resources = ospurge.NeutronFloatingIps(self.session)

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
        self.stub_url('DELETE', parts=['servers', client_fixtures.SERVERS_IDS[0]])

    def setUp(self):
        super(TestNovaServers, self).setUp()
        self.resources = ospurge.NovaServers(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestGlanceImages(TestResourcesBase):
    TEST_URL = client_fixtures.IMAGE_PUBLIC_ENDPOINT
    IDS = client_fixtures.IMAGES_IDS

    def stub_list(self):
        self.stub_url('GET', parts=['v1', 'images', 'detail'],
                      json=client_fixtures.IMAGES_LIST)

    def stub_delete(self):
        self.stub_url('DELETE', parts=['v1', 'images', client_fixtures.IMAGES_IDS[0]])

    def setUp(self):
        super(TestGlanceImages, self).setUp()
        self.resources = ospurge.GlanceImages(self.session)

    def test_list(self):
        self._test_list()

    def test_delete(self):
        self._test_delete()


class TestCeilometerAlarms(TestResourcesBase):
    TEST_URL = client_fixtures.METERING_PUBLIC_ENDPOINT

    def stub_list(self):
        self.stub_url('GET', parts=['v2', 'alarms'],
                      json=client_fixtures.ALARMS_LIST)

    def stub_delete(self):
        self.stub_url('DELETE', parts=['v2', 'alarms', client_fixtures.ALARMS_IDS[0]])

    def setUp(self):
        super(TestCeilometerAlarms, self).setUp()
        self.resources = ospurge.CeilometerAlarms(self.session)

    @httpretty.activate
    def test_list(self):
        self.stub_auth()
        self.stub_list()
        elts = list(self.resources.list())
        ids = [elt.alarm_id for elt in elts]
        self.assertEqual(client_fixtures.ALARMS_IDS, ids)

    def test_delete(self):
        self._test_delete()
