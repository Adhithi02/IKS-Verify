import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from iks_verify.api.routes import AskRequest, pipeline

router = APIRouter()


@router.post("/ask/stream")
async def ask_stream(request: AskRequest) -> StreamingResponse:
    async def events():
        async for event in pipeline.events(request.question, request.system):
            yield f"event: pipeline\ndata: {json.dumps(event)}\n\n"
    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})
