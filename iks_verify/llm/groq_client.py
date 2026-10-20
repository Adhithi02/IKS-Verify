from iks_verify.llm.openai_compatible import OpenAICompatibleLLM


class ProviderLLM(OpenAICompatibleLLM):
    def __init__(self, settings):
        super().__init__(settings)
        self.base_url = "https://api.groq.com/openai/v1"
        self.api_key = settings.groq_api_key or ""
