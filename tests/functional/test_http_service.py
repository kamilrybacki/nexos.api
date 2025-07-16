from unittest.mock import AsyncMock, patch

import pytest

from nexosapi.services.http import NexosAPIService


@pytest.mark.asyncio
@patch.object(NexosAPIService, "_request", new_callable=AsyncMock)
async def test_get_request(mock_request, initialize_nexosai_api_service, service_environment) -> None:
    with service_environment(
        {
            "NEXOSAI__BASE_URL": "http://mock-nexos-api",
            "NEXOSAI__API_KEY": "mock_api_key",
        }
    ):
        mock_request.return_value = "mock_response"
        response = await initialize_nexosai_api_service().get("test-url")
        mock_request.assert_called_once_with("GET", "test-url")
        assert response == "mock_response"


@pytest.mark.asyncio
@patch.object(NexosAPIService, "_request", new_callable=AsyncMock)
async def test_post_request(mock_request, initialize_nexosai_api_service, service_environment) -> None:
    with service_environment(
        {
            "NEXOSAI__BASE_URL": "http://mock-nexos-api",
            "NEXOSAI__API_KEY": "mock_api_key",
        }
    ):
        mock_request.return_value = "mock_response"
        response = await initialize_nexosai_api_service().post("test-url", json={"key": "value"})
        mock_request.assert_called_once_with("POST", "test-url", json={"key": "value"})
        assert response == "mock_response"


@pytest.mark.asyncio
@patch.object(NexosAPIService, "_request", new_callable=AsyncMock)
async def test_head_request(mock_request, initialize_nexosai_api_service, service_environment) -> None:
    with service_environment(
        {
            "NEXOSAI__BASE_URL": "http://mock-nexos-api",
            "NEXOSAI__API_KEY": "mock_api_key",
        }
    ):
        mock_request.return_value = "mock_response"
        response = await initialize_nexosai_api_service().head("test-url")
        mock_request.assert_called_once_with("HEAD", "test-url")
        assert response == "mock_response"


@pytest.mark.asyncio
@patch.object(NexosAPIService, "_request", new_callable=AsyncMock)
async def test_request_with_override_base(mock_request, initialize_nexosai_api_service, service_environment) -> None:
    with service_environment(
        {
            "NEXOSAI__BASE_URL": "http://mock-nexos-api",
            "NEXOSAI__API_KEY": "mock_api_key",
        }
    ):
        mock_request.return_value = "mock_response"
        response = await initialize_nexosai_api_service().get("test-url", override_base=True)
        mock_request.assert_called_once_with("GET", "test-url", override_base=True)
        assert response == "mock_response"
