import { useEffect, useState } from "react";
import type { System, VerifiedAnswer } from "../types";

export function useAsk() {
  const [result, setResult] = useState<VerifiedAnswer>();
  const [activeStage, setActiveStage] = useState<string>();
  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState(false);
  const [retryAfter, setRetryAfter] = useState<number>();

  useEffect(() => {
    if (!retryAfter) return;
    const id = window.setInterval(() => {
      setRetryAfter((value) => (value && value > 1 ? value - 1 : undefined));
    }, 1000);
    return () => window.clearInterval(id);
  }, [retryAfter]);

  const submit = async (question: string, system: System) => {
    setLoading(true);
    setError(undefined);
    setResult(undefined);
    setActiveStage("retrieving");
    setRetryAfter(undefined);
    try {
      const response = await fetch("/api/ask/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, system }),
      });
      if (response.status === 429) {
        const retry = Number(response.headers.get("Retry-After") || "60");
        setRetryAfter(retry);
        throw new Error(`Rate limited. Retry in ${retry}s.`);
      }
      if (!response.ok || !response.body) throw new Error(`Request failed (${response.status})`);
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      for (;;) {
        const item = await reader.read();
        if (item.done) break;
        buffer += decoder.decode(item.value, { stream: true });
        const messages = buffer.split("\n\n");
        buffer = messages.pop() || "";
        messages.forEach((message) => {
          const data = message.split("\ndata: ")[1];
          if (!data) return;
          const event = JSON.parse(data) as { stage: string; result?: VerifiedAnswer };
          setActiveStage(event.stage);
          if (event.result) setResult(event.result);
        });
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to reach the verifier.");
    } finally {
      setLoading(false);
    }
  };
  return { result, activeStage, error, loading, retryAfter, submit };
}
