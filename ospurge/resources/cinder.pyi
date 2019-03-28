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

from cinderclient.v3.groups import Group
from cinderclient.v3.group_snapshots import GroupSnapshot

from ospurge.resources import base


class CinderMixin(base.BaseServiceResource):
    @property
    def groups_support(self) -> bool:
        ...

    @property
    def cinder_client(self) -> object:
        ...


class Backups(base.ServiceResource):
    def list(self) -> Iterable:
        ...

    def delete(self, resource: Dict[str, Any]) -> None:
        ...

    @staticmethod
    def to_str(resource: Dict[str, Any]) -> str:
        ...


class GroupSnapshots(base.ServiceResource, CinderMixin):
    def list(self) -> Iterable:
        ...

    def should_delete(self, resource: GroupSnapshot) -> bool:
        ...

    def delete(self, resource: GroupSnapshot) -> None:
        ...

    @staticmethod
    def to_str(resource: GroupSnapshot) -> str:
        ...


class Snapshots(base.ServiceResource, CinderMixin):
    def list(self) -> Iterable:
        ...

    def should_delete(self, resource: Dict[str, Any]) -> bool:
        ...

    def delete(self, resource: Dict[str, Any]) -> None:
        ...

    @staticmethod
    def to_str(resource: Dict[str, Any]) -> str:
        ...


class VolumeGroups(base.ServiceResource, CinderMixin):
    def check_prerequisite(self) -> bool:
        ...

    def list(self) -> Iterable:
        ...

    def should_delete(self, resource: Group) -> bool:
        ...

    def delete(self, resource: Group) -> None:
        ...

    @staticmethod
    def to_str(resource: Group) -> str:
        ...


class Volumes(base.ServiceResource, CinderMixin):
    def check_prerequisite(self) -> bool:
        ...

    def list(self) -> Iterable:
        ...

    def should_delete(self, resource: Dict[str, Any]) -> bool:
        ...

    def delete(self, resource: Dict[str, Any]) -> None:
        ...

    @staticmethod
    def to_str(resource: Dict[str, Any]) -> str:
        ...
