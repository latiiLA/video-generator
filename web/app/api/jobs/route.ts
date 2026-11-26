import { NextRequest, NextResponse } from "next/server";
import { formatError } from "@/lib/errors";
import { workerConfig } from "@/lib/worker";

export const runtime = "nodejs";
export const maxDuration = 60;

export async function POST(req: NextRequest) {
  try {
    const { url: WORKER_URL, secret: WORKER_SECRET } = workerConfig();
    const body = await req.json();
    const demo = Boolean(body.demo);
    let storyline = String(body.storyline || "").trim();
    const language = String(body.language || "en");
    let storyboard: Record<string, unknown> | null =
      body.storyboard && typeof body.storyboard === "object" && !Array.isArray(body.storyboard)
        ? (body.storyboard as Record<string, unknown>)
        : null;

    // UI paste of storyboard.json into the storyline box
    if (!storyboard && storyline.startsWith("{") && storyline.includes('"shots"')) {
      try {
        const parsed = JSON.parse(storyline);
        if (parsed && typeof parsed === "object" && Array.isArray(parsed.shots)) {
          storyboard = parsed;
          storyline = String(parsed.logline || parsed.title || "storyboard.json");
        }
      } catch {
        return NextResponse.json(
          { error: "Storyboard JSON could not be parsed. Paste valid storyboard.json." },
          { status: 400 },
        );
      }
    }

    if (!demo && !storyboard && storyline.length < 20) {
      return NextResponse.json(
        { error: "Storyline too short (or paste a full storyboard.json, or use Quick Test)" },
        { status: 400 },
      );
    }

    const payload: Record<string, unknown> = {
      language: storyboard?.language || language,
      storyline:
        storyline ||
        String(storyboard?.logline || storyboard?.title || (demo ? "5-second quick test" : "storyboard job")),
      demo,
    };
    if (storyboard) payload.storyboard = storyboard;

    const res = await fetch(`${WORKER_URL}/jobs`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Worker-Secret": WORKER_SECRET,
      },
      body: JSON.stringify(payload),
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      return NextResponse.json(
        { error: formatError(data.detail || data.error || data, "Worker failed") },
        { status: res.status },
      );
    }
    return NextResponse.json(data);
  } catch (err) {
    return NextResponse.json(
      { error: formatError(err, "Worker unreachable") },
      { status: 502 },
    );
  }
}
