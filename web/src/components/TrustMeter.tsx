import type { Claim } from "../types";

export function TrustMeter({ score, claims }: { score: number; claims?: Claim[] }) {
  const percentage = Math.round(score * 100);
  const supported = claims?.filter((c) => c.verdict === "SUPPORTED").length ?? 0;
  const contradicted = claims?.filter((c) => c.verdict === "CONTRADICTED").length ?? 0;
  const unverifiable = claims?.filter((c) => c.verdict === "UNVERIFIABLE").length ?? 0;
  return (
    <section className="trust-meter" aria-label={`Trust score ${percentage}%`}>
      <div className="gauge" style={{ background: `conic-gradient(var(--saffron) ${percentage * 3.6}deg, var(--border) 0deg)` }}>
        <div><b>{percentage}</b><span>/100</span></div>
      </div>
      <p>Evidence-grounded trust score</p>
      {claims && (
        <ul className="verdict-break">
          <li>Supported {supported}</li>
          <li>Contradicted {contradicted}</li>
          <li>Unverifiable {unverifiable}</li>
        </ul>
      )}
    </section>
  );
}
