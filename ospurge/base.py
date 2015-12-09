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
import time

from keystoneclient.apiclient import exceptions as api_exceptions
from keystoneclient.v2_0 import client as keystone_client

from ospurge import constants
from ospurge import exceptions

# Decorators


def retry(service_name):
    def factory(func):
        """Decorator allowing to retry in case of failure."""
        def wrapper(*args, **kwargs):
            n = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if getattr(e, 'http_status', False) == 404:
                        # Sometimes a resource can be deleted manually by
                        # someone else while ospurge is running and listed it.
                        # If this happens, We raise a Warning.
                        logging.warning(
                            "Can not delete the resource because it does not"
                            " exist : %s" % e
                        )
                        # No need to retry deleting an non existing resource
                        break
                    else:
                        if n == constants.RETRIES:
                            raise exceptions.DeletionFailed(service_name)
                        n += 1
                        logging.info("* Deletion failed - "
                                     "Retrying in {} seconds - "
                                     "Retry count {}".format(constants.TIMEOUT, n))
                        time.sleep(constants.TIMEOUT)
        return wrapper
    return factory


# Classes


class Session(object):

    """A Session stores information that can be used by the different Openstack Clients.

    The most important data is:
    * self.token - The Openstack token to be used accross services;
    * self.catalog - Allowing to retrieve services' endpoints.
    """

    def __init__(self, username, password, project_id, auth_url,
                 endpoint_type="publicURL", region_name=None, insecure=False):
        client = keystone_client.Client(
            username=username, password=password, tenant_id=project_id,
            auth_url=auth_url, region_name=region_name, insecure=insecure)
        # Storing username, password, project_id and auth_url for
        # use by clients libraries that cannot use an existing token.
        self.username = username
        self.password = password
        self.project_id = project_id
        self.auth_url = auth_url
        self.region_name = region_name
        self.insecure = insecure
        # Session variables to be used by clients when possible
        self.token = client.auth_token
        self.user_id = client.user_id
        self.project_name = client.project_name
        self.endpoint_type = endpoint_type
        self.catalog = client.service_catalog.get_endpoints()
        try:
            # Detect if we are admin or not
            client.roles.list()  # Only admins are allowed to do this
        except (
            # The Exception Depends on OpenStack Infrastructure.
            api_exceptions.Forbidden,
            api_exceptions.ConnectionRefused,  # admin URL not permitted
            api_exceptions.Unauthorized,
        ):
            self.is_admin = False
        else:
            self.is_admin = True

    def get_endpoint(self, service_type):
        try:
            return self.catalog[service_type][0][self.endpoint_type]
        except (KeyError, IndexError):
            # Endpoint could not be found
            raise exceptions.EndpointNotFound(service_type)


class Resources(object):

    """Abstract base class for all resources to be removed."""

    def __init__(self, cloud):
        self.cloud = cloud
        self.project_id = cloud.get_session().get_project_id()

    def list(self):
        pass

    def delete(self, resource):
        """Displays informational message about a resource deletion."""
        logging.info("* Deleting {}.".format(self.resource_str(resource)))

    def purge(self):
        """Delete all resources."""
        # Purging is displayed and done only if self.list succeeds
        resources = self.list()
        c_name = self.__class__.__name__
        logging.info("* Purging {}".format(c_name))
        for resource in resources:
            retry(c_name)(self.delete)(resource)

    def dump(self):
        """Display all available resources."""
        # Resources type and resources are displayed only if self.list succeeds
        resources = self.list()
        c_name = self.__class__.__name__
        print("* Resources type: {}".format(c_name))
        for resource in resources:
            print(self.resource_str(resource))
        print("")
