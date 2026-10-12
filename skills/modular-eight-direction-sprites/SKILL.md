---
name: modular-eight-direction-sprites
description: Design, produce, repair, and validate eight-direction 2D character sprites with interchangeable body, clothing, hair, armor, and equipment parts. Use for paper-doll sprites, directional attachment systems, layered frame animation, or 3D-to-2D modular character exports.
---

# Modular eight-direction sprites

Research-backed draft v0.18, reviewed 2026-10-12. Includes rig/weight/IK study, pinned GitHub comparison, Ragnarok action audits, primary artist/coherence research, modular rig proofs, sparse body/FX clocks, source conditioning, preset retarget study, actual mesh-floor repair, detailed redraw masters, eight-facing anatomical/occlusion checks, fractional source replay, projected sole review and a shared rejection/temporal/clock review standard. Final sprite art, production game integration and mass-production readiness remain unvalidated. The linked sources establish individual techniques; this package's combined asset contract and quality gates are proposed engineering practice.

## Scope and references

Read [binding user constraints](references/user-constraints.md) before this user's project work. For Astraeon, Ragnarok is the stated inspiration, main is obsolete, and every existing branch's character art is rejected. The sole working branch for this research is now `research/modular-sprites-full-body-2026-10-11`; keep subsequent iterations on it. Study technical contracts on the newest branch, but derive no visual guidance from those rejected assets. Earlier art inferences are superseded.

Use when a character must retain identity and animation while independently replacing appearance parts in eight facing directions. A flattened sprite sheet alone does not satisfy a modular-parts request.

Read [research](references/research.md) for approach selection, [motion findings](references/motion-study.md) for animation design and measured limitations, [asset contract](references/asset-contract.md) before production, and [production recipes](references/production-recipes.md) for tool-specific work. [Sources](references/sources.md) distinguishes implementations, official documentation, research, and tutorials. [Astraeon technical brief](references/astraeon-technical-brief.md) pins the newest branch studied.

Do not claim that reading this skill permanently trains a model. The durable output is this package and project assets. Do not claim the package is installed unless the active skill loader actually registers it.

For rigged modular production, read [sprite rig production](references/sprite-rig-production.md), [GitHub skill comparison](references/github-skill-study.md) and [Ragnarok hard reference](references/ragnarok-hard-reference.md). Painted v3 is rejected for apparent hand switching, its effect and flattened parts; it is failure evidence, not a source seed. Reproduce the new [rigged-parts exercise](studies/rigged-parts/README.md). Ragnarok is an inspiration; any useful game or rig may supply motion/production techniques, and our own style determines visual acceptance. Read [original art direction](references/original-ro-art-direction.md) for native-scale cluster/contour practice, source limitations and the new unapproved four-key exercise.

## Executable workflow and pose references

Use the [pipeline commands](scripts/README.md) for isolated `doctor`, `build`, `check` and `pack` runs. The current adapter builds one original complete-part attack rig; it is not an arbitrary text-to-sprite factory. It fingerprints source/tool versions, verifies cached artifacts, retains failed-stage logs and preserves the previous completed build. Required mechanical checks precede the current review pointer; release packaging rejects the outstanding visual/color/action/integration gates.

For fresh motion study, use `scripts/capture-reference.py` on local GIF/APNG/video inputs, with optional onset windows and one recorded fixed crop. Retain source PTS and declare camera-motion uncertainty. Preserve decoded samples and available presentation times, including duplicate poses. Do not invent a playback rate for zero-delay samples or call an empty annotation template a detected skeleton. Read [pose-guide practice](references/pose-guide-practice.md) and inspect [213 external reference samples](../../research/sprite-animation/motion-reference-v6/README.md). Original source guides come from the actual reopened rig, retain anatomical ownership and use the same export camera; they remain unapproved motion guides.

Read [conditioning and redraw](references/conditioning-and-redraw.md) for the frame→rig→shape/occlusion/hand guide→original drawing→modular export path. `scripts/export-conditioning.py` adds 64 ordered source-key sets with silhouettes, part IDs, depth and grip inspection, outside verified builds. Inspect [new ToS motion studies](../../research/sprite-animation/motion-reference-v7/README.md); these are observational references, not recovered hidden skeletons. The current adapter has no articulated finger guide; its grip crops do not approve finger wrap. The user rejects this board as unnatural. Read [natural-motion practice](references/natural-motion-practice.md) and study the fresh external 65-bone walk/attack guides before re-authoring original blocking; map exports cannot approve their source pose.

