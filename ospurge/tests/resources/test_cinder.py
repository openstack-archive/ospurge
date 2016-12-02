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

from ospurge.resources import cinder


class TestBackups(unittest.TestCase):
    def setUp(self):
        self.cloud = mock.Mock(spec_set=shade.openstackcloud.OpenStackCloud)
        self.creds_manager = mock.Mock(cloud=self.cloud)

    def test_list(self):
        self.assertIs(self.cloud.list_volume_backups.return_value,
                      cinder.Backups(self.creds_manager).list())
        self.cloud.list_volume_backups.assert_called_once_with()

    def test_delete(self):
        backup = mock.MagicMock()
        self.assertIsNone(cinder.Backups(self.creds_manager).delete(backup))
        self.cloud.delete_volume_backup.assert_called_once_with(backup['id'])

    def test_to_string(self):
        backup = mock.MagicMock()
        self.assertIn("Volume Backup",
                      cinder.Backups(self.creds_manager).to_str(backup))


class TestSnapshots(unittest.TestCase):
    def setUp(self):
        self.cloud = mock.Mock(spec_set=shade.openstackcloud.OpenStackCloud)
        self.creds_manager = mock.Mock(cloud=self.cloud)

    def test_list(self):
        self.assertIs(self.cloud.list_volume_snapshots.return_value,
                      cinder.Snapshots(self.creds_manager).list())
        self.cloud.list_volume_snapshots.assert_called_once_with()

    def test_delete(self):
        snapshot = mock.MagicMock()
        self.assertIsNone(
            cinder.Snapshots(self.creds_manager).delete(snapshot))
        self.cloud.delete_volume_snapshot.assert_called_once_with(
            snapshot['id'])

    def test_to_string(self):
        snapshot = mock.MagicMock()
        self.assertIn("Volume Snapshot ",
                      cinder.Snapshots(self.creds_manager).to_str(snapshot))


class TestVolumes(unittest.TestCase):
    def setUp(self):
        self.cloud = mock.Mock(spec_set=shade.openstackcloud.OpenStackCloud)
        self.creds_manager = mock.Mock(cloud=self.cloud, project_id=42)

    def test_check_prerequisite(self):
        self.cloud.list_volume_snapshots.return_value = []
        self.assertEqual(
            False,
            cinder.Volumes(self.creds_manager).check_prerequisite()
        )
        self.cloud.list_volume_snapshots.assert_called_once_with()
        self.cloud.list_servers.assert_called_once_with()

    def test_list(self):
        self.assertIs(self.cloud.list_volumes.return_value,
                      cinder.Volumes(self.creds_manager).list())
        self.cloud.list_volumes.assert_called_once_with()

    def test_should_delete(self):
        self.assertEqual(
            False,
            cinder.Volumes(self.creds_manager).should_delete(
                {'os-vol-tenant-attr:tenant_id': 84})
        )
        self.assertEqual(
            True,
            cinder.Volumes(self.creds_manager).should_delete(
                {'os-vol-tenant-attr:tenant_id': 42})
        )

    def test_delete(self):
        volume = mock.MagicMock()
        self.assertIsNone(cinder.Volumes(self.creds_manager).delete(volume))
        self.cloud.delete_volume.assert_called_once_with(volume['id'])

    def test_to_string(self):
        volume = mock.MagicMock()
        self.assertIn("Volume ",
                      cinder.Volumes(self.creds_manager).to_str(volume))
