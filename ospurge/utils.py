#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.
import copy
import functools
import importlib
import logging
import os
import pkgutil
import re

from ospurge.resources import base


def get_resource_classes(resources=None):
    """
    Import all the modules in the `resources` package and return all the
    subclasses of the `ServiceResource` ABC that match the `resources` arg.

    This way we can easily extend OSPurge by just adding a new file in the
    `resources` dir.
    """
    iter_modules = pkgutil.iter_modules(
        [os.path.join(os.path.dirname(__file__), 'resources')],
        prefix='ospurge.resources.'
    )
    for (_, name, ispkg) in iter_modules:
        if not ispkg:
            importlib.import_module(name)

    all_classes = base.ServiceResource.__subclasses__()

    # If we don't want to filter out which classes to return, use a global
    # wildcard regex.
    if not resources:
        regex = re.compile(".*")
    # Otherwise, build a regex by concatenation.
    else:
        regex = re.compile('|'.join(resources))

    return [c for c in all_classes if regex.match(c.__name__)]


def monkeypatch_oscc_logging_warning(f):
    """
    Monkey-patch logging.warning() method to silence 'os_client_config' when
    it complains that a Keystone catalog entry is not found. This warning
    benignly happens when, for instance, we try to cleanup a Neutron resource
    but Neutron is not available on the target cloud environment.
    """
    oscc_target = 'os_client_config.cloud_config'
    orig_logging = logging.getLogger(oscc_target).warning

    def logging_warning(msg: str, *args, **kwargs):
        if 'catalog entry not found' not in msg:
            orig_logging(msg, *args, **kwargs)

    @functools.wraps(f)
    def wrapper(*args: list, **kwargs):
        try:
            setattr(logging.getLogger(oscc_target), 'warning', logging_warning)
            return f(*args, **kwargs)
        finally:
            setattr(logging.getLogger(oscc_target), 'warning', orig_logging)

    return wrapper


def call_and_ignore_exc(exc, f, *args):
    try:
        f(*args)
    except exc as e:
        logging.debug("The following exception was ignored: %r", e)


def replace_project_info(config, new_project_id):
    """
    Replace all tenant/project info in a `os_client_config` config dict with
    a new project. This is used to bind/scope to another project.
    """
    new_conf = copy.deepcopy(config)
    new_conf.pop('cloud', None)
    new_conf['auth'].pop('project_name', None)
    new_conf['auth'].pop('project_id', None)

    new_conf['auth']['project_id'] = new_project_id

    return new_conf
