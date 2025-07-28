import fastapi
import typing
from _typeshed import Incomplete
from collections.abc import Coroutine
from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse

mock_nexos_router: Incomplete

@asynccontextmanager
async def lifespan(_: fastapi.FastAPI) -> typing.AsyncGenerator[None]:
    """
    Lifespan event handler to set up routes when the application starts.
    """

mock_nexos: Incomplete
api_header_auth: Incomplete
expected_api_key: Incomplete

class MockAPIRouteDefinition(typing.TypedDict):
    request: dict[str, typing.Any]
    response: dict[str, typing.Any]

def endpoint_to_handler(
    endpoint: str, response: dict[str, typing.Any]
) -> typing.Callable[[fastapi.Request], Coroutine[None, None, fastapi.Response]]:
    """
    Converts an endpoint string to a handler function.
    """

def setup_routes() -> None: ...
async def root() -> HTMLResponse:
    """
    Root endpoint for the mock API.
    """
