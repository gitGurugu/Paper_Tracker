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
        """Call the OpenAI-compatible chat completions API.

        GPT-5 series models require ``max_completion_tokens`` and reject the
        legacy ``max_tokens``; older models / endpoints only accept
        ``max_tokens``. Try the modern parameter first, then fall back.
        """
        messages = [{"role": "user", "content": prompt}]

        try:
            response = self.client.chat.completions.create(
                model=self.config.llm.model,
                messages=messages,
                max_completion_tokens=1024,
            )
        except TypeError:
            # Older openai SDK without the max_completion_tokens kwarg.
            response = self.client.chat.completions.create(
                model=self.config.llm.model,
                messages=messages,
                max_tokens=1024,
            )
        except Exception as e:
            # Endpoint rejected max_completion_tokens — retry with max_tokens.
            if "max_completion_tokens" in str(e) or "max_tokens" in str(e):
                response = self.client.chat.completions.create(
                    model=self.config.llm.model,
                    messages=messages,
                    max_tokens=1024,
                )
            else:
                raise

        return response.choices[0].message.content
