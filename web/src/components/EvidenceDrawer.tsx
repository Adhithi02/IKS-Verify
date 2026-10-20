import { BookOpen, X } from "lucide-react";
import type { Claim, Passage } from "../types";
import { VerseCard } from "./VerseCard";

export function EvidenceDrawer({
  passages, claim, open, onClose,
}: {
  passages: Passage[];
  claim?: Claim;
  open: boolean;
  onClose: () => void;
}) {
  const ids = new Set(claim?.supporting_verse_ids || claim?.citations || []);
  const highlighted = passages.filter((p) => ids.has(`${p.text_id} ${p.chapter}.${p.verse}`));
  const rest = passages.filter((p) => !ids.has(`${p.text_id} ${p.chapter}.${p.verse}`));
  return (
    <aside className={`evidence ${open ? "open" : ""}`} aria-label="Retrieved evidence">
      <div className="evidence-head">
        <h2><BookOpen size={18} /> Evidence</h2>
        <button className="icon-btn" aria-label="Close evidence" onClick={onClose}><X size={16} /></button>
      </div>
      {claim?.rationale && <p className="evidence-note">{claim.verdict}: {claim.rationale}</p>}
      {[...highlighted, ...rest].map((verse) => (
        <VerseCard
          key={`${verse.text_id}${verse.chapter}${verse.verse}`}
          verse={verse}
          highlight={ids.has(`${verse.text_id} ${verse.chapter}.${verse.verse}`)}
        />
      ))}
    </aside>
  );
}
