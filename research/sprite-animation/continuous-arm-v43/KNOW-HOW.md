# Continuous arms and temporal ownership: reproducible findings

## 1. The old numerical pass was too narrow

v42's actual cutout rig passes22 bounded material-width, attachment, foot and composition checks. The user nevertheless rejects the malformed arms. Re-reading the 3D source finds a constant world-down wrist-to-palm vector even while the forearm changes direction. At the deepest free-arm key its world-space deviation is105.0686 degrees. A projection can conceal this; a second camera reveals it. Width consistency is therefore retained as one useful gate, never promoted into joint/anatomy acceptance.

`arm-chain-audit.py` measures actual declared 3D vectors, bone-length variation and consistency with declared lengths. For this unrotated canonical rig it also enforces the explicit RIGHT-negative-X shoulder frame. That rule is **not screen-left/screen-right sorting** and is not a universal rule for rotated actors or arbitrary motion files. Missing/degenerate/NaN joints fail. The actual old source fails; the corrected source passes. New source wrists are intentionally collinear with the distal forearm. This is an authored constraint, not a learned natural-hand model, a pronation/thumb check or proof that every rendered glove looks good.

The provisional wrist rejection threshold is60 degrees, with elbow flex limit145. They are project gates, not medical limits. CMU26_09's measured wrist/hand-axis deviations lie around19.50–42.48 degrees. Those observations motivate checking wrists; one clip cannot establish universal safe limits.

## 2. Primary motion evidence rather than an invented guide

Actual CMU files and terms are retained. The740AMC samples use120Hz according to the official subject index; the ASF length conversion from the FAQ is `.0254/.45` metres. The retained MIT reader is pinned to its public repository commit and accompanied by its license. A small local adapter replaces its display/transforms3d imports with the explicit static-XYZ rotation matrix `Rz @ Ry @ Rx`. It does not edit motion channels or claim a trained pose model.

`cmu-motion.json` retains all decoded skeletal samples and actual measured arm angles. `capture-source-video.py` decodes every actual preview frame without interpolation or a mean-FPS replacement. It distinguishes raw PTS, decoder best-effort time and DTS. Missing timestamps remain **null/UNKNOWN**. In particular, the terminal decoded frame lacks a usable timestamp. The reported stream field rate must not be confused with the number of decoded pictures.

**AMC and preview clock alignment has not been established.** The movie crop also hides the soles. The video is useful for shoulder/elbow/wrist/torso observation, not a measured planted-foot ground truth. Do not label its captures as our generated character video, or claim an exact AMC/video frame synchronization.

## 3. Corrected source authoring

The new motion is an original game-target adaptation informed by study, **not an unchanged CMU/KayKit retarget or learned inference**. It preserves the accepted8exposure source/game clocks but changes the source arm geometry/trajectory. Shoulder-to-elbow `.29`, forearm `.27`, wrist-to-palm `.07`, palm-to-grip `.05`; the distal wrist/palm/grip share an axis. The right grip reaches the object top at `(0,-.62,.15)`, and the object center stays `.075` below that grip after lift. The left free hand approaches its hip, separate from the right collecting arm.

A near-upright neutral raises the hip from the prior `.88` to `.95` while retaining a `.48` deepest hip, avoiding the old continuously bent neutral. A real neck bridge fills the mannequin neck gap. Initial unreachable targets, cape/body intersections, and the earlier free-thigh placement remain in distinct archived source folders/scripts. None is silently overwritten into a pass.

All64pose/view captures use one world pose table and8physical orthographic cameras. Facing labels S/SE/E/NE/N/NW/W/SW are declared relative to this projection; E uses a camera on negative worldX. Source ownership passes are actually depth-tested renders of the same meshes/worlds/cameras, not colored masks pasted over final art. Their world equality, image hashes and independent projections are checked.

### Size calibration must isolate the actor

An early guide calibration accidentally included the separate collectible in the full-scene silhouette. A prop on the floor in front can extend below the actor in projection. The canonical calibration now uses an actual **actor-only S-neutral render** for399pxheight/floor480, then applies that one display matrix unchanged to all views/poses/skin variants. It does not fit each crouch or each facing. Native/earlier guide inputs are retained byte-for-byte in the generation ledger rather than retrospectively described as corrected.

Projected extents can vary slightly with physical facing, foot depth, hair and cloak. Equal world dimensions do not imply identical silhouette bounds in every direction. Conversely, matching399px in one view does not prove family ratios, shoulder mass, head size or hidden hip placement. The approved front GIF remains an empirical size/clock reference; matched-view full-family acceptance is still unproved.

## 4. Actual continuous skin experiment

`render-skinned-arms.py` constructs two closed arm meshes:25rings ×32vertices =800vertices per arm. They are bound to actual Blender upperarm/forearm bones in the exact rest basis, with smooth weight transitions around the elbow. Navy sleeve/bronze forearm material regions share a continuous surface. The wrist/glove has a3Dbridge rather than a tiny disconnected sprite. The same mesh is actually evaluated in all8poses; vertex count and real pose-bone head/tail errors are recorded.

