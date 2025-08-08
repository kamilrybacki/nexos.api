import typing

import pydantic
from pydantic import BaseModel

from nexosapi.domain.data import AudioConfiguration, ChatMessage, PredictionType
from nexosapi.domain.metadata import ChatThinkingModeConfiguration


class NexosAPIRequest(BaseModel):
    """
    Base class for all API requests to the NEXOS API.
    This class serves as a foundation for defining specific API request models.
    It can be extended to create more specific request models for different API endpoints.
    """


class ChatCompletionsRequest(NexosAPIRequest):
    model: str
    messages: list[ChatMessage] = pydantic.Field(min_length=1)
    store: bool | None = None
    metadata: dict[str, str] | None = None
    frequency_penalty: float = 0.0
    logit_bias: dict[str, float] | None = None
    logprobs: bool | None = None
    top_logprobs: int | None = pydantic.Field(ge=0, le=20, default=None)
    max_completion_tokens: int | None = None
    n: int = pydantic.Field(ge=1, le=128, default=1)
    modalities: list[typing.Literal["text", "audio"]] = ["text"]
    prediction: PredictionType | None = None
    presence_penalty: float = 0.0
    audio: AudioConfiguration | None = None
    response_format: dict[str, typing.Any] | None = None
    seed: int | None = pydantic.Field(ge=-9223372036854776000, le=9223372036854776000, default=None)
    service_tier: typing.Literal["auto", "default"] = "auto"
    stop: str | list[str] | None = None
    stream: bool | None = None
    stream_options: dict[str, typing.Any] | None = None
    temperature: float = 1.0
    top_p: float = 1.0
    tools: list[dict[str, typing.Any]] | None = None
    tool_choice: str | dict[str, typing.Any] | None = None
    parallel_tool_calls: bool | None = None
    thinking: ChatThinkingModeConfiguration | None = None


class AudioSpeechRequest(NexosAPIRequest):
    model: str
    input: str = pydantic.Field(max_length=4096)
    voice: typing.Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    response_format: typing.Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] = "mp3"
    speed: float = 1.0


class AudioTranscriptionRequest(NexosAPIRequest):
    model: str
    file: bytes
    language: str | None = None
    prompt: str | None = None
    response_format: typing.Literal["json", "text", "srt", "verbose_json", "vtt"] = "json"
    temperature: float = 0.0
    timestamp_granularities: list[typing.Literal["word", "segment"]] = ["segment"]


class AudioTranslationRequest(NexosAPIRequest):
    model: str
    file: bytes
    prompt: str | None = None
    response_format: typing.Literal["json", "text", "srt", "verbose_json", "vtt"] = "json"
    temperature: float = 0.0


class ImageGenerationRequest(NexosAPIRequest):
    prompt: str
    model: str
    n: int = 1
    quality: typing.Literal["standard", "hd"] = "standard"
    response_format: typing.Literal["url", "b64_json"] = "url"
    size: typing.Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"] = "256x256"
    style: typing.Literal["vivid", "natural"] = "vivid"


class ImageEditRequest(NexosAPIRequest):
    model: str
    image: bytes
    prompt: str = pydantic.Field(max_length=1000)
    n: int = 1
    response_format: typing.Literal["url", "b64_json"] = "url"
    size: typing.Literal["256x256", "512x512", "1024x1024"] = "256x256"


class ImageVariationRequest(NexosAPIRequest):
    image: bytes
    model: str
    n: int = 1
    response_format: typing.Literal["url", "b64_json"] = "url"
    size: typing.Literal["256x256", "512x512", "1024x1024"] = "256x256"


class EmbeddingRequest(NexosAPIRequest):
    model: str
    input: str | list[str] | list[int] | list[list[int]] | None = None
    encoding_format: typing.Literal["float", "base64"] = "float"
    dimensions: int


class StorageUploadRequest(NexosAPIRequest):
    file: str | bytes | list[bytes]
    purpose: typing.Literal["assistants", "batch", "fine-tune", "vision", "user_data", "evals"]


class StorageListRequest(NexosAPIRequest):
    after: str | None = None
    limit: int = pydantic.Field(ge=0, le=10000, default=10000)
    order: typing.Literal["asc", "desc"] = "desc"
    purpose: typing.Literal["assistants", "batch", "fine-tune", "vision", "user_data", "evals"] | None = None


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


class ModelsListRequest(NexosAPIRequest):
    """
    Request to list available models.
    """
