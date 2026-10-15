# Reproduce, inspect and continue safely

## Fresh checkout

```bash
git clone --branch research/modular-sprites-full-body-2026-10-11 --single-branch https://github.com/basicbasja-cloud/Astraeon-online.git
cd Astraeon-online
git branch --show-current
```

A private repository needs your normal Git authorization; do not place tokens in this handoff. An existing sparse checkout needs `research/sprite-animation/` and `skills/modular-eight-direction-sprites/` included. Root `HANDOFF.md` and `AGENTS.md` are entry documents. Git raw-source/provider files outside this repository are not required for the retained v46 deliverables.

## Dependencies

Derived v46 assets need Python 3, Pillow, NumPy and SciPy. The retained HTML needs only a modern browser. ORA opens in Krita or GIMP. Blender 4.3.2 is the tested source tool; engine runtime and other Blender versions are not validated by this handoff. Node and Playwright are only needed for the automated viewer check. No Tripo/MiniMax account, API key, paid generation job, tracking model checkpoint or `game-dev` CLI is required for these review files.

Use your normal isolated Python environment, install `Pillow numpy scipy` if absent, then from repo root:

```bash
python research/sprite-animation/paintover-handoff-v46/verify-handoff.py
```

This read-only command may take time because it hashes all frozen leaves. Exit 0 means byte integrity/local handoff links passed; it does not mean production quality passed.

## Open the review and edit

1. Open `research/sprite-animation/paintover-handoff-v46/review.html`. Select a facing, pause, then step keys 1–8. Left is corrected source; right is painted image. Grid is 32 px. This is source comparison, not estimated painted joints.
2. Open `editor/W.ora` or another facing in Krita/GIMP. Show hidden source/owner layers for diagnosis, keep them off in final art. Save edits into a NEW case/version; retain native `raw/` unchanged.
3. For any corrected drawing, manually trace anatomical hip→knee→ankle→toe and shoulder→elbow→wrist→grip where visible, bind observations to the corrected PNG hash, and record UNKNOWN through occlusion. Do not infer left/right from screen X sorting.
4. The current ORA does not contain separated runtime head/body. Paint proper occluded surfaces when separating, retain neck/collar socket, then test at least two heads over all frames before claiming replaceability.

## Rebuild current derived previews

```bash
python research/sprite-animation/paintover-handoff-v46/build-delivery.py
```

This reads eight existing raw strips, checks exact atlas size, crops fixed cells, builds GIFs/ORA/HTML and writes `paint-review.json`. It overwrites current DERIVED preview/editor files, including ORAs; back up artist edits elsewhere first. It never calls imagegen or paid services. It performs no automatic registration, foot pinning, alpha cleanup, cropping by body bounds or image skeleton detection. GIFs use a dark composite to avoid GIF alpha limitations; PNG/ORA retain native RGBA. Native output is not guaranteed reproducible by prompt alone.

After deliberate edits to current handoff inputs/derived files, regenerate the current inventory, then verify:

```bash
python research/sprite-animation/paintover-handoff-v46/index-handoff.py
python research/sprite-animation/paintover-handoff-v46/verify-handoff.py
```

Inventory rebuilding does not validate edits. Never refresh historical evidence manifests to disguise changes. Never rerun v30–v45 authoring scripts in their frozen directories.

## Start v47 source or painted corrections

Stay on the same branch. Create `research/sprite-animation/painted-pickup-v47/` and copy only required current source assets/scripts, retaining parent SHA provenance. Open v45 `.blend` and Save As to v47 before editing. Its builder uses `continuous-arm-v43/source/source.json` and historical dependencies: inspect `ROOT`, `P.parent`, import paths and output constants before running a copied builder. Do not assume moving a script alone makes a portable reproduction.

For painting-only fixes, copy raw/frame plates into a new v47 input folder, edit new masters, and implement a new exporter that preserves the same cell geometry. Copy/adjust `build-delivery.py` only after supplying the expected eight raw paths; if using a different layout, write an explicit new layout contract. Do not silently use the v46 exact-size assertion as a resampler. Verify new art independently, then add a new manifest after review. Leave v46 native evidence and historical manifests unchanged.

The old `pipeline.py` build examples may construct rejected slash adapters. They are historical examples, not the current production command. Read [TOOLS.csv](TOOLS.csv), each tool's docstring and actual `--help`; diagnostic exit 0 may only mean a report was computed. Inspect `production_pass`, strict gating and UNKNOWN handling explicitly.

## Push / delivery

Run read-only verification, inspect `git diff --stat` and `git status`, then commit/push only `research/modular-sprites-full-body-2026-10-11`. No force push, merge to main, or credential dump. If sparse checkout excludes root entry documents, use `git add --sparse` for those named files. Check the remote commit after push. No outside messaging is authorized.

## Automated offline viewer check

`node research/sprite-animation/paintover-handoff-v46/check-delivery.cjs` checks decode, eight views, stepping, pause and grid controls with all network blocked. It writes `handoff/browser-qa.json` and `handoff/review-browser.png`. Set `PLAYWRIGHT_MODULE` to your Playwright install and `CHROMIUM_PATH` to your browser; defaults are this workspace's installed paths. Restricted containers may require an approved local browser sandbox execution environment. This check does not assess artwork anatomy.

Actual decoded artifact check: `python research/sprite-animation/paintover-handoff-v46/check-artifacts.py` verifies every crop and guide against original bytes, GIF exposure clock and ORA painted layer. It does not modify files or approve art. Exact native generation prompts are retained in `prompts/{view}-exact.txt`; JSON alongside records the reference order and metadata.

Guide assembly verification note: input atlases were alpha-composited from v45 cells on transparency. The initial raw-RGBA identity assertion failed solely on hidden RGB at alpha=0; retained `artifact-qa-initial-hidden-rgb-FAIL.json` and `guide-composite-diagnosis.json` explain it. The corrected check requires exact known alpha-composite equality for all128 guide cells, and exact raw RGBA identity for all64 painted crops. No visible tolerance/registration was introduced.
