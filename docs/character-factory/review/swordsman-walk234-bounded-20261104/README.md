# Walk SW frames 02–04: bounded sequence correction

Draft, not accepted. Three consecutive actual poses were edited together against their Blender guides. The resulting rear-leg regions are extracted into the corresponding original master frames using recorded masks. All pixels outside the masks and all thirteen other frames are byte-identical to the fixed review baseline. No frame borrows a limb from a different pose. [Frames 01–05 comparison](neighbors.gif); [02](compare02.png), [03](compare03.png), [04](compare04.png).

Three mask revisions were reviewed. The first left an old-edge fragment; the second encroached on the foreground leg; the retained third version narrows the front boundary. The hip join and foreground-leg boundary still need semantic review, and the joins to unchanged frames 01/05 require guide-relative contact and motion review. The repaired rear legs differ from the earlier one-frame correction; neither is approved. This is not a completed Walk, cutout package or game character. Coverage remains 2/96 technical imports and 0/6 completed characters.

Reproduce extraction and preview from saved inputs:

```sh
python tools/character_factory_v3/build_walk234_bounded_master.py --output /tmp/walk234-review
```

The receipt stores input/script hashes, masks and exact protected-pixel checks. Scaling is fixed review scaling and adds no painted detail. The generated triptych and its input guide/art are retained under `painted-candidates/swordsman-walk234-rearleg-20261104`. Image generation did not expose a model revision or seed; the generation is not exactly reproducible. Preview delay is 200ms per frame, diagnostic only. No runtime files were modified.
