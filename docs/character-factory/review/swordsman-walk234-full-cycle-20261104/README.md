# Full-cycle Walk review after the three-frame correction

**Draft, not accepted.** [Full-cycle comparison](cycle.gif) · [slow](cycle-slow.gif) · [03–06 guide/original/revised](boundary-3-4-5-6.png). All sixteen poses are shown at fixed shared scale, including unchanged parts of the cycle. The five-frame preview alone does not establish a passing Walk.

The 03–06 comparison shows the original guide's legs crossing during the stride; correcting only raised boots 02–04 is insufficient to qualify that whole sequence. Source mesh sample points are not verified painted soles. Absolute point-to-art distance must not be used alone as a failure or acceptance measurement because selected vertices, costume volume and body proportions differ. Actual corresponding foot landmarks, temporal body consistency, motion timing and gameplay remain unresolved. The approved tall Swordsman remains the design authority; no runtime admission or coverage increase is claimed.

The bounded extraction now rejects modified baseline or proposal inputs by SHA-256 before creating output. A fresh replay produced thirteen identical PNG/GIF artifacts byte for byte; only the receipt's script hash changed as expected. These checks validate extraction reproducibility, not painted anatomy or animation quality. Original master and runtime files remain intact.

Reproduce into fresh directories:

```sh
python tools/character_factory_v3/build_walk234_bounded_master.py --output /tmp/walk234-pinned
python tools/character_factory_v3/review_walk234_full_cycle.py --output /tmp/walk234-cycle
```

GIF delays are diagnostic choices and are not the gameplay contract. Coverage remains 2/96 technical imports and 0/6 complete characters. Next art work needs verified correspondences through the crossing-leg poses and a consistent full-body master; a series of local masked patches is not sufficient evidence of a passing motion.
