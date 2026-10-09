# Current production composition: BodyWithOutfit + independent Head

The owner-selected model supersedes the former BodySpriteSet wording for new production. Use MotionTemplate + BodyWithOutfit + Head + Hair + MainHand + OffHand + Headgear + Garment/Cape + optional FX. A costume replaces the **entire dressed body**; it never builds armour as independent shirt/pants/boots layers. Gameplay equipment remains a separate authority.

The strict schema1.1 pack is [swordsman-bodywithoutfit](../authoring/characters/appearance/swordsman-bodywithoutfit/appearance-pack.json). BodyWithOutfit and Head are required. The existing generic engine retains internal layer names Body and HeadBase as clean equivalents, preserving historical fixtures and draw profiles.

The BodyWithOutfit contract binds canvas320, root(160,264), eight directions, Idle/Walk/BasicAttack, the exact frame-duration timeline and shared semantic socket calibration. Both default and royal proof bodies bind the same contract. MotionTemplate bytes, choreography, events and timings are unchanged. Registered body anchors compose motion anchors with the single shared contract calibration; a costume cannot override them.

Each Head frame has a neck/base pivot, explicit trim origin, and Head-local hair/headgear sockets. Head uses BODY_SYNC to preserve the already-painted direction/action perspectives. Hair inherits the **selected Head transform** and local skull socket. MainHand uses its authored grip pivot and a reduced PHASE_SYNC set of existing directional blade perspectives; its registered hand transform still follows every body frame. cape uses its measured shoulder/back pivot and BODY_SYNC registration. Rear cloth has back/front passes so cloth can cover the torso while the sword arm remains readable.

Transform order is motion anchor × shared body-contract calibration × part.defaultRegistration × directionRegistration × actionPhaseRegistration × sample.localTransform. Head-local children begin from Head transform × its local socket. No runtime Swordsman action/direction/frame offset branches exist. Appearance draw profiles are validated complete layer permutations and select phase occlusion independently of choreography.

The review defaults to a clean composite. Its development controls expose solo layers, root/anchors, neck/skull/grip/back pivots, bounds, phase, sampling and order. Costume changes preserve action, direction, elapsed time, cosmetic time and all non-body raster samples. Both browser PNG comparisons and controller tests cover the complete328-frame proof. No Equipment Backbone, world, ordinary boot or gameplay source is changed.

New [animated review evidence](review/character-bodywithoutfit-registration-v1/registration-report.md) remains **OWNER VISUAL APPROVAL PENDING**. The prior rejected proof and schema1.0 fixtures remain immutable historical references. Their executable tests still run.

---

# ASTRAEON Character Assembly Engine v1

Rescue scope: reusable assembly and RO1 reference intake; painted Swordsman proof
limited to Idle, Walk and BasicAttack. The [animated painted proof](review/character-ro1-animated-v1/REPORT.md) uses rendered RO motion evidence. Exact ACT timing is unknown; owner visual approval is pending. [Historical audit](review/character-ro1-engine-v1/audit.md).

`character-motion-template.js` is the independent numeric motion authority.
`character-assembly.js` combines it with replaceable raster appearance packs.
`modular-sprites.js` exposes optional compileAssembly/loadAssembly/drawAssembly
without changing its legacy compile/load/draw API. Normal game boot is unchanged.
The painted review loads motion-template and assembly. Modular-sprites supplies
an optional bridge for existing visual callers.

## Motion and smoothing

[Motion schema](../authoring/characters/schemas/motion-template.schema.json)
stores a registered canvas/root and reference height, explicit transform units,
canonical directions, actions, direction timelines, named draw profiles,
reference-key catalogs, expanded frames and total-duration budgets. Keys contain
source identity, pose intent, phase, root, anchors and visual events. Appearance
contains none of those motion authorities.

Every expanded frame has exactly one role: referenceKey or astraeonInbetween.
The executable validator rejects changed/missing/reordered keys, changed key
timestamps, invalid neighbors, altered pose metadata and changed total duration.
In-between IDs link to the two neighboring key IDs with an interval fraction.
The last key may interpolate to the first only on a looping action. No
unclassified holds or invented choreography branches are accepted.

`smoothSequence(sequence, insertionSchedule, loop)` subdivides selected key
intervals, with positive integer milliseconds and unchanged total/key timestamps.
Position/scale interpolation and shortest-angle rotation are authoring aids;
the sprite painter must follow observed body orientation, limb/contact intent,
silhouette and weapon progression. Reference dwell may be reduced within its
interval, but landmark timestamps remain fixed. Events remain on keys. No
automatic frame doubling, duration doubling or custom procedural gait.

