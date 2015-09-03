#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright © 2014 Cloudwatt
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

TOKEN_ID = '04c7d5ffaeef485f9dc69c06db285bdb'
USER_ID = 'c4da488862bd435c9e6c0275a0d0e49a'
PROJECT_ID = '225da22d3ce34b15877ea70b2a575f58'

AUTH_URL = "http://localhost:5000/v2.0"
VOLUME_PUBLIC_ENDPOINT = 'http://public:8776/v1/225da22d3ce34b15877ea70b2a575f58'
IMAGE_PUBLIC_ENDPOINT = 'http://public:9292'
STORAGE_PUBLIC_ENDPOINT = 'http://public:8080/v1/AUTH_ee5b90900a4b4e85938b0ceadf4467f8'
NETWORK_PUBLIC_ENDPOINT = 'https://network0.cw-labs.net'
COMPUTE_PUBLIC_ENDPOINT = 'https://compute0.cw-labs.net/v2/43c9e28327094e1b81484f4b9aee74d5'
METERING_PUBLIC_ENDPOINT = 'https://metric0.cw-labs.net'
ORCHESTRATION_PUBLIC_ENDPOINT = 'https://orchestration0.cw-labs.net/v1'
VOLUME_INTERNAL_ENDPOINT = 'http://internal:8776/v1/225da22d3ce34b15877ea70b2a575f58'
IMAGE_INTERNAL_ENDPOINT = 'http://internal:9292'
STORAGE_INTERNAL_ENDPOINT = 'http://internal:8080/v1/AUTH_ee5b90900a4b4e85938b0ceadf4467f8'
NETWORK_INTERNAL_ENDPOINT = 'http://neutron.usr.lab0.aub.cw-labs.net:9696'
COMPUTE_INTERNAL_ENDPOINT = 'http://nova.usr.lab0.aub.cw-labs.net:8774/v2/43c9e28327094e1b81484f4b9aee74d5'
METERING_INTERNAL_ENDPOINT = 'http://ceilometer.usr.lab0.aub.cw-labs.net:8777'
ORCHESTRATION_INTERNAL_ENDPOINT = 'http://heat.usr.lab0.aub.cw-labs.net:8004/v1'

AUTH_URL_RESPONSE = {
    u'version': {
        u'id': u'v2.0',
        u'links': [
            {u'href': u'%s' % AUTH_URL, u'rel': u'self'},
            {u'href': u'http://docs.openstack.org/api/openstack-identity-service/2.0/content/',
             u'rel': u'describedby',
             u'type': u'text/html'},
            {u'href': u'http://docs.openstack.org/api/openstack-identity-service/2.0/identity-dev-guide-2.0.pdf',
             u'rel': u'describedby',
             u'type': u'application/pdf'}
        ],
        u'media-types': [
            {u'base': u'application/json',
             u'type': u'application/vnd.openstack.identity-v2.0+json'},
            {u'base': u'application/xml',
             u'type': u'application/vnd.openstack.identity-v2.0+xml'}
        ],
        u'status': u'stable',
        u'updated': u'2014-04-17T00:00:00Z'
    }
}

STORAGE_CONTAINERS = ['janeausten', 'marktwain']
STORAGE_OBJECTS = [{'container': 'janeausten', 'name': 'foo'},
                   {'container': 'janeausten', 'name': 'bar'},
                   {'container': 'marktwain', 'name': 'hello world'}]

VOLUMES_IDS = ["45baf976-c20a-4894-a7c3-c94b7376bf55",
               "5aa119a8-d25b-45a7-8d1b-88e127885635"]
SNAPSHOTS_IDS = ["3fbbcccf-d058-4502-8844-6feeffdf4cb5",
                 "e479997c-650b-40a4-9dfe-77655818b0d2"]
ROUTERS_IDS = ["7177abc4-5ae9-4bb7-b0d4-89e94a4abf3b",
               "a9254bdb-2613-4a13-ac4c-adc581fba50d"]
PORTS_IDS = ["d7815f5b-a228-47bb-a5e5-f139c4e476f6"]
NETWORKS_IDS = ["9d83c053-b0a4-4682-ae80-c00df269ce0a",
                "ebda9658-093b-41ba-80ce-0cf8cb8365d4"]
SECGROUPS_IDS = ["85cc3048-abc3-43cc-89b3-377341426ac5"]
FLOATING_IPS_IDS = ["2f245a7b-796b-4f26-9cf9-9e82d248fda7",
                    "61cea855-49cb-4846-997d-801b70c71bdd"]
SERVERS_IDS = ["616fb98f-46ca-475e-917e-2563e5a8cd19"]
IMAGES_IDS = ["37717f53-3707-49b9-9dd0-fd063e6b9fc5", "4e150966-cbe7-4fd7-a964-41e008d20f10",
              "482fbcc3-d831-411d-a073-ddc828a7a9ed"]
