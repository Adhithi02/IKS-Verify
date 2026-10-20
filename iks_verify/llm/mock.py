import json
import re

from iks_verify.llm.base import LLM


class MockLLM(LLM):
    """Deterministic stand-in that only synthesizes from passages embedded in a prompt."""

    async def complete(self, prompt: str, model: str | None = None, temperature: float = 0) -> str:
        """Mocks are local and deterministic, so they bypass network quota throttling.

        This prevents fixture tests from being affected by production RPM windows while
        retaining a separate cache key per prompt/model/temperature.
        """
        selected_model = model or self.settings.llm_model
        # Never share entries with a provider cache even when the configured
        # model label is the same (for example when mock mode inherits an
        # existing .env model). A mock evaluation must not replay real output.
        cache_key = f"mock-v2|{selected_model}|{temperature}|{prompt}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        self.calls += 1
        result = await self._complete(prompt, selected_model, temperature)
        self.cache.set(cache_key, result)
        return result

    async def _complete(self, prompt: str, model: str, temperature: float) -> str:
        citations = re.findall(r"\[(\w+\s+\d+\.\d+)\]", prompt)
        if "EXTRACT_CLAIMS" in prompt:
            answer_match = re.search(r"ANSWER:\s*(.*?)(?:\nEVIDENCE:|$)", prompt, re.S)
            text = answer_match.group(1).strip() if answer_match else ""
            parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]
            claims = []
            for part in parts:
                local = re.findall(r"\[(\w+\s+\d+\.\d+)\]", part)
                claims.append({"text": part, "citations": local or (citations[:1] if citations else [])})
            if not claims:
                claims = [{"text": "The corpus does not contain enough information.", "citations": []}]
            return json.dumps(claims)
        if "VERIFY_CLAIMS" in prompt:
            payload_match = re.search(r"CLAIMS:\s*(\[.*?\])\s*\nEVIDENCE:", prompt, re.S)
            try:
                claims = json.loads(payload_match.group(1)) if payload_match else []
            except (AttributeError, json.JSONDecodeError):
                claims = []
            return json.dumps([
                {
                    "verdict": "SUPPORTED" if claim.get("citations") else "UNVERIFIABLE",
                    "supporting_verse_ids": claim.get("citations", [])[:1],
                    "rationale": (
                        "Supported by retrieved evidence."
                        if claim.get("citations")
                        else "No retrieved evidence."
                    ),
                }
                for claim in claims
            ])
        if not citations:
            return "The provided texts do not contain enough information to answer this question."
        translations = re.findall(r"\[(\w+\s+\d+\.\d+)\] TRANSLATION:\s*(.*)", prompt)
        if translations:
            sentences = [
                f"{translation.strip().rstrip('.')} [{verse_id}]."
                for verse_id, translation in translations[:2]
            ]
            return " ".join(sentences)
        translation = re.search(r"TRANSLATION:\s*(.*)", prompt)
        content = translation.group(1).strip() if translation else "The retrieved passage supports a limited answer."
        extra = f" A second related statement follows from the same passage [{citations[0]}]."
        return f"{content} [{citations[0]}]{extra}"
