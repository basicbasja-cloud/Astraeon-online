# Swordsman BasicAttack NW 003: bounded body edge cleanup

**Draft correction; not production acceptance.** The alternate-hair preview exposed bright body pixels around the neck and extended arm. A bounded heuristic selects 28 nearly white BodyCostume pixels adjacent to transparency in a fixed 70×70 area and makes them transparent. [White, gray and dark comparison](comparison.png) shows reduced bright fragments on the dark background. A corrected complete master is generated from the changed body and the same original HeadHair and Weapon; these layers recompose to that corrected master exactly. The corrected master differs from the protected original master at 28 RGBA pixels by design; source and runtime files were not overwritten.

This is an image correction proposal: the threshold can remove legitimate highlights or create hard edges, and bright fringes outside the bounded region remain. The source HeadHair and Weapon are still provisional, the alternate head's neck/collar seam and matte are not approved, and no other frame, animation or gameplay has passed. [Candidate body, mask, corrected master, comparison composite and hashed receipt](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-nw003-body-edge-cleanup-20261102/receipt.json).

```sh
python tools/character_factory_v3/propose_nw003_body_edge_cleanup.py --output /tmp/nw003-body-edge-cleanup
python -m unittest discover -s tests/character_factory_v3 -p 'test_nw003_body_edge_cleanup.py' -v
```

The focused test passed protected-outside-mask and exact corrected-master recomposition. These checks do not approve the visual result or a head swap. No action or character is complete.