ALARMS_IDS = ["ca950223-e982-4552-9dec-5dc5d3ea4172"]
STACKS_IDS = ["5c136348-5550-4ec5-8bd6-b83241844db3",
              "ec4083c1-3667-47d2-91c9-ce0bc8e3c2b9"]
UNBOUND_PORT_ID = "abcdb45e-45fe-4e04-8704-bf6f58760000"

PRIVATE_PORT_IDS = ["p7815f5b-a228-47bb-a5e5-f139c4f476ft", "p78o5f5t-a228-47bb-a5e2-f139c4f476ft"]
FIREWALL_RULE_IDS = ["firebcc3-d831-411d-a073-ddc828a7a9id",
                     "fi7815f5b-a328-47cb-a5e5-f139c4e476f7"]

FIREWALL_POLICY_IDS = ["firebcc3-d831-422d-a073-ccc818a7a9id", "poa119a8-d25b-45a7-8d1b-88e127885630"]
FIREWALL_IDS = ["firewal1-d831-422d-a073-ckc818a7a9ab", "firewa1l-d831-422d-a073-ckc818a7a9ab"]
METERING_LABEL_IDS = ["mbcdb45e-45fe-4e04-8704-bf6f58760011", "meteb45e-45fe-4e04-8704-bf6f58760000"]
LBAAS_MEMBER_IDS = ["37717f53-3707-49b9-9dd0-fd063e6lbass", "la650123-e982-4552-9dec-5dc5d3ea4172"]
LBAAS_VIP_IDS = ["616fb98f-36ca-475e-917e-1563e5a8cd10", "102fbcc3-d831-411d-a333-ddc828a7a9ed"]
LBAAS_HEALTHMONITOR_IDS = ["he717f53-3707-49b9-9dd0-fd063e6lbass"]
LBAAS_POOL_IDS = ["lb815f5b-a228-17bb-a5e5-f139c3e476f6", "dlb15f5b-a228-47bb-a5e5-f139c4e47po6"]

# Simulating JSON sent from the Server

PROJECT_SCOPED_TOKEN = {
    'access': {
        'serviceCatalog':
        [{
            'endpoints': [{
                'adminURL': 'http://admin:8776/v1/225da22d3ce34b15877ea70b2a575f58',
                'internalURL': VOLUME_INTERNAL_ENDPOINT,
                'publicURL': VOLUME_PUBLIC_ENDPOINT,
                'region': 'RegionOne'}],
            'endpoints_links': [],
            'name': 'Volume Service',
            'type': 'volume'
        }, {
            'endpoints': [{
                'adminURL': 'http://admin:9292/v1',
                'internalURL': IMAGE_INTERNAL_ENDPOINT,
                'publicURL': IMAGE_PUBLIC_ENDPOINT,
                'region': 'RegionOne'}],
            'endpoints_links': [],
            'name': 'Image Service',
            'type': 'image'
        }, {
            'endpoints': [{
                'adminURL': 'http://admin:8774/v2/225da22d3ce34b15877ea70b2a575f58',
                'internalURL': COMPUTE_INTERNAL_ENDPOINT,
                'publicURL': COMPUTE_PUBLIC_ENDPOINT,
                'region': 'RegionOne'}],
            'endpoints_links': [],
            'name': 'Compute Service',
            'type': 'compute'
        }, {
            'endpoints': [{
                'adminURL': 'http://admin:8773/services/Admin',
                'internalURL': 'http://internal:8773/services/Cloud',
                'publicURL': 'http://public:8773/services/Cloud',
                'region': 'RegionOne'}],
            'endpoints_links': [],
            'name': 'EC2 Service',
            'type': 'ec2'
        }, {
            'endpoints': [{
                'adminURL': 'http://admin:35357/v2.0',
                'internalURL': 'http://internal:5000/v2.0',
                'publicURL': 'http://public:5000/v2.0',
                'region': 'RegionOne'}],
            'endpoints_links': [],
            'name': 'Identity Service',
            'type': 'identity'
        }, {
            'endpoints': [{
                'adminURL': 'http://admin:8080',
                'internalURL': STORAGE_INTERNAL_ENDPOINT,
                'publicURL': STORAGE_PUBLIC_ENDPOINT,
                'region': 'RegionOne'}],
            'endpoints_links': [],
            'name': 'Object Storage Service',
            'type': 'object-store'
        }, {
            'endpoints': [{
                'adminURL': 'http://neutron.usr.lab0.aub.cw-labs.net:9696',
                'internalURL': NETWORK_INTERNAL_ENDPOINT,
                'publicURL': NETWORK_PUBLIC_ENDPOINT,
                'region': 'RegionOne'}],
            'endpoints_links': [],
            'name': 'Network Service',
            'type': 'network'
        }, {
            'endpoints': [{
                'adminURL': 'http://ceilometer.usr.lab0.aub.cw-labs.net:8777',
                'internalURL': METERING_INTERNAL_ENDPOINT,
                'publicURL': METERING_PUBLIC_ENDPOINT,
                'region': 'RegionOne'}],
            'endpoints_links': [],
            'name': 'Metering service',
            'type': 'metering'
        }, {
            'endpoints': [{
                'adminURL': 'http://heat.usr.lab0.aub.cw-labs.net:8777',
                'internalURL': ORCHESTRATION_INTERNAL_ENDPOINT,
                'publicURL': ORCHESTRATION_PUBLIC_ENDPOINT,
                'region': 'RegionOne'}],
            'endpoints_links': [],
            'name': 'Orchestration service',
            'type': 'orchestration'
        }],
        'token': {
            'expires': '2012-10-03T16:53:36Z',
            'id': TOKEN_ID,
            'tenant': {
                'description': '',
                'enabled': True,
                'id': PROJECT_ID,
                'name': 'exampleproject'
            }
        },
        'user': {
            'id': USER_ID,
            'name': 'exampleuser',
            'roles': [{
                'id': 'edc12489faa74ee0aca0b8a0b4d74a74',
                'name': 'Member'}],
            'roles_links': [],
            'username': 'exampleuser'
        }
    }
}

