"""Runtime configuration loaded from environment variables."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    groq_api_key: str
    model: str = "openai/gpt-oss-20b"
    max_completion_tokens: int = 1000


def get_settings() -> Settings:
    try:
        import streamlit as st
    except ImportError:
        st = None

    def setting(name: str, default: str) -> str:
        value = os.getenv(name)
        if value:
            return value
        if st is not None:
            try:
                return str(st.secrets.get(name, default))
            except FileNotFoundError:
                pass
        return default

    key = setting("GROQ_API_KEY", "").strip()
    if not key:
        raise RuntimeError("GROQ_API_KEY is required. Add it to .env locally or to the app's Streamlit secrets when hosted.")
    return Settings(
        groq_api_key=key,
        model=setting("GROQ_MODEL", "openai/gpt-oss-20b"),
        max_completion_tokens=int(setting("MAX_COMPLETION_TOKENS", "1000")),
    )
