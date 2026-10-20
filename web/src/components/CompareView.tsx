import type { System, VerifiedAnswer } from "../types";

const names: Partial<Record<System, string>> = {
  plain: "Plain LLM",
  rag: "RAG only",
  verify: "RAG + Verify",
};

export function CompareView({ results }: { results: Record<string, VerifiedAnswer> }) {
  return (
    <section className="compare">
      <h2>System comparison</h2>
      <div>
        {Object.keys(results).map((key) => (
          <article key={key}>
            <span className="eyebrow">{names[key as System] || key}</span>
            <b>{Math.round(results[key].trust_score * 100)} trust</b>
            <p>{results[key].answer}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
