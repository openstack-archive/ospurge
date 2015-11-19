OpenStack project resources cleaner
===================================

* ``ospurge`` is a standalone, client-side, operators tool that aims at
  deleting all resources, taking into account their interdependencies,
  in a specified OpenStack project.

* ``ospurge`` ensures in a quick and automated way that no resource is
  left behind when a project is deleted.

* ``ospurge`` can be used by a cloud administrator, this means a user with the
  admin role, to cleanup any project or by a non-privileged user to cleanup his
  own project.


Supported resources
-------------------

At the moment it is possible to purge the following resources from a project:

* Ceilometer alarms
* floating IP addresses
* images / snapshots
* instances
* networks
* routers
* security groups
* Swift containers
* Swift objects
* volumes / snapshots


Error codes
-----------

The following error codes are returned when ``ospurge`` encounters
an error:

* ``Code 0``: Process exited sucessfully
* ``Code 1``: Unknown error
* ``Code 2``: Project doesn't exist
* ``Code 3``: Authentication failed (e.g. bad username or password)
* ``Code 4``: Resource deletion failed
* ``Code 5``: Connection error while deleting a resource (e.g. service not
  available)
* ``Code 6``: Connection to endpoint failed (e.g. wrong authentication URL)


Installation
------------

Create a Python virtual environment (requires the
`virtualenvwrapper <https://virtualenvwrapper.readthedocs.org/>`_):

.. code-block:: console

    $ mkvirtualenv ospurge

Install ``ospurge`` with ``pip``:

.. code-block:: console

    $ pip install ospurge

Available options can be displayed by using ``ospurge -h``:

.. code-block:: console

    $ ospurge -h
    usage: ospurge [-h] [--verbose] [--dry-run] [--dont-delete-project]
                   [--region-name REGION_NAME] [--endpoint-type ENDPOINT_TYPE]
                   --username USERNAME --password PASSWORD --admin-project
                   ADMIN_PROJECT [--admin-role-name ADMIN_ROLE_NAME] --auth-url
                   AUTH_URL [--cleanup-project CLEANUP_PROJECT] [--own-project]
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
      --admin-role-name ADMIN_ROLE_NAME
                                Name of admin role. Defaults to 'admin'.
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


Example usage
-------------

To remove a project, credentials have to be
provided. The usual OpenStack environment variables can be used. When
launching the ``ospurge`` script, the project to be cleaned up has
to be provided, by using either the ``--cleanup-project`` option or the
``--own-project`` option. When the command returns, any resources associated
to the project will have been definitively deleted.

* Setting OpenStack credentials:

.. code-block:: console

    $ export OS_USERNAME=admin
    $ export OS_PASSWORD=password
    $ export OS_TENANT_NAME=admin
    $ export OS_AUTH_URL=http://localhost:5000/v2.0

* Checking resources of the target project:

.. code-block:: console

    $ ./ospurge --dry-run --cleanup-project demo
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

* Removing resources without deleting the project:

.. code-block:: console

    $ ./ospurge --verbose --dont-delete-project --cleanup-project demo
    INFO:requests.packages.urllib3.connectionpool:Starting new HTTP connection (1): keystone.usr.lab0.aub.cw-labs.net
    INFO:root:* Granting role admin to user e7f562a29da3492baba2cc7c5a1f2d84 on project demo.
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

* Checking that resources have been correctly removed:

.. code-block:: console

    $ ./ospurge --dry-run --cleanup-project demo
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

* Removing project:

.. code-block:: console

    $ ./ospurge --cleanup-project demo
    $ ./ospurge --cleanup-project demo
    Project demo doesn't exist

* Users can be deleted by using the ``python-keystoneclient`` command-line
  interface:

.. code-block:: console

    $ keystone user-delete <username_or_userid>


How to contribute
-----------------

OSpurge is hosted on the OpenStack infrastructure and is using
`Gerrit <https://review.openstack.org>`_ to manage contributions. You can
contribute to the project by following the
`OpenStack Development workflow <http://docs.openstack.org/infra/manual/developers.html#development-workflow>`_.
