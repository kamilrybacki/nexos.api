import typing
from collections.abc import Callable
from enum import StrEnum
from typing import Any, Literal

import pydantic
from pydantic import field_validator
from pydantic.main import IncEx

from nexosapi.common.exceptions import InvalidWebSearchMCPSettingsError
from nexosapi.domain.base import NullableBaseModel


class Model(NullableBaseModel):
    id: str
    object: str
    created: int
    owned_by: str
    name: str
    timeout_ms: int | None = pydantic.Field(ge=1, default=None)
    stream_timeout_ms: int | None = pydantic.Field(ge=1, default=None)


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

    @field_validator("type", mode="after")
    @classmethod
    def force_type_as_function(cls, _: str) -> str:
        return "function"


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
    """
    Represents the user's location for web search purposes.
    """

    type: typing.Literal["approximate"] = "approximate"
    city: str | None = None
    country: str | None = None
    region: str | None = None
    timezone: str | None = None


class WebSearchToolMCP(NullableBaseModel):
    """
    Represents the metadata configuration for a web search tool.
    """

    type: typing.Literal["url", "query"] = "query"
    tool: typing.Literal["google_search", "bing_search", "amazon_search", "universal"] = "google_search"
    query: str | None = None
    url: str | None = None
    geo_location: str | None = None
    parse: bool | None = False

    @pydantic.model_validator(mode="after")
    def check_if_data_matches_search_type(self) -> "WebSearchToolMCP":
        if self.type == "url":
            if self.tool not in ["universal"]:
                raise InvalidWebSearchMCPSettingsError("Tool must be 'universal' when type is 'url'.")
        if self.type == "query":
            if self.tool not in ["google_search", "bing_search", "amazon_search"]:
                raise InvalidWebSearchMCPSettingsError(
                    "Tool must be 'google_search', 'bing_search', or 'amazon_search' when type is 'query'."
                )
        return self

    def model_dump(  # noqa: PLR0913
        self,
        *,
        mode: Literal["json", "python"] = "python",  # type: ignore
        include: IncEx | None = None,
        exclude: IncEx | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,  # noqa: ARG002
        round_trip: bool = False,
        warnings: bool | Literal["none", "warn", "error"] = True,
        fallback: Callable[[Any], Any] | None = None,
        serialize_as_any: bool = False,
    ) -> dict[str, Any]:
        data = super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            context=context,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=True,
            round_trip=round_trip,
            warnings=warnings,
            fallback=fallback,
            serialize_as_any=serialize_as_any,
        )
        return {
            "type": data["type"],
            "options": {
                "tool": data["tool"],
                **(
                    {
                        "url": data["url"],
                    }
                    if "url" in data
                    else {}
                ),
                **(
                    {
                        "query": data["query"],
                    }
                    if "query" in data
                    else {}
                ),
                **(
                    {
                        "geo_location": data["geo_location"],
                    }
                    if "geo_location" in data
                    else {}
                ),
                **(
                    {
                        "parse": data["parse"],
                    }
                    if "parse" in data
                    else {}
                ),
            },
        }


class WebSearchToolOptions(NullableBaseModel):
    """
    Represents the options for a web search tool, passed to the request maker method.
    """

    search_context_size: typing.Literal["low", "medium", "high"] | None = None
    user_location: WebSearchUserLocation | None = None
    mcp: WebSearchToolMCP | None = None

    def model_dump(  # noqa: PLR0913
        self,
        *,
        mode: Literal["json", "python"] = "python",  # type: ignore
        include: IncEx | None = None,
        exclude: IncEx | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,  # noqa: ARG002
        round_trip: bool = False,
        warnings: bool | Literal["none", "warn", "error"] = True,
        fallback: Callable[[Any], Any] | None = None,
        serialize_as_any: bool = False,
    ) -> dict[str, Any]:
        data = super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            context=context,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=True,
            round_trip=round_trip,
            warnings=warnings,
            fallback=fallback,
            serialize_as_any=serialize_as_any,
        )
        mcp = data.get("mcp")
        return {
            **({"search_context_size": data["search_context_size"]} if "search_context_size" in data else {}),
            **({"user_location": data["user_location"]} if "user_location" in data else {}),
            **(
                {
                    "mcp": {
                        "type": mcp["type"],
                        "options": {
                            "tool": mcp["tool"],
                            **({"query": mcp["query"]} if "query" in mcp else {}),
                            **({"url": mcp["url"]} if "url" in mcp else {}),
                            **({"geo_location": mcp["geo_location"]} if "geo_location" in mcp else {}),
                            **({"parse": mcp["parse"]} if "parse" in mcp else {}),
                        },
                    }
                }
                if mcp
                else {}
            ),
        }


class RAGToolOptions(NullableBaseModel):
    collection_uuid: str
    query: str | None = None
    threshold: float | None = None
    top_n: int | None = None
    model_uuid: str | None = None


class OCRToolOptions(NullableBaseModel):
    file_id: str


class UrlCitation(NullableBaseModel):
    end_index: int | None = None
    start_index: int | None = None
    title: str | None = None
    url: str | None = None


class Annotation(NullableBaseModel):
    """
    Represents a reference/citation annotation, created from a citation entry found in the response text.
    """

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
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    completion_token_details: CompletionTokenDetails | None = None
    prompt_token_details: PromptTokenDetails | None = None


class LogProb:
    token: str
    logprob: float
    bytes: list[int]


class LogProbs(LogProb):
    top_logprobs: list[LogProb]


class LogProbsInfo(NullableBaseModel):
    model_config: typing.ClassVar[dict[str, typing.Any]] = {"arbitrary_types_allowed": True}  # type: ignore
    content: LogProbs | None = None
    refusal: LogProbs | None = None
