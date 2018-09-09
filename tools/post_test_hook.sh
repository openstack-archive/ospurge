#!/usr/bin/env bash

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

set -x

export OSPURGE_DIR="$BASE/new/ospurge"

cd $OSPURGE_DIR
sudo chown -R stack:stack $OSPURGE_DIR

CLOUDS_YAML=/etc/openstack/clouds.yaml

if [ ! -e ${CLOUDS_YAML} ]; then
    # stable/liberty had clouds.yaml in the home/base directory
    sudo mkdir -p /etc/openstack
    sudo cp $BASE/new/.config/openstack/clouds.yaml ${CLOUDS_YAML}
    sudo chown -R stack:stack /etc/openstack
fi


echo "Running OSpurge functional test suite"
set +e
sudo -E -H -u stack tox -e functional
EXIT_CODE=$?
set -e

exit $EXIT_CODE

