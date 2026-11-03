# Hit SW 000: bounded far-arm donor study

**Not approved.** The previous whole-master far-arm donor is resized into the same fixed authoring crop; a 7,350-pixel rectangle in the original full master receives the donor. All RGBA outside the rectangle is unchanged. A white-background flood fill estimates transparency. [Three-background comparison](comparison.png) shows a bright fringe on dark backgrounds. The donor/source seam, arm position, hand-origin correspondence, sword, feet and original full motion remain unapproved. This is a bounded full-master edit, not a separately animated limb.

[Draft, mask, receipt and source hashes](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-hit-sw000-arm-bounded-20261103/receipt.json). Donor generation prompt and controls are documented in the [earlier arm-pose study](../swordsman-hit-sw000-arm-pose-20261102/README.md). Source/runtime assets were not overwritten.

Reproduce: `python tools/character_factory_v3/propose_hit_sw000_arm_bounded.py --output /tmp/hit-arm-bounded`. No full animation, cutouts, variants, gameplay or finished action is claimed.
