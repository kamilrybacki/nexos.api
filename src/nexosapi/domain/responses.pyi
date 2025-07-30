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

class AudioSpeechResponse(NexosAPIResponse): ...

class AudioTranscriptionResponse(NexosAPIResponse):
    text: str | None
    model: str | None
    language: str | None
    duration: str | None
    words: list[TranscriptionWord]
    segments: list[TranscriptionSegment]

class AudioTranslationResponse(NexosAPIResponse):
    text: str | None
    duration: str | None
    model: str | None
    language: typing.Literal["english"] | None
    segments: list[TranscriptionSegment]

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
