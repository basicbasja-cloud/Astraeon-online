# Original source conditioning diagnostics — naturalness rejected

The user reviewed this board and explicitly said the image/motion remains unnatural. **Naturalness FAIL; art/acting not approved.** These are technical maps of the existing original unapproved attack proof, preserved as evidence, not a production pose or visual seed.

The reusable `export-conditioning.py` read a verified immutable v6 build and emitted 64key sets (eight poses × eight directions) into a separate directory. It did not change the rig, retarget a new action or fix the final art. [conditioning.json](conditioning.json) records source/build/exporter hashes, maps, exact coordinates and release blockers.

- [SE maps](SE-conditioning-review.png) show FX-off source, source-known skeleton, full silhouette, visible item-piece IDs and fixed-range depth.
- [SE grip inspection](SE-grip-review.png) records the diagnostic crop on the full native canvas. Finger/palm-to-hilt surface contact remains **unverified**.
- Every facing has the same pair of review boards and all per-key maps in its directory. IDs are categorical grayscale values, not colors; review palette is a separate derivative. Two gloves sharing an item ID are not left/right hand surface identification.
- Silhouette/ownership/depth support agree at256×256; skeleton/composite is128×128, exactly2× related. All full frames keep the source camera and canvas; per-frame bbox fitting/mirroring/depth normalization is absent.
- Six independent source color discrepancies, no original walk, no articulated original fingers, no approved acting/art/FX and no production game-renderer run still block release.

For the user's naturalness correction, read [new mechanics practice](../../../skills/modular-eight-direction-sprites/references/natural-motion-practice.md) and [fresh external source walk/attack study](../source-motion-v7/README.md). Source study is not an automatic successful retarget.