Read [preset and retargeting practice](references/preset-retargeting-practice.md) before borrowing motion from Mixamo or other preset libraries. The user permits other providers; study the [eight-preset experiment](../../research/sprite-animation/preset-retarget-v8/README.md) and [primary source audit](references/retargeting-source-audit.json). It samples 339 real source timestamps, checks same-rest-basis FK and records unreachable endpoint goals. Its independent chain diagnostics are not contact-cleaned motion, an original animated mesh, or a Mixamo download. Preserve root/pelvis translation, calibrate rest axes, and check actual hand/foot surfaces before sparse-key redraw or modular export.

The user's latest emphasis is attractive original fantasy sprites with correct hands, weapon grips, limb chains and walking mechanics, even with few frames. References can extend beyond RO. More sources, image prompts or successful bone-origin checks cannot guarantee error-free generation. Review palm/finger contact, silhouettes and native appeal before multiplying items/actions; no current prototype is an approved complete modular production seed.

The latest supplied images set a higher direct quality target than the reduced v9 preview. Inspect [512-square detailed v10 masters and actual inspection UI](../../research/sprite-animation/quality-review-v10/README.md); preserve full-color RGBA rather than discarding detail into a small export. Read [anatomical continuity practice and primary research](references/anatomical-continuity.md). `scripts/leg-continuity.py` starts artwork observations unknown, binds the real baked rig/source/image hashes and actual source times, and compares hip–knee–ankle–distal-toe chains and source-timed transitions including the loop seam. Anatomical labels never come from screen sorting. Estimated/occluded points and unconfirmed identity keep review blocked. Raw and uncertainty-adjusted errors remain separate; coverage/budget fractions are not accuracy probabilities. The checker now supports all eight physical facings. Passing synthetic controls does not approve the artwork. Use the HTML annotation tool and rerun the CLI after edits before multiplying sprites.

The user rejects overlapping-leg drawings, including initial SE pose 2 and revised E pose 3, and explicitly requires image-based rechecking after tool fixes. Read [occlusion and generated-image review](references/occlusion-image-review.md) and inspect [eight-facing v11](../../research/sprite-animation/eight-direction-v11/README.md). Actual visible and isolated source-leg IDs distinguish ownership where 2D joints overlap; all 16 component-side exchange tests retain raw errors and ambiguity. Generated RGBA checks plus independently marked foreground-chain traces are required at visible crossings. Unknown or unconfirmed crossings cannot pass; a low joint residual or alpha support does not identify painted anatomy. Confirmed errors survive same-image annotation import. Preserve rejected pixels and create a new case after each redraw. The v11 calf-only local match conclusions are superseded by v12: without paired proximal evidence they are foreground-order observations, not anatomical identity matches. The user rejects the E correction again. No trained image-semantic model is executed and no painted modular part bank is established.

For a concrete one-motion test, use the [fresh walk commands](studies/walk-test/README.md) and inspect [v9 painted walk and preserved failures](../../research/sprite-animation/walk-test-v9/README.md). It transfers 41 real source samples into a freshly constructed 67-bone/170-mesh modular character, then renders eight exposures and eight physical facings. Reopened mesh checks exposed footwear penetration that bone endpoints alone missed; per-foot fixed-length IK repairs measured clearance without lifting the entire root. Clearance is not planted support, foot-lock or balance verification. Thirteen complete part slots and actual hair swapping cover SE; the painted redraw covers SE only and remains flat/unapproved. The two generated sheets change proportions and pose registration despite explicit prompts. Preserve raw outputs; measured shared grid-row correction may fix an export-grid displacement, but never per-frame fit silhouettes or report it as anatomical/contact correction. Read [one-motion acceptance practice](references/one-motion-acceptance.md) before expanding this test.

