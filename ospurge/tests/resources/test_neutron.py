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
import unittest
from unittest import mock

import shade

from ospurge.resources import neutron


class TestFloatingIPs(unittest.TestCase):
    def setUp(self):
        self.cloud = mock.Mock(spec_set=shade.openstackcloud.OpenStackCloud)
        self.creds_manager = mock.Mock(cloud=self.cloud)

    def test_check_prerequisite(self):
        self.cloud.list_servers.return_value = ['vm1']
        self.assertEqual(
            False,
            neutron.FloatingIPs(self.creds_manager).check_prerequisite()
        )
        self.cloud.list_servers.return_value = []
        self.assertEqual(
            True,
            neutron.FloatingIPs(self.creds_manager).check_prerequisite()
        )

    def test_list(self):
        self.assertIs(self.cloud.search_floating_ips.return_value,
                      neutron.FloatingIPs(self.creds_manager).list())
        self.cloud.search_floating_ips.assert_called_once_with(
            filters={'tenant_id': self.creds_manager.project_id}
        )

    def test_delete(self):
        fip = mock.MagicMock()
        self.assertIsNone(neutron.FloatingIPs(self.creds_manager).delete(fip))
        self.cloud.delete_floating_ip.assert_called_once_with(
            fip['id'])

    def test_to_string(self):
        fip = mock.MagicMock()
        self.assertIn("Floating IP ",
                      neutron.FloatingIPs(self.creds_manager).to_str(fip))


class TestRouterInterfaces(unittest.TestCase):
    def setUp(self):
        self.cloud = mock.Mock(spec_set=shade.openstackcloud.OpenStackCloud)
        self.creds_manager = mock.Mock(cloud=self.cloud)

    def test_check_prerequisite(self):
        ifaces_manager = neutron.RouterInterfaces(self.creds_manager)

        self.cloud.list_servers.return_value = []
        self.cloud.search_floating_ips.return_value = ["foo"]
        self.assertEqual(False, ifaces_manager.check_prerequisite())

        self.cloud.search_floating_ips.return_value = []
        self.assertEqual(True, ifaces_manager.check_prerequisite())

        self.cloud.list_servers.return_value = ["bar"]
        self.assertEqual(False, ifaces_manager.check_prerequisite())

        self.cloud.search_floating_ips.assert_called_with(
            filters={'tenant_id': self.creds_manager.project_id}
        )

    def test_list(self):
        self.assertIs(self.cloud.list_ports.return_value,
                      neutron.RouterInterfaces(self.creds_manager).list())
        self.cloud.list_ports.assert_called_once_with(
            filters={'device_owner': 'network:router_interface',
                     'tenant_id': self.creds_manager.project_id}
        )

    def test_delete(self):
        iface = mock.MagicMock()
        self.assertIsNone(neutron.RouterInterfaces(self.creds_manager).delete(
            iface))
        self.cloud.remove_router_interface.assert_called_once_with(
            {'id': iface['device_id']},
            port_id=iface['id']
        )

    def test_to_string(self):
        iface = mock.MagicMock()
        self.assertIn(
            "Router Interface (",
            neutron.RouterInterfaces(self.creds_manager).to_str(iface)
        )


class TestRouters(unittest.TestCase):
    def setUp(self):
        self.cloud = mock.Mock(spec_set=shade.openstackcloud.OpenStackCloud)
        self.creds_manager = mock.Mock(cloud=self.cloud)

    def test_check_prerequisite(self):
        self.cloud.list_ports.return_value = []
        self.assertEqual(
            True, neutron.Routers(self.creds_manager).check_prerequisite())

        self.cloud.list_ports.return_value = ['foo']
        self.assertEqual(
            False, neutron.Routers(self.creds_manager).check_prerequisite())

        self.cloud.list_ports.assert_called_with(
            filters={'device_owner': 'network:router_interface',
                     'tenant_id': self.creds_manager.project_id}
        )

    def test_list(self):
        self.assertIs(self.cloud.list_routers.return_value,
                      neutron.Routers(self.creds_manager).list())
        self.cloud.list_routers.assert_called_once_with()

    def test_delete(self):
        router = mock.MagicMock()
        self.assertIsNone(neutron.Routers(self.creds_manager).delete(router))
        self.cloud.delete_router.assert_called_once_with(router['id'])

    def test_to_string(self):
        router = mock.MagicMock()
        self.assertIn("Router (",
                      neutron.Routers(self.creds_manager).to_str(router))


