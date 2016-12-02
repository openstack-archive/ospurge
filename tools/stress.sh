#!/usr/bin/env bash
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

# Be strict (but not too much: '-u' doesn't always play nice with devstack)
set -eo pipefail

readonly PROGDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source ~/devstack/openrc admin admin

###############################
### Set quotas
###############################
project_id=$(openstack token issue | awk '/ project_id /{print $4}')
openstack quota set --subnets 15 ${project_id}
openstack quota set --networks 15 ${project_id}
openstack quota set --volumes 15 ${project_id}
openstack quota set --snapshots 15 ${project_id}
openstack quota set --instances 15 ${project_id}
openstack quota set --secgroups 15 ${project_id}
openstack quota set --routers 15 ${project_id}
openstack quota set --backups 15 ${project_id}



###############################
### Populate project
###############################
seq 12 | parallel --halt-on-error 1 -n0 -j3 ${PROGDIR}/populate.sh



###############################
### Cleanup project
###############################
tox -e run -- --os-cloud devstack-admin --purge-own-project --verbose
