# Swordsman Walk SW03: follow-up rear-leg repaint

**Single-frame master proposal, not approved.** A second local donor repaint moved the raised rear boot closer to the projected guide bone origin. The generated donor was resized uniformly from 1254×1254 to the existing 887×887 review cell and applied only within a saved feathered local mask on the prior full-body master. The mask includes thigh and costume; 64,766 pixels changed and no RGB pixels outside the mask changed. It does not alter frame 02 or any other frame.

The [guide/previous/new overlay](frame03-comparison.png) shows the yellow source foot-bone origin near the repainted boot edge rather than in the empty gap. This visual comparison is not a measured painted ankle or sole contact and does not validate the shape, seam, nearby body, registration or motion. Head drift between pairs remains unresolved, and no complete walk, clean alpha, same-frame cutout, variant or game transition exists. The earlier [two-frame comparison GIF](../swordsman-walk-sw-rearleg-repair-20261029/two-frame-review.gif) is a partial review, not a loop.

Reproduce with saved inputs:

```sh
python tools/character_factory_v3/propose_swordsman_walk_sw03_rearleg.py --output /tmp/walk-sw03-proposal
python tools/character_factory_v3/review_swordsman_walk_sw03_rearleg.py --candidate /tmp/walk-sw03-proposal --output /tmp/walk-sw03-review
python -m unittest discover -s tests/character_factory_v3 -p test_swordsman_walk_sw03_rearleg.py -v
```

Donor, prompt, mask and receipt are retained under `painted-candidates/swordsman-walk-sw03-rearleg-repair-20261029/` and `review/swordsman-walk-sw03-rearleg-repair-20261029/`; the generation model and seed were not exposed. Two bounded-output tests passed. No canonical or runtime asset changed; 2/96 technical imports and 0/6 complete characters remain.
