# Development log

## 2026-09-30 — Audit and production scope
- Audited the existing static Canvas2D client and live Pages build.
- Preserved inventory, saves, menus, quests and campaign rules.
- Fixed priority to one Shenzhou slice, three archetypes and one city benchmark.
- Recorded current visual/combat failures in AUDIT.md and created STYLE_GUIDE.md.
- Next: replace primitive benchmark presentation, authored ground paths and camera startup; then timed combat/animation.

## Animation / combat foundation pass
- Added original three-class 36-pose atlases, eight-species and Moonveil boss atlases; metadata includes explicit row extraction for uneven generated gutters.
- Split device bindings, ability timeline/geometry, animation presentation and ambient systems from existing progression integration. Preserved save key, equipment, crafting, shops and quest logic.
- Contact-time damage, true projectile travel with swept collision, recovery/cooldown, movement scaling while casting, continuous dodge/cancel and death presentation before recovery.
- Enemy timing/speed/range differ across eight species; phase-two boss alternates three target patterns and summons adds. Corrected world-space telegraphs.
- Added authored secondary city props, cached paved square, service walkers, quality preferences, gradual atmosphere and original synthesized audio. Removed auto combat from the active flow.
- Pure regression checks passed: no pre-impact damage, forward cone geometry, swept first-hit projectile and piercing multiple contacts.
- Browser production QA pending for this new source commit. Existing city benchmark was visually inspected in desktop and 390×844 portrait; no world boundary/void visible, but old status/quest panels were too large.
- Known gaps: no full animation blend/rig pipeline, enemy locomotion limited, dungeon authored corridors, chunk streaming, true online adapter, real phone profiling. Current benchmark gate remains under review.
