# Reproducing the rear-view study

Start from the exact accepted v39 bytes and the CC0 KayKit external preset. Reusing approved pixels as an appearance reference does not approve a newly drawn camera. Read [the decision and evidence](README.md) before using this bank.

## Physical source and projection

`render-source.py` imports the retained `Rig_Medium_General.glb`, activates only`PickUp`, samples its actual0…39 range at30fps into eight uniform times, and renders a fixed orthographic camera. The camera `(6,9,5.5)` is behind the source actor. The GLB and [creator CC0 license](../joint-tracking-ro-v30/preset-source/KayKit-License.txt) are retained in v30; no new proprietary game asset was downloaded in this experiment.

```sh
blender -b -t 4 --python research/sprite-animation/rear-motion-v40/render-source.py -- --out research/sprite-animation/rear-motion-v40/source
python skills/modular-eight-direction-sprites/scripts/physical-view-source-audit.py --original research/sprite-animation/pickup-pilot-v31/source/source.json --current research/sprite-animation/rear-motion-v40/source/source.json --out research/sprite-animation/rear-motion-v40/source-view-qa.json
```

The source auditor independently inverts the stored camera matrix. For this square-pixel orthographic camera, projected X is`width/2 + localX*height/ortho_scale`, and projected Y is`height/2 - localY*height/ortho_scale`. It checks the actual GLB/captured PNG hashes, unchanged world positions, timestamps, camera determinant and projection. Camera-space joint depth is recorded but does not establish occlusion by a mesh or cloth. A reflected raster cannot pass as a different physical source camera.

Rear projection cancels part of the vertical descent with movement in depth. In this clip the head-bone screen-Y excursion is only8.47px, while screen-X changes19.42px. The front camera's monotonic vertical return rule is inappropriate here: rear source head-Y briefly overshoots its starting value at sample6. Preserve that real camera-dependent path instead of forbidding all upward source movement as jitter.

## Native art, authoring guides and exact input bytes

`generation-ledger.json` binds the seven actual prompts, ordered references and native outputs. Whole-strip generation attempts1/2 fail motion placement; attempt3 follows a fuller painted guide better but still fails the strict geometry check. The head is newly drawn from the rear; the accepted front head is not rotated or mirrored into a rear view. Body+outfit stays one coherent drawing per pose.

`build-reference-plates.py` reproduces source/joint boards, the known square plates and the two repair guides. `build-painted-guides.py` supplies a **diagnostic** authored2D deformation of the neutral body. Its manually chosen image anchors are not recovered hidden joints. Its source displacement multiplier1.65 was declared before attempt3. An initial deformation of the hidden far arm dragged the cape into holes; the actual provider input omits that arm from cloth deformation and uses the separate source skeleton for it. The final sprites are native repaintings, never these guide warps. The failure to carry the far-arm motion into the final painting remains a limitation.

The neutral cleanup and two existing-key edits use a1024-square plate: canonical384×512 image at2× scale, pasted at`(128,0)`. A returned square`W×H` normalizes only with Pillow's inverse affine`[W/512,0,W/8,0,H/512,0]`. No bounding-box, shoe or feature fit is allowed. Twelve actual reference images reproduce byte-for-byte in`reference-reproduction.json`.

## Row packing, pose selection and equipment

The native attempt3 body strip is1536×1024,4×2. All four lower-row boot soles share the same23px upward packing offset; the entire lower row is copied down23px without resampling. This correction also moves its collar/cape/arms; it does not move individual frames to match desired poses. The row receipt records the ten clipped alpha1 noise pixels and preserves the unmodified native atlas. Visible foreground is not cut. Do not generalize this correction to a strip whose rows have different per-key foot motion.

The declared native-art map is`[6,1,2,3,4,5,7,6]`, with native repairs substituted only for logical keys1/4. Art6 supplies exact shared terminal rest; art7 supplies a slightly different near-rest recovery. This is a selected authored pose bank, not unchanged3D retargeting or native exact chronology. The raw candidate using the same selection remains available. Six other complete render keys/four passes are identical across the two repair variants.

`build-case.py` uses one neutral-calibrated body scale`300/317`, one body translation, and one rear-head scale`.13` for the entire bank. A bounded skin-color surface observation uses alpha128, a21px top band, known skin color ratios and a reviewed X region. Its centroid+3px defines an inner32px receiver tangent. These are **visible material proxies**, not an automatic neck-bone detector. Inspect the masks and collar grid for every new style; do not transfer the thresholds blindly to another palette, view, hat or covered neck.

The head has skin-only underlap. Draw the coherent body, the complete head, then a clipped region of the original body-owned collar in front. These three Canvas passes are still two logical equipment slots. The real neck validator samples opaque bridge coverage, head above/body below and exact body ownership of opaque foreground collar pixels. Passing this seam check does not approve head proportions or per-pose head pitch.

## Stronger observation and rejection

The first rectangular far-boot ROI included the front boot's heel. A range at the ROI's left boundary was a warning that the observation was not the intended shoe. `visible-boot-components.py` now finds two sufficiently large separated alpha128 components within a reviewed boot band, checks side/bottom clipping and reports screen-left/right surfaces. One merged component, a missing shoe or a third foreground component returns unknown. It cannot resolve crossed anatomical left/right legs; screen sorting is never an anatomical owner label. The original contaminated report is retained and tested against the corrected actual component.

The first phase-only comparison independently normalized X/Y with calibration frames0/3. This tests timing but can hide arbitrary amplitude changes. Here it reports held-out errors0.149/0.107 and would pass. The painted peak displacement is`(-14.59,+33.96)`px, while the fixed guide adapter expects`(-30.32,+13.23)`px. The pose is materially wrong even though its normalized timing looks right.

The new absolute displacement gate calibrates only the common rest origin. It keeps the already declared guide multiplier1.65 and the shared final body scale, then measures all seven other samples without fitting gains. Its provisional8px budget is a **new diagnostic criterion added after the false positive**, not a previously established universal production tolerance. The candidate's26.02px maximum error fails clearly. Established6px support,3px receiver and0.25 phase budgets are unchanged. Both the phase-only and strict reports remain available so future work cannot confuse them.

```sh
python research/sprite-animation/rear-motion-v40/build-case.py
python research/sprite-animation/rear-motion-v40/build-motion-runtime.py
node research/sprite-animation/rear-motion-v40/export-motion.cjs
python skills/modular-eight-direction-sprites/scripts/view-conditioned-motion.py --contract research/sprite-animation/rear-motion-v40/motion-contract.json --renders research/sprite-animation/rear-motion-v40/renders --out research/sprite-animation/rear-motion-v40/motion-qa.json --require-motion
```

The last command **must exit1 for this rejected candidate**. Do not remove the strict flag or fit the peaks and report success. Local Chromium requires the environment's allowed sandbox escalation. After actual render exports, run`package-review.py` for decoded-clock GIFs and`browser-check.cjs` for19 actual UI/render/playback checks. Python software regressions are`test-source-view.py` and`test-motion-gates.py`; passing them confirms that the real wrong pose is rejected.

## Next correction

Keep accepted v39 untouched. Correct the rear body at the existing fixed camera/guide coordinates, especially the overly deep Y drop and insufficient leftward displacement at keys2/3/4. The far right wrist must move down/inward behind correctly owned cloth; require visible wrist/occlusion evidence where available and abstain where hidden. Do not keep the outboard fist and claim a successful reach. Preserve both clocks and exact shared root; validate new actual pixels again. Only then expand further views. This experiment establishes new negative controls and a physical source-view adapter, not new user art approval, all-eight-view compatibility or a production factory.
