from enum import StrEnum

class CompletionHeaders(StrEnum):
    COMPLETION_TIME = "X-Nexos-Completion-Time-Ms"
    MODEL_ID = "X-Nexos-Model-Id"
