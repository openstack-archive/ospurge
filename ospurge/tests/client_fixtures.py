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

VOLUME_PUBLIC_ENDPOINT = 'http://public:8776/v1/225da22d3ce34b15877ea70b2a575f58'
IMAGE_PUBLIC_ENDPOINT = 'http://public:9292'
STORAGE_PUBLIC_ENDPOINT = 'http://public:8080/v1/AUTH_ee5b90900a4b4e85938b0ceadf4467f8'
NETWORK_PUBLIC_ENDPOINT = 'https://network0.cw-labs.net'
COMPUTE_PUBLIC_ENDPOINT = 'https://compute0.cw-labs.net/v2/43c9e28327094e1b81484f4b9aee74d5'
METERING_PUBLIC_ENDPOINT = 'https://metric0.cw-labs.net'
VOLUME_INTERNAL_ENDPOINT = 'http://internal:8776/v1/225da22d3ce34b15877ea70b2a575f58'
IMAGE_INTERNAL_ENDPOINT = 'http://internal:9292'
STORAGE_INTERNAL_ENDPOINT = 'http://internal:8080/v1/AUTH_ee5b90900a4b4e85938b0ceadf4467f8'
NETWORK_INTERNAL_ENDPOINT = 'http://neutron.usr.lab0.aub.cw-labs.net:9696'
COMPUTE_INTERNAL_ENDPOINT = 'http://nova.usr.lab0.aub.cw-labs.net:8774/v2/43c9e28327094e1b81484f4b9aee74d5'
METERING_INTERNAL_ENDPOINT = 'http://ceilometer.usr.lab0.aub.cw-labs.net:8777'


STORAGE_CONTAINERS = ['janeausten', 'marktwain']
STORAGE_OBJECTS = [{'container': 'janeausten', 'name': 'foo'},
                   {'container': 'janeausten', 'name': 'bar'},
                   {'container': 'marktwain', 'name': 'hello world'}]

VOLUMES_IDS = ["45baf976-c20a-4894-a7c3-c94b7376bf55", "5aa119a8-d25b-45a7-8d1b-88e127885635"]
SNAPSHOTS_IDS = ["3fbbcccf-d058-4502-8844-6feeffdf4cb5", "e479997c-650b-40a4-9dfe-77655818b0d2"]
ROUTERS_IDS = ["7177abc4-5ae9-4bb7-b0d4-89e94a4abf3b", "a9254bdb-2613-4a13-ac4c-adc581fba50d"]
PORTS_IDS = ["d7815f5b-a228-47bb-a5e5-f139c4e476f6"]
NETWORKS_IDS = ["9d83c053-b0a4-4682-ae80-c00df269ce0a", "ebda9658-093b-41ba-80ce-0cf8cb8365d4"]
SECGROUPS_IDS = ["85cc3048-abc3-43cc-89b3-377341426ac5"]
FLOATING_IPS_IDS = ["2f245a7b-796b-4f26-9cf9-9e82d248fda7", "61cea855-49cb-4846-997d-801b70c71bdd"]
SERVERS_IDS = ["616fb98f-46ca-475e-917e-2563e5a8cd19"]
IMAGES_IDS = ["37717f53-3707-49b9-9dd0-fd063e6b9fc5", "4e150966-cbe7-4fd7-a964-41e008d20f10",
              "482fbcc3-d831-411d-a073-ddc828a7a9ed"]
ALARMS_IDS = ["ca950223-e982-4552-9dec-5dc5d3ea4172"]

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
      "hash":"451e372e48e0f6b1114fa0724aa79fa1",
      "last_modified":"2014-01-15T16:41:49.390270",
      "bytes":14,
      "name":STORAGE_OBJECTS[0]['name'],
      "content_type":"application/octet-stream"
   },
   {
      "hash":"ed076287532e86365e841e92bfc50d8c",
      "last_modified":"2014-01-15T16:37:43.427570",
      "bytes":12,
      "name":STORAGE_OBJECTS[1]['name'],
      "content_type":"application/octet-stream"
   }
]