STORAGE_CONTAINERS_LIST = [
    {
        "count": 0,
        "bytes": 0,
        "name": STORAGE_CONTAINERS[0]
    },
    {
        "count": 1,
        "bytes": 14,
        "name": STORAGE_CONTAINERS[1]
    }
]


STORAGE_OBJECTS_LIST_0 = [
    {
        "hash": "451e372e48e0f6b1114fa0724aa79fa1",
        "last_modified": "2014-01-15T16:41:49.390270",
        "bytes": 14,
        "name": STORAGE_OBJECTS[0]['name'],
        "content_type":"application/octet-stream"
    },
    {
        "hash": "ed076287532e86365e841e92bfc50d8c",
        "last_modified": "2014-01-15T16:37:43.427570",
        "bytes": 12,
        "name": STORAGE_OBJECTS[1]['name'],
        "content_type":"application/octet-stream"
    }
]

STORAGE_OBJECTS_LIST_1 = [
    {
        "hash": "451e372e48e0f6b1114fa0724aa7AAAA",
        "last_modified": "2014-01-15T16:41:49.390270",
        "bytes": 14,
        "name": STORAGE_OBJECTS[2]['name'],
        "content_type":"application/octet-stream"
    }
]


VOLUMES_LIST = {
    "volumes": [
        {
            "attachments": [],
            "availability_zone": "nova",
            "bootable": "false",
            "created_at": "2014-02-03T14:22:52.000000",
            "display_description": None,
            "display_name": "toto",
            "id": VOLUMES_IDS[0],
            "metadata": {},
            "size": 1,
            "snapshot_id": None,
            "source_volid": None,
            "status": "available",
            "volume_type": "None"
        },
        {
            "attachments": [],
            "availability_zone": "nova",
            "bootable": "true",
            "created_at": "2014-02-03T14:18:34.000000",
            "display_description": "",
            "display_name": "CirrOS v0.3.0",
            "id": VOLUMES_IDS[1],
            "metadata": {},
            "size": 1,
            "snapshot_id": None,
            "source_volid": None,
            "status": "available",
            "volume_type": "None"
        }
    ]
}


SNAPSHOTS_LIST = {
    "snapshots": [
        {
            "id": SNAPSHOTS_IDS[0],
            "display_name": "snap-001",
            "display_description": "Daily backup",
            "volume_id": "521752a6-acf6-4b2d-bc7a-119f9148cd8c",
            "status": "available",
            "size": 10,
            "created_at": "2012-02-29T03:50:07Z"
        },
        {
            "id": SNAPSHOTS_IDS[1],
            "display_name": "snap-002",
            "display_description": "Weekly backup",
            "volume_id": "76b8950a-8594-4e5b-8dce-0dfa9c696358",
            "status": "available",
            "size": 25,
            "created_at": "2012-03-19T01:52:47Z"
        }
    ]
}

ROUTERS_LIST = {
    "routers": [{
        "status": "ACTIVE",
        "external_gateway_info":
                {"network_id": "3c5bcddd-6af9-4e6b-9c3e-c153e521cab8"},
                "name": "second_routers",
                "admin_state_up": True,
                "tenant_id": PROJECT_ID,
                "id": ROUTERS_IDS[0]
                }, {
        "status": "ACTIVE",
        "external_gateway_info":
                {"network_id": "3c5bcddd-6af9-4e6b-9c3e-c153e521cab8"},
                "name": "router1",
                "admin_state_up": True,
                "tenant_id": PROJECT_ID,
                "id": ROUTERS_IDS[1]
                }, {
        "status": "ACTIVE",
        "external_gateway_info":
                {"network_id": "3c5bcddd-6af9-4e6b-9c3e-c153e521cab8"},
                "name": "another_router",
                "admin_state_up": True,
                "tenant_id": "6b96ff0cb17a4b859e1e575d221683d3",
                "id": "7177abc4-5ae9-4bb7-b0d4-89e94a4abf3b"
                }]
}

