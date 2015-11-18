#!/usr/bin/env bash

# This script populates the project set in the environment variable
# OS_TENANT_NAME with various resources. The purpose is to test
# ospurge.

# Be strict
set -xue
set -o pipefail

# Check if needed environment variable OS_TENANT_NAME is set.
: "${OS_TENANT_NAME:?Need to set OS_TENANT_NAME non-empty}"

TOP_DIR=$(cd $(dirname "$0") && pwd)
source $TOP_DIR/utils.bash

UUID=$(cat /proc/sys/kernel/random/uuid)

# Name of external network
EXTNET_NAME=${EXTNET_NAME:-public}
# Name of flavor used to spawn a VM
FLAVOR=${FLAVOR:-m1.small}
# Image used for the VM
VMIMG_NAME=${VMIMG_NAME:-cirros-0.3.4-x86_64-uec}


################################
### Check resources exist
### Do that early to fail early
################################
# Retrieving external network ID
EXTNET_ID=$(neutron net-show $EXTNET_NAME | awk '/ id /{print $4}')
exit_if_empty "$EXTNET_ID" "Unable to retrieve ID of external network $EXTNET_NAME"

exit_if_empty "$(nova flavor-list | grep $FLAVOR)" "Flavor $FLAVOR is unknown to Nova"

# Looking for the $VMIMG_NAME image and getting its ID
IMAGE_ID=$(nova image-list | awk "/ $VMIMG_NAME /{print \$2}")
exit_if_empty "$IMAGE_ID" "Image $VMIMG_NAME could not be found"


KEY_NAME="ospurge_test_key_$UUID"
NET_NAME="ospurge_test_net_$UUID"
SUBNET_NAME="ospurge_test_subnet_$UUID"
ROUT_NAME="ospurge_test_rout_$UUID"
VM_NAME="ospurge_test_vm_$UUID"
VMSNAP_NAME="ospurge_test_vmsnap_$UUID"
VOL_NAME="ospurge_test_vol_$UUID"
VOLSNAP_NAME="ospurge_test_volsnap_$UUID"
VOLBACK_NAME="ospurge_test_volback_$UUID"
IMG_NAME="ospurge_test_image_$UUID"
SECGRP_NAME="ospurge_test_secgroup_$UUID"
CONT_NAME="ospurge_test_container_$UUID"
FLAV_NAME="ospurge_test_flavor_$UUID"
STACK_NAME="ospurge_test_stack_$UUID"
ALARM_NAME="ospurge_test_alarm_$UUID"

# Create a file that will be used to populate Glance and Swift
dd if="/dev/zero" of="zero_disk.raw" bs=1M count=5


###############################
### Swift
###############################
swift upload $CONT_NAME zero_disk.raw
exit_on_failure "Unable to upload file in container $CONT_NAME"


###############################
### Cinder
###############################
# Create a volume
cinder create --display-name $VOL_NAME 5
exit_on_failure "Unable to create volume"

# Getting ID of volume
VOL_ID=$(cinder show $VOL_NAME | awk '/ id /{print $4}')
exit_if_empty "$VOL_ID" "Unable to retrieve ID of volume $VOL_NAME"

# Snapshotting volume (note that it has to be detached, unless using --force)
cinder snapshot-create --display-name $VOLSNAP_NAME $VOL_ID
exit_on_failure "Unable to snapshot volume $VOL_NAME"

# Backuping volume
# Don't exit if this fails - as we may test platforms that don't
# provide this feature
if ! cinder backup-create --display-name $VOLBACK_NAME $VOL_ID; then
    :
fi


###############################
### Neutron
###############################
# Create a private network and check it exists
neutron net-create $NET_NAME
exit_on_failure "Creation of network $NET_NAME failed"

# Getting ID of private network
NET_ID=$(neutron net-show $NET_NAME | awk '/ id /{print $4}')
exit_if_empty "$NET_ID" "Unable to retrieve ID of network $NET_NAME"

# Add network's subnet
neutron subnet-create --name $SUBNET_NAME $NET_ID 192.168.0.0/24
exit_on_failure "Unable to create subnet $SUBNET_NAME for network $NET_ID"

# Create an unused port
neutron port-create $NET_ID

# retrieving subnet ID
SUBNET_ID=$(neutron subnet-show $SUBNET_NAME | awk '/ id /{print $4}')
exit_if_empty "$SUBNET_ID" "Unable to retrieve ID of subnet $SUBNET_NAME"

