# Pickup SW08 — closed-fist underpaint iteration

The previous no-sword donor opened the hand. This donor was prompted to retain a clenched right glove around an imaginary grip. From that donor, 61 nonwhite pixels inside the fixed hilt region are inserted into BodyCostume only where the existing Weapon is fully opaque and Body/Head are empty. The sword-on RGBA composite is byte-identical to the previous matte master. [Open donor, closed donor and sword-on comparison](fist-comparison.gif). The GIF toggles one still pose; it is not motion or an approved interchangeable weapon.

The closed donor is more consistent with the intended gesture, but the bounded inserted portion still has small gaps/fringe and does not demonstrate a complete natural hand beneath a different weapon. The generator model and seed were not exposed; the donor and exact prompt are retained under `painted-candidates/swordsman-pickup-sw08-hilt-fist-20261029/`. No source, production store or game asset was changed. Head, matte, hand/weapon boundaries, hidden surfaces, other frames, variants, contacts and game motion remain unapproved.

Three focused tests passed, including opaque cover and same-frame recomposition for both donors. Result layers and mask are retained under patch `review/swordsman-pickup-sw08-hilt-fist-20261029/`. The tool now accepts an explicit donor; the older open-donor study remains reproducible using its original checkpoint or the default donor. Current tool SHA-256: `c7fa1b728746aa3bf5a9cdec08f5922e14d7ef8905129a98b9978767a41b27a9`.

```sh
python3 tools/character_factory_v3/propose_pickup_sw08_hilt_underpaint.py --donor authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-pickup-sw08-hilt-fist-20261029/donor.png --output <fresh-dir>
python3 -m unittest discover -s tests/character_factory_v3 -p test_pickup_sw08_hilt_studies.py -v
```
