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

from ospurge.resources import base
from ospurge.resources.base import BaseServiceResource


class ListImagesMixin(BaseServiceResource):
    def list_images_by_owner(self) -> Iterable[Dict[str, Any]]:
        images = []
        for image in self.cloud.list_images():
            if image['owner'] != self.cleanup_project_id:
                continue

            is_public = image.get('is_public', False)
            visibility = image.get('visibility', "")
            if is_public is True or visibility == 'public':
                if self.options.delete_shared_resources is False:
                    continue

            images.append(image)

        return images


class Images(base.ServiceResource, ListImagesMixin):
    ORDER = 53

    def list(self) -> Iterable:
        return self.list_images_by_owner()

    def should_delete(self, resource: Dict[str, Any]) -> bool:
        return resource['owner'] == self.cleanup_project_id

    def delete(self, resource: Dict[str, Any]) -> None:
        self.cloud.delete_image(resource['id'])

    @staticmethod
    def to_str(resource: Dict[str, Any]) -> str:
        return "Image (id='{}', name='{}')".format(
            resource['id'], resource['name'])
