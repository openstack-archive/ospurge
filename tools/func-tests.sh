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
set -x

readonly PROGDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Try to detect whether we run in the OpenStack Gate.
if [[ -d ~stack/devstack ]]; then
    export DEVSTACK_DIR=~stack/devstack
    GATE_RUN=1
else
    export DEVSTACK_DIR=~/devstack
    GATE_RUN=0
fi

#projectname_username
invisible_to_admin_demo_pass=$(cat $DEVSTACK_DIR/accrc/invisible_to_admin/demo | sed -nr 's/.*OS_PASSWORD="(.*)"/\1/p')
admin_admin_pass=$(cat $DEVSTACK_DIR/accrc/admin/admin | sed -nr 's/.*OS_PASSWORD="(.*)"/\1/p')

function assert_stack {
    if [[ $(openstack stack list | wc -l) -lt 1 ]]; then
        echo "Less than one stack, someone cleaned our stack :("
        exit 1
    fi
}

function assert_compute {
    if [[ $(nova list | wc -l) -lt 5 ]]; then
        echo "Less than one VM, someone cleaned our VM :("
        exit 1
    fi
}

function assert_network {
    # We expect at least 1 "" (free), 1 "compute:",
    # 1 "network:router_interface" and 1 "network:dhcp" ports
    if [[ $(neutron port-list | wc -l) -lt 8 ]]; then
        echo "Less than 4 ports, someone cleaned our ports :("
        exit 1
    fi

    # We expect at least 2 security groups (default + one created by populate)
    if [[ $(openstack security group list | wc -l) -lt 6 ]]; then
        echo "Less than 2 security groups, someone cleaned our sec-groups :("
        exit 1
    fi

    if [[ $(openstack floating ip list | wc -l) -lt 5 ]]; then
        echo "Less than one floating ip, someone cleaned our FIP :("
        exit 1
    fi
}

function assert_volume {
    if [[ ${GATE_RUN} == 1 ]]; then
        # The Cinder backup service is enabled in the Gate.
        if [[ $(openstack volume backup list | wc -l) -lt 5 ]]; then
            echo "Less than one backup, someone cleaned our backup:("
            exit 1
        fi
    else
        if [[ $(openstack volume list | wc -l) -lt 5 ]]; then
            echo "Less than one volume, someone cleaned our volume:("
            exit 1
        fi
    fi
}



########################
### Pre check
########################
source $DEVSTACK_DIR/openrc admin admin
if [[ ! "$(openstack flavor list)" =~ 'm1.nano' ]]; then
    openstack flavor create --id 42 --ram 64 --disk 0 --vcpus 1 m1.nano
fi



########################
### Populate
########################
pid=()

(source $DEVSTACK_DIR/openrc admin admin && ${PROGDIR}/populate.sh) &
pid+=($!)

(source $DEVSTACK_DIR/openrc demo demo && ${PROGDIR}/populate.sh) &
pid+=($!)

(source $DEVSTACK_DIR/openrc demo invisible_to_admin && ${PROGDIR}/populate.sh) &
pid+=($!)

#(source $DEVSTACK_DIR/openrc alt_demo alt_demo && ${PROGDIR}/populate.sh) &
#pid+=($!)

for i in ${!pid[@]}; do
    wait ${pid[i]}
    if [[ $? -ne 0 ]]; then
        echo "One of the 'populate.sh' execution failed."
        exit 1
    fi
    unset "pid[$i]"
done



########################
### Cleanup
########################
tox -e run -- --os-cloud devstack-admin --purge-own-project --verbose # purges admin/admin

source $DEVSTACK_DIR/openrc demo demo
assert_stack && assert_compute && assert_network && assert_volume

tox -e run -- --os-cloud devstack --purge-own-project --verbose # purges demo/demo

source $DEVSTACK_DIR/openrc demo invisible_to_admin
assert_stack && assert_compute && assert_network && assert_volume

tox -e run -- \
    --os-auth-url http://localhost/identity \
    --os-username demo --os-project-name invisible_to_admin \
    --os-password $invisible_to_admin_demo_pass \
    --os-domain-id=$OS_PROJECT_DOMAIN_ID \
    --purge-own-project --verbose

#source $DEVSTACK_DIR/openrc alt_demo alt_demo
#assert_stack && assert_compute && assert_network && assert_volume

source $DEVSTACK_DIR/openrc admin admin
#openstack project set --disable alt_demo
#tox -e run -- --os-auth-url http://localhost/identity --os-username admin --os-project-name admin --os-password $admin_admin_pass --purge-project alt_demo --verbose
#openstack project set --enable alt_demo



########################
### Final assertion
########################
if [[ $(nova list --all-tenants --minimal | wc -l) -ne 4 ]]; then
    echo "Not all VMs were cleaned up"
    exit 1
fi

if [[ $(neutron port-list | wc -l) -ne 1 ]]; then  # This also checks FIP
    echo "Not all ports were cleaned up"
    exit 1
fi

if [[ ${GATE_RUN} == 1 ]]; then
    # The Cinder backup service is enabled in the Gate.
    if [[ $(openstack volume backup list --all-projects | wc -l) -ne 1 ]]; then
        echo "Not all volume backups were cleaned up"
        exit 1
    fi
else
    if [[ $(openstack volume list --all-projects | wc -l) -ne 1 ]]; then
        echo "Not all volumes were cleaned up"
        exit 1
    fi
fi
