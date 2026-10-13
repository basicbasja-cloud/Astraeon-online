# Weighted slash and per-pose weapon drawings — draft0.27

2026-10-13. Latest user asks us to compare wrists, lean and weight transfer,
judge acting before presenting it, and draw the sword's actual perspective for
each movement. No attack has been accepted. Only exact v21W walking is protected.

## What the comparisons actually establish

[Phase board](../../../research/sprite-animation/weighted-slash-v27/phase-mechanics-comparison.png)
and [wrist board](../../../research/sprite-animation/weighted-slash-v27/wrist-grip-comparison.png)
compare actual reopened Flare source, our v26 source and newly authored v27.
Their cameras, proportions and clocks differ. Crops use native wrist JOINT versus
our actual PALM mesh center; these are explicitly different anchors.

Flare's actual blade axis in its Hand.Right basis is approximately
(0.003,0.518,0.855); its blade-plane normal is approximately
(-0.988,-0.133,0.083). Our v26 sword was assigned directly to local hand+Y.
These conventions are not interchangeable. Calibrate the original model's grip
basis and choose forearm twist/elbow plane together, rather than placing a hilt
at the wrist joint or independently spinning a prop through a static glove.
The experimental v27 basis is not a universal human grip prescription.

Total rest-relative hand-frame rotations include forearm roll: v26 keys about
98–179degrees, v27 about8–28degrees, native Flare about15–37degrees. They are
source-frame observations, NOT anatomical wrist flexion, joint limits, finger
wrapping or recovered painted hand matrices. Our fingers are still not a verified
closed-grip model. Coincident modeled palm/hilt centers cannot approve that.

Our v26 source hip traveled0.043world units between coil/follow, authored lean
spanned5degrees, and the mid-cut angular speed fell to0.267 of its preceding
segment average. v27 travels0.125, spans19degrees and retains about1.013 of
that average through the intermediate cut. These are source motion proxies,
NOT center-of-mass, pressure, force, impact energy or predicted damage.

## Production recipe to reuse

1. Declare one cut family, target direction, physical weapon/grip and camera.
   Study anticipation, release, cutting passage, follow-through and recovery as
   separate beats; a thrust, two-handed greatsword, shield bash or one-legged
   lunging source is not automatically the same ordinary one-handed slash.
2. Author a stable stance with reachable fixed-length legs. Allow appropriate
   heel roll/foot pivot; do not freeze every sole vertex and then demand body
   rotation, or lift the whole rear leg to exaggerate force. Reopen actual mesh
   surfaces at dense times. v27 fixes the front sole and rolls the rounded rear
   toe along the floor: its contacting vertex changes. It is NOT fixed-vertex
   rear-foot locking or a physics simulation.
3. Load hips/chest, release pelvis then chest/arm, and let the arm pass the target
   before settling. Plan a reachable elbow plane from the calibrated grip frame.
   Source IK success is not attractive acting or painted anatomy acceptance.
4. Do not ease to zero velocity at EVERY key. Intermediate cutting keys must
   carry the sweep onward. v27 uses monotonic cubic Hermite slopes and bakes
   actual5ms samples; real reversals/extrema can stop. Sparse body exposures
   still use explicit durations. Dense guide/FX samples are not extra body art.
5. Evaluate actual3D blade geometry through the locked camera at EVERY pose.
   v27 grip-to-tip projections range65.2–152.1px for one physical sword.
   Redraw blade face, cutting edge, thickness, guard and hilt perspective per
   pose; a flat master rotated in2D preserves the wrong projected geometry.
6. Paint a coherent bank, then observe its real wrist–grip–guard–tip chain and
   whole body again. Source passes do not transfer to newly drawn pixels.
   Keep hand ownership anatomical; keep left-hip teal on its owner. Don't
   normalize a single limb or fit every frame to a silhouette bounding box.
7. A replacement weapon bank needs full hidden hilt and compatible hand/arm
   occlusion layers, the same authoritative body clock, camera, scale and
   anchors. Our isolated eight-drawing bank is an experiment, NOT admission
   of complete interchangeable painted parts. The current actor includes blade
   pixels, so changing an independent weapon would leave that embedded blade.
