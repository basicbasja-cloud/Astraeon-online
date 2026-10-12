# Executable modular sprite workflow — v0.7

Additional v0.10 review helpers: [anatomical leg/source-bone continuity checker](../references/anatomical-continuity.md), [standalone annotation UI and high-detail results](../../../research/sprite-animation/quality-review-v10/README.md), and [fresh walk reproduction](../studies/walk-test/README.md). These bounded studies remain outside the old attack adapter's release command. They do not unlock its blocked art, exact-color or game-integration gates. Current regression suite totals 37 passing tests; the new annotation UI has 20 passing browser checks.

This is an executable review workflow, currently with **one original rig family and one attack adapter**. It builds separate complete parts and anatomical guides; it does not produce accepted artwork from arbitrary text. No paid service is used. Read [pose/reference practice](../references/pose-guide-practice.md) and fill the [ordered production brief](../templates/pose-production-brief.md) before generating or drawing character frames.

## Setup and commands

Run from the repository root. Linux/Python 3.12 was tested with Blender 4.3.2, Node 24.19, Chromium 151 and the Python packages in [requirements](requirements.txt). Blender, Node and Chromium must be on PATH. Chromium must be permitted to launch, even for filesystem-backed Playwright routes. `game-dev` is not required by this standalone adapter. Use your environment's Python package installation; for an isolated environment:

```sh
python -m venv /tmp/sprite-pipeline-env
/tmp/sprite-pipeline-env/bin/pip install -r skills/modular-eight-direction-sprites/scripts/requirements.txt
/tmp/sprite-pipeline-env/bin/python skills/modular-eight-direction-sprites/scripts/pipeline.py doctor
/tmp/sprite-pipeline-env/bin/python skills/modular-eight-direction-sprites/scripts/pipeline.py build --output /tmp/astraeon-sprites
/tmp/sprite-pipeline-env/bin/python skills/modular-eight-direction-sprites/scripts/pipeline.py check --output /tmp/astraeon-sprites
/tmp/sprite-pipeline-env/bin/python skills/modular-eight-direction-sprites/scripts/pipeline.py pack --output /tmp/astraeon-sprites --archive /tmp/astraeon-review.zip
```

In this session OpenEXR is installed separately. The actual tested equivalent was `PYTHONPATH=/tmp/sprite-render-deps python …`. The venv setup above is a setup recipe, not another executed environment test. Avoid putting pipeline output inside the skill source. Keep older proofs intact; use a dedicated output directory.

`build` sequentially runs pose generation → complete-part rendering → independent full-scene references → composition → reopened source validation → contract/negative-fixture validation → source skeleton projection → guide drawing → actual browser checks. Blender receives `--python-exit-code 2`; Python exceptions fail the stage. Logs go to the individual build's `logs/` directory.

`current.json` points to a completed immutable review build. Resolve its `build` value relative to `--output`. Serve that directory with `python -m http.server --directory <build-directory> 8772`, or unpack `review.zip` and serve the unpacked directory. Open `http://localhost:8772/` for part swapping, directional views and playback. No production game admission is performed.

## Rebuild, failure and packaging semantics

- The fingerprint contains adapter code, imported motion helpers, runtime templates, pipeline code and discovered tool versions. No timestamp controls cache validity.
- A cache hit additionally verifies **every recorded build artifact** and recomputes required report gates. Missing, changed or extra files reject reuse. Use `--force` for a clean rebuild even with a verified hit.
- Each build starts in a new directory. Filename-only skip logic inside the research exporter therefore cannot reuse frames from an older source revision. Raw renders remain available locally for repeat comparisons.
- A nonblocking output lock rejects overlapping builders. Files changed during rendering invalidate the build. A failed stage retains its log and `FAILED` receipt; the previous `current.json` remains intact. There is no destructive cleanup of old builds.
- `check` checks completed artifact integrity and recorded gates. It **does not rerun Blender or Chromium**. Run `build --force` when new live verification is needed. Receipts are provenance, not cryptographic signatures against malicious replacement.
- `pack` verifies the selected full build first, creates a ZIP in a temporary file, verifies entries against SHA-256 and promotes it with a rename. For the same completed build its ordering/timestamps are deterministic. Blender output bytes across distinct reruns are not promised to be identical.
- The ZIP contains source `.blend`, timed poses, modular strips, standalone runtime, guides, GIFs and reports. It excludes raw EXRs, redundant per-part frames, logs and external reference art. `package-manifest.json` hashes the ZIP's contents; the larger original build inventory is deliberately not all present in the ZIP.
- `--mode release` **returns exit 2** for this adapter. Exact color, art/motion acceptance, locomotion, FX appearance and real game integration remain blocked. There is no flag that turns the current prototype into an approved release.

