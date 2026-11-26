import { NextRequest, NextResponse } from "next/server";
import { createReadStream, existsSync, statSync } from "fs";
import path from "path";
import { Readable } from "stream";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/** Serve the local showcase film for in-browser playback. */
export async function GET(req: NextRequest) {
  const aspect = req.nextUrl.searchParams.get("aspect") === "9x16" ? "9x16" : "16x9";
  const download = req.nextUrl.searchParams.get("download") === "1";
  const filename = aspect === "9x16" ? "final_9x16.mp4" : "final_16x9.mp4";

  const candidates = [
    path.join(process.cwd(), "..", "outputs", "film", filename),
    path.join(process.cwd(), "outputs", "film", filename),
  ];
  const filePath = candidates.find((p) => existsSync(p));
  if (!filePath) {
    return NextResponse.json(
      { error: `Showcase film not found (${filename}). Generate a film first.` },
      { status: 404 },
    );
  }

  const stat = statSync(filePath);
  const nodeStream = createReadStream(filePath);
  const webStream = Readable.toWeb(nodeStream) as unknown as ReadableStream;

  return new NextResponse(webStream, {
    headers: {
      "Content-Type": "video/mp4",
      "Content-Length": String(stat.size),
      "Accept-Ranges": "bytes",
      "Cache-Control": "public, max-age=60",
      "Content-Disposition": download
        ? `attachment; filename="${filename}"`
        : `inline; filename="${filename}"`,
    },
  });
}
