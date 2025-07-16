from typing import Literal

from pydantic import BaseModel

from nexos.domain.metadata import Annotation, FunctionCall, LogProbsInfo, ToolCall


class Audio(BaseModel):
    id: str
    expires_at: int
    data: str
    transcript: str


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool", "function", "developer"]
    refusal: str
    tool_calls: list[ToolCall]
    content: str
    function_call: FunctionCall
    audio: Audio
    annotations: list[Annotation]


class ChatChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str
    logprobs: LogProbsInfo


class TranscriptionWord(BaseModel):
    word: str
    start: float
    end: float


class TranscriptionSegment(BaseModel):
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


class StorageFile(BaseModel):
    size: int
    created_at: int
    expires_at: int | None
    filename: str
    id: str
    purpose: Literal[
        "assistants", "assistants_output", "batch", "batch_output", "fine-tune", "fine-tune-results", "vision"
    ]


class Image(BaseModel):
    url: str | None
    revised_prompt: str | None
    b64_json: str | None


class Embedding(BaseModel):
    object: str
    embedding: list[float]
    index: int


class TeamApiKey(BaseModel):
    api_key: str
    id: str
    name: str
    created_at: str | None
    updated_at: str | None
