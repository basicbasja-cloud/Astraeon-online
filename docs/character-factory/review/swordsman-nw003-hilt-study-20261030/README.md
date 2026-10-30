# Swordsman BasicAttack NW 003: preliminary blade and hilt mask

**Draft, not a usable weapon swap.** The prior blade-only study is extended with approximate polygons over the guard and pommel, for a total 1,034-pixel mask. Replacing those pixels with the same saved underpainting donor preserves the original master outside the mask. Reapplying their original RGBA pixels gives zero pixel differences from the original master. [Three-background comparison](comparison.png); [mask, layers and receipt](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-nw003-hilt-study-20261030/receipt.json).

The hidden-weapon view still shows stray edge pixels near the hand, and the mask can include glove, skin or costume colors. The grip underneath the hand, accurate original sword edge, correct hand occlusion, alternate weapon and all other frames remain unresolved. The underpainting uses a heuristic white-background alpha and has not passed semantic or game review. Exact reconstruction is necessary but does not verify ownership. Do not use this output as an accepted sprite or claim the action is complete.

```sh
python tools/character_factory_v3/propose_swordsman_nw003_hilt_study.py --output /tmp/nw003-hilt-study
python -m unittest discover -s tests/character_factory_v3 -p 'test_swordsman_nw003_hilt_study.py' -v
```

The focused test passed for exact RGBA reconstruction, protected outside-mask pixels and overwrite refusal. No original or runtime asset was changed.
