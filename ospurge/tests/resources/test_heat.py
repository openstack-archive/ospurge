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

import shade

from ospurge.resources import heat
from ospurge.tests import mock


class TestStacks(unittest.TestCase):
    def setUp(self):
        self.cloud = mock.Mock(spec_set=shade.openstackcloud.OpenStackCloud)
        self.creds_manager = mock.Mock(cloud=self.cloud)

    def test_list_without_service(self):
        self.cloud.has_service.return_value = False
        self.assertEqual(heat.Stacks(self.creds_manager).list(), [])
        self.cloud.list_stacks.assert_not_called()

    def test_list_with_service(self):
        self.cloud.has_service.return_value = True
        self.assertIs(self.cloud.list_stacks.return_value,
                      heat.Stacks(self.creds_manager).list())
        self.cloud.list_stacks.assert_called_once_with()

    def test_delete(self):
        stack = mock.MagicMock()
        self.assertIsNone(heat.Stacks(self.creds_manager).delete(stack))
        self.cloud.delete_stack.assert_called_once_with(stack['id'], wait=True)

    def test_to_string(self):
        stack = mock.MagicMock()
        self.assertIn("Heat Stack",
                      heat.Stacks(self.creds_manager).to_str(stack))
