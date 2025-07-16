from pydantic import BaseModel, conint


class Model(BaseModel):
    id: str
    object: str
    created: int
    owned_by: str
    name: str
    timeout_ms: conint(ge=1) | None = None
    stream_timeout_ms: conint(ge=1) | None = None


class FunctionCall(BaseModel):
    name: str
    arguments: str


class ToolCall(BaseModel):
    id: str
    type: str
    function: FunctionCall


class UrlCitation(BaseModel):
    end_index: int
    start_index: int
    title: str
    url: str


class Annotation(BaseModel):
    type: str
    url_citation: UrlCitation


class CompletionTokenDetails(BaseModel):
    accepted_prediction_tokens: int
    rejected_prediction_tokens: int
    audio_tokens: int
    reasoning_tokens: int


class PromptTokenDetails(BaseModel):
    audio_tokens: int
    cached_tokens: int


class UsageInfo(BaseModel):
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


class LogProbsInfo(BaseModel):
    content: LogProbs
    refusal: LogProbs
