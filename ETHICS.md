# Ethics

## Consent

Film subject: a **personal family memory** (summer in rural Wallaga). Portrayal is stylized AI imagery of a generic grandchild and elders — **not** photoreal clones of named living relatives, and **not** a cloned real voice.

| Person / subject | Likeness / voice used? | Consent recorded? | Notes |
|------------------|------------------------|-------------------|-------|
| Family memory (Wallaga summer) | Stylized AI scenes; Gemini TTS stock voice “Kore”, not a relative’s voice | Story told with family knowledge; no real face photo or voice clone used | If any real photo, name-as-likeness, or voice clone is added later, get informed consent **before** regenerate and record it in this table |
| Grandfather / uncles (depicted) | Generic elders in prompts, not identified real photos | Same as above | Do not upload private family photos to free endpoints |

**Gate:** If a real person’s face or voice appears without consent here, the film must not be submitted (Assignment 2 scores zero).

## Labelling

- On-film end card: “Made with AI · Summer in the Gojo”
- Platform AI disclosure switched on at publish (YouTube / TikTok / Meta)
- Leave SynthID / C2PA / watermarks intact when present

## Licences (models & outputs)

| Component | Licence / terms | Commercial use |
|-----------|-----------------|----------------|
| Wan 2.2 | Apache 2.0 | Yes (check model card) |
| ACE-Step 1.5 | MIT; trained on licensed/royalty-free/synthetic | Outputs usable commercially per project docs |
| FLUX.1 schnell (Cloudflare) | BFL + Cloudflare Workers AI terms | Note non-commercial variants if you switch models |
| Gemini API (text/TTS) | Google AI terms; free tier may train on inputs — keep private identifiers out | Follow current ToS |
| FFmpeg assembly | LGPL/GPL as installed | OK for pipeline use |
| Procedural music bed | Generated locally in-pipeline | $0; replace with ACE-Step when available |

## Style practice

Describe qualities (warm, grainy, hand-painted). Do not name living artists as style targets.

## Private data

Keep private family identifiers, exact addresses, and private photos out of free endpoints that may train on inputs. Storyboard uses place-level “Wallaga” and role words (grandfather, uncles), not ID documents or phone numbers.
