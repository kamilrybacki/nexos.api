import logging
from http import HTTPStatus

import pytest
import requests

from nexosapi.config.settings.defaults import NEXOSAI_AUTH_HEADER_NAME, NEXOSAI_AUTH_HEADER_PREFIX
from nexosapi.services.http import NexosAIAPIService
from tests.services import MOCK_API_DATA, MOCK_API_DATA_JSON_PATH, MOCK_API_KEY


@pytest.mark.asyncio
@pytest.mark.order("first")
async def test_connection_to_test_api(
    using_test_api_container, service_environment, initialize_nexosai_api_service
) -> None:
    with (
        using_test_api_container() as api_host,
        service_environment(
            {
                "NEXOSAI__BASE_URL": f"http://{api_host}",
                "NEXOSAI__VERSION": "v1",
                "NEXOSAI__API_KEY": MOCK_API_KEY,
            }
        ),
    ):
        test_endpoint = f"http://{api_host}/v1/models"

        # We expect to hit the mock API without an API key first to get unauthorized response
        unauthorized_test_request = requests.get(test_endpoint, timeout=10)
        assert unauthorized_test_request.status_code == HTTPStatus.UNAUTHORIZED
        assert unauthorized_test_request.text == "Unauthorized"

        authorized_test_request = requests.get(
            test_endpoint,
            timeout=10,
            headers={NEXOSAI_AUTH_HEADER_NAME: f"{NEXOSAI_AUTH_HEADER_PREFIX} {MOCK_API_KEY}"},
        )
        assert authorized_test_request.status_code == HTTPStatus.OK, (
            "Expected to get a successful response from the mock API with the correct API key"
        )

        nexos_api: NexosAIAPIService = initialize_nexosai_api_service()
        response = await nexos_api.request("GET", test_endpoint.split("/")[-1])
        logging.info(f"[TEST] Response from mock API: {response.json()}")

        assert response.status_code == HTTPStatus.OK

        data_key = "get:" + test_endpoint.removeprefix(f"http://{api_host}")
        logging.info(f"[TEST] Comparing with data from mock dataset ({MOCK_API_DATA_JSON_PATH}): {data_key}")
        assert response.json() == MOCK_API_DATA.get(data_key).get("response", {}), (
            "Expected response does not match response defined in the mock API dataset"
        )
