# What the rejected arm experiment teaches

1. A point-correct rig can still produce a malformed drawing. Pinning a texture's authored shoulder/elbow endpoints to projected bones does not validate the painted joint, perspective, silhouette or hand orientation.
2. Holding a flat region's transverse width while shrinking its longitudinal direction is not a general solution to 3D foreshortening. The bent arm needs suitable perspective artwork or a continuous mesh with reviewed weights and corrective shapes. A little circle at the elbow is not anatomical continuity.
3. Give the wrist an explicit orientation related to the distal forearm and the intended grasp. The old source used a constant world-down palm offset. In the deepest free-arm key its 3D deviation is 105.07 degrees. In a different camera this becomes an obvious broken wrist even when one projection looks plausible.
4. Width and attachment gates remain useful, but their names and release logic must keep their scope. All 22 bounded checks passed on a user-rejected image bank. Never add an art approval automatically after those numbers pass.
5. Compare actual alpha masters to the accepted character, not the opaque GIF canvas. The exact v39 neutral is 399px high; full head pass 113px high/127px wide. Same overall height is insufficient to approve arms, boots, torso or volume.
6. Treat costume surfaces and hidden bones differently. The belt does not locate the hip by itself; the attempted family-rig change based on that assumption remains unselected.
7. Validate render decomposition with the actual provided output passes. Re-rendering the expected prop and composing that can accidentally ignore corruption of the submitted prop pass. The negative fixture found and corrected this bug.

Reproduction commands, from repository root:

```bash
python research/sprite-animation/proportion-repair-v42/test-rig-material.py
node research/sprite-animation/proportion-repair-v42/browser-check.cjs
```

Historical render scripts write their own case outputs. After freezing this case, copy them into a new version before authoring changes. Test mutations use temporary synthetic files and are never delivered as repaired character art.
