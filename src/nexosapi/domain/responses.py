from typing import Literal

import httpx
import pydantic

from nexosapi.domain.base import NullableBaseModel
from nexosapi.domain.data import (
    ChatChoice,
    Embedding,
    Image,
    StorageFile,
    TeamApiKey,
    TranscriptionSegment,
    TranscriptionWord,
)
from nexosapi.domain.metadata import Model, UsageInfo


class NexosAPIResponse(NullableBaseModel):
    _response: httpx.Response = pydantic.PrivateAttr()

    class Config:
        # Exclude fields that are None when dumping the model
        json_encoders = {type(None): lambda _: None}  # noqa: RUF012
        use_enum_values = True  # Use enum values instead of names in JSON serialization


class ChatCompletionsResponse(NexosAPIResponse):
    id: str
    object: str
    created: int
    model: str
    choices: list[ChatChoice]
    usage: UsageInfo | None
    system_fingerprint: str | None
    service_tier: Literal["scale", "default"] | None


class EmbeddingResponse(NexosAPIResponse):
    object: str | None
    data: list[Embedding | None] | None
    model: str | None
    usage: UsageInfo | None


class AudioSpeechResponse(NexosAPIResponse): ...


class TranscriptionResponse(NexosAPIResponse):
    text: str
    language: str | None
    duration: str | None
    words: list[TranscriptionWord]
    segments: list[TranscriptionSegment]
    model: str | None


class TranslationResponse(NexosAPIResponse):
    text: str | None
    duration: str | None
    model: str | None
    language: Literal["english"] | None
    segments: list[TranscriptionSegment]


class ImageEndpointsResponse(NexosAPIResponse):
    created: int
    data: list[Image]


class StorageUploadResponse(NexosAPIResponse, StorageFile): ...


class StoragelistResponse(NexosAPIResponse):
    data: list[StorageFile]


class StorageFileResponse(NexosAPIResponse, StorageFile): ...


class StorageContentResponse(NexosAPIResponse):
    content: bytes  # This is typically sent as raw binary content


class StorageDeleteResponse(NexosAPIResponse):
    id: str
    deleted: bool


class ModelslistResponse(NexosAPIResponse):
    object: str
    data: list[Model]
    total: int


class TeamApiKeylistResponse(NexosAPIResponse, pydantic.RootModel):
    root: list[TeamApiKey]


class TeamApiKeyCreateResponse(NexosAPIResponse, TeamApiKey): ...


class TeamApiKeyDeleteResponse(NexosAPIResponse): ...


class TeamApiKeyUpdateResponse(NexosAPIResponse, TeamApiKey): ...


class TeamApiKeyRegenerateResponse(NexosAPIResponse, TeamApiKey): ...
