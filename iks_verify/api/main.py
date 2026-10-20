from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from iks_verify.api import routes, streaming

app = FastAPI(title="IKS-Verify", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(routes.router, prefix="/api")
app.include_router(streaming.router, prefix="/api")

web_dist = Path("web/dist")
if web_dist.exists():
    app.mount("/", StaticFiles(directory=web_dist, html=True), name="web")
