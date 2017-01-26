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

# This script populates the project set in the environment variable
# OS_PROJECT_NAME with various resources. The purpose is to test
# ospurge.

# Be strict
set -ueo pipefail

function exit_on_failure {
    RET_CODE=$?
    ERR_MSG=$1
    if [ ${RET_CODE} -ne 0 ]; then
        echo $ERR_MSG
        exit 1
    fi
}

function exit_if_empty {
    STRING=${1:-}
    ERR_MSG=${2:-}
    if [ -z "$STRING" ]; then
        echo $ERR_MSG
        exit 1
    fi
}

function cleanup {
    if [[ -f "${UUID}.raw" ]]; then
        rm "${UUID}.raw"
    fi

}
# Check if needed environment variable OS_PROJECT_NAME is set and non-empty.
: "${OS_PROJECT_NAME:?Need to set OS_PROJECT_NAME non-empty}"

# Some random UUID + Unicode characters
UUID="♫$(cat /proc/sys/kernel/random/uuid)✓"
# Name of external network
EXTNET_NAME=${EXTNET_NAME:-public}
# Name of flavor used to spawn a VM
FLAVOR=${FLAVOR:-m1.nano}
# Image used for the VM
VMIMG_NAME=${VMIMG_NAME:-cirros-0.3.4-x86_64-uec}



################################
### Check resources exist
### Do that early to fail early
################################
# Retrieve external network ID
EXTNET_ID=$(openstack network show $EXTNET_NAME  | awk '/ id /{print $4}')
exit_if_empty "$EXTNET_ID" "Unable to retrieve ID of external network $EXTNET_NAME"

exit_if_empty "$(openstack flavor list | grep ${FLAVOR})" "Flavor $FLAVOR is unknown to Nova"

# Look for the $VMIMG_NAME image and get its ID
IMAGE_ID=$(openstack image list | awk "/ $VMIMG_NAME /{print \$2}")
exit_if_empty "$IMAGE_ID" "Image $VMIMG_NAME could not be found"

# Create a file that will be used to populate Glance and Swift
dd if="/dev/zero" of="${UUID}.raw" bs=1M count=5
trap cleanup SIGHUP SIGINT SIGTERM EXIT



###############################
### Cinder
###############################
# Create a volume
VOL_ID=$(openstack volume create --size 1 ${UUID} | awk '/ id /{print $4}')
exit_on_failure "Unable to create volume"
exit_if_empty "$VOL_ID" "Unable to retrieve ID of volume ${UUID}"

# Snapshot the volume (note that it has to be detached, unless using --force)
openstack volume snapshot create --volume $VOL_ID ${UUID}
exit_on_failure "Unable to snapshot volume ${UUID}"

# Backup volume
# Don't exit on failure as Cinder Backup is not available on all clouds
openstack volume backup create --name ${UUID} $VOL_ID || true



###############################
### Neutron
###############################
# Create a private network and check it exists
NET_ID=$(neutron net-create ${UUID} | awk '/ id /{print $4}')
exit_on_failure "Creation of network ${UUID} failed"
echo "Network ${UUID} created, id $NET_ID"
exit_if_empty "$NET_ID" "Unable to retrieve ID of network ${UUID}"

# Add network's subnet
SUBNET_ID=$(neutron subnet-create --name ${UUID} $NET_ID 192.168.0.0/24 | awk '/ id /{print $4}')
exit_on_failure "Unable to create subnet ${UUID} for network $NET_ID"
exit_if_empty "$SUBNET_ID" "Unable to retrieve ID of subnet ${UUID}"

# Create an unused port
neutron port-create $NET_ID

# Create a router
ROUT_ID=$(neutron router-create ${UUID} | awk '/ id /{print $4}')
exit_on_failure "Unable to create router ${UUID}"
exit_if_empty "$ROUT_ID" "Unable to retrieve ID of router ${UUID}"

# Set router's gateway
openstack router set --external-gateway $EXTNET_ID $ROUT_ID
exit_on_failure "Unable to set gateway to router ${UUID}"

# Connect router on internal network
openstack router add subnet $ROUT_ID $SUBNET_ID
exit_on_failure "Unable to add interface on subnet ${UUID} to router ${UUID}"

# Create a floating IP and retrieve its IP Address
FIP_ADD=$(openstack floating ip create $EXTNET_NAME | awk '/ floating_ip_address /{print $4}')
exit_if_empty "$FIP_ADD" "Unable to create or retrieve floating IP"

# Create a security group
SECGRP_ID=$(neutron security-group-create ${UUID} | awk '/ id /{print $4}')
exit_on_failure "Unable to create security group ${UUID}"
exit_if_empty "$SECGRP_ID" "Unable to retrieve ID of security group ${UUID}"

# Add a rule to previously created security group
neutron security-group-rule-create --direction ingress --protocol TCP \
--port-range-min 22 --port-range-max 22 --remote-ip-prefix 0.0.0.0/0 $SECGRP_ID



###############################
### Nova
###############################
# Launch a VM
VM_ID=$(openstack server create --flavor $FLAVOR --image $IMAGE_ID --nic net-id=$NET_ID ${UUID} | awk '/ id /{print $4}')
exit_on_failure "Unable to boot VM ${UUID}"
exit_if_empty "$VM_ID" "Unable to retrieve ID of VM ${UUID}"



###############################
### Glance
###############################
# Upload glance image
openstack image create --disk-format raw --container-format bare --file ${UUID}.raw ${UUID}
exit_on_failure "Unable to create Glance iamge ${UUID}"



###############################
### Swift
###############################
# Don't exit on failure as Swift is not available on all clouds
swift upload ${UUID} ${UUID}.raw || true



###############################
### Link resources
###############################
# Wait for volume to be available
VOL_STATUS=$(openstack volume show $VOL_ID | awk '/ status /{print $4}')
while [ $VOL_STATUS != "available" ]; do
    echo "Status of volume ${UUID} is $VOL_STATUS. Waiting 3 sec"
    sleep 3
    VOL_STATUS=$(openstack volume show $VOL_ID | awk '/ status /{print $4}')
done

# Wait for VM to be active
VM_STATUS=$(nova show --minimal $VM_ID | awk '/ status /{print $4}')
while [ $VM_STATUS != "ACTIVE" ]; do
    echo "Status of VM ${UUID} is $VM_STATUS. Waiting 3 sec"
    sleep 3
    VM_STATUS=$(nova show --minimal $VM_ID | awk '/ status /{print $4}')
done

# Attach volume
# This must be done before instance snapshot otherwise we could run into
# ERROR (Conflict): Cannot 'attach_volume' while instance is in task_state
# image_pending_upload
openstack server add volume $VM_ID $VOL_ID
exit_on_failure "Unable to attach volume $VOL_ID to VM $VM_ID"

# Associate floating IP
# It as far away from the network creation as possible, because associating
# a FIP requires the network to be 'UP' (which could take several secs)
# See https://github.com/openstack/nova/blob/1a30fda13ae78f4e40b848cacbf6278a359a91cb/nova/api/openstack/compute/floating_ips.py#L229
openstack server add floating ip $VM_ID $FIP_ADD
exit_on_failure "Unable to associate floating IP $FIP_ADD to VM ${UUID}"
