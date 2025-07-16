import contextlib
import json
import logging
import os
from collections.abc import Callable, Generator
from pathlib import Path
from unittest import mock

import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.image import DockerImage
from testcontainers.core.waiting_utils import wait_for_logs

from nexosapi.services.http import NexosAPIService
from tests.conftest import ASSETS_DIR

MOCK_API_DIR = ASSETS_DIR / "mock_api"
MOCK_API_PORT = 5000
MOCK_API_KEY = "let-me-in"


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
def initialize_nexosai_api_service() -> Callable[[], NexosAPIService]:
    return lambda: NexosAPIService()


MOCK_API_DATA_JSON_PATH = (ASSETS_DIR / "mock_api" / "data.json").as_posix()
MOCK_API_DATA = json.loads(Path.open(MOCK_API_DATA_JSON_PATH).read())


@pytest.fixture
def using_test_api_container() -> Callable[..., Generator[str]]:
    @contextlib.contextmanager
    def _with_spawned_container() -> Generator[str]:
        with DockerImage(path=MOCK_API_DIR, dockerfile_path=MOCK_API_DIR / "Dockerfile") as image:
            api_start_command = (
                f"uvicorn main:mock_nexos --host 0.0.0.0 --port {MOCK_API_PORT} --reload --reload-dir /app"
            )
            with (
                DockerContainer(str(image))
                .with_env("MOCK_NEXOS__API_KEY", MOCK_API_KEY)
                .with_command(api_start_command)
                .with_exposed_ports(MOCK_API_PORT)
            ) as container:
                delay = wait_for_logs(container, "Uvicorn running on")
                logging.info(f"[TEST] Test API container started and ready after {delay} seconds.")
                yield f"{container.get_container_host_ip()}:{container.get_exposed_port(MOCK_API_PORT)}"

    return _with_spawned_container  # type: ignore
