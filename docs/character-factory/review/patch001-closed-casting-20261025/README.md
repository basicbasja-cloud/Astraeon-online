# Closed casting cycle and extraction gates — 25 October 2026

This checkpoint is research and factory infrastructure. It is not a completed
Mage or a completed patch. Registered production imports remain **2/96** (the
two Swordsman BasicAttack jobs); **94 jobs and all six complete characters remain
unfinished**.

## Evidence

- `mage-native-closed-cycle-four-views.gif`: all 32 native poses in four real
  diagonal views, including entry and recovery. These are **3D motion guides**,
  not final illustrated sprites.
- `native-seam-report.json`: zero endpoint matrix, projected joint and visible
  pixel differences in all four views. This verifies the native seam only.
- `validation-207-tests.log`: factory regression results, including the actual
  Blender contact/freeze checks and new raw-sheet/page tests.
- `page-upgrade-pixel-replay.json`: existing 16-pose illustrated Mage master,
  parts, sheets and GIF remain byte identical after the multi-page exporter
  upgrade; metadata now contains explicit page/rectangle bindings.
- `mage-painted-component-recovery-draft.gif`: recovered complete painted
  figures with bilateral foot correspondence. Continuous research draft;
  hand/staff alignment and semantic cutouts remain unapproved.
- `index.html`, `browser-report.json`, `browser.png`: actual 32-pose two-page
  compositor, 64 transparent/gray comparisons, zero changed pixels or page
  errors. Four visible proposal roles plus two empty FX roles yield 12 separate
  sheets and two master pages. Exact recomposition does not make the proposed
  staff/hand ownership or hidden surfaces swap-ready.
- `staff-motion-audit.json`: **FAIL**, only 10/32 poses within 12 native pixels;
  maximum painted crystal motion disagreement **91.556 native pixels**. One
  fixed frame-zero offset accommodates the decorative crystal position; no
  per-frame fitting conceals the missing staff movement. This is the current
  explicit production blocker.

The previously published illustrated one-shot remains available in
`../patch001-canonical-mage-reuse-20261025/mage-castrelease-once.gif`. It is an
isolated visible-cutout pilot, not an imported complete character.

## Changes

The closed cycle retains all 24 original Enter/Shoot/Exit source samples and
adds four explicit joint-space entry poses and four recovery poses. Original
motion files, old renderer pins and registered Swordsman artwork are preserved.
Every new guide has source/implementation snapshots and checked image hashes.

New unpublished guide PNGs were repackaged without changing any visible RGB,
alpha or non-IDAT metadata. Original capture receipts are archived; current
receipts contain a stable pose/pixel identity and per-file before/after hashes.
The supplementary class-color guide retains identical alpha and all 32 native
pose controls after packaging. See its `packaged-parent-verification.json`.

The visible-parts exporter now supports multiple 4×4 pages, at most 3072×3072
pixels per page. All parts share one fixed scale. A looping export requires
identical endpoint masters **and each separate endpoint part**. It cannot hide a
seam by adding a crossfade. Tests cover a 32-pose, two-page package and exact
recomposition of every pose. This synthetic fixture is not new production art.

## Painting failures and next production gate

Four-pose painting batches changed the leg stance and scale. Bilateral boot
correspondence rejected them; a global translation cannot correct changed
proportions. The whole-cycle image failed the original grid extraction gate:
32/32 cells entered the required cell padding. Further inspection identified
**32 complete independent figures** across those cell boundaries: the generator
changed the lattice spacing. Component ownership with one shared lattice
(169×283 source pixels), scale and offset recovers full figures without fitting
individual bounding boxes. This alternative extraction is explicitly recorded;
it does not silently override the original grid report. Bilateral correspondence
passes 32/32 poses (maximum left/right disagreement 7.713 native pixels), with
one source-verified closing-pose alias. This is a correspondence gate, not proof
of exact anatomy, stable hands or a finished character.

The second padded attempt invented spell effects and remains rejected. Raw
sources, exact prompts and extraction reports are retained under
`painted-candidates/mage-closed-cycle-20261025/NE`. Neither is registered as a
production character. Do not call exact recomposition evidence of acceptable
anatomy or motion.

Next: correct the illustrated right arm, wrist and staff to retain the actual
native movement, then review visible and hidden part ownership and exercise
actual swaps in the runtime. Empty FX layers still require authoring. Remaining
views/actions and Archer/Mage female production are still open.

## Reproduce checks

From repository root:

```sh
python tools/character_factory_v3/build_closed_mage_cycle.py \
  --output authoring/characters/factory-v3/patch-0.0.1/research/mage-closed-casting-cycle-20261025 \
  --finish-only
python tools/character_factory_v3/audit_painted_sheet.py \
  --sheet authoring/characters/factory-v3/patch-0.0.1/painted-candidates/mage-closed-cycle-20261025/NE/whole-cycle-raw.png \
  --grid 8 4 --output /tmp/mage-raw-extraction-check.json
python -m unittest discover -s tests/character_factory_v3 -p 'test_*.py'
```

Reproduce the recovered complete-figure pipeline into fresh output directories:

```sh
python tools/character_factory_v3/extract_component_sheet.py \
  --sheet authoring/characters/factory-v3/patch-0.0.1/painted-candidates/mage-closed-cycle-20261025/NE/whole-cycle-raw.png \
  --grid 8 4 --pitch 169 283 --scale 2 --offset 607 554 \
  --output .factory-replay/mage-components-new
```

Use `register_casting_paint.py` with this result and the checked native
`pose-reuse.json`, followed by `propose_mage_pilot_cutouts.py --masters` pointing
to the registered `frames` directory. SAM2 model hash is pinned in the proposer;
it runs in the cutouts Python environment. Inspect every semantic proposal.
`package_visible_pilot_parts.py --action CastingCycle --loop` creates two bounded
pages and refuses different endpoint parts. `audit_staff_motion.py` reproduces
the current movement failure from registered masters and the canonical guide.

Blender 5.2 exits normally with approved sandbox escalation. The default sandbox
can hang during PulseAudio shutdown after capture files have been written. The
diagnostic is archived; completed artifacts were verified independently. Full
capture replay requires the pinned original 4.3 and target 5.2 binaries.
