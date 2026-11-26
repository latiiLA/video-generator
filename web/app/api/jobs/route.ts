import { NextRequest, NextResponse } from "next/server";
import { workerConfig } from "@/lib/worker";

export const runtime = "nodejs";
export const maxDuration = 60;

export async function POST(req: NextRequest) {
  try {
    const { url: WORKER_URL, secret: WORKER_SECRET } = workerConfig();
    const body = await req.json();
    const storyline = String(body.storyline || "").trim();
    const language = String(body.language || "am");

    if (storyline.length < 20) {
      return NextResponse.json({ error: "Storyline too short" }, { status: 400 });
    }

    const res = await fetch(`${WORKER_URL}/jobs`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Worker-Secret": WORKER_SECRET,
      },
      body: JSON.stringify({ storyline, language }),
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      return NextResponse.json(
        { error: data.detail || data.error || "Worker failed" },
        { status: res.status },
      );
    }
    return NextResponse.json(data);
  } catch (err) {
    return NextResponse.json(
      {
        error: err instanceof Error ? err.message : "Worker unreachable",
      },
      { status: 502 },
    );
  }
}
