import json

from iks_verify.config import Settings
from iks_verify.llm.base import LLM
from iks_verify.pipeline.claims import extract_claims, parse_json
from tests.helpers import run_immediately


class ScriptedLLM(LLM):
    def __init__(self, settings: Settings, outputs: list[str]) -> None:
        super().__init__(settings)
        self.outputs = outputs

    async def _complete(self, prompt: str, model: str, temperature: float) -> str:
        return self.outputs.pop(0)


def test_parse_json_repairs_fences_commas_and_prose():
    raw = 'Here you go:\n```json\n[{"text": "A fact", "citations": ["Gita 2.47"],},]\n```\nThanks!'
    parsed = parse_json(raw)
    assert parsed[0]["text"] == "A fact"
    assert parsed[0]["citations"] == ["Gita 2.47"]


def test_multi_sentence_answer_yields_multiple_claims(tmp_path):
    settings = Settings(llm_provider="mock", llm_cache_dir=tmp_path)
    llm = ScriptedLLM(
        settings,
        [
            json.dumps([
                {"text": "One may act [Gita 2.47].", "citations": ["Gita 2.47"]},
                {"text": "Yoga is stilling the mind [YogaSutras 1.2].", "citations": ["YogaSutras 1.2"]},
            ])
        ],
    )
    answer = "One may act [Gita 2.47]. Yoga is stilling the mind [YogaSutras 1.2]."
    claims = run_immediately(extract_claims(answer, ["Gita 2.47", "YogaSutras 1.2"], llm))
    assert len(claims) == 2
    assert claims[0].citations == ["Gita 2.47"]
    assert claims[1].citations == ["YogaSutras 1.2"]


def test_malformed_json_is_retried_then_repaired(tmp_path):
    settings = Settings(llm_provider="mock", llm_cache_dir=tmp_path)
    llm = ScriptedLLM(settings, ["not json at all {", "still broken"])
    answer = "You may act [Gita 2.47]. Do not claim the fruit [Gita 2.47]."
    claims = run_immediately(extract_claims(answer, ["Gita 2.47"], llm))
    assert len(claims) >= 2
    assert all("Gita 2.47" in claim.citations for claim in claims)