Read [profile pelvis/depth and reusable contour checks](references/profile-pelvis-depth.md) before E/W redraw or repeating this problem on another character. The user's rough contour diagram supplies the near-contour-continuity/far-contour-interruption rule; leading-foot changes must not change pelvis ownership. A covered joint may have a readable occlusion boundary, so do not demand both internal hips be exposed. Source depth/cutaway proof and independently marked proximal paths are separate from generated-image hidden anatomy. The exact new W sheet is user-confirmed correct for leg readability; preserve its SHA-bound acceptance as a scoped positive reference. The later W-like sheet is different and its third pose is explicitly rejected. Never transfer approval across those bytes.

`profile-structure.py` now performs independent pixel-structure comparison against that approved same-character/view/phase reference using torso-only SIFT/RANSAC registration and pelvis/thigh edge distances. It flags the actual later rejected third pose but does not classify anatomical swaps or approve unknown anatomy automatically. Its provisional budgets and positive/negative fixture are not general accuracy. A new character/costume/camera needs its own bone/slot/depth contract and approved regions. Forty actual source render passes, the user feedback pairs, failure logs, 73 controls and browser checks are retained in [v12 evidence](../../research/sprite-animation/profile-depth-v12/README.md). The E attempt referenced from approved W instead copied W-facing art and clipped a cell: preserve it as failure, not an E result. Reusable production still requires complete separately owned painted pieces and continued image review.

For the user's latest request to match Ragnarok walking frame count, inspect [W eight-frame v13](../../research/sprite-animation/ro-walk-eight-v13/README.md). The audited male Swordman walk has eight frames; converter playback is 75ms/frame, not a universal RO/client rate. Source-time poses are 0/5/10/15/20/25/30/35. Preserve approved principal pixels rather than silently regenerating them: new slots1/3/5/7 retain the exact four approved W masters; four intermediate slots remain unapproved. Count increase does not approve anatomy or planted contacts. Keep source-clock QA separate from accelerated preview timing and compare frame counts at equal loop duration. The grid packer handles fractional cell extents, one shared transform and exact 1:1 copies; resampling RGBA at identity may alter alpha-edge color. Use explicit frame/loop durations for every action, not a global eight-frame rule.

## 1. Establish the production contract

Latest continuity practice: the user accepts v13 W leg readability and rejects its jerky movement, then requires frame-by-frame game comparisons and reusable placement checks. Read [walk spacing and registration](references/walk-spacing-and-registration.md) and the [v14 experiment](../../research/sprite-animation/continuity-v14/README.md). Separate scoped leg acceptance from motion. The new checker binds images/exposures, includes last→first, preserves unknown root/hidden joints and forbids trajectories from screen-sorted boots. A calibrated actual-pixel surface probe detects the old registration jump; low-feature SIFT remains inconclusive. A geometry-first whole-eight candidate improves placement, but source-spacing warnings and new-pixel anatomical review remain unresolved. Never repair scores through per-frame bbox fitting, freezing the head/body, or copying this hero's palette/thresholds into another character's contract. Recheck the observations themselves on enlarged image overlays before using them.

Latest floor/16-frame practice: the user says v14 still looks like hopping on flat ground, requests16frames to test the pipeline and rejects frame5 of the first v15 raw. Read [ground-plane/contact review](references/ground-plane-and-contact-review.md) and [v15 evidence](../../research/sprite-animation/ground-walk-sixteen-v15/README.md). Evaluate actual soles at16 fractional times and dense between-key samples; distinguish proximity from support/contact-lock. Near/far image floor lanes can project the same world plane. `scripts/ground-contact.py` compares actual-pixel heel/toe ROIs against SHA-bound source projections; clipped/unknown observations remain inconclusive. Calibration anchors never independently validate themselves, while another sole in the same frame can. Same-art8/16 controls keep the600ms cycle; decoded file count/timing must be checked. The generated sheet required documented shared-row registration, not per-frame fitting. Current independent floor warnings at slots1/7/8/9/15 and new frame5 proximal-chain review remain unresolved. A sole-height result is never an anatomy pass. New-character templates start unknown and require their own source/camera/transform.

