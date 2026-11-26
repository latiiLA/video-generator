# Design

## Audience

Family who know this grandfather’s countryside home, and friends who grew up only in the city—people watching on a phone who should feel how a “simple visit” can open another world.

## Intent

Feel the wonder of that Grade Seven summer—and understand that the most beautiful journeys can be the ones that take us back to where we first learned to see.

## Film

**Working title:** The Summer I Discovered Another World  
**Source:** Personal childhood essay (grandparents’ countryside; not the Kumsa Moroda history piece).  
**Logline:** In Grade Seven, a first visit to grandfather’s countryside becomes a discovery of rain, land, gojo nights, fresh milk—and a way of seeing that never leaves.

**Language:** English male narration; Amharic burned-in captions (primary); English available in storyboard fields.  
**Length plan:** 9 shots + ~3s end card ≈ 75–85s (meets 60–90s).  
**Author credit:** Made by Lata Amenu.

## Chronology (every shot has a reason)

| Shot | Reason |
|------|--------|
| 1 Arrival as Grade Seven | Thought it was only a visit |
| 2 Endless greenery | The other world appears |
| 3 Summer rain | The land feels alive and different |
| 4 Work & animals | Another rhythm; life from the earth |
| 5 Gojo night | Potatoes, fire, family—simple togetherness |
| 6 Fresh milk | A small countryside miracle |
| 7 Morning adventure | Ordinary days become memory |
| 8 What I carried | Simple living, land, ordinary joy |
| 9 Years later | The summer stays; journeys that take us back |

## Separated from Kumsa Moroda

`storyboards/kumsa_moroda.json` is a different film (public history / Nekemte leader). This storyboard is only the personal grandparents summer. Active contract: `storyboard.json` ← `wallaga_summer.json`.

## User test 1 — radio cut

- **Date:** November 2026  
- **Prototype:** narration-first / radio path (`make radio` and early VO assembly)  
- **Participants (≥3):** three listeners (classmates + family; countryside-familiar and city-only)  
- **What they said:** Opening “only a visit” line lands; gojo + milk are the emotional centre; Oromo TTS path was hard to trust; English VO clearer for mixed listeners; Amharic on-screen text helps relatives.  
- **What we changed:** Locked nine-beat personal Wallaga chronology (not Kumsa lecture); English narration spine; Amharic burned-in captions; kept longer beats on gojo and milk.

## User test 2 — near-final cut

- **Date:** November 2026  
- **Prototype:** `outputs/film/final_9x16.mp4` (+ `final_16x9.mp4`)  
- **Participants (≥3):** three viewers (phone-first vertical + one desktop horizontal)  
- **What they said:** Vertical fits phone audience; faces must read Ethiopian / Horn of Africa; gentle Ken Burns is acceptable if voice+captions carry the story; AI label fine; author credit matters.  
- **What we changed:** Stronger Ethiopian descriptors in `style_block` / prompts; Ken Burns default; dual-aspect ship; Film tab Drive embeds + “Made by Lata Amenu” in UI.
