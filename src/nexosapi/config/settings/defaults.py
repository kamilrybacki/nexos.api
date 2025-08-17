"""
Module which defines default settings for the NexosAI SDK.
"""

NEXOSAI_CONFIGURATION_PREFIX = "NEXOSAI_"
NEXOSAI_BASE_URL = "https://api.nexos.ai"
NEXOSAI_API_VERSION = "v1"
NEXOSAI_AUTH_HEADER_NAME = "Authorization"
NEXOSAI_AUTH_HEADER_PREFIX = "Bearer"

COMPLETIONS_FALLBACK_MODEL = "gpt-3.5-turbo"
COMPLETIONS_DEFAULT_SEARCH_ENGINE = "google_search"

# Regex to match thinking process in completions (it sits between <think> and </think> tags in text content)
COMPLETIONS_THINKING_SECTION_REGEX = r"<think>(.*?)</think>(.*?)$"

# Citations are expected to be in the format:
# - [Title](URL) || Description
COMPLETIONS_CITATION_REGEX = r"\[(.*?)\]\((.*?)\)"

FALLBACK_WEB_SEARCH_TOOL_DESCRIPTION = "Search the web for information."
