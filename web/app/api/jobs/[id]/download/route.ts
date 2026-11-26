import { NextRequest, NextResponse } from "next/server";
import { workerConfig } from "@/lib/worker";

export const runtime = "nodejs";
export const maxDuration = 60;

export async function GET(
  req: NextRequest,
  ctx: { params: Promise<{ id: string }> },
) {
  const { id } = await ctx.params;
  const aspect = req.nextUrl.searchParams.get("aspect") || "9x16";

  try {
    const { url: WORKER_URL, secret: WORKER_SECRET } = workerConfig();
    const res = await fetch(
      `${WORKER_URL}/jobs/${id}/download?aspect=${encodeURIComponent(aspect)}`,
      {
        headers: { "X-Worker-Secret": WORKER_SECRET },
        cache: "no-store",
      },
    );
    if (!res.ok) {
      const text = await res.text();
      return NextResponse.json({ error: text || "Not ready" }, { status: res.status });
    }
    const buf = await res.arrayBuffer();
    const filename = aspect === "16x9" ? "final_16x9.mp4" : "final_9x16.mp4";
    return new NextResponse(buf, {
      headers: {
        "Content-Type": "video/mp4",
        "Content-Disposition": `attachment; filename="${filename}"`,
      },
    });
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Worker unreachable" },
      { status: 502 },
    );
  }
}
