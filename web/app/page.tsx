"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { formatError } from "@/lib/errors";
import {
  FILM,
  PIPELINE_STAGES,
  SHOTS,
  driveDownloadUrl,
  drivePreviewUrl,
  driveViewUrl,
} from "@/lib/film";

type Job = {
  id: string;
  status: string;
  stage?: string | null;
  error?: string | null;
};

type Tab = "film" | "generate" | "storyboard" | "pipeline";
type Mode = "demo" | "full";
type Aspect = "16x9" | "9x16";

const DEFAULT_STORY = `I was in Grade Seven when I first visited my grandfather's home in the countryside.
I thought it was only a visit. Endless greenery, summer rain, gojo nights, and fresh milk changed how I see ordinary moments.`;

function stageIndex(stage?: string | null, status?: string | null): number {
  if (status === "ready") return PIPELINE_STAGES.length - 1;
  if (!stage || stage === "queued") return 0;
  const i = PIPELINE_STAGES.findIndex((s) => s.id === stage);
  return i >= 0 ? i : 0;
}

export default function HomePage() {
  const [tab, setTab] = useState<Tab>("film");
  const [aspect, setAspect] = useState<Aspect>("16x9");
  const [shotIdx, setShotIdx] = useState(0);
  const [mode, setMode] = useState<Mode>("demo");
  const [storyline, setStoryline] = useState(DEFAULT_STORY);
  const [language, setLanguage] = useState("en");
  const [job, setJob] = useState<Job | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const shot = SHOTS[shotIdx];
  const activeIdx = useMemo(
    () => stageIndex(job?.stage, job?.status),
    [job?.stage, job?.status],
  );
  const progressPct = useMemo(() => {
    if (!job) return 0;
    if (job.status === "ready") return 100;
    if (job.status === "failed") {
      return Math.max(8, Math.round((activeIdx / (PIPELINE_STAGES.length - 1)) * 100));
    }
    return Math.min(96, Math.round((activeIdx / (PIPELINE_STAGES.length - 1)) * 100));
  }, [job, activeIdx]);

  // Film tab always plays the Drive showcase cuts. Fresh job outputs stay available via Generate.
  const drivePreview = drivePreviewUrl(aspect);
  const driveView = driveViewUrl(aspect);
  const driveDownload = driveDownloadUrl(aspect);
  const jobSrc =
    job?.status === "ready" ? `/api/jobs/${job.id}/download?aspect=${aspect}` : null;

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
        if (data.status === "failed") setError(formatError(data.error, "Job failed"));
        if (data.status === "ready") setTab("film");
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
          : { demo: false, storyline, language };
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
    <div className="app">
      <aside className="sidebar">
        <div className="side-brand">
          <div className="kicker">{FILM.brand}</div>
          <h1>{FILM.title}</h1>
          <p>{FILM.place}</p>
          <div className="side-meta">
            <span>
              By <strong>{FILM.author}</strong>
            </span>
            <span>{FILM.academy}</span>
          </div>
        </div>

        <nav className="nav" aria-label="Primary">
          {(
            [
              ["film", "Film", "▶"],
              ["generate", "Generate", "✦"],
              ["storyboard", "Storyboard", "☰"],
              ["pipeline", "Pipeline", "◇"],
            ] as const
          ).map(([id, label, ico]) => (
            <button
              key={id}
              type="button"
              className={tab === id ? "active" : ""}
              onClick={() => setTab(id)}
            >
              <span className="ico" aria-hidden>
                {ico}
              </span>
              {label}
            </button>
          ))}
        </nav>

        <div className="side-foot">
          <div className="by">{FILM.madeBy}</div>
          <div>{FILM.madeWith}</div>
        </div>
      </aside>

      <main className="workspace">
        <section className="hero">
          <div className="chips">
            <span className="chip">{FILM.badge}</span>
            <span className="chip soft">{FILM.academy}</span>
            <span className="chip soft">{FILM.madeBy}</span>
          </div>
          <h2>{FILM.title}</h2>
          <p className="synopsis">{FILM.synopsis}</p>
          <div className="hero-actions">
            <div className="aspect" role="group" aria-label="Aspect ratio">
              <button
                type="button"
                className={aspect === "16x9" ? "active" : ""}
                onClick={() => setAspect("16x9")}
              >
                Horizontal 16:9
              </button>
              <button
                type="button"
                className={aspect === "9x16" ? "active" : ""}
                onClick={() => setAspect("9x16")}
              >
                Vertical 9:16
              </button>
            </div>
            <button type="button" className="ghost" onClick={() => setTab("generate")}>
              Generate new cut
            </button>
          </div>
        </section>

        {tab === "film" && (
          <div className="layout-film">
            <section className="panel">
              <div className={`player-wrap ${aspect === "9x16" ? "vertical" : ""}`}>
                <iframe
                  key={drivePreview}
                  src={drivePreview}
                  title={`${FILM.title} · ${FILM.drive[aspect].label}`}
                  allow="autoplay; encrypted-media; picture-in-picture"
                  allowFullScreen
                  className="drive-frame"
                />
              </div>
              <div className="player-bar">
                <div className="cred">
                  Watching Google Drive showcase · <b>{FILM.madeBy}</b>
                </div>
                <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                  <a className="link-btn" href={driveView} target="_blank" rel="noreferrer">
                    Open on Drive
                  </a>
                  <a className="link-btn" href={driveDownload} target="_blank" rel="noreferrer">
                    Download {aspect}
                  </a>
                  <a
                    className="link-btn"
                    href={driveViewUrl("16x9")}
                    target="_blank"
                    rel="noreferrer"
                  >
                    16:9 on Drive
                  </a>
                  <a
                    className="link-btn"
                    href={driveViewUrl("9x16")}
                    target="_blank"
                    rel="noreferrer"
                  >
                    9:16 on Drive
                  </a>
                  {jobSrc && (
                    <a className="link-btn" href={`${jobSrc}&download=1`}>
                      Latest job file
                    </a>
                  )}
                </div>
              </div>
            </section>

            <section className="panel scene">
              <h3>Scene chapters</h3>
              <p className="lede">
                Shot {shotIdx + 1} of {SHOTS.length} · bilingual memory beats from the storyboard.
              </p>
              <div className="shot-nav" aria-label="Jump to shot">
                {SHOTS.map((s, i) => (
                  <button
                    key={s.id}
                    type="button"
                    className={i === shotIdx ? "active" : ""}
                    onClick={() => setShotIdx(i)}
                  >
                    {i + 1}
                  </button>
                ))}
              </div>
              <article className="shot-card">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={`/api/media/keyframe/${shot.id}`}
                  alt={shot.label}
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = "none";
                  }}
                />
                <div className="shot-body">
                  <div className="label">
                    S{shotIdx + 1} · {shot.label}
                  </div>
                  <p className="am">{shot.narration_am}</p>
                  <p className="en">{shot.narration_en}</p>
                  <div className="shot-meta">
                    <span>Camera: {shot.camera}</span>
                    <span>Framing: {shot.framing}</span>
                    <span>{shot.reason}</span>
                  </div>
                </div>
              </article>
            </section>
          </div>
        )}

        {tab === "generate" && (
          <section className="panel gen">
            <h3>Generate on this page</h3>
            <p className="lede">
              Default is a short Quick Test (~18s) so you can verify the worker fast. Full Film uses your
              storyline. English male narration + Amharic captions.
            </p>

            <div className="mode" role="tablist" aria-label="Mode">
              <button
                type="button"
                className={mode === "demo" ? "active" : ""}
                onClick={() => setMode("demo")}
              >
                <strong>Quick Test</strong>
                <span>6 short shots · smoke job</span>
              </button>
              <button
                type="button"
                className={mode === "full" ? "active" : ""}
                onClick={() => setMode("full")}
              >
                <strong>Full Film</strong>
                <span>Your storyline or storyboard.json</span>
              </button>
            </div>

            <form onSubmit={onSubmit}>
              {mode === "full" && (
                <>
                  <label className="field">
                    Storyline
                    <textarea
                      value={storyline}
                      onChange={(e) => setStoryline(e.target.value)}
                      required
                    />
                  </label>
                  <p className="hint">Prose (≥20 chars) or paste full storyboard.json.</p>
                  <label className="field">
                    Narration language
                    <select value={language} onChange={(e) => setLanguage(e.target.value)}>
                      <option value="en">English</option>
                      <option value="am">Amharic</option>
                      <option value="om">Afaan Oromo</option>
                    </select>
                  </label>
                </>
              )}
              {mode === "demo" && (
                <p className="hint">
                  Uses the embedded demo storyboard — English VO, Amharic captions, Ken Burns.
                </p>
              )}
              <button className="primary" type="submit" disabled={!canSubmit}>
                {busy
                  ? mode === "demo"
                    ? "Running Quick Test…"
                    : "Generating…"
                  : mode === "demo"
                    ? "Run Quick Test"
                    : "Generate film"}
              </button>
            </form>

            {error && <div className="error">{error}</div>}

            <div className="progress">
              <div className="bar" aria-hidden>
                <span style={{ width: `${progressPct}%` }} />
              </div>
              <p className="jobline">
                {job ? (
                  <>
                    Job <b>{job.id}</b> · {progressPct}% · {job.status}
                    {job.stage ? ` · ${job.stage}` : ""}
                  </>
                ) : (
                  "Waiting for a run. Quick Test is selected by default."
                )}
              </p>
              <div className="stages">
                {PIPELINE_STAGES.map((stage, idx) => {
                  const failed = job?.status === "failed" && idx === activeIdx;
                  const done = !!job && !failed && (job.status === "ready" || idx < activeIdx);
                  const active =
                    !!job && job.status !== "ready" && job.status !== "failed" && idx === activeIdx;
                  const cls = failed ? "failed" : done ? "done" : active ? "active" : "";
                  return (
                    <div key={stage.id} className={`stage ${cls}`}>
                      <span className="dot" />
                      <span>{stage.label}</span>
                      <span style={{ color: "var(--muted)", fontSize: "0.75rem" }}>
                        {failed ? "failed" : done ? "done" : active ? "running" : "pending"}
                      </span>
                    </div>
                  );
                })}
              </div>
              {job?.status === "ready" && (
                <div style={{ marginTop: "0.9rem", display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                  <button type="button" className="primary" onClick={() => setTab("film")}>
                    Watch on Film tab
                  </button>
                  <a className="link-btn" href={`/api/jobs/${job.id}/download?aspect=16x9&download=1`}>
                    Download 16:9
                  </a>
                  <a className="link-btn" href={`/api/jobs/${job.id}/download?aspect=9x16&download=1`}>
                    Download 9:16
                  </a>
                </div>
              )}
            </div>
          </section>
        )}

        {tab === "storyboard" && (
          <section className="panel scene">
            <h3>Storyboard contract</h3>
            <p className="lede">
              Nine shots from grandfather&apos;s countryside—English narration lines with Amharic
              captions. {FILM.madeBy}.
            </p>
            <div className="pipe-grid">
              {SHOTS.map((s, i) => (
                <article key={s.id} className="pipe-card">
                  <h4>
                    S{i + 1} · {s.label}
                  </h4>
                  <p>
                    {s.reason} · {s.framing} · {s.camera}
                  </p>
                </article>
              ))}
            </div>
          </section>
        )}

        {tab === "pipeline" && (
          <section className="panel pipe">
            <h3>How the pipeline works</h3>
            <p className="lede">
              One storyboard file is the contract. Stages cache by hash, then FFmpeg builds dual-aspect
              films with ducked narration and burned-in Amharic captions.
            </p>
            <div className="pipe-grid">
              <article className="pipe-card">
                <h4>1. Storyboard</h4>
                <p>Validated JSON for shots, prompts, narration, music, and end card.</p>
              </article>
              <article className="pipe-card">
                <h4>2. Generative stages</h4>
                <p>Narration → keyframes → motion → music, with cache reuse.</p>
              </article>
              <article className="pipe-card">
                <h4>3. Assembly</h4>
                <p>Native 9:16 and 16:9 timelines, loudnorm mix, captions, end card.</p>
              </article>
              <article className="pipe-card">
                <h4>4. Showcase UI</h4>
                <p>Watch the cut here, browse scene chapters, then generate a new test or full film.</p>
              </article>
            </div>
          </section>
        )}

        <p className="footer-credit">
          <b>{FILM.madeBy}</b> · {FILM.madeWith} · {FILM.place}
        </p>
      </main>
    </div>
  );
}
