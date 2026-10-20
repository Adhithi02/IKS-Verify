import { expect, test, vi } from "vitest";

test("parses SSE pipeline events through to done", async () => {
  const body = [
    "event: pipeline\ndata: {\"stage\":\"retrieving\"}\n\n",
    "event: pipeline\ndata: {\"stage\":\"generating\"}\n\n",
    "event: pipeline\ndata: {\"stage\":\"extracting_claims\"}\n\n",
    "event: pipeline\ndata: {\"stage\":\"verifying\"}\n\n",
    "event: pipeline\ndata: {\"stage\":\"checking_attributions\"}\n\n",
    "event: pipeline\ndata: {\"stage\":\"done\",\"result\":{\"answer\":\"x [Gita 2.47]\",\"claims\":[{\"text\":\"x [Gita 2.47]\",\"citations\":[\"Gita 2.47\"],\"supporting_verse_ids\":[\"Gita 2.47\"],\"verdict\":\"SUPPORTED\"}],\"attribution_flags\":[],\"retrieved_passages\":[],\"trust_score\":1,\"model_name\":\"mock\",\"judge_model_name\":\"mock\",\"system\":\"verify\",\"abstained\":false}}\n\n",
  ].join("");
  const stream = new ReadableStream({
    start(controller) {
      controller.enqueue(new TextEncoder().encode(body));
      controller.close();
    },
  });
  vi.stubGlobal("fetch", vi.fn(async () => new Response(stream, { status: 200 })));
  const response = await fetch("/api/ask/stream", { method: "POST", body: "{}" });
  const text = await response.text();
  expect(text).toContain("event: pipeline");
  expect(text).toContain("\"stage\":\"done\"");
  expect(text).toContain("SUPPORTED");
  vi.unstubAllGlobals();
});