# Creating a router
neutron router-create $ROUT_NAME
exit_on_failure "Unable to create router $ROUT_NAME"

# Retrieving router ID
ROUT_ID=$(neutron router-show $ROUT_NAME | awk '/ id /{print $4}')
exit_if_empty "$ROUT_ID" "Unable to retrieve ID of router $ROUT_NAME"

# Setting router's gateway
neutron router-gateway-set $ROUT_ID $EXTNET_ID
exit_on_failure "Unable to set gateway to router $ROUT_NAME"

# Plugging router on internal network
neutron router-interface-add $ROUT_ID $SUBNET_ID
exit_on_failure "Unable to add interface on subnet $SUBNET_NAME to router $ROUT_NAME"

# Creating a floating IP and retrieving its IP Address

FIP_ADD=$(neutron floatingip-create $EXTNET_NAME | awk '/ floating_ip_address /{print $4}')
exit_if_empty "$FIP_ADD" "Unable to create or retrieve floating IP"

# Creating a security group
neutron security-group-create $SECGRP_NAME
exit_on_failure "Unable to create security group $SECGRP_NAME"

# Getting security group ID
SECGRP_ID=$(neutron security-group-show $SECGRP_NAME | awk '/ id /{print $4}')
exit_if_empty "$SECGRP_ID" "Unable to retrieve ID of security group $SECGRP_NAME"

# Adding a rule to previously created security group

neutron security-group-rule-create --direction ingress --protocol TCP \
--port-range-min 22 --port-range-max 22 --remote-ip-prefix 0.0.0.0/0 \
$SECGRP_ID


###############################
### Nova
###############################
# Launch a VM
nova boot --flavor $FLAVOR --image $IMAGE_ID --nic net-id=$NET_ID $VM_NAME
exit_on_failure "Unable to boot VM $VM_NAME"

# Getting ID of VM
VM_ID=$(nova show $VM_NAME | awk '/ id /{print $4}')
exit_if_empty "$VM_ID" "Unable to retrieve ID of VM $VM_NAME"


###############################
### Glance
###############################
# Upload glance image
glance image-create --name $IMG_NAME --disk-format raw \
--container-format bare --file zero_disk.raw
exit_on_failure "Unable to create Glance iamge $IMG_NAME"


###############################
### Heat
###############################
echo 'heat_template_version: 2013-05-23
description: >
    Hello world HOT template' > dummy_stack.yaml
# Don't exit if this fails - as we may test platforms that don't
# provide this feature
if ! heat stack-create -f dummy_stack.yaml $STACK_NAME; then
    :
fi


# Wait for VM to be spawned before snapshotting the VM
VM_STATUS=$(nova show $VM_ID | awk '/ status /{print $4}')
while [ $VM_STATUS != "ACTIVE" ]; do
    echo "Status of VM $VM_NAME is $VM_STATUS. Waiting 1 sec"
    sleep 1
    VM_STATUS=$(nova show $VM_ID | awk '/ status /{print $4}')
done

### Link resources

# Associate floating IP
nova floating-ip-associate $VM_ID $FIP_ADD
exit_on_failure "Unable to associate floating IP $FIP_ADD to VM $VM_NAME"

# Wait for volume to be available
VOL_STATUS=$(cinder show $VOL_ID | awk '/ status /{print $4}')
while [ $VOL_STATUS != "available" ]; do
    echo "Status of volume $VOL_NAME is $VOL_STATUS. Waiting 1 sec"
    sleep 1
    VOL_STATUS=$(cinder show $VOL_ID | awk '/ status /{print $4}')
done

# Attach volume
# This must be done before instance snapshot otherwise we could run into
# ERROR (Conflict): Cannot 'attach_volume' while instance is in task_state
# image_pending_upload
nova volume-attach $VM_ID $VOL_ID
exit_on_failure "Unable to attach volume $VOL_ID to VM $VM_ID"

# Create an image
nova image-create $VM_ID $VMSNAP_NAME
exit_on_failure "Unable to create VM Snapshot of $VM_NAME"

# Create a ceilometer alarm
ceilometer alarm-create --name $ALARM_NAME --meter-name cpu_util --threshold 70.0
exit_on_failure "Unable to create ceilometer alarm $ALARM_NAME"
