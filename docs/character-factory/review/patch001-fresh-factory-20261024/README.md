# Fresh capture factory checkpoint — 24 October 2026

This is a progress review, not a completed patch release.

The retained male Swordsman BasicAttack was rebuilt from a fresh Blender 4.3.2
capture into an empty isolated store: 64 poses, 384 part bindings and 265 pixel
objects match the preserved factory. Both atlas pages match. Chromium reports
128 exact pixel comparisons and no page errors. Original artwork is unchanged.

## Animation

- [Four directions GIF](animation/four-views-normal.gif)
- [SE GIF](animation/SE-normal.gif)
- [Full color four directions APNG](animation/four-views-full-color.png)
- [Native frame capture receipt](animation/capture-receipt.json)

These captures use the actual runtime compositor, the retained 1070ms timing,
and one common viewport. GIF palettes are reduced; APNG and native PNG frames
preserve full color.

## Reproduction evidence

See authoring/characters/factory-v3/patch-0.0.1/research/fresh-capture-factory-20261024.
The source capture identity seals every pose, camera, relevant job field and
visible RGBA pixel. Blender Date/RenderTime PNG metadata may change without
invalidating identical captures. Real alpha, color, camera or pose changes fail.

The Mage frozen image and mask replay also reproduces exactly, but its staff
ownership and figure placement remain rejected. Exact replay is not anatomy,
cutout quality or animation approval. Coverage remains 1/96 imported paint jobs,
95 missing; no complete newly verified six-character playable release.
