# Tall Swordsman Walk SW loop review

Status: **draft, not approved or imported**. This reviews the 16-frame SW draft already recorded in `patch001-swordsman-walk-sw-fixed-crop-20261029`. Both sheets use one fixed whole-sheet resize; no frame-specific fitting. The generated draft is a white-background contact sheet, not a usable layered master. The other seven views are missing from this draft.

The [normal](normal.gif) and [slow](slow.gif) previews show guide and draft side by side, looping with the 15→00 seam. The [seam board](loop-seam.png) compares frames 15, 00 and 01. The illustrated sword, head, feet and costume vary through the cycle and require pose-by-pose assessment. The guide itself moves at the seam, so difference at that transition alone does not prove a reset defect.

The receipt records fixed-grid adjacent-frame foreground-union RGB differences as a visual review aid. These include legitimate motion, details, weapon and changed drawing, so they neither prove nor disprove jitter, foot slip, scale stability or grip. For this draft, 07→08 and 15→00 show substantial changes and should be reviewed against source pose and identifiable contact landmarks. There is no certified sole annotation; do not infer a 1-runtime-pixel contact result from these numbers. Any improvement must retain one character scale and consistent master per frame before extracting same-frame slots.

Reproduce into a fresh directory: `python tools/character_factory_v3/audit_swordsman_walk_sw_loop.py --output /tmp/swordsman-walk-sw-loop-review`. No runtime or baseline files are altered. Three focused tool checks passed. No completed character or action is claimed.
