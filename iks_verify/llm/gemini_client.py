import httpx

from iks_verify.llm.base import LLM


class ProviderLLM(LLM):
    async def _complete(self, prompt: str, model: str, temperature: float) -> str:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            f"?key={self.settings.gemini_api_key}"
        )
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                url,
                json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": temperature}},
            )
            self._store_rate_headers(response.headers)
            if response.status_code == 429:
                raise RuntimeError(f"HTTP 429 quota retry-after={response.headers.get('retry-after', '')}")
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
