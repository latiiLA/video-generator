import { NextRequest, NextResponse } from "next/server";
import { formatError } from "@/lib/errors";
import { workerConfig } from "@/lib/worker";

export const runtime = "nodejs";
export const maxDuration = 30;

export async function GET(
  _req: NextRequest,
  ctx: { params: Promise<{ id: string }> },
) {
  const { id } = await ctx.params;
  try {
    const { url: WORKER_URL, secret: WORKER_SECRET } = workerConfig();
    const res = await fetch(`${WORKER_URL}/jobs/${id}`, {
      headers: { "X-Worker-Secret": WORKER_SECRET },
      cache: "no-store",
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      return NextResponse.json(
        { error: formatError(data.detail || data.error || data, "Not found") },
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
