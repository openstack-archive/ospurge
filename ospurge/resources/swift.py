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
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Iterator

from ospurge.resources import base
from ospurge.resources.base import BaseServiceResource
from ospurge.resources import glance


class ListObjectsMixin(BaseServiceResource):
    def list_objects(self) -> Iterator[Dict[str, Any]]:
        for container in self.cloud.list_containers():
            for obj in self.cloud.list_objects(container['name']):
                obj['container_name'] = container['name']
                yield obj


class Objects(base.ServiceResource, glance.ListImagesMixin, ListObjectsMixin):
    ORDER = 73

    def check_prerequisite(self) -> bool:
        return (self.list_images_by_owner() == [] and
                self.cloud.list_volume_backups() == [])

    def list(self) -> Iterable:
        yield from self.list_objects()

    def delete(self, resource: Dict[str, Any]) -> None:
        self.cloud.delete_object(resource['container_name'], resource['name'])

    @staticmethod
    def to_str(resource: Dict[str, Any]) -> str:
        return "Object '{}' from Container '{}'".format(
            resource['name'], resource['container_name'])


class Containers(base.ServiceResource, ListObjectsMixin):
    ORDER = 75

    def check_prerequisite(self) -> bool:
        return list(self.list_objects()) == []

    def list(self) -> Iterable:
        return self.cloud.list_containers()

    def delete(self, resource: Dict[str, Any]) -> None:
        self.cloud.delete_container(resource['name'])

    @staticmethod
    def to_str(resource: Dict[str, Any]) -> str:
        return "Container (name='{}')".format(resource['name'])
