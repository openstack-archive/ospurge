OpenStack project resources cleaner
===================================

What is OSPurge ?
-----------------

* ``ospurge`` is a standalone client-side tool that aims at
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

* Floating IP
* Glance Images
* Instances
* Networks
* Routers
* Security groups
* Swift containers
* Swift objects
* Volumes / Volume snapshots / Volume backups


Exit codes
----------

The following codes are returned when ``ospurge`` exits:

* ``Code 0``: Process exited successfully
* ``Code 1``: Something went wrong (check the logs)


Installation
------------

Create a Python 3 virtual environment:

.. code-block:: console

    $ python3 -m venv ospurge
    $ source ospurge/bin/activate

Install ``ospurge`` with ``pip``:

.. code-block:: console

    $ python3 -m pip install git+https://git.openstack.org/openstack/ospurge
    $ OR, to checkout at commit 328f6
    $ python3 -m pip install git+https://git.openstack.org/openstack/ospurge@328f6

Available options can be displayed with ``ospurge -h``:

.. code-block:: console

    $ ospurge -h
    usage: ospurge [-h] [--verbose] [--dry-run] [--delete-shared-resources]
                   (--purge-project ID_OR_NAME | --purge-own-project)
                   [--os-cloud <name>] [--os-auth-type <name>]
                   [--os-auth-url OS_AUTH_URL] [--os-domain-id OS_DOMAIN_ID]
                   [--os-domain-name OS_DOMAIN_NAME]
                   [--os-project-id OS_PROJECT_ID]
                   [--os-project-name OS_PROJECT_NAME]
                   [--os-project-domain-id OS_PROJECT_DOMAIN_ID]
                   [--os-project-domain-name OS_PROJECT_DOMAIN_NAME]
                   [--os-trust-id OS_TRUST_ID]
                   [--os-default-domain-id OS_DEFAULT_DOMAIN_ID]
                   [--os-default-domain-name OS_DEFAULT_DOMAIN_NAME]
                   [--os-user-id OS_USER_ID] [--os-username OS_USERNAME]
                   [--os-user-domain-id OS_USER_DOMAIN_ID]
                   [--os-user-domain-name OS_USER_DOMAIN_NAME]
                   [--os-password OS_PASSWORD] [--insecure]
                   [--os-cacert <ca-certificate>] [--os-cert <certificate>]
                   [--os-key <key>] [--timeout <seconds>]
                   [--os-service-type <name>] [--os-service-name <name>]
                   [--os-interface <name>] [--os-region-name <name>]
                   [--os-endpoint-override <name>] [--os-api-version <name>]

    Purge resources from an Openstack project.

    optional arguments:
      -h, --help            show this help message and exit
      --verbose             Makes output verbose
      --dry-run             List project's resources
      --delete-shared-resources
                            Whether to delete shared resources (public images and
                            external networks)
      --admin-role-name ADMIN_ROLE_NAME
                            Name of admin role. Defaults to 'admin'. This role
                            will be temporarily granted on the project to purge to
                            the authenticated user.
      --purge-project ID_OR_NAME
                            ID or Name of project to purge. This option requires
                            to authenticate with admin credentials.
      --purge-own-project   Purge resources of the project used to authenticate.
                            Useful if you don't have the admin credentials of the
                            cloud.
      --os-cloud <name>     Named cloud to connect to
      --os-auth-type <name>, --os-auth-plugin <name>
                            Authentication type to use

    Authentication Options:
      Options specific to the password plugin.

      --os-auth-url OS_AUTH_URL
                            Authentication URL
      --os-domain-id OS_DOMAIN_ID
                            Domain ID to scope to
      --os-domain-name OS_DOMAIN_NAME
                            Domain name to scope to
      --os-project-id OS_PROJECT_ID, --os-tenant-id OS_PROJECT_ID
                            Project ID to scope to
      --os-project-name OS_PROJECT_NAME, --os-tenant-name OS_PROJECT_NAME
                            Project name to scope to
      --os-project-domain-id OS_PROJECT_DOMAIN_ID
                            Domain ID containing project
      --os-project-domain-name OS_PROJECT_DOMAIN_NAME
                            Domain name containing project
      --os-trust-id OS_TRUST_ID
                            Trust ID
      --os-default-domain-id OS_DEFAULT_DOMAIN_ID
                            Optional domain ID to use with v3 and v2 parameters.
                            It will be used for both the user and project domain
                            in v3 and ignored in v2 authentication.
      --os-default-domain-name OS_DEFAULT_DOMAIN_NAME
                            Optional domain name to use with v3 API and v2
                            parameters. It will be used for both the user and
                            project domain in v3 and ignored in v2 authentication.
      --os-user-id OS_USER_ID
                            User id
      --os-username OS_USERNAME, --os-user-name OS_USERNAME
                            Username
      --os-user-domain-id OS_USER_DOMAIN_ID
                            User's domain id
      --os-user-domain-name OS_USER_DOMAIN_NAME
                            User's domain name
      --os-password OS_PASSWORD
                            User's password

    API Connection Options:
      Options controlling the HTTP API Connections

      --insecure            Explicitly allow client to perform "insecure" TLS
                            (https) requests. The server's certificate will not be
                            verified against any certificate authorities. This
                            option should be used with caution.
      --os-cacert <ca-certificate>
                            Specify a CA bundle file to use in verifying a TLS
                            (https) server certificate. Defaults to
                            env[OS_CACERT].
      --os-cert <certificate>
                            Defaults to env[OS_CERT].
      --os-key <key>        Defaults to env[OS_KEY].
      --timeout <seconds>   Set request timeout (in seconds).

    Service Options:
      Options controlling the specialization of the API Connection from
      information found in the catalog

      --os-service-type <name>
                            Service type to request from the catalog
      --os-service-name <name>
                            Service name to request from the catalog
      --os-interface <name>
                            API Interface to use [public, internal, admin]
      --os-region-name <name>
                            Region of the cloud to use
      --os-endpoint-override <name>
                            Endpoint to use instead of the endpoint in the catalog
      --os-api-version <name>
                            Which version of the service API to use



