# Actual starting production model

Audited checkout: character/ro1-reference-engine-v1, db2959b97a77b3f9b54c22d5e732fe2b2345a529. Clean checkout. The separate true-modular branch remains intact and is not merged or reset.

- `swordsman-male-painted/appearance-pack.json` calls its required slot Body and part body-swordsman. Body includes torso, arms, gloves, legs, armour, clothes, boots **and the bald head/face**. It has 328 BODY_SYNC canvas cells (Idle 9, Walk 16, BasicAttack 16, eight directions).
- No independent Outfit or BodyCore exists in this production pack. The rejected true-modular experiment is on a different branch and is not a production dependency.
- HeadBase is an available generic semantic layer but this painted pack does not supply it. The face is baked into Body.
- Hair A/B uses PHASE_SYNC with four generic quarter-cycle transforms, attached directly to the motion head anchor. Its pivot is an estimated .58 fraction of a bounds-fitted source; the head anchor uses a skin bounding-box centre and width-derived scale. There is no Head-local parent relationship.
- MainHand A/B uses ANCHOR_HOLD, the body mainHand anchor and an estimated .86 bounds-height grip pivot. Hand positions are partly searched near interpolated milestone guesses; attack frames can miss the actual glove. A fixed sword view is rotated by motion anchors.
- OffHand is independently held at offHand. Headgear is independently held at head. Both have estimated bounds-centre pivots.
- Garment uses two cape views and four PHASE_SYNC quarter-cycle samples, anchored to back (originally head centre +28 pixels), a .10 bounds-height pivot, -5 y offset and small generic phase rotations. This ignores actual shoulder/collar position and torso lean.
- Anchors live in `motion-template.json`; build source calibrations live in `authoring/characters/builds/swordsman-male/attachment-*.json`. Image pivots/local transforms live in AppearancePack sample metadata. Atlas normalization is recorded in normalization.json.
- PHASE_SYNC selects normalized **time** thresholds, using frame-start time for explicit inspection; BODY_SYNC selects expanded frame index. No action timing belongs to costumes.
- Generic draw profiles exist for front/rear/loaded/rearStrike. Their historic rear cape overlays the torso, while the initial loaded sword is behind Body. These profiles do not fix attachment positions.

Owner rejection applies to the old assembled proof: ENGINE PASS / STRUCTURAL PASS / ANIMATION EXISTS / VISUAL ASSEMBLY FAIL / OWNER VISUAL APPROVAL REJECTED. All old sources, atlases, metadata and review artifacts are preserved. New review files use a separate output folder.

Migration: preserve every dressed-body source pixel; split the existing head/neck pixels into a separately sampled identity without repainting the face. The remaining complete dressed body becomes BodyWithOutfit. Keep legacy internal layer names Body/HeadBase as the generic engine equivalent. Use a new strict production contract and appearance pack; leave historical 1.0 fixtures executable for regression checks.
