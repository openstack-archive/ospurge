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
import logging
import os
import types
import typing
import unittest

import pkg_resources

import six

import shade

from ospurge.resources.base import ServiceResource
from ospurge.tests import mock
from ospurge import utils


def register_test_entry_point():
    test_resource_file = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), 'resources/entry_points.py'
        )
    )
    distribution = pkg_resources.Distribution.from_filename(test_resource_file)
    entry_point = pkg_resources.EntryPoint(
        'foo', 'ospurge.tests.resources.entry_points', dist=distribution
    )
    distribution._ep_map = {utils.ENTRY_POINTS_NAME: {'foo': entry_point}}
    pkg_resources.working_set.add(distribution, 'foo')
    return entry_point


class TestUtils(unittest.TestCase):
    def test_replace_project_info_in_config(self):
        config = {
            'cloud': 'foo',
            'auth': {
                'project_name': 'bar'
            }
        }
        new_conf = utils.replace_project_info(
            config, mock.sentinel.project)

        self.assertEqual(new_conf, {
            'auth': {
                'project_id': mock.sentinel.project
            }
        })
        self.assertEqual(config, {
            'cloud': 'foo',
            'auth': {
                'project_name': 'bar'
            }
        })

    def test_load_ospurge_resource_modules(self):
        modules = utils.load_ospurge_resource_modules()
        self.assertIsInstance(modules, typing.Dict)
        for name, module in six.iteritems(modules):
            # assertIsInstance(name, typing.AnyStr) fails with:
            # TypeError: Type variables cannot be used with isinstance().
            self.assertIsInstance(name, six.string_types)
            self.assertIsInstance(module, types.ModuleType)

    def test_load_entry_points_modules(self):
        register_test_entry_point()
        modules = utils.load_entry_points_modules()
        self.assertIsInstance(modules, typing.Dict)
        for name, module in six.iteritems(modules):
            # assertIsInstance(name, typing.AnyStr) fails with:
            # TypeError: Type variables cannot be used with isinstance().
            self.assertIsInstance(name, six.string_types)
            self.assertIsInstance(module, types.ModuleType)

    def test_resource_overriding(self):
        classes = utils.get_resource_classes('Stacks')
        self.assertTrue(len(classes) == 1)
        stacks_class = classes[0]
        self.assertTrue(stacks_class.ORDER == 10)
        register_test_entry_point()
        classes = utils.get_resource_classes('Stacks')
        self.assertTrue(len(classes) == 1)
        stacks_class = classes[0]
        self.assertTrue(stacks_class.ORDER == 9)

    def test_get_all_resource_classes(self):
        classes = utils.get_resource_classes()
        self.assertIsInstance(classes, typing.List)
        for klass in classes:
            self.assertTrue(issubclass(klass, ServiceResource))

    def test_get_resource_classes(self):
        config = "Networks"
        classes = utils.get_resource_classes(config)
        self.assertIsInstance(classes, typing.List)
        for klass in classes:
            self.assertTrue(issubclass(klass, ServiceResource))

    def test_call_and_ignore_notfound(self):
        def raiser():
            raise shade.exc.OpenStackCloudResourceNotFound("")

        self.assertIsNone(
            utils.call_and_ignore_exc(
                shade.exc.OpenStackCloudResourceNotFound, raiser
            )
        )

        m = mock.Mock()
        utils.call_and_ignore_exc(
            shade.exc.OpenStackCloudResourceNotFound, m, 42)
        self.assertEqual([mock.call(42)], m.call_args_list)

    @mock.patch('logging.getLogger', autospec=True)
    def test_monkeypatch_oscc_logging_warning(self, mock_getLogger):
        oscc_target = 'os_client_config.cloud_config'
        m_oscc_logger, m_other_logger = mock.Mock(), mock.Mock()

        mock_getLogger.side_effect = \
            lambda m: m_oscc_logger if m == oscc_target else m_other_logger

        @utils.monkeypatch_oscc_logging_warning
        def f():
            logging.getLogger(oscc_target).warning("foo")
            logging.getLogger(oscc_target).warning("!catalog entry not found!")
            logging.getLogger("other").warning("!catalog entry not found!")

        f()

        self.assertEqual([mock.call.warning('foo'), ],
                         m_oscc_logger.mock_calls)
        self.assertEqual([mock.call.warning('!catalog entry not found!')],
                         m_other_logger.mock_calls)
