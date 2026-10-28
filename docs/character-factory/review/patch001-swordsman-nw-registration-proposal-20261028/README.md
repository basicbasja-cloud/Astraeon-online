# Preserved Swordsman NW frame 15 registration candidate

The same-frame guide overlay identified a visible NW hair-centroid jump from frame 14 to 15. This study proposes a **single whole-frame translation of −8 authoring pixels horizontally** for frame 15 only. It applies the same integer transform to BodyCostume, HeadHair, Weapon, hand occluder and both FX layers from the actual imported BasicAttack sequence; no scaling, separate limb deformation, frame copying or baseline overwrite is used. The selected long trail stays in its original frames. Each source object's pixels, role, pose and camera are verified before use, and the script verifies that translating all layers recomposes exactly to the translated full master with no visible pixels clipped.

[Normal comparison GIF](comparison.gif) · [slow comparison GIF](comparison-slow.gif) · [frame 15 enlarged](frame15-comparison-2x.png) · [receipt](receipt.json). Left is the original and right is the proposed registration. The GIF repeats a one-shot for comparison; this does not establish a seamless loop or the actual transition to idle.

## Measurements and limitations

- Guide head horizontal movement from frame 14 to 15: +0.889 authoring pixel. Hair alpha centroid movement: +9.184 before and +1.184 after. The provisional difference falls from **2.592 to 0.092 runtime pixels**.
- The largest lower-body alpha component below y=530 moved +4.215 authoring pixels, compared with the guide's `foot_r` movement of −7.017. After translation it moves −3.785, yielding a provisional residual of **1.0102 runtime pixels**. This is above the ≤1 px contact threshold and, more fundamentally, the component has not been verified as the same anatomical foot. It must not be rounded or treated as a pass.
- A hair centroid is not a head joint. Pose, hairstyle and occlusion can change it. Foot and head landmarks require visual review, as do all neighboring frames, the other views, the true ready/idle transition and game rendering.

This is an **unapproved candidate** for one frame of one view. It is not imported into the sprite store or game, and does not change patch coverage. Original baseline artwork is intact; 0/6 characters are complete. The candidate 768px layers and master are saved under `authoring/characters/factory-v3/patch-0.0.1/review/swordsman-nw-registration-proposal-20261028/frame15/`.

Reproduce to a fresh destination:

```sh
python3 tools/character_factory_v3/propose_sword_nw_endpoint_registration.py --output /tmp/swordsman-nw-registration
python3 -m unittest discover -s tests/character_factory_v3 -p test_propose_sword_nw_endpoint_registration.py -q
```

Three focused tests passed, covering pixel-preserving translation, rejection of clipping, and refusal to infer landmarks from an empty mask. A fresh replay produced eleven candidate artifacts byte-for-byte.