The `ro1-swordsman-male` template now executes rendered reference evidence.
Every key identifies source URL, image hash, indexed action/frame and confidence.
ACT_EXTRACTED, RENDERED_REFERENCE, VIDEO_DERIVED and VISUAL_DERIVED keys remain
distinct from ASTRAEON_INBETWEEN frames. Rendered evidence cannot claim exact ACT
timing. Synthetic fixtures cannot be marked production.
RO-derived rescue templates reject actions outside Idle/Walk/BasicAttack.

## Appearance and layer sampling

[Appearance schema](../authoring/characters/schemas/appearance-pack.schema.json)
declares compatible motion IDs, matching registration, slots, defaults, independent
parts and atlas references. BodySpriteSet contains body/core class clothing/boots
as one visual set. No separate runtime armor economy is introduced. HeadBase may
remain separate when the appearance requires it. Hair, weapons, offhand, headgear,
garment and effects remain replaceable. Optional slots select null and require no
transparent atlas.

| Mode | Selection authority | Typical source |
| --- | --- | --- |
| BODY_SYNC | Exact expanded body frame index | BodySpriteSet, complex garment |
| PHASE_SYNC | Explicit normalized time thresholds, starting at0 | Hair, cape with fewer phase paintings |
| ANCHOR_HOLD | One/few authored direction views with optional phase thresholds | Headgear, weapon, shield |
| OWN_LOOP | Separate cosmetic clock and its own positive frame delays | Aura or floating charm |

Time phase uses each direction's action duration, not frame-index fractions.
Diagnostic frame selection uses that frame's start timestamp. OWN_LOOP's time is
independent of action changes when supplied through createController or the
`cosmeticTimeMs` sampling option. Its timings cannot change body timings.

Canvas-space paintings use the complete shared canvas. Attachment-space paintings
may use small raster cells with authored pivots and optional local transforms.
Both preserve the same assembly root. Canvas convention and atlas bounds are
validated; no alpha-bounds fitting occurs at runtime.

## Anchors, transforms and order

Required anchors: root, head, mainHand, offHand, back, waist, footL, footR.
Optional anchors include weaponTip/fxOrigin. Each transform has x/y canvas pixels,
clockwise rotation in radians and positive uniform scale. Anchor root is exactly
the registered root. Attachment pivot/local transforms compose beneath the
motion anchor, allowing interchangeable weapon grips without repainting Body.
Perspective-critical poses may select additional authored weapon views.

Semantic profiles include Shadow, GarmentBack, Body, HeadBase, HairBack,
HairFront, HeadgearLower/Middle/Top, MainHand, WeaponSlash, OffHand, GarmentFront,
BackAccessory and CosmeticFX. Profiles list all known semantic layers; absent
layers are filtered. Slots assign each layer to at most one selected part.

Order resolution is: frame drawOrder → frame drawProfile → direction drawProfile
→ template defaultDrawProfile. Profiles are validated permutations. No per-class
if/else ordering or fixed global z-index. GarmentBack/Front can share one part
selection while supplying separate raster layers.

## Swap and gameplay boundary

compileAssembly is immutable/stateless. createController owns only presentation
action, direction and clocks. setAppearance validates and changes selection;
it cannot reset action/time/frame or access movement, collision, targeting,
equipment, inventory or Combat. Action changes reset animation only when callers
explicitly call setAction. Visual events are metadata, not callbacks into Combat.

loadAssembly preloads selected-part atlases and switches atomically after success.
Failed/superseded requests retain the previous complete appearance. Loading does
not own gameplay clocks. Unapproved packs/templates require allowDev:true.
Source, raster atlas and appearance selection identities can be hashed separately.
Development metadata and atlases use the existing `spriteDev=1` service-worker
bypass. Review assets do not consume or evict ordinary gameplay asset caches.

## Reproducible engineering proof

`python3 tools/build_assembly_debug.py` bakes colored raster shapes and two packs
from one synthetic motion fixture. Body blue, skin head, purple hair, red weapon,
yellow offhand, cyan headgear, green garment. Debug direction arrows are eight
authored raster outputs; no mirroring. Neither a gait nor a sword technique is
claimed. Run Node/Python/browser checks documented in the final checkpoint.

The second coral pack reuses the same MotionTemplate and engine with a different
Body/Hair/MainHand selection. There is no Swordsman-specific engine branch.

## Production gates

RO motion evidence must precede production animation. The owner-authorized
fallback accepts rendered/video/visual evidence when raw ACT is unavailable;
exact ACT claims still require actual extraction. Verify eight neutral
painted ASTRAEON identities from the unchanged seed, then use Game Studio's
approved-seed → edit canvas → coherent strip → shared normalization/registration
→ preview → in-engine review workflow. Do not generate each frame independently.
Keep modular raster sources, including both hair/weapon variants. Require all
three actions × eight directions, swaps and actual gameplay captures. Automated
ENGINE PASS and STRUCTURAL ASSET PASS never imply owner art approval. Mark all
new painted output REQUIRES_OWNER_VISUAL_REVIEW. Stop before any action expansion.
