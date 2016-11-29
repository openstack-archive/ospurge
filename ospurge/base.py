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

from keystoneauth1 import exceptions as api_exceptions
from keystoneauth1.identity import generic as keystone_auth
from keystoneauth1 import session as keystone_session
from keystoneclient import client as keystone_client
from keystoneclient import exceptions as keystone_exceptions

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
                            " exist : %s", e
                        )
                        # No need to retry deleting an non existing resource
                        break
                    else:
                        if n == constants.RETRIES:
                            raise exceptions.DeletionFailed(service_name)
                        n += 1
                        logging.info("* Deletion failed - "
                                     "Retrying in %s seconds - "
                                     "Retry count %s", constants.TIMEOUT, n)
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
                 endpoint_type="publicURL", insecure=False, **kwargs):

        data = {
            'username': username,
            'password': password,
            'project_id': project_id,
            'user_domain_id': kwargs.get('user_domain_id'),
            'user_domain_name': kwargs.get('user_domain_name'),
            'project_domain_id': kwargs.get('project_domain_id'),
            'project_domain_name': kwargs.get('project_domain_name'),
            'domain_id': kwargs.get('domain_id')
        }

        auth = keystone_auth.Password(auth_url, **data)
        session = keystone_session.Session(auth=auth, verify=(not insecure))
        self.client = keystone_client.Client(session=session)

        # Storing username, password, project_id and auth_url for
        # use by clients libraries that cannot use an existing token.
        self.username = username
        self.password = password
        self.project_id = auth.auth_ref.project_id
        self.auth_url = auth_url
        self.region_name = kwargs['region_name']
        self.insecure = insecure
        # Session variables to be used by clients when possible
        self.token = auth.auth_ref.auth_token
        self.user_id = auth.auth_ref.user_id
        self.project_name = self.client.project_name
        self.keystone_session = session
        self.endpoint_type = endpoint_type
        self.catalog = auth.auth_ref.service_catalog.get_endpoints()

        try:
            # Detect if we are admin or not
            self.client.roles.list()  # Only admins are allowed to do this
        except (
            # The Exception Depends on OpenStack Infrastructure.
            api_exceptions.Forbidden,
            keystone_exceptions.ConnectionRefused,  # admin URL not permitted
            api_exceptions.Unauthorized,
        ):
            self.is_admin = False
        else:
            self.is_admin = True

    def get_endpoint(self, service_type):
        try:
            if self.client.version == "v2.0":
                return self.catalog[service_type][0][self.endpoint_type]
            else:
                return self.catalog[service_type][0]['url']
        except (KeyError, IndexError):
            # Endpoint could not be found
            raise exceptions.EndpointNotFound(service_type)


class Resources(object):

    """Abstract base class for all resources to be removed."""

    def __init__(self, session):
        self.session = session

    def list(self):
        pass

    def delete(self, resource):
        """Displays informational message about a resource deletion."""
        logging.info("* Deleting %s." % self.resource_str(resource))

    def purge(self):
        """Delete all resources."""
        # Purging is displayed and done only if self.list succeeds
        resources = self.list()
        c_name = self.__class__.__name__
        logging.info("* Purging %s", c_name)
        for resource in resources:
            retry(c_name)(self.delete)(resource)

    def dump(self):
        """Display all available resources."""
        # Resources type and resources are displayed only if self.list succeeds
        resources = self.list()
        c_name = self.__class__.__name__
        print("* Resources type: %s" % c_name)
        for resource in resources:
            print(self.resource_str(resource))
        print("")
