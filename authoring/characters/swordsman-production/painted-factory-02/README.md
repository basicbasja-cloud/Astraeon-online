# Painted factory 02: paused source checkpoint

Saved 11 October 2026 on `character/production-factory-v2` at the owner's request to push progress and continue next time.

## Current scope

The approved painted concept remains the identity and rendering reference:
`../fresh-2d/candidate-01/candidate.png`.
The owner rejected the recent sword/grip results and requested restoration of the pre-Ragnarok pose checkpoint. That restoration is committed as `e130b217`; the previous experiments remain recoverable in Git history. Keep the restored body actions. Use Ragnarok-style modular composition, without reviving the rejected Ragnarok pose experiments.

The owner explicitly retained a 90-degree sword-to-forearm angle with a naturally aligned wrist. The target is painted, eight-direction 2D sprites with interchangeable outfit, weapon, headgear, hairstyle and cape across the animations.

## Saved work

- `source-master.blend` is the exact editable local native snapshot identified by `master-source.json` (SHA-256 `0310356a2cb978b309aaa4f7fd95de2d5c5264b912bd540f3618edff9f314273`). It contains the shared rig, existing action bank, equipment alternatives and new shorter silver hairstyle geometry.
- `tools/build-painted-factory-master.py` rebuilds from the preserved local `.character-tools/checkpoints/fantasy-swap-bank.blend`. It changes right digit curl/thumb opposition and glove forms, and creates the alternate head/hair mesh. The supplied model and original source bank are preserved locally.
- `guide-silver-*.png` and `guide-cropped-*.png` are full native source guides in SE, W, NW and N. `grip-*.png` are native contact close-ups. These are inspection guides, not painted deliverables or accepted artwork.
- Motion digests before/after match for all controls outside the right digits. Rest bone lengths are unchanged. These numeric checks do not prove visual grip quality.

## Still incomplete

New grip images need visual inspection. The painted finish, complete painted animation coverage, and runtime swap demonstration including the new hairstyle are not complete or owner-approved. The 1,456 available native pose positions are source coverage only. The older `fantasy-base-01` sealed package is a technical bake; it does not establish the requested painted quality.

The initial chestnut hair draft was superseded; its images are archived locally and are excluded from this checkpoint. Private Ragnarok reference assets and unrelated earlier experiments are also excluded.

## Resume in this order

1. Inspect the four `grip-*.png` close-ups and the original/cropped hairstyle guides. Repair native contact if it fails; preserve body actions and the required sword angle.
2. Produce and verify a coherent painted seed against the approved concept and the native pose guides, including the critical rear/profile views. Do not reuse rejected independent part assemblies or distorted paint trials.
3. Build registered complete body/outfit, head/hair, weapon, headgear and cape layers with proper hidden surfaces and hand occlusion. Demonstrate outfit, weapon, headgear and hairstyle swaps at the same animation time, frame and direction.
4. Extend the verified painted workflow across the required actions and eight directions; check the actual game scale and runtime rendering. Preserve the old sealed technical package while building the new candidate separately.
5. Update receipts and owner-review status honestly, then commit and push progress to this branch. The Golden character still requires owner visual approval before expansion to all classes.

No background continuation or paid provider job is scheduled. Resume only when the owner returns.
