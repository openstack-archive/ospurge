ospurge: OpenStack project resources cleaner
============================================

`ospurge` is a standalone, client-side, Python script that aims at
deleting all resources (taking into account their interdependencies)
in a specified OpenStack project. OSPurge ensures in a quick and
automated way that no resource is left behind when a project is
deleted.

`ospurge` can be used by a cloud administrator (with the admin role)
to cleanup any project or by a non-privileged user to cleanup his own
project.

Installation
------------

Create a Python virtual environment (requires package virtualenvwrapper):

    $ mkvirtualenv ospurge

Install `ospurge`:

    $ pip install ospurge

The script is installed and can be launched:

    $ ospurge -h


Usage
-----

Available options can be displayed by using `ospurge -h`:

    $ ospurge -h
    usage: ospurge [-h] [--verbose] [--dry-run] [--dont-delete-project]
                   [--region-name REGION_NAME] [--endpoint-type ENDPOINT_TYPE]
                   --username USERNAME --password PASSWORD --admin-project
                   ADMIN_PROJECT --auth-url AUTH_URL
                   [--cleanup-project CLEANUP_PROJECT] [--own-project]
                   [--insecure]

    Purge resources from an Openstack project.

    optional arguments:
      -h, --help            show this help message and exit
      --verbose             Makes output verbose
      --dry-run             List project's resources
      --dont-delete-project
                            Executes cleanup script without removing the project.
                            Warning: all project resources will still be deleted.
      --region-name REGION_NAME
                            Region to use. Defaults to env[OS_REGION_NAME] or None
      --endpoint-type ENDPOINT_TYPE
                            Endpoint type to use. Defaults to
                            env[OS_ENDPOINT_TYPE] or publicURL
      --username USERNAME   If --own-project is set : a user name with access to
                            the project being purged. If --cleanup-project is set
                            : a user name with admin role in project specified in
                            --admin-project. Defaults to env[OS_USERNAME]
      --password PASSWORD   The user's password. Defaults to env[OS_PASSWORD].
      --admin-project ADMIN_PROJECT
                            Project name used for authentication. This project
                            will be purged if --own-project is set. Defaults to
                            env[OS_TENANT_NAME].
      --auth-url AUTH_URL   Authentication URL. Defaults to env[OS_AUTH_URL].
      --cleanup-project CLEANUP_PROJECT
                            ID or Name of project to purge. Not required if --own-
                            project has been set. Using --cleanup-project requires
                            to authenticate with admin credentials.
      --own-project         Delete resources of the project used to authenticate.
                            Useful if you don't have the admin credentials of the
                            platform.
      --insecure            Explicitly allow all OpenStack clients to perform
                            insecure SSL (https) requests. The server's
                            certificate will not be verified against any
                            certificate authorities. This option should be used
                            with caution.



Error codes
-----------

The following error codes are returned when `ospurge` encounters
an error:

* Code 2: Project doesn't exist
* Code 3: Authentication failed (e.g. Bad username or password)
* Code 4: Resource deletion failed
* Code 5: Connection error while deleting a resource (e.g. Service not available)
* Code 6: Connection to endpoint failed (e.g. authentication url)
* Code 1: Unknown error
* Code 0: Process exited sucessfully


Example
-------

To remove a project, credentials have to be
provided. The usual OpenStack environment variables can be used. When
launching the `ospurge` script, the project to be cleaned up has
to be provided, by using either the `--cleanup-project` option or the
`--own-project` option. When the command returns, any resources associated
to the project will have been definitively deleted.

Setting OpenStack credentials:

    $ export OS_USERNAME=admin
    $ export OS_PASSWORD=password
    $ export OS_TENANT_NAME=admin
    $ export OS_AUTH_URL=http://localhost:5000/v2.0

