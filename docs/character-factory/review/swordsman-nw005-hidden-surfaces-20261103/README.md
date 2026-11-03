# Swordsman BasicAttack NW frame 005: hidden surface draft

Status: **not accepted; one frame only**. This is a diagnostic cutout experiment, not a playable animation or a completed action.

- The previous Weapon layer included visible hair and scarf. A previous ownership proposal recovered the visible hair while preserving the original composite.
- An image editing model generated a same-frame crop with the blade removed. Its prompt was: “Edit this exact cropped fantasy animation frame to supply the hidden hair behind the sword. Remove the silver blade crossing the back of the head and paint the missing spiky silver-lavender hair underneath it, continuing existing strand direction, color and lighting. Preserve the same head shape, scale, camera, golden scarf, shoulder armor, glove and every other feature. Do not add a weapon or change the character pose. Preserve the full square crop and white background; no text or marks.” The input and raw output are retained in `painted-candidates/swordsman-nw005-hidden-hair-20261103/`; provider seed/model were not exposed.
- The proposal adds 206 donor pixels to HeadHair behind fully opaque weapon pixels. A second proposal transfers 81 visible warm pixels from Weapon to BodyCostume. A third adds 99 generated warm pixels to BodyCostume under the opaque weapon. Original master RGBA still matches pixel for pixel when the original weapon is composited.
- **The removed-weapon view still has a large hole at the neck/scarf** and the generated strand and scarf boundaries need review. The color-filter ownership can include guard details and omit scarf. A matching composite only proves the old weapon conceals the draft: it does not validate an alternate weapon, hidden geometry, seam quality, animation, frame registration, body size or gameplay. Do not import as production.
- No source master or original layer was overwritten. The drafts and receipt hashes are under `patch-0.0.1/research/`.

Reproduce, choosing fresh directories:

```sh
python3 tools/character_factory_v3/propose_nw005_hidden_hair.py --output /tmp/nw005-hair
# The scarf script reads the checked-in draft HeadHair-underpaint.png.
python3 tools/character_factory_v3/propose_nw005_scarf_ownership.py --output /tmp/nw005-scarf
python3 tools/character_factory_v3/propose_nw005_scarf_underpaint.py --scarf-dir /tmp/nw005-scarf --output /tmp/nw005-scarf-filled
python3 -m unittest discover -s tests/character_factory_v3 -p 'test_nw005*.py' -v
```

Next: author and inspect the exposed neck/scarf for a real alternate weapon, resolve antialiased boundaries and front-hand occlusion, then repeat per frame and direction. Check the actual animation and gameplay before declaring any action complete.
