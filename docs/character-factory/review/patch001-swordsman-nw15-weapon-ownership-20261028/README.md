# Swordsman NW 15 weapon ownership — provisional

Inspection of the actual imported male BasicAttack NW frame 15 shows visible sword hilt/pommel pixels in `WeaponHandOccluder` and visible guard pixels in `BodyCostume`. When the Weapon layer is hidden, those fragments remain, so the original cutout cannot by itself demonstrate a clean weapon swap.

This same-frame proposal transfers a conservative manually drawn mask of 139 visible pixels from BodyCostume and 163 from WeaponHandOccluder into the Weapon layer. All other roles, pose, scale and source artwork are unchanged. The original and proposed six-layer compositions with the original sword are **byte-identical RGBA**. The [comparison](ownership-comparison.png) shows original and proposed with the sword and with the Weapon layer hidden; hiding the layer is a diagnostic, not a finished unarmed pose.

The masks are **not semantically approved**: individual outline, glove, guard and costume boundary pixels need native-size review; some small fragments or non-weapon pixels may be misassigned. Areas originally hidden behind the sword have not been drawn. One frame and direction do not establish a usable interchangeable weapon set, animation continuity, foot contact, variants or gameplay. The candidate is not imported or used by the game, and the baseline is preserved. Coverage remains 2/96 technical imports and 0/6 complete characters.

Candidate layers and complete same-frame master are under `authoring/characters/factory-v3/patch-0.0.1/review/swordsman-nw15-weapon-ownership-proposal-20261028/`; [receipt](receipt.json) contains mask coordinates, counts and source hashes. Reproduce to a new directory:

```sh
python3 tools/character_factory_v3/propose_sword_nw15_weapon_ownership.py --output /tmp/sword-nw15-ownership
python3 -m unittest discover -s tests/character_factory_v3 -p test_propose_sword_nw15_weapon_ownership.py -q
```

Two focused tests passed; a fresh replay reproduced the nine generated artifacts byte-for-byte. Pixel-exact reconstruction does not certify semantic boundaries.
