import importlib
import inspect

from nexosapi.common.exceptions import UndefinedEndpointModelError
from nexosapi.domain.requests import NexosAPIRequest
from nexosapi.domain.responses import NexosAPIResponse


def get_nexosai_classes_from_module[APIDataModel](reference_class: type[APIDataModel]) -> dict[str, type[APIDataModel]]:
    requests_module = reference_class.__module__
    imported_module = importlib.import_module(requests_module)
    classes_available_in_the_module = inspect.getmembers(imported_module, inspect.isclass)
    return dict(model for model in classes_available_in_the_module if model[1].__base__ == reference_class)


def get_available_request_models() -> dict[str, type[NexosAPIRequest]]:
    return get_nexosai_classes_from_module(NexosAPIRequest)


def get_available_response_models() -> dict[str, type[NexosAPIResponse]]:
    return get_nexosai_classes_from_module(NexosAPIResponse)


def get_data_model_if_available[APIDataModel](
    model_name: str, models_dict: dict[str, type[APIDataModel]]
) -> APIDataModel:
    if not (model := models_dict.get(model_name)):
        error_message = f"[API] {model_name} not found in the {[*models_dict.values()].pop().__module__} module."
        raise UndefinedEndpointModelError(error_message)
    return model  # type: ignore
