from iks_verify.pipeline.run import VerificationPipeline
from iks_verify.schemas import VerifiedAnswer


async def run(question: str, pipeline: VerificationPipeline) -> VerifiedAnswer:
    return await pipeline.ask(question, "plain")
