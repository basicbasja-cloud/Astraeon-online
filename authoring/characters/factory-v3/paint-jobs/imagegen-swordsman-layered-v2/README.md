# Swordsman V3 independent-layer generation experiment

**Status:** `SUPERSEDED_REVIEW_ONLY`

This experiment generated each layer as a separate image. It was stopped after
review because the independently generated parts did not stay in sync. Keep
the files and GIFs as diagnostic evidence; do not use these sheets as the
production art source.

## Current review

- Idle mean adjacent-frame alpha IoU: `0.835`.
- Walk mean adjacent-frame alpha IoU: `0.7849`.
- The research continuity audit uses `0.88` as a warning line. These results
  require frame review and do not establish natural motion or art quality.
- The preview also showed mismatched component scale, armor material, head and
  hair registration, and layer seams.
- No BasicAttack sheet was generated and nothing from this set was imported or
  approved.

## Current authoring method

Paint one full-character master sheet per action using the existing motion
guides. Annotate one grayscale `labels.png` over each master: `0` is transparent,
`1` BaseBody, `2` HeadHair, `3` Outfit, `4` Weapon, `5` BackAccessory, `6`
CosmeticFX, and `7` Headgear. Cutouts inherit the exact master pixels, frame
order, camera, and root. Recompose them and verify that the result matches the
master before drawing alternate equipment from those cutout templates.

Use [`cutout_master_sheet.py`](../../../../../tools/character_factory_v3/cutout_master_sheet.py)
to extract the labelled parts. This current method keeps the existing motion
and fixes frame-to-frame layer registration at the source.

## Review files

- `review/layered-v3-idle-8-directions.gif`
- `review/layered-v3-walk-8-directions.gif`
- `review/layered-v3-idle-layer-breakdown.png`
- `review/layered-v3-walk-layer-breakdown.png`
- `review/layered-v3-review-report.json`

The source hashes, image sizes, motion-guide references, and pending work are
listed in `sheets-manifest.json`. The individual images are retained under
`raw/<Layer>/<action>.png`.

The six static images in `imagegen-swordsman-layer-pilot-v1` remain visual
references only. They are not copied into animated frames.
