import dataclasses
from dependency_injector.containers import DynamicContainer
from dependency_injector.providers import Provider
from enum import StrEnum
from nexosapi.services.http import NexosAIAPIService as NexosAIAPIService

class ServiceName(StrEnum):
    NEXOSAI_API_HTTP_CLIENT = "NexosAIAPIClient"

@dataclasses.dataclass(kw_only=True)
class WiringDictionaryEntry:
    service_class: type
    provider_class: type[Provider]
    modules: set[str]

WIRING: dict[str, WiringDictionaryEntry]
SDK_SERVICES_CONTAINER: DynamicContainer

def populate_container(container: DynamicContainer, providers_config: dict[str, WiringDictionaryEntry]) -> set[str]: ...
def wire_sdk_dependencies() -> None:
    """
    Wire the SDK dependencies.
    This function is called to ensure that the SDK services are properly initialized.
    """
