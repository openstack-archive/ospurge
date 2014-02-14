ospurge: OpenStack project resources cleaner
============================================

`ospurge` is a client side script allowing an OpenStack administrator
to cleanup any project, by deleting all of its resources prior to
deleting the project itself.

Usage
-----

Available options can be displayed by using `os_purge.py -h`:

    ::::bash
    $ os_purge -h
    usage: os_purge [-h] [--verbose] [--dry_run] [--endpoint_type ENDPOINT_TYPE]
		    --username USERNAME --password PASSWORD --admin_project
		    ADMIN_PROJECT --auth_url AUTH_URL --cleanup_project
		    CLEANUP_PROJECT

    Purge resources from an Openstack project.

    optional arguments:
      -h, --help            show this help message and exit
      --verbose             Makes output verbose
      --dry_run             List project's resources
      --endpoint_type ENDPOINT_TYPE
			    Endpoint type to use. Defaults to
			    env[OS_ENDPOINT_TYPE] or publicURL
      --username USERNAME   A user name with access to the project being purged.
			    Defaults to env[OS_USERNAME]
      --password PASSWORD   The user's password. Defaults to env[OS_PASSWORD].
      --admin_project ADMIN_PROJECT
			    Name of a project the user is admin on. Defaults to
			    env[OS_TENANT_NAME].
      --auth_url AUTH_URL   Authentication URL. Defaults to env[OS_AUTH_URL].
      --cleanup_project CLEANUP_PROJECT
			    Name of project to purge

Example
-------

To remove a project, administrator credentials have to be
provided. The usual OpenStack environment variables can be used. When
launching the `os_purge.py` script, the project to be cleaned up has
to be provided, by using the `--cleanup_project` option. When the
command returns, any resources associated to the project will have
been definitively deleted.

    ::::bash
    $ export OS_USERNAME=admin
    $ export OS_PASSWORD=password
    $ export OS_TENANT_NAME=admin
    $ export OS_AUTH_URL=http://localhost:5000/v2.0
    $ os_purge.py --cleanup_project demo
    $


Deleted resources
-----------------

The following resources will be removed:

* ceilometer alarms
* floating IPs
* images / snapshots
* instances
* networks
* routers
* security groups
* swift containers
* swift objects
* volumes / snapshots


Error codes
-----------

The following error codes are returned when `os_purge` encounters
an error:

* Code 2: Project doesn't exist
* Code 3: Authentication failed (e.g. Bad username or password)
* Code 4: Resource deletion failed
* Code 5: Connection error while deleting a resource (e.g. Service not available)
* Code 6: Connection to endpoint failed (e.g. authentication url)
* Code 1: Unknown error
* Code 0: Process exited sucessfully


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