Checking resources of the target project:

    $ ./ospurge --dry-run --cleanup-project florent-demo
    * Resources type: CinderSnapshots

    * Resources type: NovaServers
    server vm0 (id 8b0896d9-bcf3-4360-824a-a81865ad2385)

    * Resources type: NeutronFloatingIps

    * Resources type: NeutronInterfaces

    * Resources type: NeutronRouters

    * Resources type: NeutronNetworks

    * Resources type: NeutronSecgroups
    security group custom (id 8c13e635-6fdc-4332-ba19-c22a7a85c7cc)

    * Resources type: GlanceImages

    * Resources type: SwiftObjects

    * Resources type: SwiftContainers

    * Resources type: CinderVolumes
    volume vol0 (id ce1380ef-2d66-47a2-9dbf-8dd5d9cd506d)

    * Resources type: CeilometerAlarms

Removing resources without deleting the project:

    $ ./ospurge --verbose --dont-delete-project --cleanup-project florent-demo
    INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): keystone.usr.lab0.aub.cw-labs.net
    INFO:root:* Granting role admin to user e7f562a29da3492baba2cc7c5a1f2d84 on project florent-demo.
    INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): keystone-admin.usr.lab0.aub.cw-labs.net
    INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): keystone-admin.usr.lab0.aub.cw-labs.net
    INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): keystone-admin.usr.lab0.aub.cw-labs.net
    INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): keystone.usr.lab0.aub.cw-labs.net
    INFO:root:* Purging CinderSnapshots
    INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): keystone.usr.lab0.aub.cw-labs.net
    INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): cinder.usr.lab0.aub.cw-labs.net
    INFO:root:* Purging NovaServers
    INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): keystone.usr.lab0.aub.cw-labs.net
    INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): nova.usr.lab0.aub.cw-labs.net
    INFO:root:* Deleting server vm0 (id 8b0896d9-bcf3-4360-824a-a81865ad2385).
    INFO:root:* Purging NeutronFloatingIps
    INFO:root:* Purging NeutronInterfaces
    INFO:root:* Purging NeutronRouters
    INFO:root:* Purging NeutronNetworks
    INFO:root:* Purging NeutronSecgroups
    INFO:root:* Deleting security group custom (id 8c13e635-6fdc-4332-ba19-c22a7a85c7cc).
    INFO:root:* Purging GlanceImages
    INFO:root:* Purging SwiftObjects
    INFO:root:* Purging SwiftContainers
    INFO:root:* Purging CinderVolumes
    INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): keystone.usr.lab0.aub.cw-labs.net
    INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): cinder.usr.lab0.aub.cw-labs.net
    INFO:root:* Deleting volume vol0 (id ce1380ef-2d66-47a2-9dbf-8dd5d9cd506d).
    INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): cinder.usr.lab0.aub.cw-labs.net
    INFO:root:* Purging CeilometerAlarms

Checking that resources have been correctly removed:

    $ ./ospurge --dry-run --cleanup-project florent-demo
    * Resources type: CinderSnapshots

    * Resources type: NovaServers

    * Resources type: NeutronFloatingIps

    * Resources type: NeutronInterfaces

    * Resources type: NeutronRouters

    * Resources type: NeutronNetworks

    * Resources type: NeutronSecgroups

    * Resources type: GlanceImages

    * Resources type: SwiftObjects

    * Resources type: SwiftContainers

    * Resources type: CinderVolumes

    * Resources type: CeilometerAlarms

Removing project:

    $ ./ospurge --cleanup-project florent-demo
    $ ./ospurge --cleanup-project florent-demo
    Project florent-demo doesn't exist


Deleted resources
-----------------

The following resources will be removed:

* ceilometer alarms
* flavors
* floating IPs
* images / snapshots
* instances
* networks
* routers
* security groups
* swift containers
* swift objects
* volumes / snapshots


Notes
-----

Users can be deleted by using the `python-keystoneclient` CLI:

    $ keystone user-delete <username_or_userid>


How to contribute
-----------------

Ospurge is hosted on Stackforge and is using Gerrit to manage
contributions. You can contribute to the project by following the
following workflow: https://wiki.openstack.org/wiki/Gerrit_Workflow


License / Copyright
-------------------

This software is released under the MIT License.

Copyright (c) 2014 Cloudwatt

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
