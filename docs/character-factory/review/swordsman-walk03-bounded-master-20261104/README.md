# Walk 03: bounded master repair

**Draft; whole motion is not accepted.** A bounded region from the actual frame-03 image-edit proposal is copied into the same frame's master. It does not use a leg from another pose. [Before/after](frame03.png), [02 → 03 → 04 diagnostic preview](neighbors-slow.gif). The raised boot moves toward the guide while every pixel outside the polygon remains identical at the 768px review resolution. The original 384px review frame is retained outside a downsampled binary mask as well. The earlier generated proposal's altered face and armor are excluded.

The first mask trial clipped the boot; the retained polygon includes it. The second trial preserves the boot outline visually. Adjacent frames 02 and 04 remain unchanged and their rear-foot alignment still requires repair: a single corrected frame does not establish temporal continuity, correct hip articulation or a grounded walk. This is not runtime admission, same-frame part separation, or a finished action. The 768px master is resized review data and does not add authored detail. Coverage remains 2/96 technical imports and 0/6 completed characters.

Rebuild from pinned saved inputs into a fresh directory:

```sh
python tools/character_factory_v3/build_walk03_bounded_master.py --output /tmp/walk03-bounded-replay
```

The receipt records source, proposal and script hashes, the polygon and zero changed protected pixels. No approved source master was overwritten.
