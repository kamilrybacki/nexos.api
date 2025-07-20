from typing import Any, Literal

from pydantic import BaseModel, conint, constr

from nexosapi.domain.data import ChatMessage


class NexosAPIRequest(BaseModel):
    """
    Base class for all API requests to the NEXOS API.
    This class serves as a foundation for defining specific API request models.
    It can be extended to create more specific request models for different API endpoints.
    """


class ChatCompletionsRequest(NexosAPIRequest):
    model: str
    messages: list[ChatMessage]
    store: bool | None = False
    metadata: dict[str, str] | None = None
    frequency_penalty: float | None = 0
    logit_bias: dict[str, float] | None = None
    logprobs: bool | None = False
    top_logprobs: conint(ge=0, le=20) | None = None
    max_tokens: int | None = None
    max_completion_tokens: int | None = None
    n: conint(ge=1, le=128) | None = 1
    modalities: list[Literal["text", "audio"]] | None = ["text"]
    presence_penalty: float | None = 0
    response_format: dict[str, Any] | None = None
    seed: int | None = None
    service_tier: Literal["auto", "default"] | None = "auto"
    stop: str | list[str] | None = None
    stream: bool | None = False
    stream_options: dict[str, Any] | None = None
    temperature: float | None = 1
    top_p: float | None = 1
    tools: list[dict[str, Any]] | None = None
    tool_choice: str | dict[str, Any] | None = "none"
    parallel_tool_calls: bool | None = True
    function_call: str | dict[str, Any] | None = "none"
    functions: list[dict[str, Any]] | None = None
    thinking: dict[str, Any] | None = None


class EmbeddingRequest(NexosAPIRequest):
    model: str
    input: str | list[str] | list[int] | list[list[int]]
    encoding_format: Literal["float", "base64"] | None = "float"
    dimensions: int | None = None


class AudioSpeechRequest(NexosAPIRequest):
    model: str
    input: constr(max_length=4096)
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] | None = "mp3"
    speed: float | None = 1


class AudioTranscriptionRequest(NexosAPIRequest):
    model: str
    language: str | None = None
    prompt: str | None = None
    response_format: Literal["json", "text", "srt", "verbose_json", "vtt"] | None = "json"
    temperature: float | None = 0
    timestamp_granularities: list[Literal["word", "segment"]] | None = ["segment"]


class AudioTranslationRequest(NexosAPIRequest):
    model: str
    prompt: str | None = None
    response_format: Literal["json", "text", "srt", "verbose_json", "vtt"] | None = "json"
    temperature: float | None = 0


class ImageGenerationRequest(NexosAPIRequest):
    prompt: str
    model: str
    n: int | None = 1
    quality: Literal["standard", "hd"] | None = "standard"
    response_format: Literal["url", "b64_json"] | None = "url"
    size: Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"] | None = "256x256"
    style: Literal["vivid", "natural"] | None = "vivid"


class ImageEditRequest(NexosAPIRequest):
    prompt: constr(max_length=1000)
    model: str
    n: int | None = 1
    response_format: Literal["url", "b64_json"] | None = "url"
    size: Literal["256x256", "512x512", "1024x1024"] | None = "256x256"


class ImageVariationRequest(NexosAPIRequest):
    model: str
    n: int | None = 1
    response_format: Literal["url", "b64_json"] | None = "url"
    size: Literal["256x256", "512x512", "1024x1024"] | None = "256x256"


class StorageUploadRequest(NexosAPIRequest):
    file: str | bytes | list[bytes]
    purpose: Literal["assistants", "batch", "fine-tune", "vision", "user_data", "evals"]


class StoragelistRequest(NexosAPIRequest):
    after: str | None = None
    limit: conint(ge=1, le=10000) | None = 10000
    order: Literal["asc", "desc"] | None = "desc"
    purpose: Literal["assistants", "batch", "fine-tune", "vision", "user_data", "evals"] | None = None


class StorageDownloadRequest(NexosAPIRequest):
    """
    Request to download a file from storage.
    """


class StorageGetRequest(NexosAPIRequest):
    """
    Request to get metadata of a file from storage.
    """


class StorageDeleteRequest(NexosAPIRequest):
    """
    Request to delete a file from storage.
    """


class TeamApiKeyCreateRequest(NexosAPIRequest):
    """
    Request to create a new API key for a team.
    """

    name: str


class TeamApiKeyUpdateRequest(NexosAPIRequest):
    """
    Request to update an existing API key for a team.
    """

    name: str


class TeamApiKeyDeleteRequest(NexosAPIRequest):
    """
    Request to delete an API key for a team.
    """


class TeamApiKeyRegenerateRequest(NexosAPIRequest):
    """
    Request to regenerate an API key for a team.
    This request does not require any additional parameters.
    It simply triggers the regeneration of the API key.
    """


class ModelslistRequest(NexosAPIRequest):
    """
    Request to list available models.
    """


class MockRequestModel(NexosAPIRequest):
    """For testing purposes."""

    key: str
    value: str
