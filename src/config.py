"""Configuration management for paper tracking system."""

import json
import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class SiteConfig(BaseModel):
    """Site configuration."""

    title: str = "Paper Tracker"
    description: str = "Daily arXiv paper tracking with AI-powered analysis"
    base_url: str = ""


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    model_config = {"protected_namespaces": ()}

    provider: Literal["claude", "openai", "ollama", "minimax", "gemini"] = "claude"
    model: str = "claude-sonnet-4-20250514"
    model_env: str | None = None
    api_key_env: str = "ANTHROPIC_API_KEY"
    base_url_env: str | None = None

    @model_validator(mode="after")
    def _resolve_model_from_env(self) -> "LLMConfig":
        """Override model name from environment variable, if configured."""
        if self.model_env:
            env_model = os.getenv(self.model_env)
            if env_model:
                self.model = env_model
        return self

    @property
    def api_key(self) -> str | None:
        """Get API key from environment variable."""
        return os.getenv(self.api_key_env)

    @property
    def base_url(self) -> str | None:
        """Get API base URL from environment variable, if configured."""
        if self.base_url_env:
            return os.getenv(self.base_url_env)
        return None


class DomainConfig(BaseModel):
    """Research domain configuration."""

    name: str = Field(description="Human-readable domain name")
    categories: list[str] = Field(description="arXiv categories to search")
    keywords: list[str] = Field(description="Keywords to filter papers")
    output_category: str = Field(description="Category slug for output")


class FetchConfig(BaseModel):
    """Fetch configuration."""

    days_back: int = 1
    max_papers_per_domain: int = 50
    min_relevance_score: int = 5


class Config(BaseModel):
    """Main configuration model."""

    site: SiteConfig = Field(default_factory=SiteConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    domains: list[DomainConfig] = Field(default_factory=list)
    fetch: FetchConfig = Field(default_factory=FetchConfig)

    @classmethod
    def load(cls, config_path: str | Path | None = None) -> "Config":
        """Load configuration from JSON file."""
        if config_path is None:
            # Default to data/config.json relative to project root
            project_root = Path(__file__).parent.parent
            config_path = project_root / "data" / "config.json"

        config_path = Path(config_path)

        if not config_path.exists():
            # Return default config if file doesn't exist
            return cls()

        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls.model_validate(data)

    def save(self, config_path: str | Path) -> None:
        """Save configuration to JSON file."""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=2, ensure_ascii=False)

    def get_all_categories(self) -> list[str]:
        """Get all unique arXiv categories from all domains."""
        categories = set()
        for domain in self.domains:
            categories.update(domain.categories)
        return sorted(categories)

    def get_output_categories(self) -> list[str]:
        """Get all output category slugs."""
        return [d.output_category for d in self.domains]

    def get_domain_by_output_category(self, output_category: str) -> DomainConfig | None:
        """Get domain config by output category slug."""
        for domain in self.domains:
            if domain.output_category == output_category:
                return domain
        return None


def load_config(config_path: str | Path | None = None) -> Config:
    """Convenience function to load configuration."""
    return Config.load(config_path)
