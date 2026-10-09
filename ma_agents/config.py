"""Runtime configuration loaded from environment variables."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    groq_api_key: str
    model: str = "openai/gpt-oss-20b"
    max_completion_tokens: int = 1000


def _clean(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    # Tolerate copy-paste with surrounding quotes from TOML editors.
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ("'", '"'):
        text = text[1:-1].strip()
    return text


def get_settings() -> Settings:
    try:
        import streamlit as st
    except ImportError:
        st = None

    def setting(name: str, default: str) -> str:
        value = _clean(os.getenv(name))
        if value:
            return value
        if st is not None:
            try:
                secrets = getattr(st, "secrets", None)
                if secrets is not None:
                    return _clean(secrets.get(name, default))
            except Exception:
                pass
        return default

    key = setting("GROQ_API_KEY", "")
    if not key:
        raise RuntimeError(
            "GROQ_API_KEY is required. "
            "Locally: add it to .env (never commit it). "
            "On Streamlit Cloud: open the app menu (⋮) → Settings → Secrets, "
            'add GROQ_API_KEY = "paste-your-groq-key-here" in TOML format, Save, then Reboot the app. '
            ".env files are git-ignored and never reach Streamlit Cloud."
        )
    return Settings(
        groq_api_key=key,
        model=setting("GROQ_MODEL", "openai/gpt-oss-20b"),
        max_completion_tokens=int(setting("MAX_COMPLETION_TOKENS", "1000")),
    )
