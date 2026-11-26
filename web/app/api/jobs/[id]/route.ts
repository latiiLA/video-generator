import { NextRequest, NextResponse } from "next/server";

const WORKER_URL = process.env.WORKER_URL || "http://localhost:8080";
const WORKER_SECRET = process.env.WORKER_SECRET || "change-me";

export async function GET(
  _req: NextRequest,
  ctx: { params: Promise<{ id: string }> },
) {
  const { id } = await ctx.params;
  try {
    const res = await fetch(`${WORKER_URL}/jobs/${id}`, {
      headers: { "X-Worker-Secret": WORKER_SECRET },
      cache: "no-store",
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      return NextResponse.json(
        { error: data.detail || "Not found" },
        { status: res.status },
      );
    }
    return NextResponse.json(data);
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Worker unreachable" },
      { status: 502 },
    );
  }
}
