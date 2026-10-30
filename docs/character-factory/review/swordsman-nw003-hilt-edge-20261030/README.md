# Swordsman BasicAttack NW 003: hilt-edge cleanup proposal

**Draft; semantic ownership still open.** Extending the previous hilt mask over a small bounded area beneath the fist reduces the obvious isolated remnant when the experimental weapon is hidden. [Three-background comparison](comparison.png). The provisional mask now has 1,159 pixels. All pixels outside it remain the original master, and restoring original pixels from the saved weapon layer reconstructs the master with zero RGBA differences. [Draft layers and source hashes](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-nw003-hilt-edge-20261030/receipt.json).

The remaining gold strip beside the glove is ambiguous, the blade/hilt mask includes neighboring garment or glove colors, the hidden grip and its occlusion are not authored, and alpha comes from an approximate white-background matte. Further manual semantic boundary and anatomy review, a truly different weapon, other frames/directions and gameplay are required. This is a single complete-master experiment, not approved BodyCostume / HeadHair / Weapon sheets or a finished action.

```sh
python tools/character_factory_v3/propose_swordsman_nw003_hilt_edge.py --output /tmp/nw003-hilt-edge
python -m unittest discover -s tests/character_factory_v3 -p 'test_swordsman_nw003_hilt_edge.py' -v
```

One focused pixel/overwrite test passed. It does not approve visual correctness or reuse. Source and runtime assets were not changed.
