from typing import Literal

from pydantic import BaseModel

from nexos.domain.data import (
    ChatChoice,
    Embedding,
    Image,
    StorageFile,
    TeamApiKey,
    TranscriptionSegment,
    TranscriptionWord,
)
from nexos.domain.metadata import Model, UsageInfo


class NexosAIResponse(BaseModel):
    class Config:
        # Exclude fields that are None when dumping the model
        json_encoders = {type(None): lambda _: None}  # noqa: RUF012
        use_enum_values = True  # Use enum values instead of names in JSON serialization


class ChatCompletionsResponse(NexosAIResponse):
    id: str
    object: str
    created: int
    model: str
    choices: list[ChatChoice]
    usage: UsageInfo | None
    system_fingerprint: str | None
    service_tier: Literal["scale", "default"] | None


class EmbeddingResponse(NexosAIResponse):
    object: str | None
    data: list[Embedding | None] | None
    model: str | None
    usage: UsageInfo | None


class AudioSpeechResponse(NexosAIResponse): ...


class TranscriptionResponse(NexosAIResponse):
    text: str
    language: str | None
    duration: str | None
    words: list[TranscriptionWord] | None
    segments: list[TranscriptionSegment] | None
    model: str | None


class TranslationResponse(NexosAIResponse):
    text: str | None
    duration: str | None
    model: str | None
    language: Literal["english"] | None
    segments: list[TranscriptionSegment] | None


class ImageEndpointsResponse(NexosAIResponse):
    created: int
    data: list[Image]


class StorageUploadResponse(NexosAIResponse, StorageFile): ...


class StoragelistResponse(NexosAIResponse):
    data: list[StorageFile]


class StorageFileResponse(NexosAIResponse, StorageFile): ...


class StorageContentResponse(NexosAIResponse):
    content: bytes  # This is typically sent as raw binary content


class StorageDeleteResponse(NexosAIResponse):
    id: str
    deleted: bool


class ModelslistResponse(NexosAIResponse):
    object: str
    data: list[Model]
    total: int


class TeamApiKeylistResponse(NexosAIResponse):
    __root__: list[TeamApiKey]


class TeamApiKeyCreateResponse(NexosAIResponse, TeamApiKey): ...


class TeamApiKeyDeleteResponse(NexosAIResponse): ...


class TeamApiKeyUpdateResponse(NexosAIResponse, TeamApiKey): ...


class TeamApiKeyRegenerateResponse(NexosAIResponse, TeamApiKey): ...
