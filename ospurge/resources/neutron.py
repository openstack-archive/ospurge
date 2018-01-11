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


class FloatingIPs(base.ServiceResource):
    ORDER = 25

    def check_prerequisite(self):
        # We can't delete a FIP if it's attached
        return self.cloud.list_servers() == []

    def list(self):
        return self.cloud.search_floating_ips(filters={
            'tenant_id': self.cleanup_project_id
        })

    def delete(self, resource):
        self.cloud.delete_floating_ip(resource['id'])

    @staticmethod
    def to_str(resource):
        return "Floating IP (id='{}')".format(resource['id'])


class RouterInterfaces(base.ServiceResource):
    ORDER = 42

    def check_prerequisite(self):
        return (
            self.cloud.list_servers() == [] and
            self.cloud.search_floating_ips(
                filters={'tenant_id': self.cleanup_project_id}
            ) == []
        )

    def list(self):
        return self.cloud.list_ports(
            filters={'device_owner': ['network:router_interface', 'network:router_interface_distributed'],
                     'tenant_id': self.cleanup_project_id}
        )

    def delete(self, resource):
        self.cloud.remove_router_interface({'id': resource['device_id']},
                                           port_id=resource['id'])

    @staticmethod
    def to_str(resource):
        return "Router Interface (id='{}', router_id='{}')".format(
            resource['id'], resource['device_id'])


class Routers(base.ServiceResource):
    ORDER = 44

    def check_prerequisite(self):
        return self.cloud.list_ports(
            filters={'device_owner': 'network:router_interface',
                     'tenant_id': self.cleanup_project_id}
        ) == []

    def list(self):
        return self.cloud.list_routers()

    def delete(self, resource):
        self.cloud.delete_router(resource['id'])

    @staticmethod
    def to_str(resource):
        return "Router (id='{}', name='{}')".format(
            resource['id'], resource['name'])


class Ports(base.ServiceResource):
    ORDER = 46

    def list(self):
        ports = self.cloud.list_ports(
            filters={'tenant_id': self.cleanup_project_id}
        )
        excluded = ['network:dhcp', 'network:router_interface']
        return [p for p in ports if p['device_owner'] not in excluded]

    def delete(self, resource):
        self.cloud.delete_port(resource['id'])

    @staticmethod
    def to_str(resource):
        return "Port (id='{}', network_id='{}, device_owner='{}')'".format(
            resource['id'], resource['network_id'], resource['device_owner'])


class Networks(base.ServiceResource):
    ORDER = 48

    def check_prerequisite(self):
        ports = self.cloud.list_ports(
            filters={'tenant_id': self.cleanup_project_id}
        )
        excluded = ['network:dhcp']
        return [p for p in ports if p['device_owner'] not in excluded] == []

    def list(self):
        networks = []
        for network in self.cloud.list_networks(
                filters={'tenant_id': self.cleanup_project_id}
        ):
            if network['router:external'] is True:
                if not self.options.delete_shared_resources:
                    continue
            networks.append(network)

        return networks

    def delete(self, resource):
        self.cloud.delete_network(resource['id'])

    @staticmethod
    def to_str(resource):
        return "Network (id='{}', name='{}')".format(
            resource['id'], resource['name'])


class SecurityGroups(base.ServiceResource):
    ORDER = 49

    def list(self):
        return [sg for sg in self.cloud.list_security_groups(
            filters={'tenant_id': self.cleanup_project_id})
            if sg['name'] != 'default']

    def delete(self, resource):
        self.cloud.delete_security_group(resource['id'])

    @staticmethod
    def to_str(resource):
        return "Security Group (id='{}', name='{}')".format(
            resource['id'], resource['name'])
