# Swordsman BasicAttack NW 005: visible head ownership

**One-frame proposal; not approved.** The original Weapon role contains visible hair on the opposite side of the sword and the original HeadHair contains warm scarf-colored pixels. A SAM2 suggestion with conservative color filtering moves **216 visible pixels from Weapon and 52 from BodyCostume to HeadHair**, and returns 18 warm pixels from HeadHair to BodyCostume. [Before/after head and proposed weapon](comparison.png); [SAM suggestions](sam-proposals.png). The original visible RGBA master reconstructs exactly, and the source role files remain unchanged.

The image still shows the hair as disconnected across the occluding sword because the hair **behind** the blade has never been authored. SAM and the warm-color rule may misclassify edge pixels, the remaining weapon still includes ambiguous gold fabric, and alpha fringes require inspection. This does not prove that changing HeadHair or Weapon is visually safe; no variant, sequence, other view or gameplay is approved. Do not use the draft as completed art merely because it recomposes exactly.

[Draft parts and hashed receipt](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-nw005-head-ownership-20261103/receipt.json). The saved SAM masks and receipt are in `research/swordsman-nw005-head-sam-20261103`. The source mask was regenerated with the same SHA-256 using the same checkpoint and seeds.

```sh
/workspace/.venvs/astraeon-cutouts/bin/python tools/character_factory_v3/propose_nw005_head_sam.py --checkpoint /workspace/.tools/SAM2/sam2.1_hiera_tiny.pt --output /tmp/nw005-head-sam
python tools/character_factory_v3/propose_nw005_head_ownership.py --output /tmp/nw005-head-ownership
python -m unittest discover -s tests/character_factory_v3 -p 'test_nw005_head_ownership.py' -v
```

The focused test passed original-source hash preservation, exact recomposition and overwrite refusal. It does not approve semantic ownership or hidden surfaces. No production asset changed and no action or character is complete.
