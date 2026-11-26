"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { formatError } from "@/lib/errors";

type Job = {
  id: string;
  status: string;
  stage?: string | null;
  error?: string | null;
  vertical_url?: string | null;
  horizontal_url?: string | null;
};

type Mode = "demo" | "full";
type Tab = "generate" | "pipeline" | "about";

const STAGES = [
  { id: "queued", label: "Queued" },
  { id: "script", label: "Storyboard" },
  { id: "narration", label: "Narration" },
  { id: "keyframes", label: "Keyframes" },
  { id: "shots", label: "Motion shots" },
  { id: "music", label: "Score" },
  { id: "assemble", label: "Assemble" },
  { id: "done", label: "Ready" },
] as const;

const DEFAULT_STORY = `I was in Grade Seven when I first visited my grandfather's home in the countryside.
I thought it was only a visit. Endless greenery, summer rain, gojo nights, and fresh milk changed how I see ordinary moments.`;

function stageIndex(stage?: string | null, status?: string | null): number {
  if (status === "ready") return STAGES.length - 1;
  if (status === "failed") {
    const i = STAGES.findIndex((s) => s.id === stage);
    return i >= 0 ? i : 0;
  }
  if (!stage || stage === "queued") return 0;
  if (stage === "failed") return 0;
  const i = STAGES.findIndex((s) => s.id === stage);
  return i >= 0 ? i : 0;
}

