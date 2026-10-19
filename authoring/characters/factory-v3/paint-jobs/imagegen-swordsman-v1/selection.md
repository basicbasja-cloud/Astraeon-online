# Painted sheet review selection

The job retains the raw outputs and guides for the eight-direction Idle, Walk, and BasicAttack candidates. The second BasicAttack generation is selected: after alpha cleanup, it has the clearest readable low sweep and a stronger, more consistent silhouette at the 160px runtime cell. The earlier attack iteration remains as `raw/basicattack-imagegen-v1.png` for comparison.

Review used the full sheet and the south-facing sprite at native runtime scale over a dark matte. Pixels below alpha 128 were removed, and the remaining alpha range was remapped to preserve smooth antialiasing. The importer also removes disconnected spill from neighboring cells and trims pixels beyond a 6px-dilated pose-guide silhouette. No checkerboard, glow, or obvious colored fringe remained at runtime scale. This is an internal visual assessment; the owner has not approved the painted art or the motion.

The Idle and Walk provider requests were not retained verbatim with the raw outputs. Their prompt files are explicitly marked as canonical reconstructions. The selected BasicAttack request is recorded verbatim.

The three actions currently form one fused character composite. Outfit, hair, and weapon are not separate painted layers, so this candidate is only for visual review and game playback, not cosmetic-swap or production admission.
