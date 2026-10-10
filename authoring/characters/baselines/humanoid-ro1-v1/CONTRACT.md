# Shared humanoid artwork baseline

Status: DRAFT. The owner rejected the old character builds. Their poses, limb
warps, joint estimates, and weapon rotations are not the reference for this baseline.
The new neutral turnaround is a candidate, not an approved animation set.

## What an artist replaces

| Part | Contents | What remains shared |
| --- | --- | --- |
| BodyWithOutfit | Torso, arms, hands, legs, clothing, armour and boots | Frame IDs, canvas, floor origin, anatomical pose, equipment sockets |
| Head | Complete RO1-style head, face and hair for each required direction/pose | Neck registration and head-local sockets |
| MainHand | All required views of one weapon design | Equipment registration, handle contact, phase and draw-order contract |
| OffHand | Shield or held object views | Offhand registration and direction-dependent occlusion |
| Headgear | Independent headwear views | Head-local attachment |
| Garment | Cape/back accessory, including front overlap when required | Body attachment and front/back order |
| WeaponSlash | Optional separate visual effect | Presentation phase; never damage authority |

Class and gender are artwork identities, not renderer branches. A female character
can select a different BodyWithOutfit and Head together. A costume change selects
only BodyWithOutfit; a hairstyle change selects a complete Head+Hair style. Equipment, action,
direction, frame, elapsed time and cosmetic time remain intact.

## Fixed authoring space

- Canvas: 320 × 320 transparent pixels, origin at upper left, positive y down.
- Direction order: S, SW, W, NW, N, NE, E, SE. Supply every view; no mirror fallback.
- Shared ground origin: (160, 264), matching the existing MotionTemplate. Art must be drawn against the supplied pose guides.
- Full-frame body sheets use one direction per row and one timeline frame per column.
- One shared scale per authored strip. Do not independently stretch frames to fit.
- Head resources use their own local pivot and explicit neck attachment. The owner's
  latest clarification requires hard RO1 reference including hair with head: the
  production baseline therefore uses complete Head+Hair style resources, separate
  from BodyWithOutfit. Hair style remains independently selectable from costume,
  weapon and accessories through the Head slot. Historical separate Hair support
  in the generic renderer does not dictate this new master resource topology.
- Equipment attachment, visible handle contact and blade tip are separate landmarks.
- Hands belong to the body. Fingers that cover a handle are a body-owned foreground
  pass; a sword image must not contain the wielder's hand.
- Perspective changes use authored weapon samples. A single rotated sword is not a
  complete weapon set. Slash pixels do not belong in a weapon sample.

Idle, Walk and BasicAttack are the only actions in this version. Keep the existing
450 ms attack presentation and 170 ms contact landmark while rebuilding the art.
Other action lengths and frame boundaries come from the shared MotionTemplate;
an artwork manifest cannot supply timing.

## Reuse boundary

Artwork-only replacement means painting to the SAME baseline pose and attachment
layout. It does not mean that arbitrary images with different proportions can be
automatically attached correctly. Normal male/female or costume variants must fit
the shared wrist, neck, offhand and back sockets. The artist may vary the silhouette
around those fixed points. Large changes in physique, weapon handling or choreography
need a separately reviewed baseline revision/profile; they must not silently stretch
an existing rig. New gameplay classes and new attack styles are outside this task.

Do not freeze production pose coordinates until the fresh RO1-referenced body,
weapon and grip have passed visual review. The mechanism for reuse is implemented;
the production pose content is still being rebuilt.

## Files and workflow

`character-art-baseline.js` builds a character family from a baseline reference pack
and artwork-only manifests. Each manifest may provide only identity, part selection
and texture paths/dimensions. Timing, socket data, pivots, grip measurements and draw
order are inherited. Unknown overrides and missing texture coverage fail validation.

1. Author and review the reference BodyWithOutfit, complete Head+Hair and equipment poses
   against the private RO1 workbench. Save the resulting appearance pack as the
   baseline's `referencePack`, with a version and honest review status.
2. Scaffold a new character using the CLI below. It refuses to overwrite a manifest.
3. Paint the required textures using the same canvas, poses, sockets and weapon
   perspectives. Reuse existing equipment and headwear by omitting those slots from
   the replacement manifest.
4. Verify the manifest and actual PNG dimensions. Preview every action/direction with
   the shared equipment, including body-only and grip/occlusion views.
5. Build the family once and use the existing assembly controller's `setAppearance`
   with the variant selection. Do not reset the animation controller on a swap.