ROUTER_CLEAR_GATEWAY = {
    "router": {
        "status": "ACTIVE",
        "external_gateway_info": None,
        "name": "second_routers",
        "admin_state_up": True,
        "tenant_id": PROJECT_ID,
        "id": ROUTERS_IDS[0]
    }
}

ROUTER0_PORTS = {
    "ports": [
        {
            "status": "ACTIVE",
            "name": "",
            "admin_state_up": True,
            "network_id": "ebda9658-093b-41ba-80ce-0cf8cb8365d4",
            "tenant_id": PROJECT_ID,
            "binding:vif_type": "ovs",
            "device_owner": "network:router_gateway",
            "binding:capabilities": {
                "port_filter": False
            },
            "mac_address": "fa:16:3e:b9:ef:05",
            "fixed_ips": [
                {
                    "subnet_id": "aca4d43c-c48c-4a2c-9bb6-ba374ef7e135",
                    "ip_address": "172.24.4.227"
                }
            ],
            "id": "664ebd1a-facd-4c20-948c-07a784475ab0",
            "device_id": ROUTERS_IDS[0]
        }
    ]
}

ROUTER1_PORTS = {
    "ports": [
        {
            "status": "DOWN",
            "name": "",
            "admin_state_up": True,
            "network_id": "ebda9658-093b-41ba-80ce-0cf8cb8365d4",
            "tenant_id": PROJECT_ID,
            "binding:vif_type": "ovs",
            "device_owner": "network:router_gateway",
            "binding:capabilities": {
                "port_filter": False
            },
            "mac_address": "fa:16:3e:4a:3a:a2",
            "fixed_ips": [
                {
                    "subnet_id": "aca4d43c-c48c-4a2c-9bb6-ba374ef7e135",
                    "ip_address": "172.24.4.226"
                }
            ],
            "id": "c5ca7017-c390-4ccc-8cd7-333747e57fef",
            "device_id": ROUTERS_IDS[1]
        },
        {
            "status": "ACTIVE",
            "name": "",
            "admin_state_up": True,
            "network_id": "9d83c053-b0a4-4682-ae80-c00df269ce0a",
            "tenant_id": PROJECT_ID,
            "binding:vif_type": "ovs",
            "device_owner": "network:router_interface",
            "binding:capabilities": {
                "port_filter": False
            },
            "mac_address": "fa:16:3e:2d:dc:7e",
            "fixed_ips": [
                {
                    "subnet_id": "a318fcb4-9ff0-4485-b78c-9e6738c21b26",
                    "ip_address": "10.0.0.1"
                }
            ],
            "id": PORTS_IDS[0],
            "device_id": ROUTERS_IDS[1]
        }
    ]
}


NEUTRON_PORTS = {
    'ports': ROUTER0_PORTS['ports'] + ROUTER1_PORTS['ports'] + [
        {
            "admin_state_up": True,
            "allowed_address_pairs": [],
            "binding:capabilities": {
                "port_filter": False
            },
            "binding:host_id": "",
            "binding:vif_type": "unbound",
            "device_id": "",
            "device_owner": "compute:azerty",
            "extra_dhcp_opts": [],
            "fixed_ips": [
                {
                    "ip_address": "10.0.0.4",
                    "subnet_id": "51351eb9-7ce5-42cf-89cd-cea0b0fc510f"
                }
            ],
            "id": UNBOUND_PORT_ID,
            "mac_address": "fa:16:3e:f5:62:22",
            "name": "custom unbound port",
            "network_id": "bf8d2e1f-221e-4908-a4ed-b6c0fd06e518",
            "security_groups": [
                "766110ac-0fde-4c31-aed7-72a97e78310b"
            ],
            "status": "DOWN",
            "tenant_id": PROJECT_ID
        },
        {
            "admin_state_up": True,
            "allowed_address_pairs": [],
            "binding:capabilities": {
                "port_filter": False
            },
            "binding:host_id": "",
            "binding:vif_type": "unbound",
            "device_id": "",
            "device_owner": "",
            "extra_dhcp_opts": [],
            "fixed_ips": [
                {
                    "ip_address": "10.0.0.4",
                    "subnet_id": "51351eb9-7ce5-42cf-89cd-cea0b0fc510f"
                }
            ],
            "id": "61c1b45e-45fe-4e04-8704-bf6f5876607d",
            "mac_address": "fa:16:3e:f5:62:22",
            "name": "custom unbound port",
            "network_id": "bf8d2e1f-221e-4908-a4ed-b6c0fd06e518",
            "security_groups": [
                "766110ac-0fde-4c31-aed7-72a97e78310b"
            ],
            "status": "DOWN",
            "tenant_id": "ANOTHER_PROJECT"
        }
    ]}

