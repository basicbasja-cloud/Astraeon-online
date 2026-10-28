# Swordsman NW frame 15: bounded ownership and underpaint proposal

This isolated candidate builds on the same-frame V2 cutout study. It refines the manual guard mask and moves a detached hilt-edge fragment from BodyCostume to Weapon. The V3 ownership proposal transfers **204 visible pixels from BodyCostume to Weapon, 163 from WeaponHandOccluder to Weapon, and 318 from WeaponHandOccluder to BodyCostume**. The resulting six-layer composition with the original sword remains byte-identical to the original master; pose, scale, HeadHair and FX are unchanged. [Body and hand layer comparison](ownership-layers.png).

The sword-covered fabric was then drafted from a bounded ImageGen close-up. The generated crop is mapped back to its original 120×100 authoring region; **the original body and canvas are not rescaled**. A manual region permits insertion of **483 candidate pixels** only where the V3 BodyCostume and hand layer are empty, the original Weapon is fully opaque, and the generated donor alpha is at least 240. Therefore the generated underpaint is concealed by the original opaque Weapon, and the **sword-on RGBA master remains byte-identical**. [No-sword and underpaint comparison](underpaint-comparison.png); magenta marks inserted pixels. [Receipt](receipt.json) pins the source layers, donor, references, prompt and implementation.

## Acceptance remains open

- Mask semantics and generated fabric need native-size review. Near-transparent weapon edges, other hidden regions, small residual fragments and surfaces not covered by this mask remain unresolved.
- A held alternative sword has not been authored or tested. Hiding the original Weapon is a diagnostic, not proof of a real weapon swap or a finished unarmed hand.
- Only NW frame 15 was studied. No motion continuity, verified planted-foot contact, recovery transition, other direction, gameplay or variant is certified.
- Both ownership and underpaint are **proposals, not imported or approved**. Original Swordsman master and runtime bindings are untouched. Coverage remains **2/96 technical imports and 0/6 complete characters**.

The V3 ownership layers are under `authoring/characters/factory-v3/patch-0.0.1/review/swordsman-nw15-weapon-ownership-v3-proposal-20261028/`; the bounded underpaint layers are under `review/swordsman-nw15-underpaint-v3-proposal-20261028/`. The generated donor, two reference crops and exact prompt are under `painted-candidates/swordsman-nw15-underpaint-20261028/`. The generation model and seed were not exposed.

Reproduce to fresh destinations:

```sh
python3 tools/character_factory_v3/propose_sword_nw15_weapon_ownership_v3.py --output /tmp/sword-nw15-ownership-v3
python3 tools/character_factory_v3/propose_sword_nw15_underpaint_v3.py --output /tmp/sword-nw15-underpaint-v3
python3 -m unittest discover -s tests/character_factory_v3 -p test_propose_sword_nw15_weapon_ownership_v3.py -q
python3 -W error::ResourceWarning -m unittest discover -s tests/character_factory_v3 -p test_sword_nw15_underpaint_proposal.py -q
```

Three ownership tests and three underpaint tests passed. Independent fresh replays reproduced ten ownership and ten underpaint artifacts byte-for-byte. Exact composition and reproducibility do not certify semantic mask quality or hidden anatomy.