STORAGE_OBJECTS_LIST_1 = [
   {
      "hash":"451e372e48e0f6b1114fa0724aa7AAAA",
      "last_modified":"2014-01-15T16:41:49.390270",
      "bytes":14,
      "name":STORAGE_OBJECTS[2]['name'],
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
    "ports":[
        {
            "status":"ACTIVE",
            "name":"",
            "admin_state_up":True,
            "network_id":"ebda9658-093b-41ba-80ce-0cf8cb8365d4",
            "tenant_id":"63878e4c5dd649d2a980e37aefddfa87",
            "binding:vif_type":"ovs",
            "device_owner":"compute:None",
            "binding:capabilities":{
                "port_filter":False
                },
            "mac_address":"fa:16:3e:b9:ef:05",
            "fixed_ips":[
                {
                    "subnet_id":"aca4d43c-c48c-4a2c-9bb6-ba374ef7e135",
                    "ip_address":"172.24.4.227"
                    }
                ],
            "id": "664ebd1a-facd-4c20-948c-07a784475ab0",
            "device_id": ROUTERS_IDS[0]
            }
        ]
    }

ROUTER1_PORTS = {
    "ports":[
        {
            "status":"DOWN",
            "name":"",
            "admin_state_up":True,
            "network_id":"ebda9658-093b-41ba-80ce-0cf8cb8365d4",
            "tenant_id":"",
            "binding:vif_type":"ovs",
            "device_owner":"network:router_gateway",
            "binding:capabilities":{
                "port_filter":False
                },
            "mac_address":"fa:16:3e:4a:3a:a2",
            "fixed_ips":[
                {
                    "subnet_id":"aca4d43c-c48c-4a2c-9bb6-ba374ef7e135",
                    "ip_address":"172.24.4.226"
                    }
                ],
            "id": "c5ca7017-c390-4ccc-8cd7-333747e57fef",
            "device_id": ROUTERS_IDS[1]
            },
        {
            "status":"ACTIVE",
            "name":"",
            "admin_state_up":True,
            "network_id":"9d83c053-b0a4-4682-ae80-c00df269ce0a",
            "tenant_id":"625887121e364204873d362b553ab171",
            "binding:vif_type":"ovs",
            "device_owner":"network:router_interface",
            "binding:capabilities":{
                "port_filter":False
                },
            "mac_address":"fa:16:3e:2d:dc:7e",
            "fixed_ips":[
                {
                    "subnet_id":"a318fcb4-9ff0-4485-b78c-9e6738c21b26",
                    "ip_address":"10.0.0.1"
                    }
                ],
            "id": PORTS_IDS[0],
            "device_id": ROUTERS_IDS[1]
            }
        ]
    }


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
    "security_groups":[
        {
            "description":"Custom Security Group",
            "id":"85cc3048-abc3-43cc-89b3-377341426ac5",
            "name":"custom",
            "security_group_rules":[
                {
                    "direction":"egress",
                    "ethertype":"IPv6",
                    "id":"3c0e45ff-adaf-4124-b083-bf390e5482ff",
                    "port_range_max":None,
                    "port_range_min":None,
                    "protocol":None,
                    "remote_group_id":None,
                    "remote_ip_prefix":None,
                    "security_group_id":"85cc3048-abc3-43cc-89b3-377341426ac5",
                    "tenant_id": PROJECT_ID
                    },
                {
                    "direction":"egress",
                    "ethertype":"IPv4",
                    "id":"93aa42e5-80db-4581-9391-3a608bd0e448",
                    "port_range_max":None,
                    "port_range_min":None,
                    "protocol":None,
                    "remote_group_id":None,
                    "remote_ip_prefix":None,
                    "security_group_id":"85cc3048-abc3-43cc-89b3-377341426ac5",
                    "tenant_id": PROJECT_ID
                    },
                {
                    "direction":"ingress",
                    "ethertype":"IPv6",
                    "id":"c0b09f00-1d49-4e64-a0a7-8a186d928138",
                    "port_range_max":None,
                    "port_range_min":None,
                    "protocol":None,
                    "remote_group_id":"85cc3048-abc3-43cc-89b3-377341426ac5",
                    "remote_ip_prefix":None,
                    "security_group_id":"85cc3048-abc3-43cc-89b3-377341426ac5",
                    "tenant_id": PROJECT_ID
                    },
                {
                    "direction":"ingress",
                    "ethertype":"IPv4",
                    "id":"f7d45c89-008e-4bab-88ad-d6811724c51c",
                    "port_range_max":None,
                    "port_range_min":None,
                    "protocol":None,
                    "remote_group_id":"85cc3048-abc3-43cc-89b3-377341426ac5",
                    "remote_ip_prefix":None,
                    "security_group_id":"85cc3048-abc3-43cc-89b3-377341426ac5",
                    "tenant_id": PROJECT_ID
                    }
                ],
            "tenant_id": PROJECT_ID
            },
        {
            "description":"default",
            "id":"12345678-1234-1234-1234-123456789012",
            "name":"default",
            "security_group_rules":[
                {
                    "direction":"egress",
                    "ethertype":"IPv6",
                    "id":"3c0e45ff-adaf-4124-b083-bf390e5482ff",
                    "port_range_max":None,
                    "port_range_min":None,
                    "protocol":None,
                    "remote_group_id":None,
                    "remote_ip_prefix":None,
                    "security_group_id":"12345678-1234-1234-1234-123456789012",
                    "tenant_id": PROJECT_ID
                    },
                {
                    "direction":"egress",
                    "ethertype":"IPv4",
                    "id":"93aa42e5-80db-4581-9391-3a608bd0e448",
                    "port_range_max":None,
                    "port_range_min":None,
                    "protocol":None,
                    "remote_group_id":None,
                    "remote_ip_prefix":None,
                    "security_group_id":"12345678-1234-1234-1234-123456789012",
                    "tenant_id": PROJECT_ID
                    },
                {
                    "direction":"ingress",
                    "ethertype":"IPv6",
                    "id":"c0b09f00-1d49-4e64-a0a7-8a186d928138",
                    "port_range_max":None,
                    "port_range_min":None,
                    "protocol":None,
                    "remote_group_id":"85cc3048-abc3-43cc-89b3-377341426ac5",
                    "remote_ip_prefix":None,
                    "security_group_id":"12345678-1234-1234-1234-123456789012",
                    "tenant_id": PROJECT_ID
                    },
                {
                    "direction":"ingress",
                    "ethertype":"IPv4",
                    "id":"f7d45c89-008e-4bab-88ad-d6811724c51c",
                    "port_range_max":None,
                    "port_range_min":None,
                    "protocol":None,
                    "remote_group_id":"85cc3048-abc3-43cc-89b3-377341426ac5",
                    "remote_ip_prefix":None,
                    "security_group_id":"12345678-1234-1234-1234-123456789012",
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
