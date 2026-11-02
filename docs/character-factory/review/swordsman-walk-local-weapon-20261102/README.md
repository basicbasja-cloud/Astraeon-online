# Swordsman Walk SW004: bounded local retouch and provider failures

**Not an accepted master, action, cutout or variant.** Three enlarged same-frame
references were prepared for Walk SW slots004/008/012. Each uses the existing
complete clothed key-pose draft, one fixed authoring crop`[224,288,544,608]`,
and the actual replayed rig's grip/tip targets. These are corrections to an
existing complete master; no separately generated arm or leg is assembled.

Only004 returned a generated image. Its whole-frame result was resampled once
at the recorded fixed crop scale, then applied solely inside an explicit5,666px
review mask on the original768px draft.3,917 pixels change; **zero RGBA pixels
outside the mask change**. In particular, the original frame's own head, distant
clothing and legs remain unchanged; no leg from another frame is copied or frozen.
This does not validate the draft's original body/contact motion.

- [Original and bounded proposal on white/gray/dark](three-background-comparison.png)
- [Complete pose with source controls](source-control-comparison.png)
- [Proposed master](master-candidate.png), [explicit review mask](review-mask.png)
- [Receipt, source hashes and fixed transform](receipt.json)

The returned blade still ends beyond the requested source tip. The manually
estimated visible core tip`[915,454]` in the raw1254px result maps to a guide
endpoint difference of approximately**6.16 runtime pixels**, with a3-raw-pixel
annotation uncertainty. This is an endpoint diagnostic, not the plan's separate
≤1-runtime-pixel sole-contact test. The mask boundary, wrist/glove seam, hilt,
occlusion and exposed cloth also remain unapproved. The proposal is not adopted
or cut into production layers.

## Image service blockage

The same local correction prompt/reference workflow for slots008 and012 returned
HTTP400`moderation_blocked` at the input stage, with category`violence`.
These requests concerned the pictured fantasy walking sprite and sword retouch;
no output was supplied for either frame. The service returned request IDs:

- 008: `4e47e889-64b9-495e-94d1-3e8b2afaca29`
- 012: `f0ee4c2e-614e-4c7d-8ce6-4355750df227`

No workaround or indirect retry of those rejected requests was attempted. Owner
authorization was already granted; this provider response is a separate
execution limitation. No blank image or duplicate pose replaces either missing
result. [Exact prompt, raw004 output and provider receipts](../../../../authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-local-weapon-20261102/).
The tool did not expose model/seed; exact image generation is not claimed as
reproducible.

## Reproduction

[Six reference PNGs and their hashes](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-walk-local-weapon-refs-20261102/reference-receipt.json)
match the exact files submitted to the generator. The seven reference files and
five proposal/review files each reproduce byte-for-byte from retained inputs.

```sh
python tools/character_factory_v3/propose_walk_local_weapon_edit.py --prepare \
  --output /tmp/walk-local-weapon-references

python tools/character_factory_v3/propose_walk_local_weapon_edit.py \
  --raw authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-local-weapon-20261102/004-raw.png \
  --output /tmp/walk-local-weapon-proposal
```

No protected original, rig, camera, production binding or runtime package changed.
All six planned characters remain incomplete, with no newly accepted action,
variant or in-game test in this checkpoint. The working intake rollback fix is
[documented separately](../patch001-cutout-import-rollback-20261102/README.md);
passing those technical tests does not admit this retouch.