export default function HomePage() {
  const [tab, setTab] = useState<Tab>("generate");
  const [mode, setMode] = useState<Mode>("demo");
  const [storyline, setStoryline] = useState(DEFAULT_STORY);
  const [language, setLanguage] = useState("en");
  const [captionLanguage, setCaptionLanguage] = useState("am");
  const [job, setJob] = useState<Job | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [aspect, setAspect] = useState<"9x16" | "16x9">("16x9");

  const activeIdx = useMemo(
    () => stageIndex(job?.stage, job?.status),
    [job?.stage, job?.status],
  );
  const progressPct = useMemo(() => {
    if (!job) return 0;
    if (job.status === "ready") return 100;
    if (job.status === "failed") return Math.max(8, Math.round((activeIdx / (STAGES.length - 1)) * 100));
    return Math.min(96, Math.round((activeIdx / (STAGES.length - 1)) * 100));
  }, [job, activeIdx]);

  useEffect(() => {
    if (!job?.id || job.status === "ready" || job.status === "failed") return;
    const t = setInterval(async () => {
      const res = await fetch(`/api/jobs/${job.id}`);
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(formatError(data.error || data.detail || data, "Failed to poll job"));
        setBusy(false);
        return;
      }
      setJob(data as Job);
      if (data.status === "ready" || data.status === "failed") {
        setBusy(false);
        if (data.status === "failed") {
          setError(formatError(data.error, "Job failed"));
        }
      }
    }, 1800);
    return () => clearInterval(t);
  }, [job]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    setJob(null);
    setTab("generate");
    try {
      const payload =
        mode === "demo"
          ? { demo: true, language: "en" }
          : {
              demo: false,
              storyline,
              language,
              // Worker currently uses storyboard language/subtitle fields when provided;
              // for prose jobs language is narration language.
            };

      const res = await fetch("/api/jobs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(formatError(data.error || data.detail || data, "Failed to start job"));
      }
      setJob(data as Job);
    } catch (err) {
      setBusy(false);
      setError(formatError(err, "Something went wrong"));
    }
  }

  const canSubmit =
    !busy &&
    (mode === "demo" ||
      storyline.trim().length >= 20 ||
      (storyline.trim().startsWith("{") && storyline.includes('"shots"')));

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-kicker">Heritage Short</div>
          <h1 className="brand-title">Family story → short film</h1>
          <p className="brand-sub">Generate on this page. Watch the pipeline move.</p>
        </div>

        <nav className="nav" aria-label="Primary">
          <button
            type="button"
            className={`nav-btn ${tab === "generate" ? "active" : ""}`}
            onClick={() => setTab("generate")}
          >
            <span className="nav-ico" aria-hidden>
              ▶
            </span>
            Generate
          </button>
          <button
            type="button"
            className={`nav-btn ${tab === "pipeline" ? "active" : ""}`}
            onClick={() => setTab("pipeline")}
          >
            <span className="nav-ico" aria-hidden>
              ◆
            </span>
            Pipeline
          </button>
          <button
            type="button"
            className={`nav-btn ${tab === "about" ? "active" : ""}`}
            onClick={() => setTab("about")}
          >
            <span className="nav-ico" aria-hidden>
              ○
            </span>
            About
          </button>
        </nav>

        <p className="sidebar-foot">
          Default mode is a <strong>5-second quick test</strong> so you can verify the UI without a
          full-length render.
        </p>
      </aside>

      <main className="workspace">
        <section className="hero-panel">
          <div className="chip-row">
            <span className="chip">AI-generated film</span>
            <span className="chip muted">storyboard.json contract</span>
          </div>
          <h2 className="hero-title">The Summer I Discovered Another World</h2>
          <p className="hero-copy">
            Share a childhood storyline—or run the built-in 5-second test. Narration, Ethiopian
            highland visuals, score, Amharic captions, and dual-aspect export land here when ready.
          </p>
        </section>

        {tab === "generate" && (
          <div className="grid-main">
            <section className="panel">
              <h2>Generate</h2>
              <p className="panel-lede">
                Start with Quick Test to confirm the worker is alive, then switch to Full Film when
                you want the complete story.
              </p>

              <div className="mode-toggle" role="tablist" aria-label="Generation mode">
                <button
                  type="button"
                  className={`mode-btn ${mode === "demo" ? "active" : ""}`}
                  onClick={() => setMode("demo")}
                >
                  <strong>Quick Test · 5s</strong>
                  <span>Default. One shot, English male VO, Amharic captions.</span>
                </button>
                <button
                  type="button"
                  className={`mode-btn ${mode === "full" ? "active" : ""}`}
                  onClick={() => setMode("full")}
                >
                  <strong>Full Film</strong>
                  <span>Your storyline or pasted storyboard.json.</span>
                </button>
              </div>

              <form className="generate-form" onSubmit={onSubmit}>
                {mode === "full" && (
                  <>
                    <label className="field">
                      Storyline
                      <textarea
                        value={storyline}
                        onChange={(e) => setStoryline(e.target.value)}
                        placeholder="The summer I spent at my grandfather's place…"
                        required={mode === "full"}
                      />
                    </label>
                    <p className="hint">
                      Prose (≥20 characters) or paste a full <code>storyboard.json</code>.
                    </p>
                    <div className="row-2">
                      <label className="field">
                        Narration language
                        <select value={language} onChange={(e) => setLanguage(e.target.value)}>
                          <option value="en">English</option>
                          <option value="am">Amharic</option>
                          <option value="om">Afaan Oromo</option>
                        </select>
                      </label>
                      <label className="field">
                        Caption language
                        <select
                          value={captionLanguage}
                          onChange={(e) => setCaptionLanguage(e.target.value)}
                          disabled
                        >
                          <option value="am">Amharic</option>
                        </select>
                      </label>
                    </div>
                    <p className="hint">
                      Full films currently burn Amharic captions. Demo uses English narration +
                      Amharic captions automatically.
                    </p>
                  </>
                )}

                {mode === "demo" && (
                  <p className="hint">
                    Uses <code>storyboards/demo_5s.json</code> — about five seconds of picture and
                    voice so you can test downloads quickly.
                  </p>
                )}

                <div className="actions">
                  <button type="submit" className="primary-btn" disabled={!canSubmit}>
                    {busy
                      ? mode === "demo"
                        ? "Running 5s test…"
                        : "Generating film…"
                      : mode === "demo"
                        ? "Run 5-second test"
                        : "Generate film"}
                  </button>
                  {job?.status === "ready" && (
                    <button
                      type="button"
                      className="ghost-btn"
                      onClick={() => {
                        setJob(null);
                        setError(null);
                      }}
                    >
                      Clear result
                    </button>
                  )}
                </div>
              </form>

              {error && <div className="error-box">{error}</div>}
            </section>

            <section className="panel progress-panel">
              <h2>Live progress</h2>
              <div className="bar-track" aria-hidden>
                <div className="bar-fill" style={{ width: `${progressPct}%` }} />
              </div>
              <p className="job-meta">
                {job ? (
                  <>
                    Job <strong>{job.id}</strong> · {progressPct}% · status{" "}
                    <strong>{job.status}</strong>
                    {job.stage ? (
                      <>
                        {" "}
                        · stage <strong>{job.stage}</strong>
                      </>
                    ) : null}
                  </>
                ) : (
                  "Waiting for a run. Quick Test is selected by default."
                )}
              </p>

              <div className="stage-list" style={{ marginTop: "1rem" }}>
                {STAGES.map((stage, idx) => {
                  const failed = job?.status === "failed" && idx === activeIdx;
                  const done =
                    !!job &&
                    !failed &&
                    (job.status === "ready" || idx < activeIdx);
                  const active =
                    !!job &&
                    job.status !== "ready" &&
                    job.status !== "failed" &&
                    idx === activeIdx;
                  const cls = failed ? "failed" : done ? "done" : active ? "active" : "";
                  return (
                    <div key={stage.id} className={`stage ${cls}`}>
                      <span className="stage-dot" />
                      <span className="stage-label">{stage.label}</span>
                      <span className="stage-meta">
                        {failed ? "failed" : done ? "done" : active ? "running" : "pending"}
                      </span>
                    </div>
                  );
                })}
              </div>

              {job?.status === "ready" && (
                <>
                  <div className="aspect-toggle" role="group" aria-label="Download aspect">
                    <button
                      type="button"
                      className={`aspect-btn ${aspect === "9x16" ? "active" : ""}`}
                      onClick={() => setAspect("9x16")}
                    >
                      Vertical 9:16
                    </button>
                    <button
                      type="button"
                      className={`aspect-btn ${aspect === "16x9" ? "active" : ""}`}
                      onClick={() => setAspect("16x9")}
                    >
                      Horizontal 16:9
                    </button>
                  </div>
                  <div className="links">
                    <a href={`/api/jobs/${job.id}/download?aspect=${aspect}`}>
                      Download {aspect}
                    </a>
                    <a href={`/api/jobs/${job.id}/download?aspect=9x16`}>Also 9:16</a>
                    <a href={`/api/jobs/${job.id}/download?aspect=16x9`}>Also 16:9</a>
                  </div>
                </>
              )}
            </section>
          </div>
        )}

        {tab === "pipeline" && (
          <section className="panel">
            <h2>How the pipeline works</h2>
            <p className="panel-lede">
              One storyboard file is the contract. Each stage writes cached outputs, then FFmpeg
              assembles dual-aspect films with ducked narration and burned-in captions.
            </p>
            <div className="pipeline-cards">
              <article className="pipe-card">
                <h3>1. Storyboard contract</h3>
                <p>Validated JSON defines shots, prompts, narration, music, and end card.</p>
              </article>
              <article className="pipe-card">
                <h3>2. Generative stages</h3>
                <p>Narration → keyframes → motion → music, with hash caching between runs.</p>
              </article>
              <article className="pipe-card">
                <h3>3. FFmpeg assembly</h3>
                <p>Native 9:16 and 16:9 timelines, loudnorm mix, Amharic captions, end card.</p>
              </article>
              <article className="pipe-card">
                <h3>4. UI quick test</h3>
                <p>
                  The Generate tab defaults to a ~5s demo so reviewers can exercise the full path
                  without waiting for a long film.
                </p>
              </article>
            </div>
          </section>
        )}

        {tab === "about" && (
          <section className="panel">
            <h2>About this build</h2>
            <p className="panel-lede">
              Heritage Short turns a personal Ethiopian countryside memory into a labeled
              AI-generated short. Visual prompts emphasize Horn of Africa features; the default
              demo narrates in English with Amharic captions.
            </p>
            <div className="pipeline-cards">
              <article className="pipe-card">
                <h3>Outputs</h3>
                <p>
                  <code>final_9x16.mp4</code> and <code>final_16x9.mp4</code> from the same job.
                </p>
              </article>
              <article className="pipe-card">
                <h3>Worker</h3>
                <p>
                  Local or Railway FastAPI worker at <code>WORKER_URL</code>. Keep the worker
                  running to test from this UI.
                </p>
              </article>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
