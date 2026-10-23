# Native composition technical review — 23 October 2026

- 62 Python tests pass, including18 actual Blender poses and held-detail PNG export.
- 146 individual Node checks pass.
- 8 actual Chromium checks pass; seven image comparisons each have zero changed pixels.
- Actual Archer independent-layer baseline: 1,509 changed pixels.

The harness tests full-resolution overlapping source layers, hidden-body retention,
weapon/head removal or swap, opacity, trimmed crop offsets, real Archer partition
seams, and missing-atlas atomicity. It is not the game and does not verify six new
playable characters. `report.json`, `browser.png` and test reports retain evidence.

The real Archer source parts are still partially fused. Synthetic underlay/swap
fixtures are explicitly labeled in the page. Passing rendering comparisons does
not approve anatomy, cutout ownership, hidden-body artwork or action continuity.
