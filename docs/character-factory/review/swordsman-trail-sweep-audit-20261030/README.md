# Swordsman BasicAttack: sword sweep audit, 2026-10-30

Status: **research only; no replacement trail admitted**. The preserved tall Swordsman and existing long trail remain intact. The 16-frame BasicAttack art is a technical import, not an approved playable character.

## What was checked

The existing long effect uses source Sword_Attack samples 11–13, registered to painted frame 7, then fades that same raster on frames 8 and 9. A stationary residual can be intentional, but on its own it does not show whether the remaining moving blade should add a continuing sweep. A source-to-art fit anchored only at frame 7 also fails to match the annotated painted tip at later poses: in SE the discrepancy is approximately 45.34 and 50.27 pixels on the 512-pixel authoring art at frames 8 and 9. The annotations themselves need visual verification; this is evidence of registration mismatch, not a measurement of anatomy.

We exported 65 native subframe grip and tip projections across source frames 11–15 in SW, NW, NE and SE. All overlapping samples at source frames 11–13 matched the preserved dense guide, and source frames 14 and 15 matched the preserved explicit guide, with 0.0 pixel maximum source discrepancy. The coordinates are a 2D projection of a 3D guide, not the painted sword itself.

## Experiments and decision

- [Independent per-frame fits](independent-fit-rejected.gif): rebuilding history from each current frame changed shape too abruptly, particularly NW.
- [Layered residual plus new sweep](layered-rejected.gif): the old and new arcs visibly split in NE and SE.
- [Interpolated registration study](comparison.gif): the fit interpolates between annotated grip/tip pairs at the five strike poses, then traces only sampled history, with a 2.4-blade-length cap and fading. [Frame 7](frame07.png), [frame 8](frame08.png), [frame 9](frame09.png). NW still has a broken/disconnected shape; NE and SE still need occlusion and arc review. Fitting 2D projections to unverified annotations does not prove a physically correct 3D sweep. All three are rejected as production replacements.

The next viable correction needs confirmed hand and blade endpoints across the painted strike, a consistent blade volume and view-specific front/back occlusion, followed by review at gameplay timing. Trail should begin after the blade starts sweeping, follow the actual forward motion, and retain the requested long impact without inventing motion beyond the sampled path. Do not use a fit or a numerical check as a substitute for visual and game review.

## Reproduction and checks

Native path: `authoring/characters/factory-v3/patch-0.0.1/research/swordsman-attack-dense-path-11-15-20261030/receipt.json` and `tools/character_factory_v3/export_swordsman_attack_dense_path.py`. Proposed FX generators are `propose_swordsman_live_sweep_trail.py`, `propose_swordsman_layered_sweep_trail.py`, and `propose_swordsman_interpolated_sweep.py` under the same tools directory. Their receipts describe source hashes and limitations; the interpolated receipt is included here.

`python -m unittest discover -s tests/character_factory_v3 -p test_interpolated_sweep_study.py`: 3 passed. These tests check interpolation, malformed inputs and history bounds; they do not certify visual correctness. No runtime asset or animation was changed, and no gameplay validation was performed.

## Painted endpoint inspection

[Contact sheet of painted frames 5–9 and existing grip/tip annotations](weapon-annotations.png): red marks grip, cyan marks tip. In NW frame 8 the blade is extremely short in projection and overlaps the figure; the marked tip is difficult to verify from the painted pixels. This weakens the frame-specific registration in precisely the view where the interpolated ribbon breaks. It does not establish whether the underlying pose or marker is wrong. Inspect the native 3D blade and correct/verify the painted grip and tip together before accepting a new FX curve. The markers are existing annotations, not newly approved landmarks.

Reproduce the contact sheet into a fresh path with `python tools/character_factory_v3/render_swordsman_weapon_annotation_audit.py --output /tmp/swordsman-weapon-annotations.png`.