## Frame-by-frame study extraction

```sh
python skills/modular-eight-direction-sprites/scripts/capture-reference.py /path/to/reference.gif --output /tmp/new-motion-study --source-url 'https://publisher.example/exact-source'
python skills/modular-eight-direction-sprites/scripts/capture-reference.py /path/to/reference.mp4 --output /tmp/new-video-study --source-url 'https://publisher.example/exact-video'
```

The source URL records provenance; the command reads a local file and does not log in or download from that URL. GIF/APNG preserves decoded samples and display durations. Video requires FFmpeg/ffprobe and keeps presentation timestamps without resampling to a guessed FPS. Duplicates remain separate samples. No per-frame bbox centering, trimming or scale fitting occurs. Review boards use one shared display scale; study PNGs keep the decoded canvas or the explicitly recorded fixed crop.

An absent/zero image delay fails by default. For **still-pose study only**, `--allow-untimed` retains those samples with unknown duration and a null total, without claiming playback timing. Fyna's two developer GIFs actually needed this mode. Video durations must be available; no guessed last-frame duration is supplied.

The output includes source/frame hashes, `frames-review.png`, and an unannotated `landmarks-template.json`. This template is **not a detected skeleton**. Record visible joints, estimates and unknowns separately. The original rig adapter instead emits 64 measured source guides in `pose-guides.json` and `guides/<direction>/`, so hidden source-known joints cannot be confused with inferred screenshot landmarks.

## Evidence

See the committed [iteration 6 review](../../../research/sprite-animation/pipeline-v6/README.md) and [external frame studies](../../../research/sprite-animation/motion-reference-v6/README.md). Run the failure-case suite with:

```sh
PYTHONDONTWRITEBYTECODE=1 python -W error::ResourceWarning skills/modular-eight-direction-sprites/scripts/tests/test_pipeline.py
```

Eight tests cover artifact corruption/missing/extra files, source fingerprint changes, failed child preservation, path escapes/symlinks, release blocking, missing tools, APNG timing/duplicates and unknown-delay extraction rollback. Fresh Blender and Chromium checks are recorded separately; unit fixtures do not replace them.


## Bounded video studies and richer original source guides

```sh
python skills/modular-eight-direction-sprites/scripts/capture-reference.py /path/to/reference.mp4 --output /tmp/shot-study --source-url 'https://publisher.example/exact-video' --start-ms 12000 --end-ms 13100 --crop 880 330 300 360 --camera-motion moving
PYTHONPATH=/tmp/sprite-render-deps python skills/modular-eight-direction-sprites/scripts/export-conditioning.py --build-root /tmp/astraeon-sprites --output /tmp/new-conditioning-study
PYTHONDONTWRITEBYTECODE=1 python -W error::ResourceWarning skills/modular-eight-direction-sprites/scripts/tests/test_reference.py
```

Capture v2 keeps original decoded frame ordinals/PTS alongside clip-relative time. Windows select complete exposures by onset in `[start,end)` relative to the first source timestamp; the last exposure is not shortened to fit the requested end. `--crop X Y WIDTH HEIGHT` uses the same unscaled source rectangle for every sample and fails outside the canvas. Source→study coordinate subtraction is recorded. Video autorotation is disabled so pixels match probed coded dimensions. Decoded sample counts and unchanged source hashes are checked. Unknown timing cannot support a timed window. Review boards paginate at 72 samples and show source timestamps. Camera motion is an operator declaration, **not** estimated compensation or measured world contacts. GIF/APNG inputs support the same onset windows when timing is known.

Conditioning export accepts the current verified silver-scarf-A completed build, reads its already-rendered complete parts, and publishes separately; it does not rebuild or alter the rig. It exports 64 sets of source skeleton/composite/silhouette/integer ownership/depth plus diagnostic grip crops. Full canvases retain their 2× registration. Part-ID maps describe render pieces, not fingers; wrist axes are not finger-contact proof. It checks support agreement and re-verifies source build integrity. The depth encoding/backend limits are documented in `conditioning.json`. Existing destinations and outputs inside the build root are rejected. No external reference pixels enter these original source guides.

