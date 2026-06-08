"""LLM analyzers for paper analysis."""

from .base import BaseAnalyzer


def get_analyzer(config) -> BaseAnalyzer:
    """Get the appropriate analyzer based on configuration.

    Provider modules are imported lazily so only the selected provider's
    SDK needs to be installed (see "install as needed" in requirements.txt).
    """
    provider = config.llm.provider

    if provider == "claude":
        from .claude_analyzer import ClaudeAnalyzer

        return ClaudeAnalyzer(config)
    elif provider == "openai":
        from .openai_analyzer import OpenAIAnalyzer

        return OpenAIAnalyzer(config)
    elif provider == "ollama":
        from .ollama_analyzer import OllamaAnalyzer

        return OllamaAnalyzer(config)
    elif provider == "minimax":
        from .minimax_analyzer import MiniMaxAnalyzer

        return MiniMaxAnalyzer(config)
    elif provider == "gemini":
        from .gemini_analyzer import GeminiAnalyzer

        return GeminiAnalyzer(config)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


__all__ = [
    "BaseAnalyzer",
    "get_analyzer",
]