REMOVE_ROUTER_INTERFACE = {
    "id": "8604a0de-7f6b-409a-a47c-a1cc7bc77b2e",
    "tenant_id": "2f245a7b-796b-4f26-9cf9-9e82d248fda7",
    "port_id": "3a44f4e5-1694-493a-a1fb-393881c673a4",
    "subnet_id": "a2f1f29d-571b-4533-907f-5803ab96ead1"
}


NETWORKS_LIST = {
    "networks": [
        {
            "status": "ACTIVE",
            "subnets": ["a318fcb4-9ff0-4485-b78c-9e6738c21b26"],
            "name": "private",
            "admin_state_up": True,
            "tenant_id": PROJECT_ID,
            "id": NETWORKS_IDS[0],
            "shared": False
        },
        {
            "status": "ACTIVE",
            "subnets": ["aca4d43c-c48c-4a2c-9bb6-ba374ef7e135"],
            "name": "nova",
            "admin_state_up": True,
            "tenant_id": PROJECT_ID,
            "id": NETWORKS_IDS[1],
            "shared": False
        },
        {
            "status": "ACTIVE",
            "subnets": ["e12f0c45-46e3-446a-b207-9474b27687a6"],
            "name": "network_3",
            "admin_state_up": True,
            "tenant_id": "ed680f49ff714162ab3612d7876ffce5",
            "id": "afc75773-640e-403c-9fff-62ba98db1f19",
            "shared": True
        }
    ]
}

SECGROUPS_LIST = {
    "security_groups": [
        {
            "description": "Custom Security Group",
            "id": "85cc3048-abc3-43cc-89b3-377341426ac5",
            "name": "custom",
            "security_group_rules": [
                {
                    "direction": "egress",
                    "ethertype": "IPv6",
                    "id": "3c0e45ff-adaf-4124-b083-bf390e5482ff",
                    "port_range_max": None,
                    "port_range_min": None,
                    "protocol": None,
                    "remote_group_id": None,
                    "remote_ip_prefix": None,
                    "security_group_id": "85cc3048-abc3-43cc-89b3-377341426ac5",
                    "tenant_id": PROJECT_ID
                },
                {
                    "direction": "egress",
                    "ethertype": "IPv4",
                    "id": "93aa42e5-80db-4581-9391-3a608bd0e448",
                    "port_range_max": None,
                    "port_range_min": None,
                    "protocol": None,
                    "remote_group_id": None,
                    "remote_ip_prefix": None,
                    "security_group_id": "85cc3048-abc3-43cc-89b3-377341426ac5",
                    "tenant_id": PROJECT_ID
                },
                {
                    "direction": "ingress",
                    "ethertype": "IPv6",
                    "id": "c0b09f00-1d49-4e64-a0a7-8a186d928138",
                    "port_range_max": None,
                    "port_range_min": None,
                    "protocol": None,
                    "remote_group_id": "85cc3048-abc3-43cc-89b3-377341426ac5",
                    "remote_ip_prefix": None,
                    "security_group_id": "85cc3048-abc3-43cc-89b3-377341426ac5",
                    "tenant_id": PROJECT_ID
                },
                {
                    "direction": "ingress",
                    "ethertype": "IPv4",
                    "id": "f7d45c89-008e-4bab-88ad-d6811724c51c",
                    "port_range_max": None,
                    "port_range_min": None,
                    "protocol": None,
                    "remote_group_id": "85cc3048-abc3-43cc-89b3-377341426ac5",
                    "remote_ip_prefix": None,
                    "security_group_id": "85cc3048-abc3-43cc-89b3-377341426ac5",
                    "tenant_id": PROJECT_ID
                }
            ],
            "tenant_id": PROJECT_ID
        },
        {
            "description": "default",
            "id": "12345678-1234-1234-1234-123456789012",
            "name": "default",
            "security_group_rules": [
                {
                    "direction": "egress",
                    "ethertype": "IPv6",
                    "id": "3c0e45ff-adaf-4124-b083-bf390e5482ff",
                    "port_range_max": None,
                    "port_range_min": None,
                    "protocol": None,
                    "remote_group_id": None,
                    "remote_ip_prefix": None,
                    "security_group_id": "12345678-1234-1234-1234-123456789012",
                    "tenant_id": PROJECT_ID
                },
                {
                    "direction": "egress",
                    "ethertype": "IPv4",
                    "id": "93aa42e5-80db-4581-9391-3a608bd0e448",
                    "port_range_max": None,
                    "port_range_min": None,
                    "protocol": None,
                    "remote_group_id": None,
                    "remote_ip_prefix": None,
                    "security_group_id": "12345678-1234-1234-1234-123456789012",
                    "tenant_id": PROJECT_ID
                },
                {
                    "direction": "ingress",
                    "ethertype": "IPv6",
                    "id": "c0b09f00-1d49-4e64-a0a7-8a186d928138",
                    "port_range_max": None,
                    "port_range_min": None,
                    "protocol": None,
                    "remote_group_id": "85cc3048-abc3-43cc-89b3-377341426ac5",
                    "remote_ip_prefix": None,
                    "security_group_id": "12345678-1234-1234-1234-123456789012",
                    "tenant_id": PROJECT_ID
                },
                {
                    "direction": "ingress",
                    "ethertype": "IPv4",
                    "id": "f7d45c89-008e-4bab-88ad-d6811724c51c",
                    "port_range_max": None,
                    "port_range_min": None,
                    "protocol": None,
                    "remote_group_id": "85cc3048-abc3-43cc-89b3-377341426ac5",
                    "remote_ip_prefix": None,
                    "security_group_id": "12345678-1234-1234-1234-123456789012",
                    "tenant_id": PROJECT_ID
                }
            ],
            "tenant_id": PROJECT_ID
        }
    ]
}


