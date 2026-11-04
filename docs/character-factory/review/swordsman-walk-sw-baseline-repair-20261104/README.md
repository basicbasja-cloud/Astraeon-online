# Swordsman Walk SW — protected baseline repair attempt

**Draft, not accepted.** This is a whole-sheet edit using the [previous 16-frame draft](../../../../authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-sw-whole-sequence-20261103/generated-sheet.png), the actual fixed-crop Mesh2Motion guide and the [protected original Swordsman reference](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-walk-ip-baseline-reference-20261104/reference.png). It retains the character's silver hair, gold scarf and bronze armor visually, but that is not proof of identity or animation acceptance. [Normal comparison](normal.gif) · [slow comparison](slow.gif) · [15 → 00 → 01 seam](loop-seam.png).

The painted leg and foot placement at the loop seam does not closely establish the corresponding guide poses. Position, proportions, sword grip and contact need frame-by-frame verification; no <=1 runtime pixel claim is established. The fixed-grid comparison uses one whole-sheet resize and 85 ms / 200 ms preview delays; these are review previews, not measured gameplay timing. No same-frame cutouts, semantic checks, swaps or game capture exist for this attempt. It has not been admitted to runtime. Coverage remains 2/96 technical imports and 0/6 newly completed characters.

The image edit had no exposed model revision or seed, so the generation is not exactly reproducible. The prompt and generated image are retained with the guide in the sibling painted-candidates directory. Input SHA-256 values: old draft `af97b2424fe6571771adb9580bb7ab03456d9608e780288df0517d199037ae74`; guide `c1e887fb710bece6e967e5d43ece0841dc22e401ef6823ee7ee66251b4264b3a`; protected identity crop `bcd70ca204c31e7ca97da3b9ef4cfce90377042753540307b94e70b8c12955da`. New sheet SHA-256 `6006e57b6896db2ca35ca4a13727259e4a3b9dd790ed2a9a80b414d210ab7c90`.

To reproduce the review from saved inputs into a fresh output directory, run from the repository root:

```sh
python -c "import sys; from pathlib import Path; sys.path.insert(0,'tools/character_factory_v3'); import audit_swordsman_walk_sw_loop as m; m.SOURCE=Path('authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-sw-baseline-repair-20261104'); m.build(Path('/tmp/walk-baseline-repair-review'))"
```

The receipt's pixel deltas include ordinary motion and are not anatomy or contact metrics. No original baseline or existing runtime file was modified.
