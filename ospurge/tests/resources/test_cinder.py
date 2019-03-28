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

from cinderclient.v3.client import Client as CinderClient
from cinderclient.v3.group_snapshots import GroupSnapshotManager
from cinderclient.v3.groups import GroupManager

import os_client_config

import shade

from ospurge.resources import cinder
from ospurge.tests import mock


def set_get_api_version_side_effect(mocked_get_api_version, **kwargs):
    """Allow the get_api_version mock to return values depending on argument"""
    def side_effect_get_api_version(service_type):
        if service_type in kwargs:
            return kwargs[service_type]
        else:
            return '2.0'
    mocked_get_api_version.side_effect = side_effect_get_api_version


class TestBackups(unittest.TestCase):
    def setUp(self):
        self.cloud = mock.Mock(spec=shade.openstackcloud.OpenStackCloud)
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


class TestGroupSnapshots(unittest.TestCase):

    def setUp(self):
        self.cloud = mock.Mock(spec=shade.openstackcloud.OpenStackCloud)
        self.cloud.cloud_config = mock.Mock(
            spec=os_client_config.cloud_config.CloudConfig)
        set_get_api_version_side_effect(
            self.cloud.cloud_config.get_api_version,
            volume='3.13'
        )
        self.creds_manager = mock.Mock(cloud=self.cloud, project_id=42)
        cinder_client = mock.Mock(
            spec=CinderClient,
            group_snapshots=mock.Mock(spec=GroupSnapshotManager)
        )
        self.cloud.cloud_config.get_legacy_client.return_value = cinder_client
        self.cinder_client = cinder_client
        self.group_snapshots = cinder.GroupSnapshots(self.creds_manager)

    def test_list_groups_not_supported(self):
        set_get_api_version_side_effect(
            self.cloud.cloud_config.get_api_version,
            volume='3.12'
        )
        self.assertEqual(self.group_snapshots.list(), [])
        self.cinder_client.group_snapshots.list.assert_not_called()
        self.cloud.cloud_config.get_api_version.assert_called_once_with(
            'volume')

    def test_list(self):
        self.assertIs(self.group_snapshots.list(),
                      self.cinder_client.group_snapshots.list.return_value)
        self.cinder_client.group_snapshots.list.assert_called_once_with()
        self.cloud.cloud_config.get_api_version.assert_called_once_with(
            'volume')

    def test_should_delete(self):
        group_snapshot = mock.MagicMock()
        self.assertFalse(
            self.group_snapshots.should_delete(group_snapshot)
        )
        group_snapshot.to_dict.return_value = {'project_id': 42}
        self.assertTrue(
            self.group_snapshots.should_delete(group_snapshot)
        )

    def test_delete(self):
        group_snapshot = mock.MagicMock()
        self.assertIsNone(
            self.group_snapshots.delete(group_snapshot)
        )
        self.cinder_client.group_snapshots.delete.assert_called_once_with(
            group_snapshot.id
        )

    def test_to_str(self):
        group_snapshot = mock.MagicMock()
        self.assertIn("Group Snapshot ",
                      self.group_snapshots.to_str(group_snapshot))


class TestSnapshots(unittest.TestCase):
    def setUp(self):
        self.cloud = mock.Mock(spec=shade.openstackcloud.OpenStackCloud)
        self.creds_manager = mock.Mock(cloud=self.cloud, project_id=42)

    def test_check_prerequisite(self):
        self.cloud.cloud_config = mock.Mock(
            spec=os_client_config.cloud_config.CloudConfig)
        cinder_client = mock.Mock(
            spec=CinderClient,
            group_snapshots=mock.Mock(spec=GroupSnapshotManager)
        )
        self.cloud.cloud_config.get_legacy_client.return_value = cinder_client
        volume_snapshots = cinder.Snapshots(self.creds_manager)

        set_get_api_version_side_effect(
            self.cloud.cloud_config.get_api_version,
            volume='3.12'
        )
        self.assertTrue(volume_snapshots.check_prerequisite())
        self.assertFalse(volume_snapshots.groups_support)
        cinder_client.group_snapshots.list.assert_not_called()

        set_get_api_version_side_effect(
            self.cloud.cloud_config.get_api_version,
            volume='3.13'
        )
        self.assertTrue(volume_snapshots.groups_support)
        self.assertFalse(volume_snapshots.check_prerequisite())
        cinder_client.group_snapshots.list.assert_called_once_with()
        cinder_client.group_snapshots.list.return_value = []
        self.assertTrue(volume_snapshots.check_prerequisite())
        cinder_client.group_snapshots.list.assert_called_with()

    def test_list(self):
        self.assertIs(self.cloud.list_volume_snapshots.return_value,
                      cinder.Snapshots(self.creds_manager).list())
        self.cloud.list_volume_snapshots.assert_called_once_with()

    def test_should_delete(self):
        self.assertFalse(
            cinder.Snapshots(self.creds_manager).should_delete(
                {cinder.SNAPSHOT_PROJECT_ID_KEY: 84})
        )
        self.cloud.get_volume.return_value = {cinder.VOLUME_PROJECT_ID_KEY: 84}
        self.assertFalse(
            cinder.Snapshots(self.creds_manager).should_delete(
                {'volume_id': 'foo'})
        )
        self.assertEqual(
            True,
            cinder.Snapshots(self.creds_manager).should_delete(
                {cinder.SNAPSHOT_PROJECT_ID_KEY: 42})
        )
        self.cloud.get_volume.return_value = {cinder.VOLUME_PROJECT_ID_KEY: 42}
        self.assertTrue(
            cinder.Snapshots(self.creds_manager).should_delete(
                {'volume_id': 'foo'})
        )

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


