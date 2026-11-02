# Swordsman BasicAttack NW 003: same-frame slots and head swap study

**One-frame draft; not approved.** The old HeadHair layer included an arm fragment and omitted face pixels. Three SAM suggestions were reviewed; a proximity and face-color heuristic recovers 204 pixels for an isolated head proposal. The sword-free same-frame master is partitioned into BodyCostume and HeadHair, then recomposed with the existing experimental Weapon layer. The result exactly matches the original master RGBA in this single frame. [Separate slots](slots.png).

A generated dark-haired alternative was extracted as a provisional head and composed over the saved BodyCostume and Weapon. [Three-background comparison](comparison.png); [alternative masks](alt-mask-proposals.png). This exposes bright fringes and an uncertain neck/collar seam, especially on a dark background. The position, head fit, binary edge and hidden surfaces require repair before a real asset swap can be accepted. The original weapon layer itself has unresolved glove/costume edge ownership. No other pose or direction was produced and no gameplay run occurred. Exact reconstruction and outside-mask preservation do not establish semantic correctness.

The source, candidate masks, layers, receipts and generator input are stored under `authoring/characters/factory-v3/patch-0.0.1/` in `research/swordsman-nw003-head-sam-20261102`, `research/swordsman-nw003-head-refined-20261102`, `research/swordsman-nw003-three-slots-20261102`, `research/swordsman-nw003-alt-head-sam-20261102`, `research/swordsman-nw003-alt-head-swap-20261102`, and `painted-candidates/swordsman-nw003-alt-head-20261102`. SAM2 checkpoint and inputs are hashed in receipts. The image generator did not expose a model or seed. Prompt:

> Edit this exact fantasy animation frame to explore a different hairstyle. Change only the character's hair to a short dark brown swept-back hairstyle with distinct strands and a small tied tuft at the back. Preserve the SAME head shape, face, downward gaze, ear and neck, and exact head position and angle. Keep character pose, proportions, scarf, armor, hands, sword, camera, crop and white background unchanged. One coherent character, hand-painted game sprite style, no text.

Reproduction from saved masks:

```sh
python tools/character_factory_v3/refine_nw003_head_proposal.py --output /tmp/nw003-head-refined
python tools/character_factory_v3/propose_nw003_three_slots.py --output /tmp/nw003-three-slots
python tools/character_factory_v3/propose_nw003_alt_head_swap.py --output /tmp/nw003-alt-head
python -m unittest discover -s tests/character_factory_v3 -p 'test_nw003_three_slots.py' -v
```

The focused test passed exact master reconstruction, outside-union preservation, and overwrite refusal. Production and runtime assets remain unchanged; no action or character is complete.