FLOATING_IPS_LIST = {
    "floatingips":
    [
        {
            "router_id": "d23abc8d-2991-4a55-ba98-2aaea84cc72f",
            "tenant_id": PROJECT_ID,
            "floating_network_id": "376da547-b977-4cfe-9cba-275c80debf57",
            "fixed_ip_address": "10.0.0.3",
            "floating_ip_address": "172.24.4.228",
            "port_id": "ce705c24-c1ef-408a-bda3-7bbd946164ab",
            "id": FLOATING_IPS_IDS[0]
        },
        {
            "router_id": None,
            "tenant_id": PROJECT_ID,
            "floating_network_id": "376da547-b977-4cfe-9cba-275c80debf57",
            "fixed_ip_address": None,
            "floating_ip_address": "172.24.4.227",
            "port_id": None,
            "id": FLOATING_IPS_IDS[1]
        }
    ]
}

LBAAS_HEALTHMONITOR_LIST = {
    "health_monitors":
    [
        {
            "admin_state_up": True,
            "tenant_id": PROJECT_ID,
            "delay": 5,
            "expected_codes": "200",
            "max_retries": 5,
            "http_method": "GET",
            "timeout": 2,
            "pools": [],
            "url_path": "/",
            "type": "HTTP",
            "id": LBAAS_HEALTHMONITOR_IDS[0]
        }
    ]
}

LBAAS_VIP_LIST = {
    "vips":
    [
        {
            "status": "ACTIVE",
            "protocol": "HTTP",
            "description": "",
            "address": "10.0.0.125",
            "protocol_port": 80,
            "port_id": PRIVATE_PORT_IDS[0],
            "id": LBAAS_VIP_IDS[0],
            "status_description": "",
            "name": "test-http-vip",
            "admin_state_up": True,
            "tenant_id": PROJECT_ID,
            "subnet_id": "b892434a-59f7-4404-a05d-9562977e1678",
            "connection_limit": -1,
            "pool_id": LBAAS_POOL_IDS[0],
            "session_persistence": None
        },
        {
            "status": "ACTIVE",
            "protocol": "HTTP",
            "description": "",
            "address": "10.0.0.126",
            "protocol_port": 80,
            "port_id": PRIVATE_PORT_IDS[1],
            "id": LBAAS_VIP_IDS[1],
            "status_description": "",
            "name": "test-http-vip",
            "admin_state_up": True,
            "tenant_id": PROJECT_ID,
            "subnet_id": "b892434a-49f7-4404-a05d-9562977e1678",
            "connection_limit": -1,
            "pool_id": LBAAS_POOL_IDS[1],
            "session_persistence": None
        }
    ]
}

LBAAS_POOL_LIST = {
    "pools":
    [
        {
            "status": "ACTIVE",
            "lb_method": "ROUND_ROBIN",
            "protocol": "HTTP",
            "description": "",
            "health_monitors": [],
            "subnet_id": "b892434a-59f7-4404-a05d-9562977e1678",
            "tenant_id": PROJECT_ID,
            "admin_state_up": True,
            "name": "Test-Pools",
            "health_monitors_status": [],
            "members": [],
            "provider": "haproxy",
            "status_description": None,
            "id": LBAAS_POOL_IDS[0]
        },
        {
            "status": "ACTIVE",
            "lb_method": "ROUND_ROBIN",
            "protocol": "HTTP",
            "description": "",
            "health_monitors": [],
            "subnet_id": "b892434a-49f7-4404-a05d-9562977e1678",
            "tenant_id": PROJECT_ID,
            "admin_state_up": True,
            "name": "Test-Pools",
            "health_monitors_status": [],
            "members": [],
            "provider": "haproxy",
            "status_description": None,
            "id": LBAAS_POOL_IDS[1]
        }
    ]
}

