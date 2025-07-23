from nexosapi.domain.data import ChatMessage as ChatMessage
from pydantic import BaseModel
from typing import Any, Literal

class NexosAPIRequest(BaseModel): ...

class ChatCompletionsRequest(NexosAPIRequest):
    model: str
    messages: list[ChatMessage]
    store: bool | None
    metadata: dict[str, str] | None
    frequency_penalty: float | None
    logit_bias: dict[str, float] | None
    logprobs: bool | None
    top_logprobs: None
    max_tokens: int | None
    max_completion_tokens: int | None
    n: None
    modalities: list[Literal["text", "audio"]] | None
    presence_penalty: float | None
    response_format: dict[str, Any] | None
    seed: int | None
    service_tier: Literal["auto", "default"] | None
    stop: str | list[str] | None
    stream: bool | None
    stream_options: dict[str, Any] | None
    temperature: float | None
    top_p: float | None
    tools: list[dict[str, Any]] | None
    tool_choice: str | dict[str, Any] | None
    parallel_tool_calls: bool | None
    function_call: str | dict[str, Any] | None
    functions: list[dict[str, Any]] | None
    thinking: dict[str, Any] | None

class EmbeddingRequest(NexosAPIRequest):
    model: str
    input: str | list[str] | list[int] | list[list[int]]
    encoding_format: Literal["float", "base64"] | None
    dimensions: int | None

class AudioSpeechRequest(NexosAPIRequest):
    model: str
    input: None
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] | None
    speed: float | None

class AudioTranscriptionRequest(NexosAPIRequest):
    model: str
    language: str | None
    prompt: str | None
    response_format: Literal["json", "text", "srt", "verbose_json", "vtt"] | None
    temperature: float | None
    timestamp_granularities: list[Literal["word", "segment"]] | None

class AudioTranslationRequest(NexosAPIRequest):
    model: str
    prompt: str | None
    response_format: Literal["json", "text", "srt", "verbose_json", "vtt"] | None
    temperature: float | None

class ImageGenerationRequest(NexosAPIRequest):
    prompt: str
    model: str
    n: int | None
    quality: Literal["standard", "hd"] | None
    response_format: Literal["url", "b64_json"] | None
    size: Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"] | None
    style: Literal["vivid", "natural"] | None

class ImageEditRequest(NexosAPIRequest):
    prompt: None
    model: str
    n: int | None
    response_format: Literal["url", "b64_json"] | None
    size: Literal["256x256", "512x512", "1024x1024"] | None

class ImageVariationRequest(NexosAPIRequest):
    model: str
    n: int | None
    response_format: Literal["url", "b64_json"] | None
    size: Literal["256x256", "512x512", "1024x1024"] | None

class StorageUploadRequest(NexosAPIRequest):
    file: str | bytes | list[bytes]
    purpose: Literal["assistants", "batch", "fine-tune", "vision", "user_data", "evals"]

class StorageListRequest(NexosAPIRequest):
    after: str | None
    limit: None
    order: Literal["asc", "desc"] | None
    purpose: Literal["assistants", "batch", "fine-tune", "vision", "user_data", "evals"] | None

class StorageDownloadRequest(NexosAPIRequest): ...
class StorageGetRequest(NexosAPIRequest): ...
class StorageDeleteRequest(NexosAPIRequest): ...

class TeamApiKeyCreateRequest(NexosAPIRequest):
    name: str

class TeamApiKeyUpdateRequest(NexosAPIRequest):
    name: str

class TeamApiKeyDeleteRequest(NexosAPIRequest): ...
class TeamApiKeyRegenerateRequest(NexosAPIRequest): ...
class ModelsListRequest(NexosAPIRequest): ...
