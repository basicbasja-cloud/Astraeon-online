# Preserved tall Swordsman: guide overlay and size diagnostic

This review uses the existing male BasicAttack technical import, not the retired compact preview. It composites the actual six bound layers, including the long sword-trail layers, in their recorded order and adds the same-frame rig's projected head, hands, pelvis and feet. All 64 poses use one 768×768 authoring canvas mapped uniformly to 240×240; no image is independently fitted or translated. Asset role, pose, camera and decoded pixel hashes are checked. Cyan lines only connect landmarks for visual inspection; they are not a full anatomical skeleton.

- [Four views at native runtime canvas](four-view-guide-overlay.gif)
- [Four views enlarged 2× for inspection](four-view-guide-overlay-2x.gif) — nearest-neighbour enlargement, not extra source detail
- [Frame 0](frame00.png) · [Frame 7](frame07.png) · [64 frame metrics](frame-metrics.csv) · [hash receipt](receipt.json)

The GIF repeats a **one-shot** for inspection with its source timing and final hold. The repeat is not a gameplay transition or proof of a seamless idle loop. No character is installed in the game by this review.

## What the measurements do and do not show

For frame 0, visible distance from the top of the HeadHair alpha to the bottom of BodyCostume alpha is approximately SW 64.38, NW 69.38, NE 58.75 and SE 69.38 pixels on a 240 canvas. The `referenceHeight=88` metadata value is a rendering reference, not a direct measurement of the painted body. These extents include hairstyle, costume and projected pose, so the differences alone neither certify nor disprove size shift. Game zoom and actual game capture must be checked separately.

Between the first and last sampled frames, the source guide's projected head y changes by less than 0.5 runtime pixel and each projected foot y by at most 0.01 pixel in these four views. The visible HeadHair top differs by approximately 2.5–3.1 pixels and the BodyCostume alpha bottom by approximately 0.9–2.2 pixels in the respective views. Those alpha extrema are not confirmed anatomical crown or planted-foot landmarks and can shift with hair, shoe silhouette, antialiasing or pose. They identify frames for manual landmark review, not a verified contact error. BasicAttack is a one-shot, so its recovery must be compared to the actual ready/idle transition rather than forced to match its first image.

## Reproduction and status

```sh
python3 tools/character_factory_v3/review_swordsman_guide_geometry.py --output /tmp/swordsman-guide-review
```

A fresh replay reproduced all six generated artifacts byte-for-byte. The generator checked 269 unique referenced RGBA objects and the recorded role/pose/camera metadata. This does not validate anatomy, semantic cutouts, hidden surfaces, FX occlusion or gameplay. No baseline was overwritten. Swordsman visual acceptance remains open, Mage and Archer pilots remain open, and overall coverage remains **2/96 technical imports, 0/6 complete characters**.