class TestPorts(unittest.TestCase):
    def setUp(self):
        self.cloud = mock.Mock(spec_set=shade.openstackcloud.OpenStackCloud)
        self.creds_manager = mock.Mock(cloud=self.cloud)

    def test_list(self):
        self.cloud.list_ports.return_value = [
            {'device_owner': 'network:dhcp'},
            {'device_owner': 'network:router_interface'},
            {'device_owner': ''}
        ]
        ports = neutron.Ports(self.creds_manager).list()
        self.assertEqual([{'device_owner': ''}], ports)
        self.cloud.list_ports.assert_called_once_with(
            filters={'tenant_id': self.creds_manager.project_id})

    def test_delete(self):
        port = mock.MagicMock()
        self.assertIsNone(neutron.Ports(self.creds_manager).delete(port))
        self.cloud.delete_port.assert_called_once_with(port['id'])

    def test_to_string(self):
        port = mock.MagicMock()
        self.assertIn("Port (",
                      neutron.Ports(self.creds_manager).to_str(port))


class TestNetworks(unittest.TestCase):
    def setUp(self):
        self.cloud = mock.Mock(spec_set=shade.openstackcloud.OpenStackCloud)
        self.creds_manager = mock.Mock(cloud=self.cloud)

    def test_check_prerequisite(self):
        self.cloud.list_ports.return_value = [{'device_owner': 'network:dhcp'}]
        self.assertEqual(
            True, neutron.Networks(self.creds_manager).check_prerequisite())

        self.cloud.list_ports.return_value = [{'device_owner': 'compute:None'}]
        self.assertEqual(
            False, neutron.Networks(self.creds_manager).check_prerequisite())

        self.cloud.list_ports.assert_called_with(
            filters={'tenant_id': self.creds_manager.project_id}
        )

    def test_list(self):
        self.creds_manager.options.delete_shared_resources = False
        self.cloud.list_networks.return_value = [
            {'router:external': True}, {'router:external': True}]
        nw_list = neutron.Networks(self.creds_manager).list()
        self.assertEqual(0, len(nw_list))

        self.creds_manager.options.delete_shared_resources = True
        nw_list = neutron.Networks(self.creds_manager).list()
        self.assertEqual(2, len(nw_list))

        self.cloud.list_networks.assert_called_with(
            filters={'tenant_id': self.creds_manager.project_id}
        )

    def test_delete(self):
        nw = mock.MagicMock()
        self.assertIsNone(neutron.Networks(self.creds_manager).delete(nw))
        self.cloud.delete_network.assert_called_once_with(nw['id'])

    def test_to_string(self):
        nw = mock.MagicMock()
        self.assertIn("Network (",
                      neutron.Networks(self.creds_manager).to_str(nw))


class TestSecurityGroups(unittest.TestCase):
    def setUp(self):
        self.cloud = mock.Mock(spec_set=shade.openstackcloud.OpenStackCloud)
        self.creds_manager = mock.Mock(cloud=self.cloud)

    def test_list(self):
        self.cloud.list_security_groups.return_value = [
            {'name': 'default'}, {'name': 'bar'}
        ]
        self.assertEqual(
            1, len(neutron.SecurityGroups(self.creds_manager).list()))
        self.cloud.list_security_groups.assert_called_once_with(
            filters={'tenant_id': self.creds_manager.project_id}
        )

    def test_delete(self):
        sg = mock.MagicMock()
        self.assertIsNone(
            neutron.SecurityGroups(self.creds_manager).delete(sg))
        self.cloud.delete_security_group.assert_called_once_with(sg['id'])

    def test_to_string(self):
        sg = mock.MagicMock()
        self.assertIn("Security Group (",
                      neutron.SecurityGroups(self.creds_manager).to_str(sg))
