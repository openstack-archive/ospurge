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

from ospurge.resources import nova


class TestServers(unittest.TestCase):
    def setUp(self):
        self.cloud = mock.Mock(spec_set=shade.openstackcloud.OpenStackCloud)
        self.creds_manager = mock.Mock(cloud=self.cloud)

    def test_list(self):
        self.assertIs(self.cloud.list_servers.return_value,
                      nova.Servers(self.creds_manager).list())
        self.cloud.list_servers.assert_called_once_with()

    def test_delete(self):
        server = mock.MagicMock()
        self.assertIsNone(nova.Servers(self.creds_manager).delete(server))
        self.cloud.delete_server.assert_called_once_with(server['id'])

    def test_to_string(self):
        server = mock.MagicMock()
        self.assertIn("VM (",
                      nova.Servers(self.creds_manager).to_str(server))
