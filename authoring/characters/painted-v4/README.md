# Painted Warrior locomotion v4

Original full-body illustrations generated with the built-in image generation tool
against `assets/warrior-directional-v1.webp`. Each shipped clip has eight views and
eight chronological frames per view. Transparency is preserved.

Sources are versioned alongside the registration contact sheets and animated GIF
previews. The generation requests required the original silver-haired Warrior,
yellow cape, navy/cream/gold costume, sword in the right hand, exactly two legs,
full-body sequential contacts/compression/passing/airborne poses, fixed elevated
camera, eight explicit directions, transparent backgrounds and no text/shadows.

The first sprint sheet supplied seven directions. `warrior-sprint-SW-source.png`
supplies the separately generated front three-quarter down-left sprint strip.
Two source bodies overlapped vertically. Their slots use corresponding complete
run bodies, recorded as `run-repair` in `sprint-assembly.json`; no cut limbs or
procedural feet are assembled. This tradeoff remains visible in the source record.
The final NW row is replaced in all three modes by whole strips generated from
the original NW idle seed; their rear-facing orientation is consistent throughout.
The final W sprint row also uses a separately authored eight-frame strip from
the original W idle seed. Both temporary run repairs are superseded in the
shipped atlases; the intermediate assembly record is retained for provenance.

Reproduce registration:

```powershell
python tools/assemble-painted-sprint.py authoring/characters/painted-v4/warrior-sprint-seven-directions-source.png authoring/characters/painted-v4/warrior-sprint-SW-source.png authoring/characters/painted-v4/warrior-run-v4-source.png
python tools/register-painted-locomotion.py authoring/characters/painted-v4/warrior-walk-v4-source.png authoring/characters/painted-v4/warrior-run-v4-source.png authoring/characters/painted-v4/warrior-sprint-complete-source.png
python tools/register-warrior-nw.py authoring/characters/painted-v4/warrior-NW-three-gaits-source.png
python tools/register-warrior-nw.py authoring/characters/painted-v4/warrior-W-sprint-source.png --direction W --modes sprint
```

Registration isolates alpha components, uses one scale per clip, matches silver
hair scale between clips, and shares the foot baseline per direction. It does not
repaint source pixels, normalize each pose independently, or claim mathematically
exact planted-foot travel from generated artwork. Inspect loops in the real game.