Latest common standard: the user rejects the shown v15 sequence9–11 as wrong-legged and requests smoother GIFs plus a reusable standard for all sprite work. Read [sprite production standard](references/sprite-production-standard.md) and [v16 evidence](../../research/sprite-animation/leg-ownership-v16/README.md). `sprite-review-gate.py` preserves exact-image sequence rejection across changed phase labels; `sprite-standard.py` recomputes bound anatomy/continuity/contact cases and refuses different banks/order or loop mode. Unknown roots/owners/contacts/parts stay blocked; promotion must use `--require-production`, not interpret a diagnostic exit as acceptance. Three redraws remain unapproved. Third seam improves to1.46px but internal12→13 still exceeds the provisional20px hair-surface budget; do not claim overall smoothness from seam alone or raise the threshold. One-shot excerpts now omit artificial return edges/looping. `animation-cadence.py` diagnoses actual600ms16-frame GIF30/40ms exposure variation; a same-master800ms50ms-per-frame test has uniform timing in all formats, changes speed and never repairs anatomy. Fresh AniDoc/ToonCrafter primary study motivates temporal geometry control; no external model inference is executed. The common standard's executed adapter is Wwalk, not every action/rig or accepted mass production.

Latest upright-walk practice: the user rejects v16 smoothness and asks for standing/walking upright like RO instead of sneaking. Read [upright compact gait](references/upright-compact-gait.md) and [v17 evidence](../../research/sprite-animation/ro-gait-v17/README.md). Re-author neutral-rest spine and compact source foot trajectories before redraw; never treat a preset lean as mandatory. Hash-bound source checks measure129bake/257dense samples, actual fixed-vertex flat stance, floor candidates and cyclic joints. These source-only checks pass; both new imagegen attempts fail promotion. First redraw still has40.66px4→5/32.20px8→1 hair-region jumps and pose drift; second fails clipping. New8-pose art test is not the prior16-frame pixel bank, and no art/owner/parts acceptance transfers. Historical template fields are explicitly scoped. The user subsequently approves the exact W upright source GIF,16×50ms/800ms: [approval receipt](../../research/sprite-animation/ro-gait-v17/evidence/user-approved-upright-source.json). Use that bound source as the accepted motion baseline for the next paintover; preserve posture, phase order and registration. This approval does not cover either new art attempt, other views or painted parts.

Latest production-depth practice: the user asks for broad cross-game shot/frame studies, quality references near RO/RO3/ToS and open-source/GitHub skills. Read [cross-game production](references/cross-game-production.md) and [v18 evidence](../../research/sprite-animation/cross-game-factory-v18/README.md). Distinguish301 actual container/video samples from14 atlas/script reconstructions, read/located sources and unexecuted backends. Source code exposes per-view draw orders, duration distribution, repeated IDs, terminal holds and separate gameplay/FX thresholds. Actual approved-source inventory has170meshes/67bones/13itemgroups; hair variants share one of12logical categories. `factory-plan.py` binds approval/rig/camera/clock/images into16poses/208unreviewed part-frame jobs and rejects changed bindings/unapproved facings. It is an authoring planner, not a finished generator. Preserve the approved upright W source and our painted detail; pixel-onlyQA/mirroring/presetdefaults from external skills do not override them. Browser reader behavior is unverified after sandbox launch failure; network-shell article fetch was blocked by approval-service usage limit and not retried.

Inspect the allowed project contracts, renderer, direction convention, and authoring tools on the newest permitted branch. Inspect existing sprites only when the user permits them as study inputs; all Astraeon branch character assets are excluded. Reuse known answers; ask only for consequential missing decisions. Continue independent research and contract work while optional answers are pending.

Record in a character brief:

- Style: pixel art, painted, cutout, or rendered 3D; native display size and sampling rules.
- Projection: top-down, oblique, or isometric; sprite capture elevation, game camera ranges, billboard behavior, and lighting convention.
- Eight facing names and exact storage order; world-to-screen conversion when needed.
- Body/rig family, anatomical left/right, handedness, proportions, and silhouette.
- Replaceable gameplay slots, coverage rules, compatibility constraints, and render-piece splits.
- Required actions and weapon grip families; frame counts, durations, loop rules, and pose phases.
- Logical frame dimensions, ground-root anchor, attachment sockets, and allowed intentional root motion.
- Output engine, authoring source format, memory budget, and provenance requirements.

