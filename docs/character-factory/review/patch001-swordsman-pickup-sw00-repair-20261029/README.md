# Swordsman Pickup SW frame 00 — free-hand repair study

A single-frame guide paintover reproduced the overall standing design, but the free left hand visibly grasped the sword blade. The first generated repair released the hand but made the sword much longer and changed its angle. A second targeted repair shows a free hand and a shorter blade closer to the guide. [Guide / initial / bounded repair](comparison.png) · [three-study visibility toggle](repair-toggle.gif). These are **single stills**, not motion, approved masters or in-game assets.

The repair uses a donor only within a feathered mask created from source rectangle `[430,530,910,730]` at 1254×1254. The blur extends beyond the rectangle; outside the actual nonzero mask every initial RGB pixel is unchanged. The final candidate changes 95,966 pixels inside that mask; these can include costume and other donor details, not just the hand. The raw initial, both donors, prompts and guide crop are retained under `painted-candidates/swordsman-pickup-sw00-repair-20261029/`. The selected output and actual mask are under patch `review/swordsman-pickup-sw00-short-repair-20261029/`.

The candidate still needs exact guide-relative hand and blade landmark review, consistent body placement/scale across the 35 frames, background extraction, same-frame layer boundaries, underpaint/variants, temporal review and gameplay. Model and seed for the image generation were not exposed. No source baseline or production runtime asset was changed. Two focused tests passed; they establish mask containment and output preservation, not anatomy.

Tool SHA-256: `84147053f2e60df8c374a3891cbe908e5243b5c28ae31d80a18b54b744fefe93`. Reproduce from the preserved inputs:

```sh
python3 tools/character_factory_v3/propose_pickup_sw00_grip_repair.py --donor authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-pickup-sw00-repair-20261029/donor-short-blade.png --output <fresh-dir>
python3 -m unittest discover -s tests/character_factory_v3 -p test_pickup_sw00_grip_repair.py -v
```
