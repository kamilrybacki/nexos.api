import typing

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
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[ChatChoice]
    usage: UsageInfo | None = None
    system_fingerprint: str | None = None
    service_tier: typing.Literal["scale", "default"] | None = None


class AudioSpeechResponse(NexosAPIResponse): ...


class AudioTranscriptionResponse(NexosAPIResponse):
    text: str | None = None
    model: str | None = None
    language: str | None = None
    duration: str | None = None
    words: list[TranscriptionWord] | None = None
    segments: list[TranscriptionSegment] | None = None


class AudioTranslationResponse(NexosAPIResponse):
    text: str | None = None
    duration: str | None = None
    model: str | None = None
    language: typing.Literal["english"] | None = None
    segments: list[TranscriptionSegment] | None = None


class ImageEndpointsResponse(NexosAPIResponse):
    created: int
    data: list[Image]


class EmbeddingResponse(NexosAPIResponse):
    object: str = "list"
    data: list[Embedding] | None = None
    model: str | None = None
    usage: UsageInfo | None = None


class StorageUploadResponse(NexosAPIResponse, StorageFile): ...


class StorageListResponse(NexosAPIResponse):
    data: list[StorageFile]


class StorageFileResponse(NexosAPIResponse, StorageFile): ...


class StorageContentResponse(NexosAPIResponse):
    content: bytes  # This is typically sent as raw binary content


class StorageDeleteResponse(NexosAPIResponse):
    id: str
    deleted: bool


class ModelsListResponse(NexosAPIResponse):
    object: str
    data: list[Model]
    total: int


class TeamApiKeyListResponse(NexosAPIResponse, pydantic.RootModel):
    root: list[TeamApiKey]


class TeamApiKeyCreateResponse(NexosAPIResponse, TeamApiKey): ...


class TeamApiKeyDeleteResponse(NexosAPIResponse): ...


class TeamApiKeyUpdateResponse(NexosAPIResponse, TeamApiKey): ...


class TeamApiKeyRegenerateResponse(NexosAPIResponse, TeamApiKey): ...
