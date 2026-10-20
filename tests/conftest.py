import os

from iks_verify.runtime import configure_event_loop

configure_event_loop()

os.environ["LLM_PROVIDER"] = "mock"
os.environ["CORPUS_PATH"] = "tests/fixtures/corpus.jsonl"
