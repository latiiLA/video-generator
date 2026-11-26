"use client";

import { FormEvent, useEffect, useState } from "react";

type Job = {
  id: string;
  status: string;
  stage?: string | null;
  error?: string | null;
  vertical_url?: string | null;
  horizontal_url?: string | null;
};

export default function HomePage() {
  const [storyline, setStoryline] = useState("");
  const [language, setLanguage] = useState("am");
  const [job, setJob] = useState<Job | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!job?.id || job.status === "ready" || job.status === "failed") return;
    const t = setInterval(async () => {
      const res = await fetch(`/api/jobs/${job.id}`);
      if (!res.ok) return;
      const data = (await res.json()) as Job;
      setJob(data);
      if (data.status === "ready" || data.status === "failed") setBusy(false);
    }, 2500);
    return () => clearInterval(t);
  }, [job]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    setJob(null);
    try {
      const res = await fetch("/api/jobs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ storyline, language }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to start job");
      setJob(data as Job);
    } catch (err) {
      setBusy(false);
      setError(err instanceof Error ? err.message : "Something went wrong");
    }
  }

  return (
    <main>
      <h1 className="brand">Heritage Short</h1>
      <p className="lede">
        Share a family storyline. We turn it into a short film you can download—
        narration, pictures, score, and an AI end card.
      </p>

      <form onSubmit={onSubmit}>
        <label>
          Storyline
          <textarea
            value={storyline}
            onChange={(e) => setStoryline(e.target.value)}
            placeholder="How your grandmother walked to the market in Dessie…"
            required
            minLength={20}
          />
        </label>
        <div className="row">
          <label>
            Narration language
            <select value={language} onChange={(e) => setLanguage(e.target.value)}>
              <option value="am">Amharic</option>
              <option value="en">English</option>
              <option value="om">Afaan Oromo</option>
              <option value="ti">Tigrinya</option>
              <option value="so">Somali</option>
            </select>
          </label>
        </div>
        <button type="submit" disabled={busy || storyline.trim().length < 20}>
          {busy ? "Generating…" : "Generate film"}
        </button>
      </form>

      {error && (
        <div className="status error">
          <strong>Error</strong>
          <div>{error}</div>
        </div>
      )}

      {job && (
        <div className="status">
          <strong>Job {job.id}</strong>
          <div>
            Status: {job.status}
            {job.stage ? ` · stage: ${job.stage}` : ""}
          </div>
          {job.error && <div className="error">{job.error}</div>}
          {job.status === "ready" && (
            <div className="links">
              <a href={`/api/jobs/${job.id}/download?aspect=9x16`}>Download 9:16</a>
              <a href={`/api/jobs/${job.id}/download?aspect=16x9`}>Download 16:9</a>
            </div>
          )}
        </div>
      )}

      <p className="foot">Films are labelled as AI-generated. Pipeline contract: storyboard.json</p>
    </main>
  );
}
