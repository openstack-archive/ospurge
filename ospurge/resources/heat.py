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

from heatclient import client as heat_client

from ospurge import base


class HeatStacks(base.Resources):

    def __init__(self, session):
        self.client = heat_client.Client(
            "1",
            endpoint=session.get_endpoint("orchestration"),
            token=session.token, insecure=session.insecure)
        self.project_id = session.project_id

    def list(self):
        return self.client.stacks.list()

    def delete(self, stack):
        super(HeatStacks, self).delete(stack)
        if stack.stack_status == "DELETE_FAILED":
            self.client.stacks.abandon(stack.id)
        else:
            self.client.stacks.delete(stack.id)

    def resource_str(self, stack):
        return "stack {})".format(stack.id)
