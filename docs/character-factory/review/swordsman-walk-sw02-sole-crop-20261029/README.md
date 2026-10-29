# Swordsman Walk SW02: focused rear-boot repaint study

**One-frame candidate, not approved.** Two image-generated donors edited a fixed square crop around the bent rear leg, guided by the corresponding projected source mesh point. Each donor was mapped uniformly back to the same crop and composited into the original full-body frame only within a saved feathered mask; the V2 generation used V1 as its image reference but V2 is composited directly onto the original saved master. No RGB pixels outside the nonzero mask changed. The mask includes nearby knee, thigh and costume, which still need seam and anatomy review.

[Three labeled stills](still-comparison.gif) compare the unmodified frame with the two bounded proposals. The orange ring is the selected projected source mesh point; cyan indicates the nearest pixel satisfying a coarse brown-color search. The warning distance changed from 6.13 runtime px to 2.64 and then 1.19. This is **not** a ground-contact or acceptance measurement: the source selected vertex may not correspond to painted footwear, and the color pixel is not a confirmed painted sole. In the final proposal the boot visually approaches the projected point but is not fully verified.

Only SW frame 02 was altered. Frame 03, adjacent movement, hair/body fit, source/game floor, seam quality, full 16-frame loop, seven other directions, alpha, cutouts, variants and gameplay remain open. This GIF cycles stills, not animation. Donors, exact prompts, input crops, source master, mask and receipts are retained in the corresponding `painted-candidates` and `review` directories. Model/seed information was unavailable.

```sh
python tools/character_factory_v3/propose_swordsman_walk_sw02_sole_crop.py --output /tmp/walk-sw02-sole
python -m unittest discover -s tests/character_factory_v3 -p test_swordsman_walk_sw02_sole_crop.py -v
```

Two bounded-output tests passed. No baseline or runtime assets changed; 2/96 technical imports, 0/6 complete characters.
