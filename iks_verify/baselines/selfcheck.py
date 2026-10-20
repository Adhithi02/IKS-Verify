from collections import Counter

from iks_verify.pipeline.run import VerificationPipeline
from iks_verify.schemas import VerifiedAnswer


async def run(question: str, pipeline: VerificationPipeline, samples: int | None = None) -> VerifiedAnswer:
    n = samples if samples is not None else pipeline.settings.selfcheck_samples
    answers = [await pipeline.ask(question, "rag") for _ in range(max(1, n))]
    selected = Counter(answer.answer for answer in answers).most_common(1)[0][0]
    result = next(answer for answer in answers if answer.answer == selected)
    result.system = "selfcheck"
    return result
