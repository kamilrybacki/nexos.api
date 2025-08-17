import dataclasses
import importlib
from enum import StrEnum

from dependency_injector.containers import DynamicContainer
from dependency_injector.providers import Provider, Singleton

from nexosapi.services.http import NexosAIAPIService


class ServiceName(StrEnum):
    NEXOSAI_API_HTTP_CLIENT = "NexosAIAPIClient"


@dataclasses.dataclass(kw_only=True)
class WiringDictionaryEntry:
    """
    Class representing a wiring dictionary entry for dependency injection.

    :ivar service_class: The service class to be wired.
    :ivar provider_class: The provider class to be used for the service.
    :ivar modules: The modules that require this service.
    """

    service_class: type
    provider_class: type[Provider]
    modules: set[str]


WIRING: dict[str, WiringDictionaryEntry] = {
    ServiceName.NEXOSAI_API_HTTP_CLIENT: WiringDictionaryEntry(
        service_class=NexosAIAPIService, provider_class=Singleton, modules={"nexosapi.api.controller"}
    )
}


SDK_SERVICES_CONTAINER: DynamicContainer = DynamicContainer()


def populate_container(container: DynamicContainer, providers_config: dict[str, WiringDictionaryEntry]) -> set[str]:
    """
    Populate the dependency injection container with the provided services.

    :param container: The dependency injection container to populate.
    :param providers_config: The configuration dictionary containing service providers.
    :return: A set of module names that the container will be wired to.
    """
    modules_to_wire = set()
    for provider_name, provider_info in providers_config.items():
        provided_cls = provider_info.service_class
        provider_cls = provider_info.provider_class
        provider_instance = provider_cls(provided_cls)  # type: ignore[call-arg]
        setattr(container, provider_name, provider_instance)
        modules_to_wire.update(provider_info.modules)
    return modules_to_wire


def wire_sdk_dependencies() -> None:
    """
    Wire the SDK dependencies.
    This function is called to ensure that the SDK services are properly initialized.
    """
    modules = populate_container(SDK_SERVICES_CONTAINER, WIRING)
    for module in modules:
        imported_module = importlib.import_module(module)
        setattr(imported_module, SDK_SERVICES_CONTAINER.__class__.__name__, SDK_SERVICES_CONTAINER)
    SDK_SERVICES_CONTAINER.wire(modules=[*modules])
    SDK_SERVICES_CONTAINER.init_resources()
