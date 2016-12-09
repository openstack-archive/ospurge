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


class Servers(base.ServiceResource):
    ORDER = 15

    def list(self) -> Iterable:
        return self.cloud.list_servers()

    def delete(self, resource: Dict[str, Any]) -> None:
        self.cloud.delete_server(resource['id'])

    @staticmethod
    def to_str(resource: Dict[str, Any]) -> str:
        return "VM (id='{}', name='{}')".format(
            resource['id'], resource['name'])
