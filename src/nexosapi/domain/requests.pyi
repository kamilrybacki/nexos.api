from __future__ import annotations
import typing
import typing
from nexosapi.domain.data import (
    AudioConfiguration as AudioConfiguration,
    ChatMessage as ChatMessage,
    PredictionType as PredictionType,
)
from nexosapi.domain.metadata import ChatThinkingModeConfiguration as ChatThinkingModeConfiguration
from pydantic import BaseModel

class NexosAPIRequest(BaseModel):
    """
    Base class for all API requests to the NEXOS API.
    This class serves as a foundation for defining specific API request models.
    It can be extended to create more specific request models for different API endpoints.
    """

class ChatCompletionsRequest(NexosAPIRequest):
    model: str
    messages: list[ChatMessage]
    store: bool | None
    metadata: dict[str, str] | None
    frequency_penalty: float
    logit_bias: dict[str, float] | None
    logprobs: bool | None
    top_logprobs: int | None
    max_completion_tokens: int | None
    n: int
    modalities: list[typing.Literal["text", "audio"]]
    prediction: PredictionType | None
    presence_penalty: float
    audio: AudioConfiguration | None
    response_format: dict[str, typing.Any] | None
    seed: int | None
    service_tier: typing.Literal["auto", "default"]
    stop: str | list[str] | None
    stream: bool | None
    stream_options: dict[str, typing.Any] | None
    temperature: float
    top_p: float
    tools: list[dict[str, typing.Any]] | None
    tool_choice: str | dict[str, typing.Any] | None
    parallel_tool_calls: bool | None
    thinking: ChatThinkingModeConfiguration | None

class AudioSpeechRequest(NexosAPIRequest):
    model: str
    input: str
    voice: typing.Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    response_format: typing.Literal["mp3", "opus", "aac", "flac", "wav", "pcm"]
    speed: float

class AudioTranscriptionRequest(NexosAPIRequest):
    model: str
    file: bytes
    language: str | None
    prompt: str | None
    response_format: typing.Literal["json", "text", "srt", "verbose_json", "vtt"]
    temperature: float
    timestamp_granularities: list[typing.Literal["word", "segment"]]

class AudioTranslationRequest(NexosAPIRequest):
    model: str
    file: bytes
    prompt: str | None
    response_format: typing.Literal["json", "text", "srt", "verbose_json", "vtt"]
    temperature: float

class ImageGenerationRequest(NexosAPIRequest):
    prompt: str
    model: str
    n: int
    quality: typing.Literal["standard", "hd"]
    response_format: typing.Literal["url", "b64_json"]
    size: typing.Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]
    style: typing.Literal["vivid", "natural"]

class ImageEditRequest(NexosAPIRequest):
    model: str
    image: bytes
    prompt: str
    n: int
    response_format: typing.Literal["url", "b64_json"]
    size: typing.Literal["256x256", "512x512", "1024x1024"]

class ImageVariationRequest(NexosAPIRequest):
    image: bytes
    model: str
    n: int
    response_format: typing.Literal["url", "b64_json"]
    size: typing.Literal["256x256", "512x512", "1024x1024"]

class EmbeddingRequest(NexosAPIRequest):
    model: str
    input: str | list[str] | list[int] | list[list[int]] | None
    encoding_format: typing.Literal["float", "base64"]
    dimensions: int

class StorageUploadRequest(NexosAPIRequest):
    file: str | bytes | list[bytes]
    purpose: typing.Literal["assistants", "batch", "fine-tune", "vision", "user_data", "evals"]

class StorageListRequest(NexosAPIRequest):
    after: str | None
    limit: int
    order: typing.Literal["asc", "desc"]
    purpose: typing.Literal["assistants", "batch", "fine-tune", "vision", "user_data", "evals"] | None

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

class NexosAPIRequestData(typing.TypedDict):
    pass

