# Patch 0.0.1 implementation: reuse contract

Corrected misleading Mage metadata: 24-frame BasicAttack is its own sequence;
24-frame SkillAction reuses that sequence. Neither aliases the 16-frame
CastRelease. The existing planner already distinguished their real guide jobs;
this was not evidence of previously substituted runtime art. No source guide,
painted pixel, runtime timing or coverage changes.

Added a reproducible validator checking source job identity, sequence, frame
counts and authored-view coverage. Existing declared aliases pass. Tests reject
the old Mage declaration and a missing target. Pose reuse is not art approval.

Run `python tools/character_factory_v3/audit_reuse_bindings.py` from repo root.

## Execution order

1. Lock source mapping, camera and six-character size references.
2. Preserve tall Swordsman; correct complete Mage/Archer pilot masters against
   actual guides, with both-foot and full-anatomy checks before segmentation.
3. Cut BodyCostume (all limbs), HeadHair, Weapon; verify exact recomposition and
   semantic boundaries, then grip, occlusion and independent FX.
4. Produce locomotion, combat and remaining utility actions for all six fits.
5. Demonstrate hair/costume/weapon swaps for both sexes of each class.
6. Validate full gameplay transitions, packaging and reproducibility.

Current baseline remains 114 requested action instances, 96 paint jobs,
2/96 imported jobs and zero newly complete characters. No stage is complete
merely because its code tests pass. Master-art correction and playable admission
remain open.
