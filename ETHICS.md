# Ethics

## Consent

| Person | Likeness / voice used? | Consent recorded? | Notes |
|--------|------------------------|-------------------|-------|
| Etye Almaz (portrayed character) | Stylized AI likeness; not a real photo clone | N/A for fictionalized composite — **if a real relative’s face/voice is used, record informed consent here before generation** | Update before posting |

**Gate:** If a real person’s face or voice appears without consent here, the film must not be submitted.

## Labelling

- On-film end card: “Made with AI”  
- Platform AI disclosure switched on at publish (YouTube / TikTok / Meta)  
- Leave SynthID / C2PA / watermarks intact when present

## Licences (models & outputs)

| Component | Licence / terms | Commercial use |
|-----------|-----------------|----------------|
| Wan 2.2 | Apache 2.0 | Yes (check model card) |
| ACE-Step 1.5 | MIT; trained on licensed/royalty-free/synthetic | Outputs usable commercially per project docs |
| FLUX.1 schnell / FLUX.2 klein | Check Black Forest Labs + Cloudflare terms | Note non-commercial variants if used |
| Gemini API (text/TTS) | Google AI terms; free tier may use data for training — avoid private family details | Follow current ToS |
| FFmpeg assembly | LGPL/GPL components as installed | OK for pipeline use |

## Style practice

Describe qualities (warm, grainy, hand-painted). Do not name living artists as style targets.

## Private data

Keep private family identifiers out of free endpoints that may train on inputs.
