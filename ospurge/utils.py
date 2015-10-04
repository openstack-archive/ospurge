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

import logging

from keystoneclient.apiclient import exceptions as api_exceptions
import keystoneclient.openstack.common.apiclient.exceptions
from keystoneclient.v2_0 import client as keystone_client

from ospurge import exceptions


class KeystoneManager(object):

    """Manages Keystone queries."""

    def __init__(self, username, password, project, auth_url, insecure, **kwargs):
        try:
            self.client = keystone_client.Client(
                username=username, password=password,
                tenant_name=project, auth_url=auth_url,
                insecure=insecure, **kwargs)
        except api_exceptions.Unauthorized as exc:
            raise exceptions.Unauthorized()
        
        self.admin_role_id = None
        self.tenant_info = None

    def get_project_id(self, project_name_or_id=None):
        """Get a project by its id

        Returns:
        * ID of current project if called without parameter,
        * ID of project given as parameter if one is given.
        """

        if project_name_or_id is None:
            return self.client.tenant_id

        try:
            self.tenant_info = self.client.tenants.get(project_name_or_id)
            # If it doesn't raise an 404, project_name_or_id is
            # already the project's id
            project_id = project_name_or_id
        except api_exceptions.NotFound:
            try:
                # Can raise api_exceptions.Forbidden:
                tenants = self.client.tenants.list()
                project_id = filter(
                    lambda x: x.name == project_name_or_id, tenants)[0].id
            except IndexError:
                raise exceptions.NoSuchProject(project_name_or_id)

        if not self.tenant_info:
            self.tenant_info = self.client.tenants.get(project_id)
        return project_id

    def enable_project(self, project_id):
        logging.info("* Enabling project {}.".format(project_id))
        self.tenant_info = self.client.tenants.update(project_id, enabled=True)

    def disable_project(self, project_id):
        logging.info("* Disabling project {}.".format(project_id))
        self.tenant_info = self.client.tenants.update(project_id, enabled=False)

    def get_admin_role_id(self):
        if not self.admin_role_id:
            roles = self.client.roles.list()
            self.admin_role_id = filter(lambda x: x.name == "admin", roles)[0].id
        return self.admin_role_id

    def become_project_admin(self, project_id):
        user_id = self.client.user_id
        admin_role_id = self.get_admin_role_id()
        logging.info("* Granting role admin to user {} on project {}.".format(
            user_id, project_id))

        result = True
        try:
            self.client.roles.add_user_role(user_id, admin_role_id, project_id)
        except api_exceptions.Conflict:
            result = False

        return result

    def undo_become_project_admin(self, project_id):
        user_id = self.client.user_id
        admin_role_id = self.get_admin_role_id()
        logging.info("* Removing role admin to user {} on project {}.".format(
            user_id, project_id))

        return self.client.roles.remove_user_role(user_id, admin_role_id, project_id)

    def delete_project(self, project_id):
        logging.info("* Deleting project {}.".format(project_id))
        self.client.tenants.delete(project_id)
