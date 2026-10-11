# Original modular rig exercise

This exercises [rig production](../../references/sprite-rig-production.md) and [Ragnarok hard references](../../references/ragnarok-hard-reference.md). The [review package](../../../../research/sprite-animation/silver-scarf/rig-proof-v4/README.md) contains the original editable source, independent parts, GIFs, browser harness and actual reports. This is one-family/one-attack technical evidence, not approved character art or a complete factory.

## Tools actually used

Blender 4.3.2, Node, host Python with Pillow/numpy/OpenEXR, and Chromium through Playwright. The `game-dev` CLI described by the available asset-production skill was not installed; these are direct local Blender exports, not a CLI-canonical validated package. No paid provider was used. Third-party skill text was studied statically; its commands were not installed or run.

From the repository root:

```sh
node skills/modular-eight-direction-sprites/studies/rigged-parts/rig-poses.mjs
blender -b --factory-startup -t 4 --python skills/modular-eight-direction-sprites/studies/rigged-parts/build-character.py -- batch
blender -b -t 4 --python skills/modular-eight-direction-sprites/studies/rigged-parts/render-owner-checks.py
python skills/modular-eight-direction-sprites/studies/rigged-parts/compose-proof.py
blender -b -t 4 --python skills/modular-eight-direction-sprites/studies/rigged-parts/check-source.py
node skills/modular-eight-direction-sprites/studies/rigged-parts/validate-contract.mjs
```

Install dependencies in an isolated local environment if missing; do not vendor them into the research package. This session used OpenEXR from `/tmp/sprite-render-deps` and invoked host composition with `PYTHONPATH=/tmp/sprite-render-deps`.

For browser checks, start a local HTTP server serving the output directory, then:

```sh
python skills/modular-eight-direction-sprites/studies/rigged-parts/browser-check.py http://127.0.0.1:8772/
```

The batch skips existing per-part color PNGs. If geometry, camera, lighting, source poses or output settings change, invalidate affected outputs before rerunning; otherwise it will reuse stale frames. The published PNGs/strips can be previewed without regenerating; raw EXRs and per-frame packed depth PNGs are intentionally untracked. Full-scene owner/depth EXRs must be regenerated to rerun numerical comparisons.

## What each script proves

- `rig-poses.mjs`: original pose keys and continuous analytic-IK/blade-history samples. It reuses our mathematical helpers, not rejected art.
- `build-character.py`: complete original meshes, named armature, rigid segment weights, held action, shared camera and independent per-item renders. Its editable action has eight held keys; the 1,000 FPS scene time base represents integer milliseconds, not a 1,000-pose-per-second export.
- `render-owner-checks.py`: independent full-scene render with per-part object IDs, separating visibility errors from color differences.
- `compose-proof.py`: source-depth visibility, packed-depth fidelity, reference comparisons, item coverage, canvas bounds, timing, GIFs and hash records. Exact color failure stays separately reported even when visibility succeeds.
- `check-source.py`: reopens the actual `.blend`, inspects weapon hierarchy/vertex weights and evaluates baked keys without manual pose assignment. It is not visual acceptance.
- `validate-contract.mjs`: pose/item coverage, actual strip headers, and six deliberately invalid metadata fixtures. Actual source weights are covered by the independent source check.
- `browser-check.py`: renders actual exported strips and exercises swaps, coverage, all eight views, stop, one-shot, slow playback, rapid load requests and a deliberately missing diagonal asset.

The armature contains editable deform bones and baked poses. Analytic IK targets are in the source code; the `.blend` does not provide a finished animator-facing IK control rig. Hair/capes are complete rigid sources in this exercise, not finished secondary-motion rigs. Dynamic trail history is generated during export, not baked into the saved Blender action.
