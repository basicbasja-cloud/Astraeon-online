# NW 15 weapon and hand ownership — V2 proposal

The prior same-frame proposal moved exposed hilt/pommel and guard pixels to `Weapon`, but inspection also found cloth, forearm and leg pixels inside the circular `WeaponHandOccluder`. This V2 keeps the same weapon transfers and proposes returning **318 visible pixels** from the hand-occluder layer to `BodyCostume`, using two bounded manual masks. The remaining hand layer is visually closer to a glove-only occluder.

[Original vs proposed body and hand layers](ownership-layers.png) · [Original and proposed composition, with/without Weapon](ownership-comparison.png) · [receipt and masks](receipt.json). The complete six-layer RGBA composition with the original sword is byte-identical to the original. HeadHair, source poses, FX and baseline files remain unchanged. Source hashes, role, camera and pose are verified; no pixels are independently warped, copied from another frame, or redrawn.

## Not yet a usable variant

These manual masks still require native-size semantic review. Small forearm, glove, cloth, trouser, guard or outline pixels may be assigned to the wrong slot. The exposed surfaces beneath the removed sword have not been authored. This is **one frame in one direction**; it does not establish a usable weapon swap or solve timing, foot contact, other frames, gameplay or the six-character scope. V2 is not imported or approved; coverage remains **2/96 technical imports and 0/6 complete characters**.

Candidate layers and the same-frame master are under `authoring/characters/factory-v3/patch-0.0.1/review/swordsman-nw15-weapon-ownership-v2-proposal-20261028/`. Reproduce with a fresh destination:

```sh
python3 tools/character_factory_v3/propose_sword_nw15_weapon_ownership_v2.py --output /tmp/sword-nw15-ownership-v2
python3 -m unittest discover -s tests/character_factory_v3 -p test_propose_sword_nw15_weapon_ownership_v2.py -q
```

Two focused tests passed, including exact recomposition and a nonempty body return. A fresh run reproduced all ten artifacts byte-for-byte. These checks do not prove semantic correctness.
