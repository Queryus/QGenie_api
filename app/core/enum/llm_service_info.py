from enum import Enum


class LLMServiceEnum(str, Enum):
    """지원하는 외부 LLM 서비스 목록"""

    OPENAI = "OpenAI"
    ANTHROPIC = "Anthropic"
    GEMINI = "Gemini"
    # TODO: 다른 지원 서비스를 여기에 추가
