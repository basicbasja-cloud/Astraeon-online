# Modular 2D sprites

`<characterId>/sprite.json` declares shared poses and interchangeable parts.
`<characterId>/atlases/<partId>-<animation>.png` contains lossless padded RGBA
frames in **S, SW, W, NW, N, NE, E, SE** order. Modular images remain separate.
`schemas/sprite-definition.schema.json` describes the 0.1 machine contract.

`swordsman-proof` and `mage-proof` are geometric **DEV_ONLY / PLACEHOLDER /
NOT_FINAL_ART** fixtures. Normal gameplay continues to use its existing painted
characters. Their original strips can be reproduced with
`python3 tools/build-modular-proof.py --sources /tmp/astraeon-modular-sources`.
There is no approved final replacement art in these proof folders.

Run `python3 tools/validate-sprites.py`. Open `sprite-preview.html` through the
local static server. See [authoring/runtime instructions](../../docs/MODULAR_SPRITES.md).
