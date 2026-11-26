import asyncio
from pathlib import Path

import edge_tts

TEXT = "በሰባተኛ ክፍል ነበርኩ ለመጀመሪያ ጊዜ የአያቴን የገጠር ቤት ስጎበኝ።"
OUT = Path("outputs/debug/am_edge.mp3")


async def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(TEXT, voice="am-ET-MekdesNeural", rate="-10%")
    await communicate.save(str(OUT))
    print("OK", OUT, OUT.stat().st_size)


if __name__ == "__main__":
    asyncio.run(main())
