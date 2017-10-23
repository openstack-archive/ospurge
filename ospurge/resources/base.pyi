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
import abc
import threading
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Optional

from ospurge.main import CredentialsManager  # noqa: F401


class MatchSignaturesMeta(type):
    def __init__(
        self, clsname: str, bases: Optional[Any],
        clsdict: Optional[Dict]
    ) -> None:
        ...


class OrderedMeta(type):
    def __new__(
            cls, clsname: str, bases: Optional[Any],
            clsdict: Optional[Dict]
    ) -> type:
        ...

    @classmethod
    def __prepare__(cls, clsname: str, bases: Optional[Any]) -> Dict:
        ...


class CodingStyleMixin(OrderedMeta, MatchSignaturesMeta, abc.ABCMeta):
    ...


class BaseServiceResource(object):
    def __init__(self) -> None:
        ...


class ServiceResource(BaseServiceResource, metaclass=CodingStyleMixin):
    def __init__(self, creds_manager: 'CredentialsManager') -> None:
        ...

    @classmethod
    def order(cls) -> int:
        ...

    def check_prerequisite(self) -> bool:
        ...

    @abc.abstractmethod
    def list(self) -> Iterable:
        ...

    def should_delete(self, resource: Dict[str, Any]) -> bool:
        ...

    @abc.abstractmethod
    def delete(self, resource: Dict[str, Any]) -> None:
        ...

    @staticmethod
    @abc.abstractmethod
    def to_str(resource: Dict[str, Any]) -> str:
        ...

    def wait_for_check_prerequisite(self, exit: threading.Event) -> None:
        ...
