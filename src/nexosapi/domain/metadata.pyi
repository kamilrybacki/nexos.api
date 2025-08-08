from __future__ import annotations
import typing
import typing
from collections.abc import Callable as Callable
from enum import StrEnum
from nexosapi.common.exceptions import InvalidWebSearchMCPSettingsError as InvalidWebSearchMCPSettingsError
from nexosapi.domain.base import NullableBaseModel as NullableBaseModel
from pydantic.main import IncEx as IncEx
from typing import Any, Literal

class Model(NullableBaseModel):
    id: str
    object: str
    created: int
    owned_by: str
    name: str
    timeout_ms: int | None
    stream_timeout_ms: int | None

class ChatThinkingModeConfiguration(typing.TypedDict, total=False):
    type: str
    budget_tokens: int

class FunctionCall(NullableBaseModel):
    name: str
    arguments: str

class ToolChoiceFunction(typing.TypedDict, total=False):
    name: str

class ToolChoiceAsDictionary(NullableBaseModel):
    type: str
    function: ToolChoiceFunction

    @classmethod
    def force_type_as_function(cls, _: str) -> str: ...

class ToolType(StrEnum):
    WEB_SEARCH = "web_search"
    RAG = "rag"
    OCR = "tika_ocr"

class ToolCall(NullableBaseModel):
    id: str
    type: str
    function: FunctionCall

class FunctionToolDefinition(typing.TypedDict, total=False):
    """
    Represents a function tool definition for use in chat completions.

    :ivar name: The name of the tool.
    :ivar description: A description of the tool, if any.
    :ivar parameters: Additional parameters for the tool, if any.
    :ivar strict: Whether the tool should be used strictly or not.
    """

    name: str
    description: str | None
    parameters: dict[str, typing.Any] | None
    strict: bool | None

class ToolModule(typing.TypedDict, total=False):
    type: str
    options: dict[str, typing.Any]

class WebSearchUserLocation(NullableBaseModel):
    type: typing.Literal["approximate"]
    city: str | None
    country: str | None
    region: str | None
    timezone: str | None

class WebSearchToolMCP(NullableBaseModel):
    type: typing.Literal["url", "query"]
    tool: typing.Literal["google_search", "bing_search", "amazon_search", "universal"]
    query: str | None
    url: str | None
    geo_location: str | None
    parse: bool | None

    def check_if_data_matches_search_type(self) -> WebSearchToolMCP: ...
    def model_dump(
        self,
        *,
        mode: Literal["json", "python"] = "python",
        include: IncEx | None = None,
        exclude: IncEx | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool | Literal["none", "warn", "error"] = True,
        fallback: Callable[[Any], Any] | None = None,
        serialize_as_any: bool = False,
    ) -> dict[str, Any]: ...

class WebSearchToolOptions(NullableBaseModel):
    search_context_size: typing.Literal["low", "medium", "high"] | None
    user_location: WebSearchUserLocation | None
    mcp: WebSearchToolMCP | None

    def model_dump(
        self,
        *,
        mode: Literal["json", "python"] = "python",
        include: IncEx | None = None,
        exclude: IncEx | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool | Literal["none", "warn", "error"] = True,
        fallback: Callable[[Any], Any] | None = None,
        serialize_as_any: bool = False,
    ) -> dict[str, Any]: ...

class RAGToolOptions(NullableBaseModel):
    collection_uuid: str
    query: str | None
    threshold: float | None
    top_n: int | None
    model_uuid: str | None

class OCRToolOptions(NullableBaseModel):
    file_id: str

class UrlCitation(NullableBaseModel):
    end_index: int
    start_index: int
    title: str
    url: str

class Annotation(NullableBaseModel):
    type: str
    url_citation: UrlCitation

class CompletionTokenDetails(NullableBaseModel):
    accepted_prediction_tokens: int
    rejected_prediction_tokens: int
    audio_tokens: int
    reasoning_tokens: int

class PromptTokenDetails(NullableBaseModel):
    audio_tokens: int
    cached_tokens: int

class UsageInfo(NullableBaseModel):
    total_tokens: int
    prompt_tokens: int | None
    completion_tokens: int | None
    completion_token_details: CompletionTokenDetails | None
    prompt_token_details: PromptTokenDetails | None

class LogProb:
    token: str
    logprob: float
    bytes: list[int]

class LogProbs(LogProb):
    top_logprobs: list[LogProb]

class LogProbsInfo(NullableBaseModel):
    model_config: typing.ClassVar[dict[str, typing.Any]]
    content: LogProbs | None
    refusal: LogProbs | None

class ModelData(typing.TypedDict):
    id: str
    object: str
    created: int
    owned_by: str
    name: str
    timeout_ms: typing.NotRequired[int | None]
    stream_timeout_ms: typing.NotRequired[int | None]

class FunctionCallData(typing.TypedDict):
    name: str
    arguments: str

class ToolChoiceAsDictionaryData(typing.TypedDict):
    type: str
    function: ToolChoiceFunction

class ToolCallData(typing.TypedDict):
    id: str
    type: str
    function: FunctionCallData

class WebSearchUserLocationData(typing.TypedDict):
    type: typing.Literal["approximate"]
    city: typing.NotRequired[str | None]
    country: typing.NotRequired[str | None]
    region: typing.NotRequired[str | None]
    timezone: typing.NotRequired[str | None]

class WebSearchToolMCPData(typing.TypedDict):
    type: typing.Literal["url", "query"]
    tool: typing.Literal["google_search", "bing_search", "amazon_search", "universal"]
    query: typing.NotRequired[str | None]
    url: typing.NotRequired[str | None]
    geo_location: typing.NotRequired[str | None]
    parse: typing.NotRequired[bool | None]

class WebSearchToolOptionsData(typing.TypedDict):
    search_context_size: typing.NotRequired[typing.Literal["low", "medium", "high"] | None]
    user_location: typing.NotRequired[WebSearchUserLocationData | None]
    mcp: typing.NotRequired[WebSearchToolMCPData | None]

class RAGToolOptionsData(typing.TypedDict):
    collection_uuid: str
    query: typing.NotRequired[str | None]
    threshold: typing.NotRequired[float | None]
    top_n: typing.NotRequired[int | None]
    model_uuid: typing.NotRequired[str | None]

class OCRToolOptionsData(typing.TypedDict):
    file_id: str

class UrlCitationData(typing.TypedDict):
    end_index: int
    start_index: int
    title: str
    url: str

class AnnotationData(typing.TypedDict):
    type: str
    url_citation: UrlCitationData

class CompletionTokenDetailsData(typing.TypedDict):
    accepted_prediction_tokens: int
    rejected_prediction_tokens: int
    audio_tokens: int
    reasoning_tokens: int

class PromptTokenDetailsData(typing.TypedDict):
    audio_tokens: int
    cached_tokens: int

class UsageInfoData(typing.TypedDict):
    total_tokens: int
    prompt_tokens: typing.NotRequired[int | None]
    completion_tokens: typing.NotRequired[int | None]
    completion_token_details: typing.NotRequired[CompletionTokenDetailsData | None]
    prompt_token_details: typing.NotRequired[PromptTokenDetailsData | None]

class LogProbsInfoData(typing.TypedDict):
    model_config: typing.ClassVar[dict[str, typing.Any]]
    content: typing.NotRequired[LogProbs | None]
    refusal: typing.NotRequired[LogProbs | None]
