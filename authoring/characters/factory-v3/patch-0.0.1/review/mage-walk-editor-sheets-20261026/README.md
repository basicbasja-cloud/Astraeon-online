# Native Mage walk editable sprite sheets

Each PNG is a transparent 4 by 4 chronological grid: 16 native 1536-square cells, 6144-square sheet. Camera NE only. Do not rescale individual cells or crop their margins when editing; each role retains the same root [768,1100.8].

Layers compose in this order: Weapon, BodyCostume, WeaponHandOccluder, HeadHair. Master is the expected composite, not an extra drawing layer. The hand is behind the head in this view. Complete head and staff include hidden pixels.

Male and female folders reuse byte-identical Weapon, BodyCostume and WeaponHandOccluder sheets; see shared-role-proof.json. Only HeadHair and the derived Master differ. The body is a shared covered costume, not an anatomy demonstration for both sexes.

All 160 exported cells were reopened and compared byte for byte with their real source RGBA frames. This establishes lossless editable export, not anatomical approval or full 0.0.1 readiness. Only the current NE walking study is included.

Reproduce from the repository root:

```sh
python tools/character_factory_v3/export_review_part_sheets.py --samples authoring/characters/factory-v3/patch-0.0.1/review/mage-walk-editor-sheets-20261026/source-samples.json --output /tmp/mage-walk-editor-replay
```
