import httpx

from iks_verify.llm.base import LLM


class OpenAICompatibleLLM(LLM):
    base_url: str
    api_key: str

    async def _complete(self, prompt: str, model: str, temperature: float) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            self._store_rate_headers(response.headers)
            if response.status_code == 429:
                retry = response.headers.get("retry-after", "")
                raise RuntimeError(f"HTTP 429 quota retry-after={retry}")
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
