import { useEffect, useState } from "react";
import { Scale } from "lucide-react";
import { compare, health } from "./api/client";
import { AnswerPanel } from "./components/AnswerPanel";
import { AskBox } from "./components/AskBox";
import { CompareView } from "./components/CompareView";
import { EvidenceDrawer } from "./components/EvidenceDrawer";
import { ExampleChips } from "./components/ExampleChips";
import { PipelineProgress } from "./components/PipelineProgress";
import { SystemToggle } from "./components/SystemToggle";
import { ThemeToggle } from "./components/ThemeToggle";
import { useAsk } from "./hooks/useAsk";
import type { Health, System, VerifiedAnswer } from "./types";

export default function App() {
  const [question, setQuestion] = useState("What does the Gita say about action and its fruits?");
  const [system, setSystem] = useState<System>("verify");
  const [dark, setDark] = useState(() => localStorage.getItem("iks-theme") === "dark");
  const [info, setInfo] = useState<Health>();
  const [compareMode, setCompareMode] = useState(false);
  const [comparison, setComparison] = useState<Record<System, VerifiedAnswer>>();
  const [selectedClaim, setSelectedClaim] = useState<number | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const { result, activeStage, error, loading, retryAfter, submit } = useAsk();

  useEffect(() => {
    document.documentElement.dataset.theme = dark ? "dark" : "light";
    localStorage.setItem("iks-theme", dark ? "dark" : "light");
    health().then(setInfo).catch(() => undefined);
  }, [dark]);

  useEffect(() => {
    if (result) {
      setSelectedClaim(0);
      setDrawerOpen(true);
    }
  }, [result]);

  const run = () => {
    setCompareMode(false);
    setComparison(undefined);
    submit(question, system);
  };
  const runCompare = async () => {
    setCompareMode(true);
    setComparison(await compare(question));
  };
  const selected = result && selectedClaim !== null ? result.claims[selectedClaim] : undefined;

  return (
    <div className="app-shell">
      <header>
        <div className="brand"><Scale /><span>IKS-Verify</span></div>
        <nav>
          <button className="text-button" onClick={runCompare}>Compare systems</button>
          <ThemeToggle dark={dark} onToggle={() => setDark(!dark)} />
        </nav>
      </header>
      <section className="hero">
        <div className="mandala">✦</div>
        <span className="eyebrow">Truth beyond the text</span>
        <h1>Test an answer<br />against the verses.</h1>
        <p>Grounded question answering and claim-level verification for classical Indian texts.</p>
        <AskBox value={question} onChange={setQuestion} onSubmit={run} disabled={loading} />
        <div className="hero-bottom">
          <SystemToggle value={system} onChange={setSystem} />
          <kbd>Ctrl ↵</kbd>
        </div>
        <ExampleChips onSelect={setQuestion} />
      </section>
      <PipelineProgress active={activeStage} loading={loading} />
      {loading && <div className="skeleton" aria-hidden="true"><i /><i /><i /></div>}
      {error && (
        <div className="toast error" role="alert">
          {error}
          {retryAfter ? ` Retry in ${retryAfter}s.` : " Check quota and try again."}
        </div>
      )}
      {retryAfter && (
        <p className="rate-banner">Rate limited. Automatic retry available in {retryAfter}s.</p>
      )}
      {compareMode && comparison ? (
        <CompareView results={comparison} />
      ) : result && (
        <section className="result-grid">
          <AnswerPanel result={result} selectedClaim={selectedClaim} onSelectClaim={(i) => { setSelectedClaim(i); setDrawerOpen(true); }} />
          <EvidenceDrawer
            passages={result.retrieved_passages}
            claim={selected}
            open={drawerOpen}
            onClose={() => setDrawerOpen(false)}
          />
        </section>
      )}
      <footer>
        {info && <><span>{info.provider} · {info.model || "unset"}</span>{info.mock_mode && <span className="mock">Mock mode</span>}</>}
        <span>Research prototype · ingested corpus only</span>
      </footer>
    </div>
  );
}
