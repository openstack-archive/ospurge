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
import time

import six

from ospurge import exceptions
from ospurge.resources import base
from ospurge.tests import mock
from ospurge.tests import unittest


def generate_timeout_series(timeout):
    """Generate a series of times that exceeds the given timeout.
    Yields a series of fake time.time() floating point numbers
    such that the difference between each pair in the series just
    exceeds the timeout value that is passed in.  Useful for
    mocking time.time() in methods that otherwise wait for timeout
    seconds.
    """
    iteration = 0
    while True:
        iteration += 1
        yield (iteration * timeout) + iteration


class SignatureMismatch(Exception):
    pass


class WrongMethodDefOrder(Exception):
    pass


@mock.patch('logging.warning', mock.Mock(side_effect=SignatureMismatch))
class TestMatchSignaturesMeta(unittest.TestCase):
    class Test(six.with_metaclass(base.MatchSignaturesMeta)):
        def a(self, arg1):
            pass

        def b(self, arg1=True):
            pass

        def c(self, arg1, arg2):
            pass

        def _private(self):
            pass

    def test_nominal(self):
        class Foo1(self.Test):
            def a(self, arg1):
                pass

        class Foo2(self.Test):
            def b(self, arg1=True):
                pass

        class Foo3(self.Test):
            def c(self, arg1, arg2):
                pass

        class Foo4(self.Test):
            def _startswith_underscore(self, arg1, arg2):
                pass

        class Foo5(self.Test):
            def new_method(self):
                pass

    def test_method_arg1_has_different_name(self):
        with self.assertRaises(SignatureMismatch):
            class Foo(self.Test):
                def a(self, other_name):
                    pass

    def test_method_arg1_has_different_value(self):
        with self.assertRaises(SignatureMismatch):
            class Foo(self.Test):
                def b(self, arg1=False):
                    pass

    def test_method_has_different_number_of_args(self):
        with self.assertRaises(SignatureMismatch):
            class Foo(self.Test):
                def c(self, arg1, arg2, arg3):
                    pass


# OrderedMeta requires Python 3
if six.PY3:
    @mock.patch('logging.warning', mock.Mock(side_effect=WrongMethodDefOrder))
    class TestOrderedMeta(unittest.TestCase):
        class Test(base.OrderedMeta):
            ordered_methods = ['a', 'b']

        def test_nominal(self):
            class Foo1(six.with_metaclass(self.Test)):
                def a(self):
                    pass

            class Foo2(six.with_metaclass(self.Test)):
                def b(self):
                    pass

            class Foo3(six.with_metaclass(self.Test)):
                def a(self):
                    pass

                def b(self):
                    pass

            class Foo4(six.with_metaclass(self.Test)):
                def a(self):
                    pass

                def other(self):
                    pass

                def b(self):
                    pass

        def test_wrong_order(self):
            with self.assertRaises(WrongMethodDefOrder):
                class Foo(six.with_metaclass(self.Test)):
                    def b(self):
                        pass

                    def a(self):
                        pass


class TestServiceResource(unittest.TestCase):
    def test_init_without_order_attr(self):
        class Foo5(base.ServiceResource):
            def list(self):
                pass

            def delete(self, resource):
                pass

            @staticmethod
            def to_str(resource):
                pass

        self.assertRaisesRegex(ValueError, 'Class .*ORDER.*',
                               Foo5, mock.Mock())

    def test_instantiate_without_concrete_methods(self):
        class Foo6(base.ServiceResource):
            ORDER = 1

        self.assertRaises(TypeError, Foo6)

    @mock.patch.multiple(base.ServiceResource, ORDER=12,
                         __abstractmethods__=set())
    def test_instantiate_nominal(self):
        creds_manager = mock.Mock()
        resource_manager = base.ServiceResource(creds_manager)

        self.assertEqual(resource_manager.cloud, creds_manager.cloud)
        self.assertEqual(resource_manager.options, creds_manager.options)
        self.assertEqual(resource_manager.cleanup_project_id,
                         creds_manager.project_id)

        self.assertEqual(12, resource_manager.order())
        self.assertEqual(True, resource_manager.check_prerequisite())

        self.assertRaises(NotImplementedError, resource_manager.delete, '')
        self.assertRaises(NotImplementedError, resource_manager.to_str, '')
        self.assertRaises(NotImplementedError, resource_manager.list)

    @mock.patch.multiple(base.ServiceResource, ORDER=12,
                         __abstractmethods__=set())
    def test_should_delete(self):
        creds_manager = mock.Mock()
        resource_manager = base.ServiceResource(creds_manager)

        resource = mock.Mock(get=mock.Mock(side_effect=[None, None]))
        self.assertEqual(True, resource_manager.should_delete(resource))
        resource.get.call_args = [mock.call('project_id'),
                                  mock.call('tenant_id')]

        resource.get.side_effect = ["Foo", "Bar"]
        self.assertEqual(False, resource_manager.should_delete(resource))

        resource.get.side_effect = [42, resource_manager.cleanup_project_id]
        self.assertEqual(True, resource_manager.should_delete(resource))

    @mock.patch('time.sleep', autospec=True)
    @mock.patch.multiple(base.ServiceResource, ORDER=12,
                         __abstractmethods__=set())
    @mock.patch.object(base.ServiceResource, 'check_prerequisite',
                       return_value=False)
    def test_wait_for_check_prerequisite_runtimeerror(
            self, mock_check_prerequisite, mock_sleep):
        resource_manager = base.ServiceResource(mock.Mock())
        mock_exit = mock.Mock(is_set=mock.Mock(return_value=False))

        with mock.patch('time.time') as mock_time:
            mock_time.side_effect = generate_timeout_series(30)
            self.assertRaisesRegex(
                exceptions.TimeoutError, "^Timeout exceeded .*",
                resource_manager.wait_for_check_prerequisite, mock_exit
            )

        self.assertEqual(mock_check_prerequisite.call_args_list,
                         [mock.call()] * (120 // 30 - 1))
        self.assertEqual(mock_sleep.call_args_list,
                         [mock.call(i) for i in (2, 4, 8)])

        mock_sleep.reset_mock()
        mock_check_prerequisite.reset_mock()
        mock_exit.is_set.return_value = True
        self.assertRaisesRegex(
            RuntimeError, ".* exited because it was interrupted .*",
            resource_manager.wait_for_check_prerequisite, mock_exit
        )

    @mock.patch('time.sleep', mock.Mock(spec_set=time.sleep))
    @mock.patch.multiple(base.ServiceResource, ORDER=12,
                         __abstractmethods__=set())
    def test_wait_for_check_prerequisite_nominal(self):
        resource_manager = base.ServiceResource(mock.Mock())

        with mock.patch.object(resource_manager, 'check_prerequisite') as m:
            m.side_effect = [False, False, True]
            resource_manager.wait_for_check_prerequisite(
                mock.Mock(is_set=mock.Mock(return_value=False)))

        self.assertEqual(3, m.call_count)