If unspecified, propose a small proof consisting of one body family, eight facings, idle and walk, two torso items, two head items, and one weapon/shield combination. Include one attack clip if weapons are part of the requested scope. Treat dimensions and frame counts as provisional choices, never as an industry-wide standard.

## 2. Choose the authoring method

Use aligned frame layers for strict pixel art and direct control of each pose. Use directional cutout rigs where deformation and tweening fit the aesthetic, with authored view changes. Use a modular 3D rig rendered to sprites when numerous directions, clips, or equipment variants justify the setup. Use AI as an assisted concept, view, pose, or layer-generation step with explicit review gates.

These choices can feed the same layered runtime. Preserve the editable source and record which steps were actually executed.

Never substitute rotation of one flat image for new facing views. Do not assume a four-direction asset library provides diagonal sprites.

Do not automatically mirror asymmetrical characters. Keep anatomical ownership in the source hierarchy and actual weights, reopen the baked action, then inspect visible wrist–grip continuity in every pose. A socket declaration or prompt word cannot validate a visually switched hand.

## 3. Define slots, pieces, and compatibility

Separate gameplay equipment slots from render pieces. A single equipped cape may provide `cape_back` and `cape_front`; one helmet may hide selected hair regions; one glove item may supply both anatomical hands.

Choose the least complex split that supports the target poses. Full-frame part layers often need fewer sockets than separately positioned limbs. Segment only where independent replacement, attachment motion, or occlusion needs it.

Every part declares its compatible rig family, body proportions, actions, direction coverage, grip family, render pieces, and hiding/coverage rules. Two-handed items can reserve both hand slots. Reject incompatible combinations or apply a documented, visible fallback. Never silently use a south-facing or idle-only part in a missing attack direction.

Separate selectable directions from uniquely authored views. RO-style actions may declare an eight-to-four diagonal view map; standing/walking/sitting can use another map. The inspected male Swordman has eight distinct sitting views too; do not assume only standing/walking need eight. Resolve that action view once for all equipped pieces. Explicit reuse preserves coverage; it does not permit undeclared missing views, independent part mappings, weapon-hand flips or altered gameplay aim.

## 4. Lock the base and pose timeline

Establish an approved neutral turnaround in all eight views and a base animation for each required action. With an existing approved base, work directly from it.

Give every body pose a stable key: `(rig, action, direction, frame)`, with an authoritative phase and duration. Replacement parts must fit that pose. They may reuse static images or have fewer source frames if an explicit phase/pose map covers every required body sample and supplies the appropriate anchors. Do not require identical raw image counts, or synchronize parts merely by equal average FPS. Maintain anatomical handedness through turns.

Use a shared logical canvas, shared scale, and authored root anchor. Do not center, crop, or scale each part according to its own visible bounds. Preserve intentional bobbing and pose motion relative to the fixed root. Retain invisible frames as explicit timeline entries.

For AI-assisted animation, generate a coherent clip or strip from approved references, then verify exact frames, pose phases, and grid. Whole-strip generation reduces opportunities for drift but does not guarantee correctness. Avoid independent unconstrained frame prompts. Do not treat semantic masks from a flattened sprite as complete hidden parts.

### Build motion before adding detail

For a simple grounded walk, establish alternating contacts and the contact/down/passing/up structure before polishing clothes. Coordinate hips, torso, shoulders, arms, neck, and head. Movement can be modest; do not paste moving legs beneath a frozen torso. Keep the root as a ground registration reference while allowing body motion around it.

During straight stance, a planted foot's local backward velocity should cancel root travel in world space. For direction changes, retain a world-space contact target until release or use reviewed authored transition poses. Distance-driven phase helps match cadence to travel, but correct phase selection alone cannot remove sliding from faulty drawings or held poses.

For a rig, keep targets inside the limb's reach envelope, choose anatomical bend directions, and inspect contact activation/release and knee motion. An analytic IK solution guarantees a target position only within its assumptions; it does not establish weight, pleasing silhouettes, or smooth transitions.

