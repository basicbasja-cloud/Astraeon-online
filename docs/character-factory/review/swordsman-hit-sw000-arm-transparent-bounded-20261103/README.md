# Hit SW 000: transparent bounded far-arm donor

**Not approved.** The prior far-arm donor was sent to image editing with transparent background requested, then mapped to the same fixed crop and inserted within the same 7,350-pixel full-master rectangle. [Three-background comparison](comparison.png) shows the large bright fringe from the earlier flood-fill study is reduced. A focused test verifies all pixels outside the mask remain unchanged and output overwrite is refused.

The background-removal model redrew parts of the character rather than producing a byte-identical cutout. Head, hand, forearm and sword geometry have not been verified against their correct physical landmarks, and the body/weapon boundary and residual edges remain unapproved. This is a single-frame master study, not a separated or independently positioned arm, an animation, a usable character or gameplay evidence. Source/runtime files were not overwritten.

[Candidate master, mask, receipt and input hashes](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-hit-sw000-arm-transparent-bounded-20261103/receipt.json). Generated transparent donor is retained in `painted-candidates/swordsman-hit-sw000-arm-transparent-20261103/`; original donor and pose controls are in `painted-candidates/swordsman-hit-sw000-arm-pose-20261102/`. Generator model/seed were not exposed. Prompt: “Remove only the plain white background from this exact fighter image and make it transparent. Preserve the character, sword, pose, colors, details, scale, position and full square canvas exactly, with clean antialiased edges and no white fringe. Do not redraw or add anything.”

```sh
python tools/character_factory_v3/propose_hit_sw000_arm_transparent_bounded.py --output /tmp/hit-arm-transparent-bounded
python -m unittest discover -s tests/character_factory_v3 -p 'test_hit_sw000_arm_transparent_bounded.py' -v
```

No action or character is complete.
