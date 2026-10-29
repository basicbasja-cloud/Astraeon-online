# Pickup SW08 — hilt ownership and underpaint drafts

Two isolated steps build on the previous single-frame matte/SAM cutout. Neither is approved for a weapon swap or runtime.

1. Six small detached components totaling **9 visible pixels** inside the reviewed hilt region were reassigned from BodyCostume to Weapon. The original matte master remains exactly reconstructible. [Before/after ownership](debris-comparison.png). Because the selection is based on connected components in a region, it might move glove or antialias pixels; semantic review is required.
2. An image-generated no-sword donor was mapped using the same full-canvas scale and placement. **84 pixels** were inserted into BodyCostume only inside a bounded hilt-area mask where the original Weapon is fully opaque and Body/Head are empty. Sword-on RGBA remains byte-identical to the prior matte master. [Underpaint comparison](underpaint-comparison.png) · [single-frame weapon visibility toggle](weapon-toggle.gif).

**The underpaint is rejected as a finished grip.** The donor opened the hand and the bounded pixels do not join the original glove naturally. Near-transparent hilt edges and hidden handle/body regions are not reconstructed. The picture when a sword is hidden is not evidence of an interchangeable weapon. Head/collar ownership, alpha, pose registration, all other frames and directions, motion and gameplay remain open.

The generated donor and exact prompt are retained under `painted-candidates/swordsman-pickup-sw08-hilt-underpaint-20261029/`; model and seed were not exposed. Results and masks are under patch `review/swordsman-pickup-sw08-hilt-debris-20261029/` and `review/swordsman-pickup-sw08-hilt-underpaint-20261029/`. Two focused tests passed. Reproduce to fresh destinations:

```sh
python3 tools/character_factory_v3/refine_pickup_sw08_weapon_debris.py --output <debris-dir>
python3 tools/character_factory_v3/propose_pickup_sw08_hilt_underpaint.py --output <underpaint-dir>
python3 -m unittest discover -s tests/character_factory_v3 -p test_pickup_sw08_hilt_studies.py -v
```

The underpaint script reads the preserved in-repository debris study; its output is not a chain from `<debris-dir>`. Tool SHA-256 values: debris `57362a65bbe72ba560b51b5c6cc1e0e5795af0760f541066af814fb811a84542`; underpaint `6eddee5ec0a9f85117025b9152d282d2c5c9afa4a0e10b7fa8675cba51283553`. No source image, production store or game asset changed.
