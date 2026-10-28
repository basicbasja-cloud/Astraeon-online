# Swordsman NW frame 15 alternate sword — single-frame proposal

This isolated study adds a distinct slim steel-and-teal sword to the earlier V3 same-frame ownership/underpaint candidate. The generated transparent sword uses the original weapon's fixed square reference crop. It is uniformly mapped from the full 1254×1254 donor into the recorded 150×150 authoring crop, without fitting to the generated bounding box or changing character pose/canvas. Its complete handle sits below the existing visible hand layer.

[Original / alternate / no-weapon comparison](weapon-swap-comparison.png) · [three-state single-frame toggle GIF](weapon-swap-toggle.gif) · [receipt](receipt.json). The GIF changes equipment on one static frame; it is **not** an animation or a loop-continuity test.

The original manually annotated grip maps to approximately `(353.98, 486.42)` in the 768 authoring canvas. At the nearest pixel, both the alternate sword and the occluding hand have alpha 255, and the original annotated tip location has alternate alpha 193. The source reference crop is verified against the current candidate's original Weapon layer. These point checks establish limited pixel coverage, **not** a correct hand grip, wrist, semantic ownership or full blade alignment. All non-Weapon layers remain byte-identical to the unapproved underpaint candidate; the original artwork and runtime bindings are unchanged.

## Limitations and status

- The generated weapon, glove boundary, occlusion, underpaint and transparent edges require semantic visual review. Hidden surfaces and other mask regions remain incomplete.
- Only **male NW frame 15** is represented. No other frame or direction, coherent alternative weapon animation, long trail alignment, real game, or body/hair variant is established.
- The proposal is **not imported, approved or ready for production**. It does not establish a reusable factory variant. Coverage remains **2/96 technical imports and 0/6 completed characters**.
- Raw generated sword, reference crop and prompt are under `authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-nw15-alternate-sword-20261028/`. The generated model and seed were not exposed. The proposed Weapon and assembled frame are under `review/swordsman-nw15-alternate-sword-proposal-20261028/`.

Reproduce using a fresh destination:

```sh
python3 tools/character_factory_v3/propose_sword_nw15_alternate_weapon.py --output /tmp/sword-nw15-alternate
python3 -W error::ResourceWarning -m unittest discover -s tests/character_factory_v3 -p test_sword_nw15_alternate_weapon.py -q
```

Three focused tests passed, and a second run reproduced all five outputs byte-for-byte. These checks do not replace semantic review or game validation.