LBAAS_MEMBER_LIST = {
    "members":
    [
        {
            "id": LBAAS_MEMBER_IDS[0],
            "address": "10.0.0.122",
            "protocol_port": 80,
            "tenant_id": PROJECT_ID,
            "admin_state_up": True,
            "weight": 1,
            "status": "ACTIVE",
            "status_description": "member test1",
            "pool_id": LBAAS_POOL_IDS[0]
        },
        {
            "id": LBAAS_MEMBER_IDS[1],
            "address": "10.0.0.123",
            "protocol_port": 80,
            "tenant_id": PROJECT_ID,
            "admin_state_up": True,
            "weight": 1,
            "status": "ACTIVE",
            "status_description": "member test1",
            "pool_id": LBAAS_POOL_IDS[1]
        }
    ]
}

FIREWALL_LIST = {
    "firewalls":
    [
        {
            "status": "ACTIVE",
            "name": "fwass-test-1",
            "admin_state_up": True,
            "tenant_id": PROJECT_ID,
            "firewall_policy_id": FIREWALL_POLICY_IDS[0],
            "id": FIREWALL_IDS[0],
            "description": ""
        },
        {
            "status": "ACTIVE",
            "name": "fwass-test-2",
            "admin_state_up": True,
            "tenant_id": PROJECT_ID,
            "firewall_policy_id": FIREWALL_POLICY_IDS[1],
            "id": FIREWALL_IDS[1],
            "description": ""
        }
    ]
}

METERING_LABEL_LIST = {
    "metering_labels":
    [
        {
            "tenant_id": PROJECT_ID,
            "description": "Meter label test1",
            "name": "Meterlabel1",
            "id": METERING_LABEL_IDS[0]
        },
        {
            "tenant_id": PROJECT_ID,
            "description": "Meter label test2",
            "name": "Meterlabel2",
            "id": METERING_LABEL_IDS[1]
        }
    ]
}

FIREWALL_POLICY_LIST = {
    "firewall_policies":
    [
        {
            "name": "TestFireWallPolicy1",
            "firewall_rules": [FIREWALL_RULE_IDS[0]],
            "tenant_id": PROJECT_ID,
            "audited": False,
            "shared": False,
            "id": FIREWALL_POLICY_IDS[0],
            "description": "Testing firewall policy 1"
        },
        {
            "name": "TestFireWallPolicy2",
            "firewall_rules": [FIREWALL_RULE_IDS[1]],
            "tenant_id": PROJECT_ID,
            "audited": False,
            "shared": False,
            "id": FIREWALL_POLICY_IDS[1],
            "description": "Testing firewall policy 2"
        }
    ]
}

FIREWALL_RULE_LIST = {
    "firewall_rules":
    [
        {
            "protocol": "tcp",
            "description": "Firewall rule 1",
            "source_port": None,
            "source_ip_address": None,
            "destination_ip_address": None,
            "firewall_policy_id": None,
            "position": None,
            "destination_port": "80",
            "id": FIREWALL_RULE_IDS[0],
            "name": "",
            "tenant_id": PROJECT_ID,
            "enabled": True,
            "action": "allow",
            "ip_version": 4,
            "shared": False
        },
        {
            "protocol": "tcp",
            "description": "Firewall rule 1",
            "source_port": None,
            "source_ip_address": None,
            "destination_ip_address": None,
            "firewall_policy_id": None,
            "position": None,
            "destination_port": "80",
            "id": FIREWALL_RULE_IDS[1],
            "name": "",
            "tenant_id": PROJECT_ID,
            "enabled": True,
            "action": "allow",
            "ip_version": 4,
            "shared": False
        }
    ]
}


SERVERS_LIST = {
    "servers": [
        {
            "accessIPv4": "",
            "accessIPv6": "",
            "addresses": {
                "private": [
                    {
                        "addr": "192.168.0.3",
                        "version": 4
                    }
                ]
            },
            "created": "2012-09-07T16:56:37Z",
            "flavor": {
                "id": "1",
                "links": [
                    {
                        "href": "http://openstack.example.com/openstack/flavors/1",
                        "rel": "bookmark"
                    }
                ]
            },
            "hostId": "16d193736a5cfdb60c697ca27ad071d6126fa13baeb670fc9d10645e",
            "id": SERVERS_IDS[0],
            "image": {
                "id": "70a599e0-31e7-49b7-b260-868f441e862b",
                "links": [
                    {
                        "href": "http://openstack.example.com/openstack/images/70a599e0-31e7-49b7-b260-868f441e862b",
                        "rel": "bookmark"
                    }
                ]
            },
            "links": [
                {
                    "href": "http://openstack.example.com/v2/openstack/servers/05184ba3-00ba-4fbc-b7a2-03b62b884931",
                    "rel": "self"
                },
                {
                    "href": "http://openstack.example.com/openstack/servers/05184ba3-00ba-4fbc-b7a2-03b62b884931",
                    "rel": "bookmark"
                }
            ],
            "metadata": {
                "My Server Name": "Apache1"
            },
            "name": "new-server-test",
            "progress": 0,
            "status": "ACTIVE",
            "tenant_id": "openstack",
            "updated": "2012-09-07T16:56:37Z",
            "user_id": "fake"
        }
    ]
}

