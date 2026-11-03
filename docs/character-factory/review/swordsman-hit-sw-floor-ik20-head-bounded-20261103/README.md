# Swordsman Hit-to-Idle SW — bounded head proposal

**Draft; not accepted.** The image model edited a full 5×4 sheet to lower the heads of frames 05 and 06. It changed pixels across all 20 slots despite the instruction to protect them. The proposal therefore composites only two recorded head/neck/collar rectangles from the saved donor into the previous master sheet, with feathered edges; source and donor are both 1403×1121. The mask is clipped to those rectangles. The original sheet and runtime are untouched.

[Normal comparison](normal.gif) · [slow](slow.gif) · [04](frame04.png) · [05](frame05.png) · [06](frame06.png) · [07](frame07.png). Frame 06 no longer looks upward as before. This is not visual acceptance: the region includes scarf pixels and could have seams or head-to-neck mismatch, and the change from 04 through 07, anatomy, grip, feet and resulting transition need review. These GIFs repeat a one-shot and use illustrative timings. Remaining frames, seven directions, separate parts, variants and game validation are incomplete.

Reproduce into fresh output directories:

```sh
python3 tools/character_factory_v3/propose_hit_ik20_head_patch.py --output /tmp/hit-head-patch
python3 tools/character_factory_v3/review_hit_ik20_head_patch.py --candidate /tmp/hit-head-patch --output /tmp/hit-head-review
```

The receipt under `research/swordsman-hit-sw-floor-ik20-head-bounded-20261103/` pins both inputs and verifies no pixel changed outside the two permitted rectangles. This invariant does not certify semantic boundaries or animation. The donor and prompt are retained; model/seed unavailable. Coverage remains 2/96 technical imports and 0/6 completed characters.
