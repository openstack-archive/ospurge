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

from ospurge.resources import swift
from ospurge.tests import mock


class TestListObjectsMixin(unittest.TestCase):
    def setUp(self):
        self.cloud = mock.Mock(spec_set=shade.openstackcloud.OpenStackCloud)
        self.obj_lister = swift.ListObjectsMixin()
        self.obj_lister.cloud = self.cloud

    def test_list_objects(self):
        containers = [{"name": "foo"}, {"name": "bar"}]
        objects = {
            "foo": [{"name": "toto"}, {"name": "tata"}],
            "bar": [{"name": "titi"}, {"name": "tutu"}]
        }

        def list_objects(container_name):
            return objects[container_name]

        self.cloud.list_containers.return_value = containers
        self.cloud.list_objects.side_effect = list_objects
        self.assertEqual(
            [{'name': 'toto', 'container_name': 'foo'},
             {'name': 'tata', 'container_name': 'foo'},
             {'name': 'titi', 'container_name': 'bar'},
             {'name': 'tutu', 'container_name': 'bar'}],
            list(self.obj_lister.list_objects())
        )


class TestObjects(unittest.TestCase):
    def setUp(self):
        self.cloud = mock.Mock(spec_set=shade.openstackcloud.OpenStackCloud)
        self.creds_manager = mock.Mock(cloud=self.cloud)

    def test_check_prerequisite(self):
        objects_manager = swift.Objects(self.creds_manager)
        with mock.patch.object(objects_manager, 'list_images_by_owner') as m:
            m.return_value = []
            self.cloud.list_volume_backups.return_value = ["foo"]
            self.assertEqual(False, objects_manager.check_prerequisite())

            self.cloud.list_volume_backups.return_value = []
            self.assertEqual(True, objects_manager.check_prerequisite())

            m.return_value = ["bar"]
            self.assertEqual(False, objects_manager.check_prerequisite())

    @mock.patch('ospurge.resources.swift.ListObjectsMixin.list_objects')
    def test_list(self, mock_list_objects):
        def list_objects():
            yield 1
            yield 2

        mock_list_objects.side_effect = list_objects

        objects = swift.Objects(self.creds_manager).list()
        self.assertEqual(1, next(objects))
        self.assertEqual(2, next(objects))
        self.assertRaises(StopIteration, next, objects)

    def test_delete(self):
        obj = mock.MagicMock()
        self.assertIsNone(swift.Objects(self.creds_manager).delete(obj))
        self.cloud.delete_object.assert_called_once_with(
            obj['container_name'], obj['name'])

    def test_to_string(self):
        obj = mock.MagicMock()
        self.assertIn("Object '",
                      swift.Objects(self.creds_manager).to_str(obj))


class TestContainers(unittest.TestCase):
    def setUp(self):
        self.cloud = mock.Mock(spec_set=shade.openstackcloud.OpenStackCloud)
        self.creds_manager = mock.Mock(cloud=self.cloud)

    @mock.patch('ospurge.resources.swift.ListObjectsMixin.list_objects')
    def test_check_prerequisite(self, mock_list_objects):
        mock_list_objects.return_value = ['obj1']
        self.assertEqual(
            False,
            swift.Containers(self.creds_manager).check_prerequisite()
        )
        mock_list_objects.return_value = []
        self.assertEqual(
            True,
            swift.Containers(self.creds_manager).check_prerequisite()
        )

    def test_list(self):
        self.assertIs(self.cloud.list_containers.return_value,
                      swift.Containers(self.creds_manager).list())
        self.cloud.list_containers.assert_called_once_with()

    def test_delete(self):
        cont = mock.MagicMock()
        self.assertIsNone(swift.Containers(self.creds_manager).delete(cont))
        self.cloud.delete_container.assert_called_once_with(cont['name'])

    def test_to_string(self):
        container = mock.MagicMock()
        self.assertIn("Container (",
                      swift.Containers(self.creds_manager).to_str(
                          container))
