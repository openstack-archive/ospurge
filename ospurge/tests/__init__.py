try:
    from unittest import mock   # Python 3.3+
except ImportError:
    import mock  # noqa: Python 2.7

try:
    import unittest2 as unittest   # Pyton 2.7
except ImportError:
    import unittest   # noqa
