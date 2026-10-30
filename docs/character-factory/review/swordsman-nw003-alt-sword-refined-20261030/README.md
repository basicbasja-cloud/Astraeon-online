# Swordsman BasicAttack NW 003: refined alternate sword mask

**Single-frame draft; not approved for runtime or reusable variants.** A manually inspected polygon constrains the previous SAM blade mask while retaining the separate guard and pommel portions. It excludes 4,008 pixels of the original 1,254px SAM mask; [isolated comparison](weapon-isolation-comparison.png) shows the dark arm fragments beneath the blade are reduced. [Original and alternate on three backgrounds](comparison.png). The remaining mask and hand boundary still require close semantic and alpha inspection; the polygon can cut blade pixels or retain neighboring color.

The prototype uses the prior provisional sword-free complete master and a same-frame glove polygon. Nothing outside the union of the candidate weapon and hand is changed. A distinct source sword exists for this single frame only; the mask does not establish correct wrist anatomy, hidden grip, animation, other directions, factory reuse or gameplay. No protected original or runtime asset changed.

[Draft layers and hashed receipt](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-nw003-alt-sword-refined-20261030/receipt.json). Input donor, SAM masks, model hash and generation prompt are documented in the [preceding prototype](../swordsman-nw003-alt-sword-swap-20261030/README.md).

```sh
python tools/character_factory_v3/propose_swordsman_nw003_alt_sword_refined.py --output /tmp/nw003-alt-sword-refined
python -m unittest discover -s tests/character_factory_v3 -p 'test_swordsman_nw003_alt_sword_refined.py' -v
```

The focused outside-union and overwrite test passed. The visual and semantic gates remain open; no action or character is complete.
