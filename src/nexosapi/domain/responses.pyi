from __future__ import annotations
import typing
import httpx
import pydantic
import typing
from _typeshed import Incomplete
from nexosapi.domain.base import NullableBaseModel as NullableBaseModel
from nexosapi.domain.data import (
    ChatChoice as ChatChoice,
    Embedding as Embedding,
    Image as Image,
    StorageFile as StorageFile,
    TeamApiKey as TeamApiKey,
    TranscriptionSegment as TranscriptionSegment,
    TranscriptionWord as TranscriptionWord,
)
from nexosapi.domain.metadata import Model as Model, UsageInfo as UsageInfo

class NexosAPIResponse(NullableBaseModel):
    _response: httpx.Response

    class Config:
        json_encoders: Incomplete
        use_enum_values: bool

class ChatCompletionsResponse(NexosAPIResponse):
    id: str
    object: str
    created: int
    model: str
    choices: list[ChatChoice]
    usage: UsageInfo | None
    system_fingerprint: str | None
    service_tier: typing.Literal["scale", "default"] | None

    @property
    def tool_calls(self) -> list[dict[str, typing.Any]]:
        """
        Extracts and returns a list of tool calls from the chat response choices.
        Each tool call is represented as a dictionary.
        """

class AudioSpeechResponse(NexosAPIResponse): ...

class AudioTranscriptionResponse(NexosAPIResponse):
    text: str | None
    model: str | None
    language: str | None
    duration: str | None
    words: list[TranscriptionWord] | None
    segments: list[TranscriptionSegment] | None

class AudioTranslationResponse(NexosAPIResponse):
    text: str | None
    duration: str | None
    model: str | None
    language: typing.Literal["english"] | None
    segments: list[TranscriptionSegment] | None

class ImageEndpointsResponse(NexosAPIResponse):
    created: int
    data: list[Image]

class EmbeddingResponse(NexosAPIResponse):
    object: str
    data: list[Embedding] | None
    model: str | None
    usage: UsageInfo | None

class StorageUploadResponse(NexosAPIResponse, StorageFile): ...

class StorageListResponse(NexosAPIResponse):
    data: list[StorageFile]

class StorageFileResponse(NexosAPIResponse, StorageFile): ...

class StorageContentResponse(NexosAPIResponse):
    content: bytes

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

class NexosAPIResponseData(typing.TypedDict):
    _response: httpx.Response

class ChatCompletionsResponseData(typing.TypedDict):
    id: str
    object: str
    created: int
    model: str
    choices: list[ChatChoice]
    usage: typing.NotRequired[UsageInfo | None]
    system_fingerprint: typing.NotRequired[str | None]
    service_tier: typing.NotRequired[typing.Literal["scale", "default"] | None]

class AudioSpeechResponseData(typing.TypedDict):
    pass

class AudioTranscriptionResponseData(typing.TypedDict):
    text: typing.NotRequired[str | None]
    model: typing.NotRequired[str | None]
    language: typing.NotRequired[str | None]
    duration: typing.NotRequired[str | None]
    words: typing.NotRequired[list[TranscriptionWord] | None]
    segments: typing.NotRequired[list[TranscriptionSegment] | None]

class AudioTranslationResponseData(typing.TypedDict):
    text: typing.NotRequired[str | None]
    duration: typing.NotRequired[str | None]
    model: typing.NotRequired[str | None]
    language: typing.NotRequired[typing.Literal["english"] | None]
    segments: typing.NotRequired[list[TranscriptionSegment] | None]

class ImageEndpointsResponseData(typing.TypedDict):
    created: int
    data: list[Image]

class EmbeddingResponseData(typing.TypedDict):
    object: str
    data: typing.NotRequired[list[Embedding] | None]
    model: typing.NotRequired[str | None]
    usage: typing.NotRequired[UsageInfo | None]

class StorageUploadResponseData(typing.TypedDict):
    pass

class StorageListResponseData(typing.TypedDict):
    data: list[StorageFile]

class StorageFileResponseData(typing.TypedDict):
    pass

class StorageContentResponseData(typing.TypedDict):
    content: bytes

class StorageDeleteResponseData(typing.TypedDict):
    id: str
    deleted: bool

class ModelsListResponseData(typing.TypedDict):
    object: str
    data: list[Model]
    total: int

class TeamApiKeyListResponseData(typing.TypedDict):
    root: list[TeamApiKey]

class TeamApiKeyCreateResponseData(typing.TypedDict):
    pass

class TeamApiKeyDeleteResponseData(typing.TypedDict):
    pass

class TeamApiKeyUpdateResponseData(typing.TypedDict):
    pass

class TeamApiKeyRegenerateResponseData(typing.TypedDict):
    pass