```sh
node tools/character_art_variant.cjs scaffold BASELINE.json MOTION.json swordsman-female OUTPUT.json
node tools/character_art_variant.cjs verify BASELINE.json MOTION.json OUTPUT.json
```

`allowDraft: true` permits development inspection only. The normal family build
rejects unapproved baselines; newly supplied artwork always requires visual review.
Tests use explicitly synthetic fixtures and do not certify the rejected Swordsman
art or declare a female/class artwork set finished.

## Reusable toolchain

| Stage | Tool | Result |
| --- | --- | --- |
| RO1 source inspection | `tools/build_ro1_rebuild_reference.py` | Private decoded Body/Head imagery; published numeric attachment measurements |
| Authoring configuration | `pipeline.json` beside this document | Canonical slots, directions, actions, root and review requirements |
| Review original pose studies | `tools/export_character_pose_study.py` and `character-pose-study.html` | All eight views on the shared clock; reports source-boundary failures and never emits a production pack |
| Normalize original art | `tools/normalize_character_art.py` | Deterministic atlas + SHA256/layout receipt; rejects clipped/cross-cell art, per-frame transforms, unexplained reuse and private source pixels |
| Review any appearance pack | `character-production-review.html?motion=PATH&appearance=PATH` | Timeline-preserving part swaps, layer isolation, grip/attachment overlays |
| Play any complete candidate | `character-playable.html?motion=PATH&appearance=PATH` | Eight-direction movement, finite attack completion, time-preserving swaps; rejects missing actions and explicitly rejected art |
| Fit partial independent parts | `character-layer-fit.html?config=PATH` | Body/head/weapon isolation, authored neck/grip and body-owned finger overlap; never pretends one direction is a full pack |
| Inspect geometry | `character-production-validation.js` | Independent grip/equipment/tip measurements and non-mutating arc warnings |
| Audit planted stance | `tools/audit_character_stance.py` | Sole drift from artist-isolated boot regions; reports failures without transforming source pixels |
| Export any appearance pack | `tools/export_character_production_review.py` | Eight-direction normal/half-speed GIFs, exact-time APNGs, per-direction boards and export receipt |
| Create candidate master | `tools/create_character_master.cjs` | Validated versioned baseline; never automatically approved |
| Scaffold/validate replacement | `tools/character_art_variant.cjs` | Artwork-only manifest and actual PNG dimension validation |
| Compose reusable family | `character-art-baseline.js` | New selectable parts using unchanged baseline geometry and timing |

The normalizer consumes an explicit source-cell map, not guessed bounding boxes.
Authored direction origins remain fixed across every frame of that direction.
The study exporter likewise uses one declared origin and scale per source sheet;
it deliberately exposes foot drift. Its optional bounded alpha noise cleanup is
recorded in the receipt and never overwrites the source image.
The current neutral-study plan is an example of a four-column/two-row source being
normalized into canonical eight-direction rows. It has one neutral study frame per
direction and is not a replacement for the complete Idle/Walk/BasicAttack master.

Example export after the fresh appearance pack exists:

```sh
python tools/export_character_production_review.py --motion MOTION_PATH --appearance APPEARANCE_PATH --action BasicAttack --output NEW_REVIEW_FOLDER
```

The toolchain is tested with synthetic fixtures until the fresh master is ready.
Do not pass the rejected Swordsman candidate through the master creator and describe
the result as a new approved template.

## RO1 evidence

The pinned public body and complete-head ACT/SPR are decoded into ignored private
storage. `docs/review/character-ro1-rebuild-v2/ro1-part-registration.json` records
208 numeric body/head frame pairs. Head placement follows parent ACT anchor minus
child ACT anchor, followed by the child's layer offsets. ACT anchors are NOT named
shoulder, elbow or grip measurements.

- https://ragnarokresearchlab.github.io/file-formats/act/
- https://ragnarokresearchlab.github.io/file-formats/spr/
- https://github.com/zhad3/zrenderer/blob/main/RESOLVER.md
- https://github.com/adsonpleal/ragassets/blob/4de4fa747431979d35c747d7edd549a872efd9e1/gateway/internal/render/sprite/sprite.go

Raw sword ACT/SPR is not yet acquired. Captured assembled RO1 sword/slash animation
is rendered-reference evidence, not proof of independently decoded weapon pivots.
Raw attack body records repeat adjacent pairs; eight source IDs do not prove eight
unique projected attacks. Original additional projections must be labelled derived.
