import contextlib
import os
from collections.abc import Callable, Generator
from unittest import mock

import pytest

from nexos.services.http import NexosHTTPAPIService


@pytest.fixture
def service_environment(monkeypatch: pytest.MonkeyPatch) -> Callable[..., Generator]:
    @contextlib.contextmanager
    def _patch_envvars(env_vars: dict[str, str]) -> Generator[None]:
        with mock.patch.dict(os.environ, clear=True):
            for key, value in env_vars.items():
                monkeypatch.setenv(key, value)
            yield

    return _patch_envvars  # type: ignore


@pytest.fixture
def initialize_nexosai_api_service() -> Callable[[], NexosHTTPAPIService]:
    return lambda: NexosHTTPAPIService()
