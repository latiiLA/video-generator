import { NextRequest, NextResponse } from "next/server";
import { existsSync, readFileSync } from "fs";
import path from "path";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/** Serve a local keyframe still for scene chapters. */
export async function GET(
  _req: NextRequest,
  ctx: { params: Promise<{ id: string }> },
) {
  const { id } = await ctx.params;
  if (!/^shot_\d{2}$/.test(id)) {
    return NextResponse.json({ error: "Invalid shot id" }, { status: 400 });
  }

  const filename = `${id}.png`;
  const candidates = [
    path.join(process.cwd(), "..", "outputs", "keyframes", filename),
    path.join(process.cwd(), "outputs", "keyframes", filename),
  ];
  const filePath = candidates.find((p) => existsSync(p));
  if (!filePath) {
    return NextResponse.json({ error: "Keyframe not found" }, { status: 404 });
  }

  const buf = readFileSync(filePath);
  return new NextResponse(buf, {
    headers: {
      "Content-Type": "image/png",
      "Cache-Control": "public, max-age=120",
    },
  });
}
