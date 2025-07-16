import json
import logging
import os
import typing
from collections.abc import Coroutine
from contextlib import asynccontextmanager
from pathlib import Path

import fastapi
from fastapi.responses import HTMLResponse
from fastapi.security import APIKeyHeader

mock_nexos_router = fastapi.APIRouter()


@asynccontextmanager
async def lifespan() -> typing.AsyncGenerator[None]:
    """
    Lifespan event handler to set up routes when the application starts.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:  %(message)s")
    logging.info(f"[API] Mock NEXOS API key: {expected_api_key}")
    setup_routes()
    mock_nexos.include_router(mock_nexos_router)
    yield
    logging.info("[API] Mock NEXOS API shutdown.")


mock_nexos = fastapi.FastAPI(
    title="Mock NEXOS API",
    description="This is a mock implementation of the NEXOS API for testing purposes.",
    version="1.0.0",
    lifespan=lifespan,
)
api_header_auth = APIKeyHeader(name="Authorization", auto_error=False)
expected_api_key = os.environ.get("MOCK_NEXOS__API_KEY")


class MockAPIRouteDefinition(typing.TypedDict):
    endpoint: str
    request: dict[str, typing.Any]
    response: dict[str, typing.Any]


def endpoint_to_handler(
    endpoint: str, response: dict[str, typing.Any]
) -> typing.Callable[[fastapi.Request], Coroutine[None, None, fastapi.Response]]:
    """
    Converts an endpoint string to a handler function.
    """
    verb, path = endpoint.split(":", 1)
    verb = verb.strip().lower()

    if verb not in ["get", "post", "put", "delete", "patch"]:
        raise ValueError(f"Invalid HTTP verb '{verb}' in endpoint '{endpoint}'.")

    async def mock_api_handler(
        request: fastapi.Request, api_key: str = fastapi.Depends(api_header_auth)
    ) -> fastapi.Response:
        """
        Mock API handler that returns a predefined response.
        """
        if api_key != f"Bearer {expected_api_key}":
            logging.warning(f"[TEST] Unauthorized access attempt with API key: {api_key}")
            return fastapi.Response(status_code=fastapi.status.HTTP_401_UNAUTHORIZED, content="Unauthorized")
        logging.info(f"[TEST] Mock API called: {request.method} {request.url.path}")
        return fastapi.Response(content=json.dumps(response), media_type="application/json")

    return mock_api_handler  # type: ignore


def setup_routes() -> None:
    with Path.open(Path(__file__).parent / "data.json") as file:
        mock_responses: list[MockAPIRouteDefinition] = json.load(file)
        logging.info(f"[API] Setting up {len(mock_responses)} routes")
        for route_index in range(len(mock_responses)):
            route = mock_responses[route_index]
            handler = endpoint_to_handler(route["endpoint"], route["response"])
            mock_nexos_router.add_api_route(
                path=route["endpoint"].split(":", 1)[1].strip(),
                endpoint=handler,
                methods=[route["endpoint"].split(":")[0].strip().upper()],
                name=f"{route['endpoint'].replace(':', '_').replace('/', '_').strip('_')}",
            )


@mock_nexos.get("/")
async def root() -> HTMLResponse:
    """
    Root endpoint for the mock API.
    """
    routes_list = "\n".join(
        f"<li>({next(iter(route.methods))}) <b>{route.path}</b></li>"  # type: ignore
        for route in mock_nexos_router.routes
    )
    logging.info(routes_list)
    return HTMLResponse(
        content=f"""
            <h1>Mock NEXOS API</h1><p>This is a mock implementation of the NEXOS API for testing purposes.</p>
            <h2>Available endpoints</h2>
            <ul>
                {routes_list}
            </ul>
            <p>Mock API is running. Use the endpoints to test your application.</p>
        """
    )
