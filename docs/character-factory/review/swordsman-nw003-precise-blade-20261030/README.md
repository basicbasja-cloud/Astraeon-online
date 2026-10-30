# Swordsman BasicAttack NW 003: bounded blade-only reconstruction

**Experimental; semantic cutout and weapon swap not approved.** This revision starts from the preserved complete master rather than the earlier incomplete no-Weapon composite. A 743-pixel manually drawn blade polygon is replaced with the saved generated underpaint, and pixels outside the polygon remain exactly the original. The saved blade copies original RGBA pixels from that polygon. For original nonopaque silhouette pixels, the underpaint is made transparent to avoid double alpha. Recombining blade over underpaint yields **zero RGBA differences** against the 512px master.

[Three-background comparison](comparison.png). [Layers, mask and receipt](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-nw003-precise-blade-20261030/receipt.json). This improves on the prior 1,378-pixel mismatch, but **does not pass the full requirement**: the polygon contains some neighboring scarf/skin edge pixels, the hilt remains in the body, underpaint alpha is heuristic, and the result is one complete master plus blade rather than validated BodyCostume / HeadHair / Weapon roles. Correct grip, hand occlusion, hidden surfaces, alternative weapon, all other frames and directions, motion and gameplay remain open. Exact reconstruction cannot prove semantic separation.

Reproduce in a fresh path:

```sh
python tools/character_factory_v3/propose_swordsman_nw003_precise_blade.py --output /tmp/nw003-precise-blade
python -m unittest discover -s tests/character_factory_v3 -p 'test_swordsman_nw003_precise_blade.py' -v
```

The focused test passed, including zero RGBA differences, preservation outside the mask and refusal to overwrite output. Original source, production and runtime data remain unchanged. No completed action is claimed.
