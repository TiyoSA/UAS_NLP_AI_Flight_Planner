from config import AppConfig
from langchain_google_genai import ChatGoogleGenerativeAI


def main():
    config = AppConfig()

    if not config.google_api_key:
        raise ValueError(
            "GOOGLE_API_KEY belum diisi di file .env"
        )

    llm = ChatGoogleGenerativeAI(
        model=config.gemini_model,
        google_api_key=config.google_api_key,
        temperature=0.3,
    )

    response = llm.invoke(
        "Jelaskan secara singkat apa itu AI Flight Planner dalam bahasa Indonesia."
    )

    print("=== RESPONSE GEMINI ===")
    print(response.content)


if __name__ == "__main__":
    main()
