from typing import Literal

import pydantic
from _typeshed import Incomplete as Incomplete

from nexosapi.domain.base import NullableBaseModel as NullableBaseModel
from nexosapi.domain.data import (
    ChatChoice as ChatChoice,
)
from nexosapi.domain.data import (
    Embedding as Embedding,
)
from nexosapi.domain.data import (
    Image as Image,
)
from nexosapi.domain.data import (
    StorageFile as StorageFile,
)
from nexosapi.domain.data import (
    TeamApiKey as TeamApiKey,
)
from nexosapi.domain.data import (
    TranscriptionSegment as TranscriptionSegment,
)
from nexosapi.domain.data import (
    TranscriptionWord as TranscriptionWord,
)
from nexosapi.domain.metadata import Model as Model
from nexosapi.domain.metadata import UsageInfo as UsageInfo

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
