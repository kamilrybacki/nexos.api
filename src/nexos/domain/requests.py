from typing import Any, ClassVar, Literal

from pydantic import BaseModel, conint, constr

from nexos.domain.data import ChatMessage


class NexosAPIRequest(BaseModel):
    """
    Base class for all API requests to the NEXOS API.
    This class serves as a foundation for defining specific API request models.
    It can be extended to create more specific request models for different API endpoints.

    :cvar: _endpoint: The path of the API endpoint.
    """

    _endpoint: ClassVar[str]

    @classmethod
    def _validate_endpoint(cls, endpoint: str) -> None:
        """
        Validates the endpoint format.
        Raises ValueError if the endpoint does not match the expected format.

        :param endpoint: The API endpoint to validate.
        """
        verbs = ("get:", "post:", "put:", "delete:", "patch:")
        if not isinstance(endpoint, str) or not endpoint.startswith(verbs):
            raise ValueError(f"Invalid endpoint format: {endpoint}. Must start with one of {verbs}.")

    def __init_subclass__(cls, **kwargs: Any) -> None:
        if cls._endpoint is None or not isinstance(cls._endpoint, str):
            raise ValueError("Subclasses of NexosAPIRequest must define a valid '_endpoint' class variable.")
        cls._validate_endpoint(cls._endpoint)


class ChatCompletionsRequest(NexosAPIRequest):
    _endpoint = "post:/v1/chat/completions"

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
    _endpoint = "post:/v1/embeddings"

    model: str
    input: str | list[str] | list[int] | list[list[int]]
    encoding_format: Literal["float", "base64"] | None = "float"
    dimensions: int | None = None


class AudioSpeechRequest(NexosAPIRequest):
    _endpoint = "post:/v1/audio/speech"

    model: str
    input: constr(max_length=4096)
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] | None = "mp3"
    speed: float | None = 1


class AudioTranscriptionRequest(NexosAPIRequest):
    _endpoint = "post:/v1/audio/transcriptions"

    model: str
    language: str | None = None
    prompt: str | None = None
    response_format: Literal["json", "text", "srt", "verbose_json", "vtt"] | None = "json"
    temperature: float | None = 0
    timestamp_granularities: list[Literal["word", "segment"]] | None = ["segment"]


class AudioTranslationRequest(NexosAPIRequest):
    _endpoint = "post:/v1/audio/translations"

    model: str
    prompt: str | None = None
    response_format: Literal["json", "text", "srt", "verbose_json", "vtt"] | None = "json"
    temperature: float | None = 0


class ImageGenerationRequest(NexosAPIRequest):
    _endpoint = "post:/v1/images/generations"

    prompt: str
    model: str
    n: int | None = 1
    quality: Literal["standard", "hd"] | None = "standard"
    response_format: Literal["url", "b64_json"] | None = "url"
    size: Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"] | None = "256x256"
    style: Literal["vivid", "natural"] | None = "vivid"


class ImageEditRequest(NexosAPIRequest):
    _endpoint = "post:/v1/images/edits"

    prompt: constr(max_length=1000)
    model: str
    n: int | None = 1
    response_format: Literal["url", "b64_json"] | None = "url"
    size: Literal["256x256", "512x512", "1024x1024"] | None = "256x256"


class ImageVariationRequest(NexosAPIRequest):
    _endpoint = "post:/v1/images/variations"

    model: str
    n: int | None = 1
    response_format: Literal["url", "b64_json"] | None = "url"
    size: Literal["256x256", "512x512", "1024x1024"] | None = "256x256"


class StorageUploadRequest(NexosAPIRequest):
    _endpoint = "post:/v1/storage"

    file: str | bytes | list[bytes]
    purpose: Literal["assistants", "batch", "fine-tune", "vision", "user_data", "evals"]


class StoragelistRequest(NexosAPIRequest):
    _endpoint = "get:/v1/storage"

    after: str | None = None
    limit: conint(ge=1, le=10000) | None = 10000
    order: Literal["asc", "desc"] | None = "desc"
    purpose: Literal["assistants", "batch", "fine-tune", "vision", "user_data", "evals"] | None = None


class StorageDownloadRequest(NexosAPIRequest):
    _endpoint = "get:/v1/storage/{file_id}/content"


class StorageGetRequest(NexosAPIRequest):
    _endpoint = "get:/v1/storage/{file_id}"


class StorageDeleteRequest(NexosAPIRequest):
    _endpoint = "delete:/v1/storage/{file_id}"


class TeamApiKeyCreateRequest(NexosAPIRequest):
    _endpoint = "post:/v1/teams/{team_id}/api_keys"

    name: str


class TeamApiKeyUpdateRequest(NexosAPIRequest):
    _endpoint = "patch:/v1/teams/{team_id}/api_keys/{api_key_id}"

    name: str


class TeamApiKeyDeleteRequest(NexosAPIRequest):
    _endpoint = "delete:/v1/teams/{team_id}/api_keys/{api_key_id}"


class TeamApiKeyRegenerateRequest(NexosAPIRequest):
    _endpoint = "post:/v1/teams/{team_id}/api_keys/{api_key_id}/regenerate"


class ModelslistRequest(NexosAPIRequest):
    _endpoint = "get:/v1/models"
