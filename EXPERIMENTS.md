# Experiments

Log: hypothesis → change → result. Target ~10 entries.

| # | Hypothesis | Change | Result |
|---|------------|--------|--------|
| 1 | Radio cut first will catch pacing issues cheaper than regenerating images | Build `make radio` before keyframes | _pending_ |
| 2 | Fixed style_block reduces character drift | Append style_block to every image prompt | _pending_ |
| 3 | Ken Burns is acceptable for shots where Wan quota fails | `SHOT_BACKEND` fallback chain | _pending_ |
| 4 | Short motion prompts beat full scene re-description for I2V | Motion-only prompts in storyboard | _pending_ |
| 5 | Generating 3 music candidates improves choice quality | ACE-Step batch → pick one | _pending_ |
| 6 | Ducking threshold 0.02 / ratio 6 keeps voice clear | FFmpeg sidechaincompress defaults | _pending_ |
| 7 | Amharic TTS needs native listener check | Play narration to native speaker | _pending_ |
| 8 | Mid-frame subjects survive both 9:16 and 16:9 | Compose keyframes centered | _pending_ |
| 9 | Hash cache saves quota on prompt tweaks | content_hash per stage | _pending_ |
| 10 | Web Ken Burns path finishes under free-tier limits | Default web motion = kenburns | _pending_ |
