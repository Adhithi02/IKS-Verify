import httpx

from iks_verify.llm.base import LLM


class ProviderLLM(LLM):
    async def _complete(self, prompt: str, model: str, temperature: float) -> str:
        headers = {"x-api-key": self.settings.anthropic_api_key or "", "anthropic-version": "2023-06-01"}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json={"model": model, "max_tokens": 1024, "temperature": temperature, "messages": [{"role": "user", "content": prompt}]})
            response.raise_for_status()
            return response.json()["content"][0]["text"]
