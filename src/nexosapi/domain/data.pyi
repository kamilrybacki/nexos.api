from __future__ import annotations
import typing
from nexosapi.domain.base import NullableBaseModel as NullableBaseModel
from nexosapi.domain.metadata import Annotation as Annotation, LogProbsInfo as LogProbsInfo, ToolCall as ToolCall
from typing import Literal

class Audio(NullableBaseModel):
    id: str
    expires_at: int
    data: str
    transcript: str

class ChatMessage(NullableBaseModel):
    role: Literal["system", "user", "assistant", "tool", "function", "developer"] | None
    refusal: str | None
    tool_calls: list[ToolCall] | None
    content: str | None
    audio: Audio | None
    annotations: list[Annotation] | None
    name: str | None

class PredictionType(NullableBaseModel):
    type: str
    content: str | None

class AudioConfiguration(NullableBaseModel):
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    format: Literal["mp3", "opus", "flac", "wav", "pcm16"]

class ChatChoice(NullableBaseModel):
    index: int
    message: ChatMessage
    finish_reason: str
    logprobs: LogProbsInfo | None

class TranscriptionWord(NullableBaseModel):
    word: str
    start: float
    end: float

class TranscriptionSegment(NullableBaseModel):
    id: int
    seek: int
    start: float
    end: float
    text: str
    tokens: list[int]
    temperature: float
    avg_logprob: float
    compression_ratio: float
    no_speech_prob: float

class StorageFile(NullableBaseModel):
    size: int | None
    created_at: int | None
    expires_at: int | None
    filename: str | None
    id: str | None
    purpose: (
        Literal["assistants", "assistants_output", "batch", "batch_output", "fine-tune", "fine-tune-results", "vision"]
        | None
    )

class Image(NullableBaseModel):
    url: str | None
    revised_prompt: str | None
    b64_json: str | None

class Embedding(NullableBaseModel):
    object: str
    embedding: list[float]
    index: int

class TeamApiKey(NullableBaseModel):
    api_key: str
    id: str
    name: str
    created_at: str | None
    updated_at: str | None

class AudioData(typing.TypedDict):
    id: str
    expires_at: int
    data: str
    transcript: str

class ChatMessageData(typing.TypedDict):
    role: typing.NotRequired[Literal["system", "user", "assistant", "tool", "function", "developer"] | None]
    refusal: typing.NotRequired[str | None]
    tool_calls: typing.NotRequired[list[ToolCall] | None]
    content: typing.NotRequired[str | None]
    audio: typing.NotRequired[AudioData | None]
    annotations: typing.NotRequired[list[Annotation] | None]
    name: typing.NotRequired[str | None]

class PredictionTypeData(typing.TypedDict):
    type: str
    content: typing.NotRequired[str | None]

class AudioConfigurationData(typing.TypedDict):
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    format: Literal["mp3", "opus", "flac", "wav", "pcm16"]

class ChatChoiceData(typing.TypedDict):
    index: int
    message: ChatMessageData
    finish_reason: str
    logprobs: typing.NotRequired[LogProbsInfo | None]

class TranscriptionWordData(typing.TypedDict):
    word: str
    start: float
    end: float

class TranscriptionSegmentData(typing.TypedDict):
    id: int
    seek: int
    start: float
    end: float
    text: str
    tokens: list[int]
    temperature: float
    avg_logprob: float
    compression_ratio: float
    no_speech_prob: float

class StorageFileData(typing.TypedDict):
    size: typing.NotRequired[int | None]
    created_at: typing.NotRequired[int | None]
    expires_at: typing.NotRequired[int | None]
    filename: typing.NotRequired[str | None]
    id: typing.NotRequired[str | None]
    purpose: typing.NotRequired[
        Literal["assistants", "assistants_output", "batch", "batch_output", "fine-tune", "fine-tune-results", "vision"]
        | None
    ]

class ImageData(typing.TypedDict):
    url: typing.NotRequired[str | None]
    revised_prompt: typing.NotRequired[str | None]
    b64_json: typing.NotRequired[str | None]

class EmbeddingData(typing.TypedDict):
    object: str
    embedding: list[float]
    index: int

class TeamApiKeyData(typing.TypedDict):
    api_key: str
    id: str
    name: str
    created_at: typing.NotRequired[str | None]
    updated_at: typing.NotRequired[str | None]
