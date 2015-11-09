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

import ceilometerclient.exc
from ceilometerclient.v2 import client as ceilometer_client

from ospurge import base
from ospurge import exceptions


class CeilometerAlarms(base.Resources):

    def __init__(self, session):
        # Ceilometer Client needs a method that returns the token
        def get_token():
            return session.token

        try:
            self.client = ceilometer_client.Client(
                auth_url=session.auth_url,
                endpoint=session.get_endpoint("metering"),
                token=get_token, insecure=session.insecure)
        except ceilometerclient.exc.InvalidEndpoint:
            raise exceptions.InvalidEndpoint
        self.project_id = session.project_id

    def list(self):
        query = [{'field': 'project_id',
                  'op': 'eq',
                  'value': self.project_id}]
        return self.client.alarms.list(q=query)

    def delete(self, alarm):
        super(CeilometerAlarms, self).delete(alarm)
        self.client.alarms.delete(alarm.alarm_id)

    def resource_str(self, alarm):
        return "alarm {}".format(alarm.name)
