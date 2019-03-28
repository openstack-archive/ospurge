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

from ospurge.resources import base


VOLUME_PROJECT_ID_KEY = 'os-vol-tenant-attr:tenant_id'
SNAPSHOT_PROJECT_ID_KEY = 'os-extended-snapshot-attributes:project_id'


class CinderMixin(base.BaseServiceResource):

    @property
    def groups_support(self):
        groups_support = False
        volume_api_version = self.cloud.cloud_config.get_api_version(
            'volume')
        try:
            if float(volume_api_version) >= 3.13:
                groups_support = True
        except (TypeError, ValueError):
            pass
        return groups_support

    @property
    def cinder_client(self):
        """Cinder Legacy Client

        We need this because volume groups are not yet implemented in shade nor
        in openstacksdk.
        """
        return self.cloud.cloud_config.get_legacy_client('volume')


class Backups(base.ServiceResource):
    ORDER = 33

    def list(self):
        return self.cloud.list_volume_backups()

    def delete(self, resource):
        self.cloud.delete_volume_backup(resource['id'])

    @staticmethod
    def to_str(resource):
        return "Volume Backup (id='{}', name='{}'".format(
            resource['id'], resource['name'])


class GroupSnapshots(base.ServiceResource, CinderMixin):
    ORDER = 36

    def list(self):
        if self.groups_support:
            return self.cinder_client.group_snapshots.list()
        else:
            return []

    def should_delete(self, resource):
        return super(GroupSnapshots, self).should_delete(
            resource.to_dict()
        )

    def delete(self, resource):
        self.cinder_client.group_snapshots.delete(resource.id)

    @staticmethod
    def to_str(resource):
        return "Group Snapshot (id='{}', name='{}')".format(
            resource.id, resource.name)


class Snapshots(base.ServiceResource, CinderMixin):
    ORDER = 39

    def check_prerequisite(self):
        if self.groups_support:
            return self.cinder_client.group_snapshots.list() == []
        else:
            return True

    def list(self):
        return self.cloud.list_volume_snapshots()

    def should_delete(self, resource):
        # SNAPSHOT_PROJECT_ID_KEY might not exist depending on the platform
        # version.
        if SNAPSHOT_PROJECT_ID_KEY in resource:
            return resource[SNAPSHOT_PROJECT_ID_KEY] == self.cleanup_project_id
        else:
            # A snapshot can normally not be deleted when the volume exists.
            return self.cloud.get_volume(
                resource['volume_id']
            )[VOLUME_PROJECT_ID_KEY] == self.cleanup_project_id

    def delete(self, resource):
        self.cloud.delete_volume_snapshot(resource['id'])

    @staticmethod
    def to_str(resource):
        return "Volume Snapshot (id='{}', name='{}')".format(
            resource['id'], resource['name'])


class VolumeGroups(base.ServiceResource, CinderMixin):
    ORDER = 60

    def check_prerequisite(self):
        if self.groups_support:
            return (
                self.cinder_client.group_snapshots.list() == [] and
                self.cloud.list_volume_snapshots() == []
            )
        else:
            return True

    def list(self):
        if self.groups_support:
            return self.cinder_client.groups.list()
        else:
            return []

    def should_delete(self, resource):
        return super(VolumeGroups, self).should_delete(resource.to_dict())

    def delete(self, resource):
        self.cinder_client.groups.delete(resource.id, delete_volumes=True)

    @staticmethod
    def to_str(resource):
        return "Volume Group (id='{}', name='{}')".format(
            resource.id, resource.name)


class Volumes(base.ServiceResource, CinderMixin):
    ORDER = 65

    def check_prerequisite(self):
        groups_prerequisite = True
        if self.groups_support:
            groups_prerequisite = self.cinder_client.groups.list() == []
        return (self.cloud.list_volume_snapshots() == [] and
                self.cloud.list_servers() == [] and
                groups_prerequisite)

    def list(self):
        return self.cloud.list_volumes()

    def should_delete(self, resource):
        return resource[VOLUME_PROJECT_ID_KEY] == self.cleanup_project_id

    def delete(self, resource):
        self.cloud.delete_volume(resource['id'])

    @staticmethod
    def to_str(resource):
        return "Volume (id='{}', name='{}')".format(
            resource['id'], resource['name'])
