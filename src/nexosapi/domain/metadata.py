import typing

import pydantic

from nexosapi.domain.base import NullableBaseModel


class Model(NullableBaseModel):
    id: str
    object: str
    created: int
    owned_by: str
    name: str
    timeout_ms: int | None = pydantic.Field(ge=1, default=None)
    stream_timeout_ms: int | None = pydantic.Field(ge=1, default=None)


class FunctionCall(NullableBaseModel):
    name: str
    arguments: str


class ToolCall(NullableBaseModel):
    id: str
    type: str
    function: FunctionCall


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
    model_config: typing.ClassVar[dict[str, typing.Any]] = {"arbitrary_types_allowed": True}
    content: LogProbs | None = None
    refusal: LogProbs | None = None
