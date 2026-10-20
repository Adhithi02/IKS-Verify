export type System = "plain" | "rag" | "verify" | "selfcheck";
export type Verdict = "SUPPORTED" | "CONTRADICTED" | "UNVERIFIABLE";
export interface Passage {
  text_id: string; chapter: string; verse: string; sanskrit_devanagari: string;
  transliteration_iast?: string; english_translation: string; source: string; license: string; score: number;
}
export interface Claim {
  text: string; citations: string[]; verdict?: Verdict; supporting_verse_ids: string[]; rationale?: string;
}
export interface AttributionFlag {
  kind: string; cited: string; message: string; closest_verse_id?: string; quoted_text?: string; actual_text?: string;
}
export interface VerifiedAnswer {
  answer: string; claims: Claim[]; attribution_flags: AttributionFlag[]; retrieved_passages: Passage[];
  trust_score: number; model_name: string; judge_model_name: string; system: System; abstained: boolean;
}
export interface Health { status: string; provider: string; model: string; mock_mode: boolean; api_calls?: number }
