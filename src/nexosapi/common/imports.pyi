from nexosapi.domain.requests import NexosAPIRequest as NexosAPIRequest
from nexosapi.domain.responses import NexosAPIResponse as NexosAPIResponse

def get_nexosai_classes_from_module[APIDataModel](
    reference_class: type[APIDataModel],
) -> dict[str, type[APIDataModel]]: ...
def get_available_request_models() -> dict[str, type[NexosAPIRequest]]: ...
def get_available_response_models() -> dict[str, type[NexosAPIResponse]]: ...
def get_data_model_if_available[APIDataModel](
    model_name: str, models_dict: dict[str, type[APIDataModel]]
) -> APIDataModel: ...
