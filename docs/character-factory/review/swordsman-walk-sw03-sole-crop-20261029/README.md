# Swordsman Walk SW03: focused rear-boot repaint study

**One-frame candidate, not approved.** A generated crop donor redrew the raised rear leg towards the projected source skin point. It was uniformly mapped back to the fixed square crop and composited into the original saved full-body frame within a feathered mask. The mask includes knee/thigh/costume; no RGB pixels outside its nonzero area changed. The head and complete body remain in the same master image.

The [labeled still comparison](still-comparison.gif) shows the source and proposal. Orange marks the selected projected source skin point and cyan is the nearest pixel passing a coarse brown search. The warning distance changed from 5.78 to 1.12 runtime px. This is **not** an anatomical sole, a ground-contact measurement or a pass: source vertex selection may change, the brown pixel may belong to another region, and painted footwear need not coincide with bare mesh. Natural leg anatomy, mask seams, contact and actual temporal continuity remain open.

Only SW frame 03 was altered; frame 02 has a [separate crop study](../swordsman-walk-sw02-sole-crop-20261029/README.md). The 16-frame loop, other seven directions, alpha, same-frame cutouts, variants and gameplay are not complete. The GIF cycles stills, not animation. Donor, prompt, source/guide crops, source master, mask and receipt are retained; the generator model and seed were not exposed.

```sh
python tools/character_factory_v3/propose_swordsman_walk_sw03_sole_crop.py --output /tmp/walk-sw03-sole
python -m unittest discover -s tests/character_factory_v3 -p test_swordsman_walk_sw03_sole_crop.py -v
```

Two focused tests passed. No production or runtime data changed; 2/96 technical imports and 0/6 complete characters remain.
