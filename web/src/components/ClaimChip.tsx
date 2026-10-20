import type { Claim } from "../types";

export function ClaimChip({
  claim, selected, onSelect,
}: { claim: Claim; selected?: boolean; onSelect?: () => void }) {
  const verdict = claim.verdict?.toLowerCase() || "unverifiable";
  return (
    <article className={`claim ${verdict} ${selected ? "selected" : ""}`}>
      <button type="button" className="claim-hit" onClick={onSelect} aria-pressed={selected}>
        <span className="verdict">{claim.verdict || "UNCHECKED"}</span>
        <p>{claim.text}</p>
      </button>
      {claim.rationale && <small>{claim.rationale}</small>}
    </article>
  );
}
