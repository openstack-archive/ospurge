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
import abc
import collections
import logging
import time
from typing import TYPE_CHECKING

try:
    import funcsigs as inspect   # Python 2.7
except ImportError:
    import inspect
import six

from ospurge import exceptions

if TYPE_CHECKING:  # pragma: no cover
    import argparse  # noqa: F401
    import shade  # noqa: F401
    from typing import Optional  # noqa: F401


class MatchSignaturesMeta(type):
    def __init__(self, clsname, bases, clsdict):
        super(MatchSignaturesMeta, self).__init__(clsname, bases, clsdict)
        sup = super(self, self)  # type: ignore   # See python/mypy #857
        for name, value in clsdict.items():
            if name.startswith('_') or not callable(value):
                continue

            # Get the previous definition (if any) and compare the signatures
            prev_dfn = getattr(sup, name, None)
            if prev_dfn:
                prev_sig = inspect.signature(prev_dfn)
                val_sig = inspect.signature(value)
                if prev_sig != val_sig:
                    value_name = getattr(value, '__qualname__', value.__name__)
                    logging.warning('Signature mismatch in %s. %s != %s',
                                    value_name, prev_sig, val_sig)


if six.PY3:
    class OrderedMeta(type):
        def __new__(cls, clsname, bases, clsdict):
            ordered_methods = cls.ordered_methods
            allowed_next_methods = list(ordered_methods)
            for name, value in clsdict.items():
                if name not in ordered_methods:
                    continue

                if name not in allowed_next_methods:
                    value_name = value.__qualname__
                    logging.warning(
                        "Method %s not defined at the correct location."
                        " Methods in class %s must be defined in the following"
                        " order %r",
                        value_name, clsname, ordered_methods
                    )
                    continue  # pragma: no cover

                _slice = slice(allowed_next_methods.index(name) + 1, None)
                allowed_next_methods = allowed_next_methods[_slice]

            # Cast to dict is required. We can't pass an OrderedDict here.
            return super().__new__(cls, clsname, bases, dict(clsdict))

        @classmethod
        def __prepare__(cls, clsname, bases):
            return collections.OrderedDict()

    class CodingStyleMixin(OrderedMeta, MatchSignaturesMeta, abc.ABCMeta):
        ordered_methods = ['order', 'check_prerequisite', 'list',
                           'should_delete', 'delete', 'to_string']
else:   # pragma: no cover here
    # OrderedMeta is not supported on Python 2. Class members are unordered in
    # Python 2 and __prepare__() was introduced in Python 3.
    class CodingStyleMixin(MatchSignaturesMeta, abc.ABCMeta):
        pass


class BaseServiceResource(object):
    def __init__(self):
        self.cleanup_project_id = None  # type: Optional[str]
        self.cloud = None  # type: Optional[shade.OpenStackCloud]
        self.options = None  # type: Optional[argparse.Namespace]


class ServiceResource(six.with_metaclass(CodingStyleMixin,
                                         BaseServiceResource)):
    ORDER = None  # type: int

    def __init__(self, creds_manager):
        super(ServiceResource, self).__init__()
        if self.ORDER is None:
            raise ValueError(
                'Class {}.{} must override the "ORDER" class attribute'.format(
                    self.__module__, self.__class__.__name__)  # type: ignore
            )

        self.cleanup_project_id = creds_manager.project_id
        self.cloud = creds_manager.cloud
        self.options = creds_manager.options

    @classmethod
    def order(cls):
        return cls.ORDER

    def check_prerequisite(self):
        return True

    @abc.abstractmethod
    def list(self):
        raise NotImplementedError

    def should_delete(self, resource):
        project_id = resource.get('project_id', resource.get('tenant_id'))
        if project_id:
            return project_id == self.cleanup_project_id
        else:
            # Uncomment the following line once Shade and all OpenStack
            # services returns the resource owner. In the mean time no need
            # to be worrying.
            # logging.warning("Can't determine owner of resource %s", resource)
            return True

    @abc.abstractmethod
    def delete(self, resource):
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def to_str(resource):
        raise NotImplementedError

    def wait_for_check_prerequisite(self, exit):
        timeout = time.time() + 360
        sleep = 2
        while time.time() < timeout:
            if exit.is_set():
                raise RuntimeError(
                    "Resource manager exited because it was interrupted or "
                    "another resource manager failed"
                )
            if self.check_prerequisite():
                break
            logging.info("Waiting for check_prerequisite() in %s",
                         self.__class__.__name__)
            time.sleep(sleep)
            sleep = min(sleep * 2, 8)
        else:
            raise exceptions.TimeoutError(
                "Timeout exceeded waiting for check_prerequisite()")
