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
        ...


class Objects(base.ServiceResource, glance.ListImagesMixin, ListObjectsMixin):
    def check_prerequisite(self) -> bool:
        ...

    def list(self) -> Iterable:
        ...

    def delete(self, resource: Dict[str, Any]) -> None:
        ...

    @staticmethod
    def to_str(resource: Dict[str, Any]) -> str:
        ...


class Containers(base.ServiceResource, ListObjectsMixin):
    def check_prerequisite(self) -> bool:
        ...

    def list(self) -> Iterable:
        ...

    def delete(self, resource: Dict[str, Any]) -> None:
        ...

    @staticmethod
    def to_str(resource: Dict[str, Any]) -> str:
        ...
