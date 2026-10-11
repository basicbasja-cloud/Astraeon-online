---
name: modular-eight-direction-sprites
description: Design, produce, repair, and validate eight-direction 2D character sprites with interchangeable body, clothing, hair, armor, and equipment parts. Use for paper-doll sprites, directional attachment systems, layered frame animation, or 3D-to-2D modular character exports.
---

# Modular eight-direction sprites

Research-backed draft v0.3, reviewed 2026-10-11. Includes original motion, separate-part export, depth-composition studies, and a full-body attack repair study responding to rejected painted animations. Final sprite art, production packing, and game integration remain unvalidated. The linked sources establish individual techniques; this package's combined asset contract and quality gates are proposed engineering practice.

## Scope and references

Read [binding user constraints](references/user-constraints.md) before this user's project work. For Astraeon, Ragnarok is the stated inspiration, main is obsolete, and every existing branch's character art is rejected. The sole working branch for this research is now `research/modular-sprites-full-body-2026-10-11`; keep subsequent iterations on it. Study technical contracts on the newest branch, but derive no visual guidance from those rejected assets. Earlier art inferences are superseded.

Use when a character must retain identity and animation while independently replacing appearance parts in eight facing directions. A flattened sprite sheet alone does not satisfy a modular-parts request.

Read [research](references/research.md) for approach selection, [motion findings](references/motion-study.md) for animation design and measured limitations, [asset contract](references/asset-contract.md) before production, and [production recipes](references/production-recipes.md) for tool-specific work. [Sources](references/sources.md) distinguishes implementations, official documentation, research, and tutorials. [Astraeon technical brief](references/astraeon-technical-brief.md) pins the newest branch studied.

Do not claim that reading this skill permanently trains a model. The durable output is this package and project assets. Do not claim the package is installed unless the active skill loader actually registers it.

## 1. Establish the production contract

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

## 3. Define slots, pieces, and compatibility

Separate gameplay equipment slots from render pieces. A single equipped cape may provide `cape_back` and `cape_front`; one helmet may hide selected hair regions; one glove item may supply both anatomical hands.

Choose the least complex split that supports the target poses. Full-frame part layers often need fewer sockets than separately positioned limbs. Segment only where independent replacement, attachment motion, or occlusion needs it.

Every part declares its compatible rig family, body proportions, actions, direction coverage, grip family, render pieces, and hiding/coverage rules. Two-handed items can reserve both hand slots. Reject incompatible combinations or apply a documented, visible fallback. Never silently use a south-facing or idle-only part in a missing attack direction.

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

Export the sword trail as a separate phase-controlled layer. Activate it on the fast forward cut, optionally retain a collapsing remnant, then clear it in recovery and on interruption. Register it to the actual projected blade sweep. A generic crescent drifting away from the blade is a failed effect, even if its timing is correct.

Measure exported-sprite contact drift at the actual game speed, scale, zoom, and projection. Declare a pixel budget; inspect normal and quarter speed. Add strategically placed poses, change holds/cadence, or implement reviewed contact correction when the export fails. Do not prescribe eight frames as a universal walk standard.

## 5. Produce each replacement against the base

Author a part while the approved body and neighboring pieces remain visible as alignment references. Export only the intended piece. Reuse camera, pixel density, palette, lighting, timing, and source coordinates.

Complete the entire supported action/direction/frame matrix. A palette variant can reuse geometry; a new silhouette generally needs new authored content or a rigged/rendered variant.

Keep useful overlap under joints and clothing seams. Supply hidden anatomy or intentional replacement coverage where needed. Do not cut parts exactly at visible contours and assume movement will keep the seam closed.

For 3D exports, preserve identical sample times for all equipment passes. Choose explicitly whether a pass contains isolated full geometry or visibility clipped by a canonical combination. The second choice may require regenerating masks when combinations change. Validate reconstructed composites against full reference renders.

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
- Inspect seams, clipping, silhouette drift, mirrored asymmetry, hair coverage, alpha fringes, and world depth.
- Measure relevant draw cost, decoded texture memory, loading latency, and bounded cache growth.

Do not approve from a contact sheet alone. Do not claim an in-engine or visual check passed unless it was run. Save actual results, unresolved cases, and tool versions in the quality report.

## Deliverables and iteration

Deliver editable source, approved turnaround, separate part assets, runtime manifest, compatibility rules, preview artifacts, provenance/credits, and a quality report. Include a flattened composite only as a preview or deliberate runtime cache output.

When the user teaches a new rule, record the concrete failure it prevents, the revised procedure, an example, and the check that detects regressions. Put fixed project choices in a project brief; keep broadly reusable rules in this skill. Raise the package version after substantive revisions.

Use the [competency ladder](references/motion-study.md#competency-ladder) to select the next exercise. Continue from the highest demonstrated stage; do not equate source count, passing mathematical tests, or a mannequin preview with mastery of final sprite animation. The original [motion lab](studies/motion-lab/README.md) is a reproducible study, not an approved production base.
