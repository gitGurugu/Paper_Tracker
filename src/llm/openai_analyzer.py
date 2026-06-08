"""OpenAI analyzer implementation."""

from openai import OpenAI

from ..config import Config
from .base import BaseAnalyzer


class OpenAIAnalyzer(BaseAnalyzer):
    """Paper analyzer using OpenAI API."""

    def __init__(self, config: Config):
        super().__init__(config)

        api_key = config.llm.api_key
        if not api_key:
            raise ValueError(
                f"API key not found. Set {config.llm.api_key_env} environment variable."
            )

        self.client = OpenAI(api_key=api_key, base_url=config.llm.base_url)

    def _call_llm(self, prompt: str) -> str:
        """Call the OpenAI-compatible Responses API (POST /v1/responses).

        The configured endpoint (e.g. the ccswitch relay) serves the OpenAI
        *Responses* API used by Codex, not Chat Completions. Returns the
        concatenated output text.
        """
        response = self.client.responses.create(
            model=self.config.llm.model,
            input=prompt,
            max_output_tokens=2048,
        )

        # SDK convenience that joins all output text segments.
        text = getattr(response, "output_text", None)
        if text:
            return text

        # Fallback: walk the output items if output_text isn't available.
        chunks = []
        for item in getattr(response, "output", None) or []:
            for part in getattr(item, "content", None) or []:
                part_text = getattr(part, "text", None)
                if part_text:
                    chunks.append(part_text)
        return "".join(chunks)
