# SkillOverhead — registered layered review

The owner reclassified the previous B overhead cut as a skill. The former `four-direction-attack-review` stays as history; this directory is a new translated layer set.

- Mesh2Motion CC0 original rig: `Sword_Regular_B` plus matching recovery; actual SW/NW/NE/SE cameras.
- 16 illustrated poses per view, 512px cells. Manual visible pelvis annotations register each whole pose to the source pelvis at a fixed 0.5 projection scale. The identical integer translation applies to all parts and effects. No scaling, anatomy warp, camera following or individual layer drift.
- `registration-annotations.json` is the explicit approximate annotation input. `registration-audit.json` records translations and rounding residuals. Those residuals measure alignment to the annotations, not independent anatomical accuracy.
- The short independent trail still emits at pose4, fades at5 and clears afterward. Gripping-hand and blade overlays stay above it.
- `HeadHair` is visible head+hair; `BodyCostume` is the complete clothed body. No hidden anatomy is invented.
- Sheets: columns SW,NW,NE,SE; rows0–15; 512px cells; 2048×8192 overall. `Master` and merged `WeaponLight` are references, not extra drawable layers. ORA files retain editable per-view layers.

## Remaining review

Registration removes cell-packing drift but cannot correct pose/proportion differences already painted into the images. NE recovery blade foreshortening remains. Manual collar/hilt boundaries remain provisional. One-shot playback is intentional; no artificial final-to-first warp is applied. This is not owner approval or runtime admission.

## Rebuild

From the repository root:

```bash
python tools/character_factory_v3/layered_action_factory.py --action SkillOverhead
python tools/character_factory_v3/package_layered_factory_review.py --output /workspace/outputs
```
