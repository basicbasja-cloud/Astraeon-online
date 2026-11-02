# Swordsman BasicAttack NW 003: two-slot swap review

**One-frame draft.** The same corrected BodyCostume is combined with original or alternate HeadHair and original or alternate Weapon, including the alternate hand-occluder when needed. [Four combinations](comparison.png) and [still-frame toggle](still-toggle.gif). The GIF alternates equipment on a single pose; it is not an animation or a smoothness test.

All four comparisons report zero changed pixels outside the union of the relevant head or weapon/hand masks. This narrow invariant does not prove mask semantics: the head/collar seam, white fringes, guard and glove overlap and hidden surfaces still require review. The alternate assets exist for one pose/view only and are not yet usable factory variants. No source or runtime asset was overwritten and no gameplay was tested.

[Full-frame draft outputs and receipt](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-nw003-two-slot-swaps-20261102/receipt.json). Input hashes bind the source slots; see the linked head, weapon and body-edge reviews for their generation and limitations.

```sh
python tools/character_factory_v3/review_nw003_two_slot_swaps.py --output /tmp/nw003-two-slot-swaps
```

The script verifies the outside-slot-union invariant and refuses an existing output. No action or character is complete.
