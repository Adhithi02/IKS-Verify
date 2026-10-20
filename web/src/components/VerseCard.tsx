import { Copy } from "lucide-react";
import type { Passage } from "../types";

export function VerseCard({ verse, highlight }: { verse: Passage; highlight?: boolean }) {
  const id = `${verse.text_id} ${verse.chapter}.${verse.verse}`;
  return (
    <article className={`verse-card ${highlight ? "tied" : ""}`}>
      <div className="verse-head">
        <b>{id}</b>
        <button
          aria-label={`Copy ${id}`}
          onClick={() => navigator.clipboard.writeText(`${verse.sanskrit_devanagari}\n${verse.english_translation}`)}
        >
          <Copy size={15} />
        </button>
      </div>
      <p className="devanagari">{verse.sanskrit_devanagari}</p>
      <em>{verse.transliteration_iast}</em>
      <p>{verse.english_translation}</p>
      <small>Relevance {verse.score.toFixed(2)} · {verse.source}</small>
    </article>
  );
}
