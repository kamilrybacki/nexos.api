import typing

import pydantic

from nexosapi.domain.base import NullableBaseModel
from nexosapi.domain.data import AudioConfiguration, ChatMessage, PredictionType
from nexosapi.domain.metadata import ChatThinkingModeConfiguration


class NexosAPIRequest(NullableBaseModel):
    """
    Base class for all API requests to the NEXOS API.
    This class serves as a foundation for defining specific API request models.
    It can be extended to create more specific request models for different API endpoints.
    """


class ChatCompletionsRequest(NexosAPIRequest):
    """
    Request model for the Nexos.ai Chat Completions API.

    Use this model to serialize the HTTP request body for the chat completions
    endpoint. Fields mirror the public API and include validation where applicable.

    :ivar model: The model ID to use for this completion (e.g., "6948fe4d-98ce-4f36-bc49-5f652cc07b65").
    :ivar messages: The ordered conversation so far (min length: 1). Depending on the
        model, different message modalities are supported (e.g., text, images, audio).
        Common roles include:
        - Developer/System: instructions the model should follow. With o1 models and
            newer, prefer a developer message instead of system.
        - User: end-user prompts or context.
        - Assistant: prior model responses.
        - Tool / Function: tool results routed back to the model.
    :ivar store: Whether to store the output of this request.
    :ivar metadata: Developer-defined tags and values used for filtering completions in
        the dashboard.
    :ivar frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new
        tokens based on their existing frequency in the text so far, decreasing the
        likelihood of verbatim repetition. Default: 0.
    :ivar logit_bias: Per-token bias added to the model's logits. Keys are tokenizer
        token IDs (as strings) and values are in [-100, 100]. Small magnitudes tweak
        likelihood; large magnitudes can effectively ban or force tokens.
    :ivar logprobs: Whether to return log probabilities of the output tokens. If true,
        returns log probabilities for each output token in the message content.
    :ivar top_logprobs: The number of most likely tokens to return at each token
        position, each with an associated log probability. Range: [0, 20].
        Requires ``logprobs == True``. Default: None.
    :ivar max_completion_tokens: Upper bound for the number of tokens that can be
        generated for a completion, including visible output tokens and reasoning tokens.
    :ivar n: How many chat completion choices to generate for each input message.
        Range: [1, 128]. Costs scale with the number of generated tokens across
        all choices. Default: 1.
    :ivar modalities: Output types to generate. Most models support ["text"](default).
        To request both text and audio: ["text", "audio"].
    :ivar prediction: Configuration for a Predicted Output, which can improve response
        times when large parts of the response are known ahead of time (e.g., static content).
    :ivar presence_penalty: Number between -2.0 and 2.0. Positive values penalize tokens
        that already appeared, nudging the model toward new topics. Default: 0.
    :ivar audio: Parameters for audio output. Required when ``modalities`` includes "audio".
    :ivar response_format: Constrains the output format. Supported values include:
        - {"type": "text"}
        - {"type": "json_object"}
        - {"type": "json_schema", "json_schema": {...}}  (Structured Outputs)
        When using {"type": "json_object"}, also instruct the model (via messages) to
        produce JSON; otherwise it may stream whitespace until the token limit. Note:
        message content may be truncated if ``finish_reason="length"``.
    :ivar seed: Best-effort deterministic sampling seed. Range:
        [-9223372036854776000, 9223372036854776000]. Determinism is not guaranteed;
        monitor changes via ``system_fingerprint``.
    :ivar service_tier: Latency tier selection.
        - "auto": Uses scale tier if enabled; otherwise default tier.
        - "default": Uses the default tier (lower uptime SLA, no latency guarantee).
        The response may include the service tier utilized. Default: "auto".
    :ivar stop: Up to 4 stop sequences at which token generation will halt.
    :ivar stream: If true, sends partial message deltas as server-sent events (SSE).
        The stream terminates with: ``data: [DONE]``.
    :ivar stream_options: Options for streaming responses. Only set when ``stream == True``.
    :ivar temperature: Sampling temperature in [0, 2]. Higher values increase randomness;
        lower values increase determinism. Default: 1. Generally tune either
        ``temperature`` or ``top_p``, not both.
    :ivar top_p: Nucleus sampling probability mass in (0, 1]. For example, 0.1 considers
        only the tokens comprising the top 10% probability mass. Default: 1. Generally
        tune either ``top_p`` or ``temperature``, not both.
    :ivar tools: A list of tools the model may call (max 128). Supported tool types:
        "function", "web_search", "rag", "tika_ocr". Provide tool-specific payloads
        under their respective keys.
    :ivar tool_choice: Controls tool invocation.
        - "none": do not call tools (generate a message instead)
        - "auto": model may choose to generate a message or call tools
        - "required": model must call one or more tools
        - Object to force a specific tool, e.g.
            {"type": "function", "function": {"name": "my_function"}}
        Defaults: "none" if no tools; "auto" if tools are present.
    :ivar parallel_tool_calls: Whether to enable parallel function calling during tool use.
        API default: true.
    :ivar thinking: Reasoning/thinking configuration.
        Common fields:
        - type (e.g., "enabled")
        - budget_tokens (e.g., 1024)

    Notes
    -----

    - ``max_tokens`` is deprecated in favor of ``max_completion_tokens`` and is not
    compatible with o1-series models.
    - When requesting audio in ``modalities``, also provide a valid ``audio`` configuration.
    - ``top_logprobs`` requires ``logprobs == True``.
    - Costs scale with the number of generated tokens across all choices (``n``).
    """

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
    modalities: list[typing.Literal["text", "audio"]] = ["text"]  # noqa: RUF012
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
    timestamp_granularities: list[typing.Literal["word", "segment"]] = ["segment"]  # noqa: RUF012


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