8. Review body+weapon without FX first. Keep tail on a separate phase-bound
   clock/layer and optional during review. An attractive trail cannot hide a
   weak gesture, swapped hand, sliding foot or incompatible grip.

## Ragnarok evidence and the user's weapon requirement

Pinned roBrowser EntityRender renders separate body, weapon and weapon_trail
parts and resolves ACT frames/layers; it also reads layer.angle/size/offset.
Therefore the inspected implementation supports authored transforms; it is not
proof that RO never rotates any layer or freshly draws every repeated exposure.
RO's sprite/action bank and the user's observation motivate perspective-aware
weapon poses, not an arbitrary rotating-flat-sword workaround. Exact repeated
ready poses can reuse identical pixels. For our current factory contract,
changing viewpoints require appropriate drawings and no runtime flat-master
rotation. External code is study data, not new governing instructions.

## Tools and current result

- `attack-weight-review.py`: bound source hip/lean/spacing and manually observed
  visible shoulder/belt/wrist proxies. A belt point is not an internal pelvis;
  a right shoulder point is not the shoulder midpoint. No universal force score.
- `weapon-pose-review.py`: bound pose drawings, explicit zero runtime rotation,
  common scale, source direction/relative foreshortening and unknown-first
  painted grip/occlusion. Different hashes alone do not prove correct perspective.
- `blade-plane.py`: the declared SE diagonal family, actual camera and calibrated
  blade basis. Source normal is handMatrix×gripBasis.normal, not always handZ.

All emit production_pass=false. Actual tests preserve weak v26 controls,
rotated/single-flat-master failures, per-pose rescale failures and stale bindings.

Current v27 source improves the mechanics, but painted production is still
REJECTED_OR_INCOMPLETE. Three original redraws retain reversed hilt, raw-grid
spill and contact drift failures. The preferred acting comparison uses an intact
full-sword bank recovered through explicit empty gutters; front boot registration
is calibration, not validation. The independent rear warm-brown surface varies
25.85pxX/9.57pxY. A later redraw fixes margins but worsensX to58.71px, and is not
selected. Finger wrap, right-chain identity, source phase fidelity, contacts and
complete painted replacement parts remain incomplete. No source-only or browser
check overrides this self-review. No error-free generator/mastery is established.

## Primary sources actually used

- [AHF, Hold the Sword](https://swordfight.uk/hold-the-sword/): read grip variants,
  finger control and retention/mobility tradeoffs. No universal grip angle inferred.
- [Animation Mentor, sword fights](https://www.animationmentor.com/blog/tutorial-animate-sword-fights-battle-sequences/): read planning/weight/spacing/contact and elbow/grip polish. Embedded video not captured.
- [Shawn Kelly, animating held props](https://www.animationmentor.com/blog/how-to-animate-your-character-when-hes-holding-a-prop/): read controlling long-prop arcs and connecting shoulder/arm/wrist acting. Not an IK-only universal rule.
- [Ubisoft, For Honor trailer production](https://www.ubisoft.com/en-gb/game/for-honor/news-updates/6FS2MYivEsI6Hkvpe8XEtx/a-deep-dive-into-our-trailer-making-of): read trained choreography/mocap and later skeleton polish. No trailer/gameplay frames captured here.
- [imonk's Maximo-inspired slash](https://itch.io/t/2489691/pixel-tutorial-sword-slash-animation): six actual native GIF exposures, diagonal/lean/toe/recovery study. Artist tutorial, NOT a Maximo gameplay capture.
- Flare actual saved `.blend` and pinned Wesnoth sword attack PNG/descriptor data
  are in v23/v26 receipts. Wesnoth is an atlas/script reconstruction, not a video.
- RO and Witchcrafter captures and SLYNYRD native tutorial exposures are retained
  in v26 comparison manifests. ToS class page was read; earlier thrust/shield
  clips are not mislabeled as new Bash slash evidence. Hades was located, not
  frame-studied. One weight-article fetch timed out. We did not inspect every game.