See [iteration 7 conditioning evidence](../../../research/sprite-animation/conditioning-v7/README.md), [ToS observations](../../../research/sprite-animation/motion-reference-v7/README.md) and [redraw practice](../references/conditioning-and-redraw.md). Five added fixtures actually decode a variable-frame-rate FFV1 video, check exact source PTS/window boundaries, fixed crop registration, unknown final hold rejection, invalid/empty/oversized windows and atomic crop failure. Together with the previous suite: **13 tests**. A test passing is not artistic approval.

## Preset motion and proportional skeleton diagnostics

The separate [iteration 8 experiment](../../../research/sprite-animation/preset-retarget-v8/README.md) adds `studies/source-motion/sample-presets.py`, `assess-presets.py` and `retarget_math.py`. The bounded adapter reads the audited CC0 author GLB at actual clip input times and checks same-rest-basis FK on a fresh generic proportion skeleton. Independent two-segment endpoint diagnostics expose unreachable trajectory goals without stretching limbs. These are not the original production adapter, a general Mixamo retargeter, a baked original rig or surface-contact proof.

Read [preset/retargeting practice](../references/preset-retargeting-practice.md) first. Run the full test command shown in the new evidence README: **20 tests** now cover the previous 13 cases plus transform-order, hierarchy/mapping, rigid-transform and mirroring failures, reachable/unreachable chains, inner reach limits and degenerate poles. The existing original animation/art/release gates remain blocked.


## Eight-facing leg ownership and actual image review

Use [occlusion-image-review](../references/occlusion-image-review.md) and [v11 image evidence](../../../research/sprite-animation/eight-direction-v11/README.md). `leg-continuity.py init --facing VIEW --owners OWNER_INDEX` binds eight-facing actual source geometry. Coordinates start unknown; image crossing traces and reviewer errors are separate gates. No automatic semantic detector or mass-production guarantee is established. The source rendering/packing and browser commands are documented in the linked practice.


## Profile pelvis/depth and approved-reference image structure

Read [profile-pelvis-depth](../references/profile-pelvis-depth.md) for the source cutaway/depth contract, SHA-bound W approval, paired proximal checks and `profile-structure.py` commands/dependencies. The comparator finds independent edge-structure differences; it is not an automatic semantic anatomy detector. Never transfer approval to a different generated image.

## v14: cyclic placement and spacing review for reproduction

Read [walk spacing and registration](../references/walk-spacing-and-registration.md). `walk-continuity.py` creates unknown-first SHA-bound contracts, checks every exposure and the cyclic seam, and keeps body placement, unsigned ankle spread and anatomical owners separate. Optional fixed-ROI SIFT and calibrated palette-region probes inspect actual pixels without warping art. Low feature coverage stays inconclusive; screen-sorted boots do not get anatomical trajectories. A stable hair centroid never approves contact or naturalness. Pupil measurements must be inspected on coordinate overlays; v14 retains a failed first marking attempt.

```bash
python skills/modular-eight-direction-sprites/scripts/walk-continuity.py --init-from-frames path/to/new/frames --frame-ms 75 \
  --label new-character --out /tmp/new-character-review.json
PYTHONPATH=/tmp/astraeon-vision-deps python skills/modular-eight-direction-sprites/scripts/walk-continuity.py \
  --observations research/sprite-animation/continuity-v14/evidence/v14-observations.json \
  --out /tmp/placement-and-spacing.json
```

Run these commands from the repository root; bound image paths in JSON are repository-relative. The75ms default is a study choice, not a rule for other actions. Calibrate palette/ROI/budgets, dimensions, camera, surfaces and timeline per character. `requirements-continuity.txt` pins the actually tested optional dependency set; its NumPy version differs from earlier render recipes.

The study builder/HTML/native reference loops are in `studies/walk-test/`. [Actual v14 before/after and reports](../../../research/sprite-animation/continuity-v14/README.md) retain the accepted v13 legs/rejected motion, new unapproved pixels, source-spacing warnings, raw clipped failure and full game-reference frames. These outputs are flat research previews, not replaceable painted production parts.
