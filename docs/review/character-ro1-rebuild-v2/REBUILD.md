# Fresh RO1 character rebuild

Status (2026-10-10): reusable pipeline implemented and tested; fresh artwork remains
a study, not an approved production master.

Open `http://127.0.0.1:8022/character-pose-study.html` for the new eight-direction
BasicAttack study. Normal and half-speed APNG/GIF exports are in `attack-study/`.
There are 48 original painted key poses, held on the existing 16-frame, 450 ms clock.
This does not imply 128 independently painted frames or separated equipment.

The shared baseline contract and tools live in
`authoring/characters/baselines/humanoid-ro1-v1/CONTRACT.md`. Artwork-only manifests
inherit geometry, timing, attachment points and draw order. Normal family builds
reject unapproved baselines. Complete Head+Hair is separate from BodyWithOutfit.

New work includes original separated neutral body/head studies, a source reference
workbench, generic appearance review/export, grip diagnostics, normalization,
candidate-master creation, replacement manifests and a fixed-proportion pose guide.
The guide's anatomy is explicitly derived planning data, not decoded RO skeletons.

Current visual limitations: painted foot movement between key poses, inconsistent
profile/diagonal facing in some frames, recovery discontinuities, and weapon/head
separation still outstanding. Idle/Walk and alternate costume/weapon production
art are not completed by this attack study. None of these are waived by code tests.

The first 48-pose generation omitted a direction and was rejected. Northwest's
initial strip switched hands at contact and was corrected. Northeast and Southeast
source-cell collisions required fresh padded sheets. Original sources are retained;
the review exporter records a uniform per-sheet scale and an explicit alpha noise
floor of 16/255, removing only near-transparent background residue. No per-frame
fitting or limb deformation is used. Source hashes and cleanup counts are recorded.

Validation: 312 Node tests and 34 Python tests passed before addition of the five
focused pose-study exporter tests. Browser checks exercise live animation,
half-speed, six pose stops, mobile layout and console errors. Historical tests
cover rejected packs too; their passing does not validate this new artwork.

Owner directive supersedes the previous surgical-repair preference: rebuild the
character artwork and assembly rather than repairing rejected candidates.

Scope: Idle, Walk, BasicAttack; original ASTRAEON character identity; BodyWithOutfit,
complete Head+Hair styles separate from BodyWithOutfit (latest RO1 clarification),
MainHand, OffHand, Headgear, Garment, and
optional slash. Preserve gameplay and the 450 ms attack clock unless direct evidence
justifies a presentation change. No changes to Combat.

Reference gate: inspect actual RO1 body-only and assembled sword/head animation,
record per-frame registration and visible grip/occlusion; inspect eight directions
without claiming duplicated source records are independent projections. Review a
new full-body pose board before producing animation art. Do not import rejected
limb warps or old inferred joints into this baseline.

Source pixels and raw ACT/SPR stay in ignored private reference storage. Only
measurements, source citations, original art, and original runtime data are shipped.