IMAGES_LIST = {
    "images": [
        {
            "checksum": "f8a2eeee2dc65b3d9b6e63678955bd83",
            "container_format": "ami",
            "created_at": "2014-02-03T14:13:53",
            "deleted": False,
            "deleted_at": None,
            "disk_format": "ami",
            "id": "37717f53-3707-49b9-9dd0-fd063e6b9fc5",
            "is_public": True,
            "min_disk": 0,
            "min_ram": 0,
            "name": "cirros-0.3.1-x86_64-uec",
            "owner": PROJECT_ID,
            "properties": {
                "kernel_id": "4e150966-cbe7-4fd7-a964-41e008d20f10",
                "ramdisk_id": "482fbcc3-d831-411d-a073-ddc828a7a9ed"
            },
            "protected": False,
            "size": 25165824,
            "status": "active",
            "updated_at": "2014-02-03T14:13:54"
        },
        {
            "checksum": "c352f4e7121c6eae958bc1570324f17e",
            "container_format": "aki",
            "created_at": "2014-02-03T14:13:52",
            "deleted": False,
            "deleted_at": None,
            "disk_format": "aki",
            "id": "4e150966-cbe7-4fd7-a964-41e008d20f10",
            "is_public": True,
            "min_disk": 0,
            "min_ram": 0,
            "name": "cirros-0.3.1-x86_64-uec-kernel",
            "owner": PROJECT_ID,
            "properties": {},
            "protected": False,
            "size": 4955792,
            "status": "active",
            "updated_at": "2014-02-03T14:13:52"
        },
        {
            "checksum": "69c33642f44ca552ba4bb8b66ad97e85",
            "container_format": "ari",
            "created_at": "2014-02-03T14:13:53",
            "deleted": False,
            "deleted_at": None,
            "disk_format": "ari",
            "id": "482fbcc3-d831-411d-a073-ddc828a7a9ed",
            "is_public": True,
            "min_disk": 0,
            "min_ram": 0,
            "name": "cirros-0.3.1-x86_64-uec-ramdisk",
            "owner": PROJECT_ID,
            "properties": {},
            "protected": False,
            "size": 3714968,
            "status": "active",
            "updated_at": "2014-02-03T14:13:53"
        }
    ]
}

ALARMS_LIST = [
    {
        "alarm_actions": [
            "http://site:8000/alarm"
        ],
        "alarm_id": ALARMS_IDS[0],
        "combination_rule": None,
        "description": "An alarm",
        "enabled": True,
        "insufficient_data_actions": [
            "http://site:8000/nodata"
        ],
        "name": "SwiftObjectAlarm",
        "ok_actions": [
            "http://site:8000/ok"
        ],
        "project_id": "c96c887c216949acbdfbd8b494863567",
        "repeat_actions": False,
        "state": "ok",
        "state_timestamp": "2013-11-21T12:33:08.486228",
        "threshold_rule": None,
        "timestamp": "2013-11-21T12:33:08.486221",
        "type": "threshold",
        "user_id": "c96c887c216949acbdfbd8b494863567"
    }
]

STACKS_LIST = {
    "stacks": [
        {
            "description": "First test",
            "links": [
                {
                    "href": "http://site/5c136348-5550-4ec5-8bd6-b83241844db3",
                    "rel": "self"
                }
            ],
            "stack_status_reason": "",
            "stack_name": "stack1",
            "creation_time": "2015-03-03T14:08:54Z",
            "updated_time": None,
            "stack_status": "CREATE_SUCCESS",
            "id": "5c136348-5550-4ec5-8bd6-b83241844db3"
        },
        {
            "description": "Second test",
            "links": [
                {
                    "href": "http://site/ec4083c1-3667-47d2-91c9-ce0bc8e3c2b9",
                    "rel": "self"
                }
            ],
            "stack_status_reason": "",
            "stack_name": "stack2",
            "creation_time": "2015-03-03T17:34:21Z",
            "updated_time": None,
            "stack_status": "DELETE_FAILED",
            "id": "ec4083c1-3667-47d2-91c9-ce0bc8e3c2b9"
        }
    ]
}