The first test toggles linear blend skinning and Blender's preserve-volume/dual-quaternion mode on that **same** mesh/bone pose. Across sampled rings, LBS area ratios range about `.25185..1.00000`; DQ about `.9999994..1.0000010`. Actual isolated LBS/DQ comparison renders are retained. This is direct evidence that the chosen bind/rotation/weight configuration can collapse under LBS and that this DQ configuration preserves those sampled ring areas.

### Do not hide a bad bone basis behind preserve-volume

Further actual saved-bone inspection finds that independently tracking upperarm/forearm toward worldZ produces a relative elbow-axis deviation up to142.19deg. The surface numbers alone do not catch this unintended local roll. `render-hinge-skin.py` therefore constructs both bone frames from the **same elbow bend-plane normal**. The forearm rotates around the common hinge axis, and the straight wrist/hand inherit the distal frame for this declared zero-pronation pickup. This is an additional64actual-capture experiment, retained separately from the first one.

With the corrected bone basis, sampled LBS areas remain at least95.55% and DQ near100%; real pose-bone hinge-axis errors are checked directly. Eleven corrected-hinge checks pass. `actual-bone-frame-comparison.json` evaluates both saved Blender rigs rather than merely trusting the constructor. Near-zero axis angles use `atan2(transverse_length, axial_component)` to avoid false angle inflation from float32 normalization error.

For a perfectly straight arm the bend plane is ambiguous. The prototype deliberately refuses that singularity instead of silently choosing worldZ. A production adapter must use an explicit rest/transported plane fallback, then add authored forearm pronation/hand grip orientation separately when the action requires it. A pure hinge/zero-roll policy is not a universal attack or hand-animation solution.

**Do not call either experiment whole-arm volume, soft-tissue anatomy or final art proof.** Ring area does not measure the entire enclosed volume, longitudinal distortion, self-intersections, hand roll, finger anatomy or dense-time collisions. Other mannequin body geometry is reconstructed at each capture, not fully skinned in the saved model. It remains source research. The reviewer defaults to the corrected common-hinge captures.

The practical production recipe is: review rest axes, bind in setup/rest space, test both action extremes, inspect topology/weights and elbow silhouettes in animation, then add limited corrective geometry or view/pose-specific drawings where genuinely required. A 2D mesh/rig alone cannot invent missing perspective artwork. The primary Spine documentation supports those individual techniques; it does not certify this combined factory.

## 5. Critical-pose success does not establish motion continuity

Three initial new strips fail near/far arm roles or camera continuity. A new eight-view deepest-pickup turnaround improves the visible arm overlap: in NW/W the near free forearm crosses toward the waist, while the collecting far arm emerges below it. The back-facing view keeps the cape/back and hides parts of the reach. These are useful **single-pose appearance references**, not eight accepted runtime frames or a full8direction motion bank.

The native turnaround ignores equal-height row packing: some top-row pixels extend beyond y512. Its static reference crops therefore use the reviewed empty gutter at y600 and explicit crop records. This does not repair animation registration, prove source alignment or authorize per-key fitting. Preserve the original whole atlas.

The subsequent NW motion strip keeps its camera better and draws the deepest overlap correctly, **but swaps the collecting limb during lift**. At key3/index3 the far right glove collects; at key4/index4 the visible near left shoulder/elbow/cuff connects to the gem-holding glove. Each isolated drawing can look plausible while the animation is semantically wrong.

`painted-owner-continuity.py` now enforces explicit image-side review records. The observed current cuff/shoulder/glove points are bound to exact RGBA pixels. A known rejection survives PNG filename/metadata changes and cannot be fixed by relabeling the same pixels “right”. Missing held-frame reviews stayUNKNOWN and block the temporal owner gate. The actual strict current-strip command returns1.

**This is not an automatic anatomy detector.** The visible-chain/owner observations are manual. The tool checks their current-pixel binding, foreground support and temporal consistency; alpha support alone does not prove a landmark's anatomical meaning. New drawings and hidden chains need fresh evidence. Never infer final ownership from input guide colors or move a colored label and claim a repaired hand.

## 6. Reuse and release gates

For each new character retain: original style/neutral approval scope, uniform rest-family calibration, source rig/rest bases, canonical LR frame, physical cameras, phase/clock/contact/holding-owner table, actual mesh weights or pose-specific artwork, logical body+outfit/head grouping, raw outputs and lossless frame manifests. Run source, real-surface and final-image gates separately. A controlled renderer can establish actual vertex/attachment ownership behind occlusion; a whole-frame native redraw cannot inherit that authority merely from conditioning.

The current final-image bank remains rejected. The optional external-mesh proposal is fully separated: one front-only Tpose image, proposed model/rig calls and estimated55credits; automatic review blocked CLI execution. Public package source was inspected as data only. There is no executed dry-run, login/account inspection, image upload, provider job or billed cost. Await explicit authorization; never treat elapsed time or a preselected UI option as consent.
