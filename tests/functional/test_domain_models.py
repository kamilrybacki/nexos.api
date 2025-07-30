from nexosapi.domain.base import NullableBaseModel
from nexosapi.domain.responses import AudioTranscriptionResponse, ChatCompletionsResponse


class SampleModel(NullableBaseModel):
    field1: str
    field2: int | None = None
    field3: dict[str, str] | None = None
    field4: list[int]


def test_nullable_base_model_null() -> None:
    instance: SampleModel = SampleModel.null()
    assert instance.field1 == ""
    assert instance.field2 is None
    assert instance.field3 is None
    assert instance.field4 == []


def test_nullable_base_model_initialization() -> None:
    instance: SampleModel = SampleModel(field1="test", field2=None, field3={"key": "value"}, field4=[1, 2, 3])
    assert instance.field1 == "test"
    assert instance.field2 is None
    assert instance.field3 == {"key": "value"}
    assert instance.field4 == [1, 2, 3]


def test_nulling_domain_models() -> None:
    """
    Test that the null method of a domain model returns an instance with default values.
    """
    """
        id: str
        object: str
        created: int
        model: str
        choices: list[ChatChoice]
        usage: UsageInfo | None
        system_fingerprint: str | None
        service_tier: Literal["scale", "default"] | None
    """
    completions_model: ChatCompletionsResponse = ChatCompletionsResponse.null()
    assert completions_model.id == ""
    assert completions_model.object == ""
    assert completions_model.created == 0
    assert completions_model.model == ""
    assert completions_model.choices == []
    assert completions_model.usage is None
    assert completions_model.system_fingerprint is None
    assert completions_model.service_tier is None, (
        f"Expected service_tier to be None, but got: {completions_model.service_tier}"
    )

    """
        text: str
        language: str | None
        duration: str | None
        words: list[TranscriptionWord]
        segments: list[TranscriptionSegment]
        model: str | None
    """

    transcription_model: AudioTranscriptionResponse = AudioTranscriptionResponse.null()
    assert transcription_model.text is None
    assert transcription_model.language is None
    assert transcription_model.duration is None
    assert transcription_model.words == []
    assert transcription_model.segments == []
    assert transcription_model.model is None, f"Expected model to be None, but got: {transcription_model.model}"