Example usage
-------------

To remove a project, credentials have to be provided. The usual OpenStack
environment variables can be used. When launching the ``ospurge`` script, the
project to be cleaned up has to be provided, by using either the
``--purge-project`` option or the ``--purge-own-project`` option. When the
command returns, any resources that belong to the project will have been
definitively deleted.

* Setting OpenStack credentials:

.. code-block:: console

    $ export OS_USERNAME=admin
    $ export OS_PASSWORD=password
    $ export OS_TENANT_NAME=admin
    $ export OS_AUTH_URL=http://localhost:5000/v2.0

* Removing resources:

.. code-block:: console

    $ ./ospurge --verbose --purge-project demo
    WARNING:root:2016-10-27 20:59:12,001:Going to list and/or delete resources from project 'demo'
    INFO:root:2016-10-27 20:59:12,426:Going to delete VM (id='be1cce96-fd4c-49fc-9029-db410d376258', name='cb63bb6c-de93-4213-9998-68c2a532018a')
    INFO:root:2016-10-27 20:59:12,967:Waiting for check_prerequisite() in FloatingIPs
    INFO:root:2016-10-27 20:59:15,169:Waiting for check_prerequisite() in FloatingIPs
    INFO:root:2016-10-27 20:59:19,258:Going to delete Floating IP (id='14846ada-334a-4447-8763-829364bb0d18')
    INFO:root:2016-10-27 20:59:19,613:Going to delete Snapshot (id='2e7aa42f-5596-49bf-976a-e572e6c96224', name='cb63bb6c-de93-4213-9998-68c2a532018a')
    INFO:root:2016-10-27 20:59:19,953:Going to delete Volume Backup (id='64a8b6d8-021e-4680-af58-0a5a04d29ed2', name='cb63bb6c-de93-4213-9998-68c2a532018a'
    INFO:root:2016-10-27 20:59:20,717:Going to delete Router Interface (id='7240a5df-eb83-447b-8966-f7ad2a583bb9', router_id='7057d141-29c7-4596-8312-16b441012083')
    INFO:root:2016-10-27 20:59:27,009:Going to delete Router Interface (id='fbae389d-ff69-4649-95cb-5ec8a8a64d03', router_id='7057d141-29c7-4596-8312-16b441012083')
    INFO:root:2016-10-27 20:59:28,672:Going to delete Router (id='7057d141-29c7-4596-8312-16b441012083', name='router1')
    INFO:root:2016-10-27 20:59:31,365:Going to delete Port (id='09e452bf-804d-489a-889c-be0eda7ecbca', network_id='e282fc84-7c79-4d47-a94c-b74f7a775682)'
    INFO:root:2016-10-27 20:59:32,398:Going to delete Security Group (id='7028fbd2-c998-428d-8d41-28293c3de052', name='6256fb6c-0118-4f18-8424-0f68aadb9457')
    INFO:root:2016-10-27 20:59:33,668:Going to delete Network (id='dd33dd12-4c3e-4162-8a5c-23941922271f', name='private')
    INFO:root:2016-10-27 20:59:36,119:Going to delete Image (id='39df8b40-3acd-404c-935c-d9f15732dfa6', name='cb63bb6c-de93-4213-9998-68c2a532018a')
    INFO:root:2016-10-27 20:59:36,953:Going to delete Volume (id='f482283a-25a9-419e-af92-81ec8c62e1cd', name='cb63bb6c-de93-4213-9998-68c2a532018a')
    INFO:root:2016-10-27 20:59:48,790:Going to delete Object 'cb63bb6c-de93-4213-9998-68c2a532018a.raw' from Container 'cb63bb6c-de93-4213-9998-68c2a532018a'
    INFO:root:2016-10-27 20:59:48,895:Going to delete Container (name='6256fb6c-0118-4f18-8424-0f68aadb9457')
    INFO:root:2016-10-27 20:59:48,921:Going to delete Container (name='volumebackups')

* Projects can be deleted with the ``python-openstackclient`` command-line
  interface:

.. code-block:: console

   $ openstack project delete <project>

* Users can be deleted with the ``python-openstackclient`` command-line
  interface:

.. code-block:: console

   $ openstack user delete <user>


How to extend
-------------

Given the ever-widening OpenStack ecosystem, OSPurge can't support every
OpenStack services. We intend to support in-tree, only the 'core' services.
Fortunately, OSPurge is easily extensible. There are 2 methods and you can
chose the one you prefer:

1: Add a new Python module in the ``resources`` package and define one or more
Python class(es) that subclass ``ospurge.resources.base.ServiceResource``.
Your module will automatically be loaded and your methods called.

2: Create your standalone python modules and in your module's setup.py or
setup.cfg file add an entry point to ``ospurge_resource`` pointing to the
python module in which you subclass ``ospurge.resources.base.ServiceResource``.

setup.py example:

    from setuptools import setup

    setup(
        name='my_ospurge_extension',
        entry_points={
            'ospurge_resource': [
                'foo = my_module.submodule_with_subclass',
            ],
        }
    )

setup.cfg example:

    [entry_points]
    ospurge_resource =
        foo = my_module.submodule_with_subclass

Once your module installed, it will automatically be loaded and your methods
called.

More examples on entry points:
https://amir.rachum.com/blog/2017/07/28/python-entry-points/

Have a look
at the
``main.main`` and ``main.runner`` functions to fully understand the mechanism.

Note: We won't accept any patch that broaden what OSPurge supports, beyond
the core services.


How to contribute
-----------------

OSPurge is hosted on the OpenStack infrastructure and is using
`Gerrit <https://review.openstack.org/#/q/project:openstack/ospurge>`_ to
manage contributions. You can contribute to the project by following the
`OpenStack Development workflow <http://docs.openstack.org/infra/manual/developers.html#development-workflow>`_.

Start hacking right away with:

.. code-block:: console

   $ git clone git://git.openstack.org/openstack/ospurge


Design decisions
----------------
* OSPurge depends on `os-client-config`_ to manage authentication. This way,
  environment variables (OS_*) and CLI options are properly handled.

* OSPurge is built on top of `shade`_. shade is a simple client library for
  interacting with OpenStack clouds. With shade, OSPurge can focus on the
  cleaning resources logic and not on properly building the various Python
  OpenStack clients and dealing with their not-so-intuitive API.

.. _shade: https://github.com/openstack-infra/shade/
.. _os-client-config: https://github.com/openstack/os-client-config



