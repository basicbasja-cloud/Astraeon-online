# Fixed-viewport Archer repaint study

Four 2x2 batches retain all 16 new paintovers, exact prompts, source plates,
same-pose head references, viewport recipes and transparent fixed-grid slices.
Two additional marked-grid studies are retained separately, not silently selected.

The material-only Blender source matches all 16 current world-landmark records
exactly. See `source-provenance.json`. All batches use the shared detail viewport
`[170,30,590,740]`; normalization rejects an aspect error above 0.5% and never
fits individual painted figure bounds. `normalize_fixed_viewport_batch.py` is the
reusable rectangular-cell adapter.

The source-locked four-frame prefix in the neighboring
`head-locked-prefix-study/tight-fixed-viewport/` improves hair-top layout to 0–1px
in its color-bound diagnostic. This did not generalize to every batch: some
lower-row figures move upward. The full sequence is therefore **not accepted**.

`sequence-review/normal.gif` and `slow.gif` use the canonical 768px canvas and
shared source viewport, followed by one 240px reduction. Their timing is the
existing 1000ms review proposal, not gameplay admission. `source-vs-paint.gif`
shows enlarged detail comparisons. The original individual-frame study and
its cutout sheets remain separate and are not overwritten.

These experiments do not replace the earlier Swordsman artwork that the owner
said was already okay. No patch paint job, complete semantic cutout package or
playable-character coverage is claimed here.
