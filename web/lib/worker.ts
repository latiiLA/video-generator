/** Shared worker connection for Vercel API routes. */

export function workerConfig() {
  const url = (process.env.WORKER_URL || "http://127.0.0.1:8080").replace(/\/$/, "");
  const secret = process.env.WORKER_SECRET || "change-me";
  const isProd = process.env.NODE_ENV === "production" || process.env.VERCEL === "1";

  if (isProd && /localhost|127\.0\.0\.1/.test(url)) {
    throw new Error(
      "WORKER_URL still points at localhost. On Vercel, set WORKER_URL to your public Railway/Render worker URL (Project → Settings → Environment Variables).",
    );
  }

  return { url, secret };
}