class ChatCompletionsRequestData(typing.TypedDict):
    model: str
    messages: list[ChatMessage]
    store: typing.NotRequired[bool | None]
    metadata: typing.NotRequired[dict[str, str] | None]
    frequency_penalty: float
    logit_bias: typing.NotRequired[dict[str, float] | None]
    logprobs: typing.NotRequired[bool | None]
    top_logprobs: typing.NotRequired[int | None]
    max_completion_tokens: typing.NotRequired[int | None]
    n: int
    modalities: list[typing.Literal["text", "audio"]]
    prediction: typing.NotRequired[PredictionType | None]
    presence_penalty: float
    audio: typing.NotRequired[AudioConfiguration | None]
    response_format: typing.NotRequired[dict[str, typing.Any] | None]
    seed: typing.NotRequired[int | None]
    service_tier: typing.Literal["auto", "default"]
    stop: typing.NotRequired[str | list[str] | None]
    stream: typing.NotRequired[bool | None]
    stream_options: typing.NotRequired[dict[str, typing.Any] | None]
    temperature: float
    top_p: float
    tools: typing.NotRequired[list[dict[str, typing.Any]] | None]
    tool_choice: typing.NotRequired[str | dict[str, typing.Any] | None]
    parallel_tool_calls: typing.NotRequired[bool | None]
    thinking: typing.NotRequired[ChatThinkingModeConfiguration | None]

class AudioSpeechRequestData(typing.TypedDict):
    model: str
    input: str
    voice: typing.Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    response_format: typing.Literal["mp3", "opus", "aac", "flac", "wav", "pcm"]
    speed: float

class AudioTranscriptionRequestData(typing.TypedDict):
    model: str
    file: bytes
    language: typing.NotRequired[str | None]
    prompt: typing.NotRequired[str | None]
    response_format: typing.Literal["json", "text", "srt", "verbose_json", "vtt"]
    temperature: float
    timestamp_granularities: list[typing.Literal["word", "segment"]]

class AudioTranslationRequestData(typing.TypedDict):
    model: str
    file: bytes
    prompt: typing.NotRequired[str | None]
    response_format: typing.Literal["json", "text", "srt", "verbose_json", "vtt"]
    temperature: float

class ImageGenerationRequestData(typing.TypedDict):
    prompt: str
    model: str
    n: int
    quality: typing.Literal["standard", "hd"]
    response_format: typing.Literal["url", "b64_json"]
    size: typing.Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]
    style: typing.Literal["vivid", "natural"]

class ImageEditRequestData(typing.TypedDict):
    model: str
    image: bytes
    prompt: str
    n: int
    response_format: typing.Literal["url", "b64_json"]
    size: typing.Literal["256x256", "512x512", "1024x1024"]

class ImageVariationRequestData(typing.TypedDict):
    image: bytes
    model: str
    n: int
    response_format: typing.Literal["url", "b64_json"]
    size: typing.Literal["256x256", "512x512", "1024x1024"]

class EmbeddingRequestData(typing.TypedDict):
    model: str
    input: typing.NotRequired[str | list[str] | list[int] | list[list[int]] | None]
    encoding_format: typing.Literal["float", "base64"]
    dimensions: int

class StorageUploadRequestData(typing.TypedDict):
    file: str | bytes | list[bytes]
    purpose: typing.Literal["assistants", "batch", "fine-tune", "vision", "user_data", "evals"]

class StorageListRequestData(typing.TypedDict):
    after: typing.NotRequired[str | None]
    limit: int
    order: typing.Literal["asc", "desc"]
    purpose: typing.NotRequired[
        typing.Literal["assistants", "batch", "fine-tune", "vision", "user_data", "evals"] | None
    ]

class StorageDownloadRequestData(typing.TypedDict):
    pass

class StorageGetRequestData(typing.TypedDict):
    pass

class StorageDeleteRequestData(typing.TypedDict):
    pass

class TeamApiKeyCreateRequestData(typing.TypedDict):
    name: str

class TeamApiKeyUpdateRequestData(typing.TypedDict):
    name: str

class TeamApiKeyDeleteRequestData(typing.TypedDict):
    pass

class TeamApiKeyRegenerateRequestData(typing.TypedDict):
    pass

class ModelsListRequestData(typing.TypedDict):
    pass