For an attack, define anticipation, contact, recovery, support foot/feet, grip, and gameplay event timing. Use pose holds and fast arcs intentionally. Review the actual visible blade/hand silhouette at gameplay scale. A socket following the hand is necessary but does not establish a convincing strike.

For the current attack, the user's latest instruction supersedes the earlier higher-FPS target: use a lower, RO-like authored pose cadence. A rendered public RO reference studied in the [attack repair](references/full-body-attack-repair.md) has nine 100 ms poses; this is one community-renderer example, not proof of a universal original-client rate. Use explicit durations and intentional holds. Keep the render/update rate independent from source poses. Do not confuse eight directions with eight frames or an animation-rate limit.

### Repair shaking without freezing the body

Read [full-body attack repair](references/full-body-attack-repair.md) before retrying the rejected character. Registration, anatomy, silhouette consistency and acting are separate gates. A six-pose animation with cloned legs can pass a boot-drift check and still fail the intended attack.

Block the action before adding detail or trails. Establish a visible rear-leg load, hip travel and rotation, torso counter-rotation/drive, lead-knee absorption, rear-heel lift or authored step, empty-arm counterbalance, and coordinated recovery. Exact motions depend on the attack; do not apply a fencing lunge literally to every slash. Define which sole, toe or heel remains planted during each phase. Measure only active contacts; a released heel's motion is intentional.

Use one fixed ground root and consistent scale/camera. Do not normalize each pose to the changing silhouette's bottom-center, sword bounds, head center or the average of both feet when the attack deliberately pivots or steps. Preserve authored body travel relative to the root. A pose guide should contain joint targets, contact states and timing; copying only sword angles from it is insufficient.

Review the body with the sword/trail hidden and in silhouette. If the load, drive and recovery cannot be distinguished from the legs, pelvis and torso, reject the motion before detail work. Check visible knee/hip/shoulder changes, coherent head attachment, stable bone lengths/grip and a readable planted support. A rigid-length/contact diagnostic proves only its mathematical assumptions; it does not approve the final drawings.

Export the sword trail as a separate phase-controlled layer. Use one authoritative action time while allowing body poses and effect decay to have different samples. A held body key must not keep a baked trail alive beyond emission end plus lifetime. Check the cutoff between pose keys as well as cancellation; include effect changes in render invalidation. The current proof fixes a 90 ms late exposure without adding body poses; scalar fading alone does not improve trail geometry. Activate it on the fast forward cut, optionally retain a collapsing remnant, then clear it in recovery and on interruption. Register it to the actual projected blade sweep. A generic crescent drifting away from the blade is a failed effect, even if its timing is correct.

Measure exported-sprite contact drift at the actual game speed, scale, zoom, and projection. Declare a pixel budget; inspect normal and quarter speed. Add strategically placed poses, change holds/cadence, or implement reviewed contact correction when the export fails. Do not prescribe eight frames as a universal walk standard.

## 5. Produce each replacement against the base

Author a part while the approved body and neighboring pieces remain visible as alignment references. Export only the intended piece. Reuse camera, pixel density, palette, lighting, timing, and source coordinates.

Inspect native resolution before detail and before promoting a turnaround. Establish broad material/identity clusters and deliberate contours, then refine face, glove/grip, folds and accents. A rendered mannequin or large generated illustration can establish perspective but remains unapproved art. Verify returned canvas/grid/alpha; a prompt requesting pixels or parts is not evidence. Independently outlined pieces can create dark seams after swapping, so review outer and internal boundaries against shared visibility.

Complete the entire supported action/direction/frame matrix. A palette variant can reuse geometry; a new silhouette generally needs new authored content or a rigged/rendered variant.

Keep useful overlap under joints and clothing seams. Supply hidden anatomy or intentional replacement coverage where needed. Do not cut parts exactly at visible contours and assume movement will keep the seam closed.

For 3D exports, preserve identical sample times for all equipment passes. Choose explicitly whether a pass contains isolated full geometry or visibility clipped by a canonical combination. The second choice may require regenerating masks when combinations change. Validate reconstructed composites against full reference renders.

Validate actual evaluated scene time before batch export. Manually posing while an active action evaluates another frame can freeze rendered animation. Check distinct image outputs as well as metadata. Report independent full-scene owner/alpha and color comparisons separately; exact visibility cannot conceal unresolved color differences. Translucent FX require additional sorting tests.

