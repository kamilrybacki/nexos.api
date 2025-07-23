import fastapi
import typing
from _typeshed import Incomplete as Incomplete
from collections.abc import Coroutine
from fastapi.responses import HTMLResponse as HTMLResponse

mock_nexos_router: Incomplete

async def lifespan(_: fastapi.FastAPI) -> typing.AsyncGenerator[None]: ...

mock_nexos: Incomplete
api_header_auth: Incomplete
expected_api_key: Incomplete

class MockAPIRouteDefinition(typing.TypedDict):
    request: dict[str, typing.Any]
    response: dict[str, typing.Any]

def endpoint_to_handler(
    endpoint: str, response: dict[str, typing.Any]
) -> typing.Callable[[fastapi.Request], Coroutine[None, None, fastapi.Response]]: ...
def setup_routes() -> None: ...
async def root() -> HTMLResponse: ...
