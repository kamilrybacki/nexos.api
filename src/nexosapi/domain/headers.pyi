from __future__ import annotations
import typing
from enum import StrEnum

class CompletionHeaders(StrEnum):
    """
    Headers for chat completions.
    """

    COMPLETION_TIME = "X-Nexos-Completion-Time-Ms"
    MODEL_ID = "X-Nexos-Model-Id"
