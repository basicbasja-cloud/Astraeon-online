# Skill SW frame 04: blade repair proposal

**Rejected draft; not a final or imported asset.** The key-pose sheet's drawn blade was longer than the motion guide. An image-generated donor attempted to shorten it, but also altered the body, so only a bounded feathered blade region was composited. The donor was offset −3,+2 px to bring its blade base closer to the original hilt. The exact mask is saved; no RGB pixels outside its nonzero area changed. This candidate does not replace the original sheet.

The blade is closer in length but still has a visible transition at its base when enlarged, and its tip is not proven to match the guide. The original grip and anatomy have not been certified. See the [comparison](comparison.png), [nearest-neighbor detail](blade-close-nearest.png) and [receipt](receipt.json). A shorter blade or zero outside-mask changes do not establish a usable weapon or clean cutout.

Reproduce: `python tools/character_factory_v3/propose_swordsman_skill_sw04_blade.py --output /tmp/skill-sw04-blade` using the preserved original sheet and donor. The generator's model/seed are unavailable. Two focused checks passed. No frame, action or character is marked complete.
