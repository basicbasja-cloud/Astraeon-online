# NW foot association: still not verified

[Enlarged fixed-crop inspection](foot-landmarks.png) shows the original male Swordsman BasicAttack frames 0, 14 and 15, plus the whole-frame registration candidate for frame 15. Red marks the projected rig `foot_r` origin and cyan marks `foot_l`; these are bone origins, not ground-contact points. Each original BodyCostume is verified against its actual imported RGBA object. The candidate is verified to be exactly the proposed −8 authoring-pixel whole-frame translation.

The red origin lies over the forward visible boot. The cyan origin lies over the illustrated lower-leg area rather than an unambiguously distinct rear shoe. This does **not** establish which painted pixels correspond to the other foot, its contact state, or a valid foot-to-ground error. The provisional lower-component metric in the candidate report remains 1.0102 runtime px and cannot be treated as a verified or passing contact measurement. Do not promote the candidate on this evidence. Inspect the 3D foot bone and projected ankle/sole, the painted leg/boot ownership, and recovery to the actual ready pose before deciding whether registration or master anatomy needs correction.

No original or imported art was changed. 0/6 characters are complete. Reproduce to a new destination with:

```sh
python3 tools/character_factory_v3/review_sword_nw_foot_landmarks.py --output /tmp/sword-nw-foot-review
```

A fresh replay reproduced the image and receipt byte-for-byte; see [receipt](receipt.json). The 3× enlargement shows pixels for inspection and does not add source detail.
