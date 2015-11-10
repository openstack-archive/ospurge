# This software is released under the MIT License.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Available resources classes

# The order of the Openstack resources in the subsequent list
# corresponds to the order in which ospurge will delete the
# resources. This order takes into account inter-resources
# dependencies, and tries to minimize the overall time duration of the
# purge operation.

RESOURCES_CLASSES = [
    'CinderSnapshots',
    'CinderBackups',
    'NeutronFireWall',
    'NeutronFireWallPolicy',
    'NeutronFireWallRule',
    'NeutronLbMembers',
    'NeutronLbVip',
    'NeutronLbHealthMonitor',
    'NeutronLbPool',
    'NovaServers',
    'NovaKeyPairs',
    'NeutronFloatingIps',
    'NeutronMeteringLabel',
    'NeutronInterfaces',
    'NeutronRouters',
    'NeutronPorts',
    'NeutronNetworks',
    'NeutronSecgroups',
    'GlanceImages',
    'SwiftObjects',
    'SwiftContainers',
    'CinderVolumes',
    'CeilometerAlarms',
    'HeatStacks'
]

# Error codes

NO_SUCH_PROJECT_ERROR_CODE = 2
AUTHENTICATION_FAILED_ERROR_CODE = 3
DELETION_FAILED_ERROR_CODE = 4
CONNECTION_ERROR_CODE = 5
NOT_AUTHORIZED_ERROR_CODE = 6

# Constants

RETRIES = 10  # Retry a delete operation 10 times before exiting
TIMEOUT = 5   # 5 seconds timeout between retries
