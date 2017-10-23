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

from ospurge.resources import glance
from ospurge.tests import mock


class TestListImagesMixin(unittest.TestCase):
    def setUp(self):
        self.cloud = mock.Mock(spec_set=shade.openstackcloud.OpenStackCloud)
        self.img_lister = glance.ListImagesMixin()
        self.img_lister.cloud = self.cloud
        self.img_lister.cleanup_project_id = 42
        self.img_lister.options = None

    def test_list_images_by_owner_no_image(self):
        self.cloud.list_images.return_value = []
        self.assertEqual([], self.img_lister.list_images_by_owner())

    def test_list_images_by_owner_different_owner(self):
        self.cloud.list_images.return_value = [
            {'owner': 84},
            {'owner': 85}
        ]
        self.assertEqual([], self.img_lister.list_images_by_owner())

    def test_list_images_by_owner_public_images(self):
        self.cloud.list_images.return_value = [
            {'owner': 42, 'is_public': True},
            {'owner': 42, 'visibility': 'public'},
        ]
        with mock.patch.object(self.img_lister, 'options',
                               mock.Mock(delete_shared_resources=True)):
            self.assertEqual(self.cloud.list_images.return_value,
                             self.img_lister.list_images_by_owner())

        with mock.patch.object(self.img_lister, 'options',
                               mock.Mock(delete_shared_resources=False)):
            self.assertEqual([], self.img_lister.list_images_by_owner())


class TestImages(unittest.TestCase):
    def setUp(self):
        self.cloud = mock.Mock(spec_set=shade.openstackcloud.OpenStackCloud)
        self.creds_manager = mock.Mock(cloud=self.cloud, project_id=42)

    @mock.patch.object(glance.ListImagesMixin, 'list_images_by_owner')
    def test_list(self, mock_list_images_by_owner):
        self.assertIs(mock_list_images_by_owner.return_value,
                      glance.Images(self.creds_manager).list())
        mock_list_images_by_owner.assert_called_once_with()

    def test_should_delete(self):
        self.assertEqual(
            False,
            glance.Images(self.creds_manager).should_delete(
                {'owner': 84})
        )
        self.assertEqual(
            True,
            glance.Images(self.creds_manager).should_delete(
                {'owner': 42})
        )

    def test_delete(self):
        image = mock.MagicMock()
        self.assertIsNone(glance.Images(self.creds_manager).delete(image))
        self.cloud.delete_image.assert_called_once_with(image['id'])

    def test_to_string(self):
        image = mock.MagicMock()
        self.assertIn("Image (",
                      glance.Images(self.creds_manager).to_str(image))
