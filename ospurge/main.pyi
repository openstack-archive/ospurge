#!/usr/bin/env python3
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
import argparse
import threading
import typing
from typing import Optional  # noqa: F401

from ospurge.resources.base import ServiceResource
from ospurge import utils


def configure_logging(verbose: bool) -> None:
    ...


def create_argument_parser() -> argparse.ArgumentParser:
    ...


class CredentialsManager(object):
    def __init__(self, options: argparse.Namespace) -> None:
        ...

    def ensure_role_on_project(self) -> None:
        ...

    def revoke_role_on_project(self) -> None:
        ...

    def ensure_enabled_project(self) -> None:
        ...

    def disable_project(self) -> None:
        ...


def runner(
        resource_mngr: ServiceResource, options: argparse.Namespace,
        exit: threading.Event
) -> None:
    ...


@utils.monkeypatch_oscc_logging_warning
def main() -> None:
    ...
