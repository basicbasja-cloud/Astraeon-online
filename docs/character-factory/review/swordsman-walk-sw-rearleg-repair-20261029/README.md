# Swordsman Walk SW: bounded rear-leg repaint

**Two-frame master proposal, not accepted or admitted.** A generated donor attempted to move the raised rear leg in source poses 02 and 03 closer to the corresponding rig poses. Only two feathered regions were applied to the original full-body master sheet; 119,231 RGB pixels changed, and none outside the saved nonzero mask changed. The mask includes nearby thigh/costume; it is a master repaint study, not separately animated limbs. Source art is preserved.

In the [frame 02 overlay](frame02.png), the projected right-foot bone origin moves into the painted boot region after the repaint. In [frame 03](frame03.png), its relationship to the painted ankle remains uncertain. A projected bone origin is not a verified painted ankle, ground contact or sole, and these screenshots do not certify anatomy or stable movement. The [two-frame GIF](two-frame-review.gif) is a comparison of only two frames, not a complete walk loop. Check feather seams, head and body registration across pairs, actual foot motion, all other frames and seven other views before production.

Reproduce to fresh outputs:

```sh
python tools/character_factory_v3/propose_swordsman_walk_rearleg_repair.py --output /tmp/walk-rearleg-proposal
python tools/character_factory_v3/review_swordsman_walk_rearleg_repair.py --candidate /tmp/walk-rearleg-proposal --output /tmp/walk-rearleg-review
python -m unittest discover -s tests/character_factory_v3 -p test_swordsman_walk_rearleg_repair.py -v
```

The donor, prompt, source, candidate, mask and receipt are retained under `painted-candidates/swordsman-walk-sw-rearleg-repair-20261029/` and `review/swordsman-walk-sw-rearleg-repair-20261029/`. The generator model and seed were not provided. Two focused tests passed. No runtime or canonical asset changed; 2/96 technical imports and 0/6 complete characters remain.
