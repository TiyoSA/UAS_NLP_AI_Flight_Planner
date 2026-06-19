import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AppConfig:
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    searchapi_key: str = os.getenv("SEARCHAPI_KEY", "")

    langsmith_api_key: str = os.getenv("LANGSMITH_API_KEY", "")
    langsmith_project: str = os.getenv(
        "LANGSMITH_PROJECT",
        "AI-Flight-Planner-UAS"
    )
    langsmith_tracing: str = os.getenv("LANGSMITH_TRACING", "true")


def enable_langsmith(config: AppConfig) -> None:
    """
    Mengaktifkan LangSmith tracing untuk LangChain dan LangGraph.
    """

    os.environ["LANGSMITH_PROJECT"] = config.langsmith_project
    os.environ["LANGSMITH_TRACING"] = config.langsmith_tracing

    os.environ["LANGCHAIN_PROJECT"] = config.langsmith_project
    os.environ["LANGCHAIN_TRACING_V2"] = config.langsmith_tracing

    if config.langsmith_api_key:
        os.environ["LANGSMITH_API_KEY"] = config.langsmith_api_key
        os.environ["LANGCHAIN_API_KEY"] = config.langsmith_api_key
