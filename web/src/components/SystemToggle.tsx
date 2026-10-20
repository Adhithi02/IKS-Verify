import type { System } from "../types";

const labels: Record<System, string> = {
  plain: "Plain LLM",
  rag: "RAG only",
  verify: "RAG + Verify",
  selfcheck: "Self-check",
};

export function SystemToggle({ value, onChange }: { value: System; onChange: (value: System) => void }) {
  return (
    <div className="system-toggle" role="group" aria-label="System selection">
      {(Object.keys(labels) as System[]).map((system) => (
        <button key={system} className={value === system ? "active" : ""} onClick={() => onChange(system)}>
          {labels[system]}
        </button>
      ))}
    </div>
  );
}
