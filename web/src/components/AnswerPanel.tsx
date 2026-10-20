import { useMemo } from "react";
import { Download } from "lucide-react";
import type { Claim, VerifiedAnswer, Verdict } from "../types";
import { AttributionAlert } from "./AttributionAlert";
import { ClaimChip } from "./ClaimChip";
import { TrustMeter } from "./TrustMeter";

function highlight(answer: string, claims: Claim[], selected: number | null) {
  if (!claims.length) return [answer];
  const nodes: Array<{ text: string; claim?: Claim; index?: number }> = [];
  let cursor = 0;
  const lower = answer;
  const found = claims
    .map((claim, index) => ({ claim, index, at: lower.indexOf(claim.text.slice(0, Math.min(24, claim.text.length))) }))
    .filter((item) => item.at >= 0)
    .sort((a, b) => a.at - b.at);
  if (!found.length) return [answer];
  for (const item of found) {
    if (item.at < cursor) continue;
    if (item.at > cursor) nodes.push({ text: answer.slice(cursor, item.at) });
    const end = item.at + item.claim.text.length <= answer.length
      ? item.at + item.claim.text.length
      : item.at + Math.min(80, item.claim.text.length);
    nodes.push({ text: answer.slice(item.at, end), claim: item.claim, index: item.index });
    cursor = end;
  }
  if (cursor < answer.length) nodes.push({ text: answer.slice(cursor) });
  return nodes.map((node, key) => {
    if (!node.claim) return <span key={key}>{node.text}</span>;
    const verdict = (node.claim.verdict || "UNVERIFIABLE") as Verdict;
    return (
      <mark
        key={key}
        className={`hl ${verdict.toLowerCase()} ${selected === node.index ? "on" : ""}`}
        title={`${node.claim.verdict}: ${node.claim.rationale || ""}\n${node.claim.supporting_verse_ids.join(", ")}`}
      >
        {node.text}
      </mark>
    );
  });
}

export function AnswerPanel({
  result, selectedClaim, onSelectClaim,
}: {
  result: VerifiedAnswer;
  selectedClaim: number | null;
  onSelectClaim: (index: number | null) => void;
}) {
  const nodes = useMemo(
    () => highlight(result.answer, result.claims, selectedClaim),
    [result.answer, result.claims, selectedClaim],
  );
  const downloadJson = () => {
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "iks-verify-answer.json";
    a.click();
    URL.revokeObjectURL(a.href);
  };
  const downloadPng = async () => {
    const node = document.getElementById("answer-view");
    if (!node) return;
    const { default: html2canvas } = await import("html2canvas");
    const canvas = await html2canvas(node, { backgroundColor: null, scale: 2 });
    const a = document.createElement("a");
    a.href = canvas.toDataURL("image/png");
    a.download = "iks-verify-answer.png";
    a.click();
  };
  return (
    <main className="answer-panel" id="answer-view">
      {result.abstained ? (
        <div className="abstain">
          <h2>Evidence stops here</h2>
          <p>The retrieved texts do not support a reliable answer to this question.</p>
        </div>
      ) : (
        <>
          <div className="answer-heading">
            <div>
              <span className="eyebrow">Grounded response</span>
              <h2>Answer</h2>
            </div>
            <TrustMeter score={result.trust_score} claims={result.claims} />
          </div>
          <p className="answer-text">{nodes}</p>
          <div className="claims">
            {result.claims.map((claim, index) => (
              <ClaimChip
                key={index}
                claim={claim}
                selected={selectedClaim === index}
                onSelect={() => onSelectClaim(selectedClaim === index ? null : index)}
              />
            ))}
          </div>
        </>
      )}
      <AttributionAlert flags={result.attribution_flags} />
      <div className="export-row">
        <button className="export" onClick={downloadJson}><Download size={16} /> JSON</button>
        <button className="export" onClick={downloadPng}><Download size={16} /> PNG</button>
      </div>
    </main>
  );
}
