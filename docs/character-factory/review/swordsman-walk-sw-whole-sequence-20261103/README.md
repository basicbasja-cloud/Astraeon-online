# Swordsman Walk SW — whole sequence candidate

**Draft; not accepted.** A 16-pose sheet was generated in one request using the existing fixed-crop Mesh2Motion guide and previous same-view draft for character identity. Both inputs and the raw output are retained; see the sibling painted-candidates directory for prompt and output. Model identifier and generation seed were not exposed. It is a new candidate, not an approved painted master or runtime asset.

[Normal](normal.gif) and [slow](slow.gif) display the entire loop next to the guide. [Seam](loop-seam.png) shows 15 → 00 → 01. A fixed whole-sheet resize, without per-frame fitting, is used for both. The rendered figure and sword change orientation through the sequence, and hand-to-grip alignment, foot contact, pose and anatomy require landmark review; no 1 runtime pixel contact claim can be made. White background, cutout semantics, swap surfaces, other seven directions, real gameplay and repeatability of generation are unresolved. It is not evidence of a finished Walk or character.

The single-frame RGB delta in the receipt includes legitimate changes in motion and shading; it is a review aid only. No source or runtime assets were overwritten. Coverage remains 2/96 technical imports, 0/6 complete characters.

Reproduce preview from saved source with `python3 tools/character_factory_v3/review_swordsman_walk_sw_whole_sequence.py --output /tmp/walk-sw-whole-sequence-review` using a fresh output directory. Script delegates to `audit_swordsman_walk_sw_loop.py`; its generator output is fixed data and cannot itself be reproduced from a seed.
