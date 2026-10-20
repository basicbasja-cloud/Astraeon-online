# WeaponLight cutout contract

There is no accepted `WeaponLight` artwork yet. The old `WeaponSlash` vector
pilot crossed the character, so it is rejected and kept only in paint job v1.
Both 16-frame SE full-master trials are rejected for blade clipping. An
effects-only `WeaponLight` trial on the tighter variant is also rejected: its
repeated curved strokes cross the torso and fail to track the blade. Review
these diagnostics in `../../prototypes/basicattack-se-iteration-3/README.md`.
The separate tip-motion trace is closer to the sword path, but remains
review-only because it covers only SE and the base master still clips the blade.

When painting the 16-frame BasicAttack master, add `WeaponLight` as a separate
transparent 8-direction sheet with 16 chronological rows. Match the exact pose,
facing, root, and sword pixels in each cell. Keep frames transparent outside
the strike, use a narrow blade-aligned streak plus a compact contact glint, and
check its overlap order in all eight facings. Do not copy the rejected strokes
or broad crescent.

`review_layered_sheets.py` can inspect this sheet directly or through
`--weapon-light-sheet`. `import_layered_sheets.py` accepts
`WeaponLight/basicattack.png`, maps it to the optional runtime FX slot, and
leaves the slot transparent when the reviewed sheet is missing. It ignores
legacy `WeaponSlash` files.