class TestVolumeGroups(unittest.TestCase):

    def setUp(self):
        self.cloud = mock.Mock(spec=shade.openstackcloud.OpenStackCloud)
        self.cloud.cloud_config = mock.Mock(
            spec=os_client_config.cloud_config.CloudConfig)
        set_get_api_version_side_effect(
            self.cloud.cloud_config.get_api_version,
            volume='3.13'
        )
        self.creds_manager = mock.Mock(cloud=self.cloud, project_id=42)
        cinder_client = mock.Mock(
            spec=CinderClient,
            groups=mock.Mock(spec=GroupManager),
            group_snapshots=mock.Mock(spec=GroupSnapshotManager)
        )
        self.cloud.cloud_config.get_legacy_client.return_value = cinder_client
        self.cinder_client = cinder_client
        self.volume_groups = cinder.VolumeGroups(self.creds_manager)

    def test_check_prerequisite(self):
        set_get_api_version_side_effect(
            self.cloud.cloud_config.get_api_version,
            volume='3.12'
        )
        self.assertTrue(self.volume_groups.check_prerequisite())
        self.assertFalse(self.volume_groups.groups_support)
        self.cinder_client.group_snapshots.list.assert_not_called()
        set_get_api_version_side_effect(
            self.cloud.cloud_config.get_api_version,
            volume='3.13'
        )
        self.assertTrue(self.volume_groups.groups_support)
        self.assertFalse(self.volume_groups.check_prerequisite())
        self.cinder_client.group_snapshots.list.assert_called_once_with()
        self.cinder_client.group_snapshots.list.return_value = []
        self.cloud.list_volume_snapshots.return_value = []
        self.assertTrue(self.volume_groups.check_prerequisite())
        self.cinder_client.group_snapshots.list.assert_called_with()

    def test_list_groups_not_supported(self):
        set_get_api_version_side_effect(
            self.cloud.cloud_config.get_api_version,
            volume='3.12'
        )
        self.assertEqual(self.volume_groups.list(), [])
        self.cinder_client.groups.list.assert_not_called()
        self.cloud.cloud_config.get_api_version.assert_called_once_with(
            'volume')

    def test_list(self):
        self.assertIs(self.volume_groups.list(),
                      self.cinder_client.groups.list.return_value)
        self.cinder_client.groups.list.assert_called_once_with()
        self.cloud.cloud_config.get_api_version.assert_called_once_with(
            'volume')

    def test_should_delete(self):
        group = mock.MagicMock()
        self.assertFalse(
            self.volume_groups.should_delete(group)
        )
        group.to_dict.return_value = {'project_id': 42}
        self.assertTrue(
            self.volume_groups.should_delete(group)
        )

    def test_delete(self):
        group = mock.MagicMock()
        self.assertIsNone(
            self.volume_groups.delete(group)
        )
        self.cinder_client.groups.delete.assert_called_once_with(
            group.id, delete_volumes=True
        )

    def test_to_str(self):
        group = mock.MagicMock()
        self.assertIn("Volume Group ",
                      self.volume_groups.to_str(group))


class TestVolumes(unittest.TestCase):
    def setUp(self):
        self.cloud = mock.Mock(spec=shade.openstackcloud.OpenStackCloud)
        self.cloud.cloud_config = mock.Mock(
            spec=os_client_config.cloud_config.CloudConfig)
        self.creds_manager = mock.Mock(cloud=self.cloud, project_id=42)

    def test_check_prerequisite(self):
        cinder_client = mock.Mock(
            spec=CinderClient,
            groups=mock.Mock(spec=GroupManager),
            group_snapshots=mock.Mock(spec=GroupSnapshotManager)
        )
        self.cloud.cloud_config.get_legacy_client.return_value = cinder_client
        self.cloud.list_volume_snapshots.return_value = []

        self.assertFalse(
            cinder.Volumes(self.creds_manager).check_prerequisite()
        )
        self.cloud.list_volume_snapshots.assert_called_once_with()
        self.cloud.list_servers.assert_called_once_with()

        self.cloud.list_servers.return_value = []
        self.assertTrue(
            cinder.Volumes(self.creds_manager).check_prerequisite()
        )

        set_get_api_version_side_effect(
            self.cloud.cloud_config.get_api_version,
            volume='3.13'
        )
        self.assertFalse(
            cinder.Volumes(self.creds_manager).check_prerequisite()
        )

        cinder_client.groups.list.return_value = []
        self.assertTrue(
            cinder.Volumes(self.creds_manager).check_prerequisite()
        )

    def test_list(self):
        self.assertIs(self.cloud.list_volumes.return_value,
                      cinder.Volumes(self.creds_manager).list())
        self.cloud.list_volumes.assert_called_once_with()

    def test_should_delete(self):
        self.assertEqual(
            False,
            cinder.Volumes(self.creds_manager).should_delete(
                {cinder.VOLUME_PROJECT_ID_KEY: 84})
        )
        self.assertEqual(
            True,
            cinder.Volumes(self.creds_manager).should_delete(
                {cinder.VOLUME_PROJECT_ID_KEY: 42})
        )

    def test_delete(self):
        volume = mock.MagicMock()
        self.assertIsNone(cinder.Volumes(self.creds_manager).delete(volume))
        self.cloud.delete_volume.assert_called_once_with(volume['id'])

    def test_to_string(self):
        volume = mock.MagicMock()
        self.assertIn("Volume ",
                      cinder.Volumes(self.creds_manager).to_str(volume))
