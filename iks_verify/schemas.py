from enum import Enum

from pydantic import BaseModel, Field


class Verse(BaseModel):
    text_id: str
    chapter: str
    verse: str
    sanskrit_devanagari: str
    transliteration_iast: str | None = None
    english_translation: str
    source: str
    license: str

    @property
    def verse_id(self) -> str:
        return f"{self.text_id} {self.chapter}.{self.verse}"


class Passage(Verse):
    score: float = 0.0


class Verdict(str, Enum):
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    UNVERIFIABLE = "UNVERIFIABLE"


class Claim(BaseModel):
    text: str
    citations: list[str] = Field(default_factory=list)
    verdict: Verdict | None = None
    supporting_verse_ids: list[str] = Field(default_factory=list)
    rationale: str | None = None


class AttributionFlag(BaseModel):
    kind: str
    cited: str
    message: str
    closest_verse_id: str | None = None
    quoted_text: str | None = None
    actual_text: str | None = None


class VerifiedAnswer(BaseModel):
    answer: str
    claims: list[Claim] = Field(default_factory=list)
    attribution_flags: list[AttributionFlag] = Field(default_factory=list)
    retrieved_passages: list[Passage] = Field(default_factory=list)
    trust_score: float = 0.0
    model_name: str
    judge_model_name: str
    system: str = "verify"
    abstained: bool = False


class EvalRecord(BaseModel):
    id: str
    category: str
    system: str
    answer: VerifiedAnswer
    gold_verses: list[str] | str
    should_abstain: bool
