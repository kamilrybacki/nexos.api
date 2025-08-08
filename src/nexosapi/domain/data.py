from typing import Literal

from nexosapi.domain.base import NullableBaseModel
from nexosapi.domain.metadata import Annotation, LogProbsInfo, ToolCall


class Audio(NullableBaseModel):
    id: str
    expires_at: int
    data: str
    transcript: str


class ChatMessage(NullableBaseModel):
    role: Literal["system", "user", "assistant", "tool", "function", "developer"] | None
    refusal: str | None = None
    tool_calls: list[ToolCall] | None = None
    content: str | None = None
    audio: Audio | None = None
    annotations: list[Annotation] | None = None
    name: str | None = None


class PredictionType(NullableBaseModel):
    type: str
    content: str | None = None


class AudioConfiguration(NullableBaseModel):
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    format: Literal["mp3", "opus", "flac", "wav", "pcm16"]


class ChatChoice(NullableBaseModel):
    index: int
    message: ChatMessage
    finish_reason: str
    logprobs: LogProbsInfo | None = None


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
    size: int | None = None
    created_at: int | None = None
    expires_at: int | None = None
    filename: str | None = None
    id: str | None = None
    purpose: (
        Literal["assistants", "assistants_output", "batch", "batch_output", "fine-tune", "fine-tune-results", "vision"]
        | None
    ) = None


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
    created_at: str | None = None
    updated_at: str | None = None
