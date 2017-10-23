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


class Snapshots(base.ServiceResource):
    ORDER = 36

    def list(self):
        return self.cloud.list_volume_snapshots()

    def delete(self, resource):
        self.cloud.delete_volume_snapshot(resource['id'])

    @staticmethod
    def to_str(resource):
        return "Volume Snapshot (id='{}', name='{}')".format(
            resource['id'], resource['name'])


class Volumes(base.ServiceResource):
    ORDER = 65

    def check_prerequisite(self):
        return (self.cloud.list_volume_snapshots() == [] and
                self.cloud.list_servers() == [])

    def list(self):
        return self.cloud.list_volumes()

    def should_delete(self, resource):
        attr = 'os-vol-tenant-attr:tenant_id'
        return resource[attr] == self.cleanup_project_id

    def delete(self, resource):
        self.cloud.delete_volume(resource['id'])

    @staticmethod
    def to_str(resource):
        return "Volume (id='{}', name='{}')".format(
            resource['id'], resource['name'])
