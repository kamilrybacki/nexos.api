import logging
import re
from typing import Any, Literal, Self, TypedDict

from pydantic import model_validator

from nexosapi.config.settings.defaults import COMPLETIONS_CITATION_REGEX, COMPLETIONS_THINKING_SECTION_REGEX
from nexosapi.domain.base import NullableBaseModel
from nexosapi.domain.metadata import Annotation, LogProbsInfo, ToolCall, UrlCitation


class Audio(NullableBaseModel):
    id: str
    expires_at: int
    data: str
    transcript: str


class CitationEntryExtractedData(TypedDict):
    title: str
    url: str


class ChatMessage(NullableBaseModel):
    """
    Model representing a chat message, contained within a request or response model under messages or choices field.

    :ivar role: The role of the message sender (user, assistant, etc.).
    :ivar refusal: The refusal message, if applicable.
    :ivar tool_calls: A list of tool calls made during the message.
    :ivar content: The content of the message.
    :ivar audio: The audio data associated with the message.
    :ivar annotations: Any annotations associated with the message.
    :ivar name: The name of the message sender.
    :ivar thinking: The thinking process associated with the message.
    """

    role: Literal["system", "user", "assistant", "tool", "function", "developer"] = "user"
    refusal: str | None = None
    tool_calls: list[ToolCall] | None = None
    content: str | list[dict[str, Any]] | None = None
    audio: Audio | None = None
    annotations: list[Annotation] | None = None
    name: str | None = None
    thinking: str | None = None

    @staticmethod
    def transform_citation_into_annotation(citation: CitationEntryExtractedData) -> Annotation:
        return Annotation(
            type="url_citation",
            url_citation=UrlCitation(
                title=citation["title"],
                url=citation["url"],
            ),
        )

    @staticmethod
    def extract_citations(text: str) -> list[CitationEntryExtractedData]:
        matches = re.findall(COMPLETIONS_CITATION_REGEX, text)
        return [CitationEntryExtractedData(title=match[0], url=match[1]) for match in matches]

    @staticmethod
    def extract_thinking_section(text: str) -> re.Match | None:
        return re.search(COMPLETIONS_THINKING_SECTION_REGEX, text, re.DOTALL)

    @model_validator(mode="after")
    def split_thinking_from_response(self) -> Self:
        """
        Splits the thinking process from the response content.

        :return: A tuple containing the thinking process and the response content.
        """
        if self.role == "assistant" and self.content:
            # First, check if content is a string and contains citations (they appear after the predefined text marker)
            if isinstance(self.content, str):
                citations = self.extract_citations(self.content)
                # If present, split the citations sections into individual list items (either starting from dash or a bullet point)
                if citations:
                    for citation in citations:
                        if not self.annotations:
                            self.annotations = []

                        self.annotations.append(self.transform_citation_into_annotation(citation))
                        citation_text = f"[{citation['title']}]({citation['url']})"
                        self.content = self.content.replace(citation_text, "").strip()

                thinking = self.extract_thinking_section(self.content)
                self.content = self.content.replace("<think>", "").replace("</think>", "")
                if thinking:
                    logging.info(f"[SDK] Thinking process detected for message from {self.name}")
                    self.thinking = thinking.group(0)
                    self.content = self.content.replace(thinking.group(1), "").strip()
        return self


class PredictionType(NullableBaseModel):
    type: str
    content: str | None = None


class AudioConfiguration(NullableBaseModel):
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    format: Literal["mp3", "opus", "flac", "wav", "pcm16"]


class ChatChoice(NullableBaseModel):
    index: int
    message: ChatMessage
    finish_reason: str
    logprobs: LogProbsInfo | None = None


class TranscriptionWord(NullableBaseModel):
    word: str
    start: float
    end: float


class TranscriptionSegment(NullableBaseModel):
    id: int
    seek: int
    start: float
    end: float
    text: str
    tokens: list[int]
    temperature: float
    avg_logprob: float
    compression_ratio: float
    no_speech_prob: float


class StorageFile(NullableBaseModel):
    size: int | None = None
    created_at: int | None = None
    expires_at: int | None = None
    filename: str | None = None
    id: str | None = None
    purpose: (
        Literal["assistants", "assistants_output", "batch", "batch_output", "fine-tune", "fine-tune-results", "vision"]
        | None
    ) = None


class Image(NullableBaseModel):
    url: str | None
    revised_prompt: str | None
    b64_json: str | None


class Embedding(NullableBaseModel):
    object: str
    embedding: list[float]
    index: int


class TeamApiKey(NullableBaseModel):
    api_key: str
    id: str
    name: str
    created_at: str | None = None
    updated_at: str | None = None