## 6. Author occlusion

Store a default draw order for each facing, with action/frame overrides where necessary. Inspect diagonal facings and crossing limbs, not just front and back.

When one piece must pass both behind and in front of another in the same frame, split it, use pose-specific coverage masks, or use a validated depth-aware renderer. One scalar order for a whole sprite cannot express that overlap.

Keep character-internal ordering distinct from the character's depth among world objects. An equipped character should remain a coherent world-sort unit unless deliberate scene interleaving is part of the design.

## 7. Export and integrate

Start with aligned untrimmed RGBA frames. Pack for shipping only after correctness is established. A packed frame must retain logical source size, trimmed rectangle placement, anchor, atlas rectangle, and any rotation flag. Record alpha convention and sampling behavior.

Export a machine-readable manifest identifying rig, items, directions, clips, timings, frames, sockets, coverage rules, draw order, and provenance. Verify the target engine's interpretation of pivots and trim metadata.

Drive all pieces from one authoritative animation state. Sample its current pose once; resolve all equipped pieces from that sample; apply visibility, ordering, and root placement; render them. Keep cosmetic swaps on the current frame and subframe progress. Stage texture loading before atomically committing a replacement. Gameplay stance or grip changes may transition animation according to explicit state-machine rules.

In Godot, restoring only `frame` loses subframe progress; check `set_frame_and_progress`. In Phaser, Container child order needs explicit management; child `depth` alone does not reorder the Container display list. In Unity or Spine, verify rig/attachment compatibility as well as selecting the replacement artwork. Pin APIs to the installed engine/tool version.

## 8. Required quality gates

Structural checks:

- Every required pose key resolves for every supported item or has an explicit supported fallback.
- Parts share source dimensions, root registration, authoritative pose timing, and rig family; explicit source-image phase mappings may differ.
- Blank and duplicate poses preserve their logical frame entries.
- Atlas rectangles, trims, pivots, socket coordinates, and ordering references are valid.
- Item conflicts, hidden parts, and handedness are represented explicitly.

Visual and runtime checks:

- Preview all eight facings at native game scale and enlarged nearest-neighbor scale for pixel art.
- Play every supported clip at normal and quarter speed; inspect loop boundaries, contact drift, body coordination, attack poses, and direction changes.
- Test start, stop, turn, speed change, and action interruption independently from clip playback. A seamless loop does not validate these transitions.
- Show parts individually, a diagnostic layered composite, and the final appearance.
- Stress large helmets, long hair, capes, bulky sleeves, broad shields, and long weapons where relevant.
- Swap compatible items in motion and during attacks; preserve phase and avoid partial-load frames.
- Exercise missing diagonal parts, wrong hand ownership, incompatible rig families and rapid asynchronous requests; reject unsupported tuples explicitly.
- Inspect seams, clipping, silhouette drift, mirrored asymmetry, hair coverage, alpha fringes, and world depth.
- Measure relevant draw cost, decoded texture memory, loading latency, and bounded cache growth.

Do not approve from a contact sheet alone. Do not claim an in-engine or visual check passed unless it was run. Save actual results, unresolved cases, and tool versions in the quality report.

## Deliverables and iteration

Deliver editable source, approved turnaround, separate part assets, runtime manifest, compatibility rules, preview artifacts, provenance/credits, and a quality report. Include a flattened composite only as a preview or deliberate runtime cache output.

When the user teaches a new rule, record the concrete failure it prevents, the revised procedure, an example, and the check that detects regressions. Put fixed project choices in a project brief; keep broadly reusable rules in this skill. Raise the package version after substantive revisions.

Use the [competency ladder](references/motion-study.md#competency-ladder) to select the next exercise. Continue from the highest demonstrated stage; do not equate source count, passing mathematical tests, or a mannequin preview with mastery of final sprite animation. The original [motion lab](studies/motion-lab/README.md) is a reproducible study, not an approved production base.

For the user's “ultimate skill” target, keep a capability/evidence/gap record. One family and one attack cannot validate a factory for additional proportions, actions or grips. Preserve failed comparisons and user rejections when new iterations improve individual gates.
