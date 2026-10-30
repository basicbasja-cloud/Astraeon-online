# Swordsman BasicAttack NW 003: alternate sword prototype

**One frame; draft, not an accepted variant.** A generated, visibly different blue-fuller sword is extracted from a same-pose donor and composed onto the prior bounded sword-free master. A small same-frame glove polygon is drawn above it. The [white/gray/dark comparison](comparison.png) shows the original and prototype. An isolated pommel mask restores the end of the grip that the first sword mask missed.

This is a test of the slot idea, not a completed reusable weapon: [sword segmentation](sword-mask-proposals.png) includes attached arm/dark edge pixels, [pommel segmentation](pommel-mask-proposals.png) is approximate, the hand polygon and inferred alpha need detailed review, and the underlying master still has an ambiguous guard edge. The generated shape, grip and scale need comparison with the source rig; there are no other frames, directions, true factory variant package or gameplay evidence. Source and runtime assets are unchanged.

The saved [draft layers and receipt](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-nw003-alt-sword-swap-20261030/receipt.json) include the separate weapon, hand occluder and composite. The focused test confirms no changes outside the union of the proposed weapon and hand; this does not mean every pixel inside those masks belongs to those parts. SAM2 scores are suggestions, not acceptance.

Inputs and generated donor are retained in `authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-nw003-sword-variant-20261030/`. Image editing prompt:

> Edit the provided fantasy animation frame: replace only the silver sword with a visually distinct original fantasy longsword, a slightly broader tapered steel blade with a blue central fuller and an ornate bronze crossguard. Keep the sword in EXACTLY the same position, length, angle and hand grip as the existing sword, with the blade crossing the same way. Preserve the character's full pose, gloves, head, hair, scarf, clothing, camera, size, background and crop. The right gloved hand must convincingly grip the weapon and partially occlude its handle. Painterly high detail, matching the original style. One sword, no extra limbs, no text.

The generator did not expose model or seed. SAM2 checkpoint hash and prompts are in the two research receipts; production assets remain untouched. Reproduce with retained masks:

```sh
python tools/character_factory_v3/propose_swordsman_nw003_alt_sword_swap.py --output /tmp/nw003-alt-sword
python -m unittest discover -s tests/character_factory_v3 -p 'test_swordsman_nw003_alt_sword_swap.py' -v
```

One focused outside-mask and overwrite test passed. Full visual, motion, semantic and in-game gates remain open; no completed action is claimed.
