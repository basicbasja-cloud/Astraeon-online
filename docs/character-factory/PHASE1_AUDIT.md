# Phase 1 — audit and freeze

Audit date: 10 October 2026 (Asia/Bangkok). Base: latest fetched `origin/swordman`,
`b43f9d2ba5820f7b0ec48f137e1014fddd2e8442`. Working branch:
`character/production-factory-v2`, as requested by the owner. No merge or deployment.

**10 October owner override:** neutral guide 01 was rejected for the arm, sword
and overall anatomy. The owner subsequently instructed a fresh rebuild and deep
internet research, rather than further repair of the failed approach. The earlier
phase progression below is historical. Current decision and source-backed tool
comparison: [fresh 2D research](RESEARCH_2D_EIGHT_DIRECTION.md). No approved new
motion library or Golden character exists.

The existing modular painted sprite system is suitable. No failing runtime
contract justifies replacing it. Proceed only with the upstream structural guide
foundation; no Golden production, final paint, class expansion or visual approval.

## Authority and status

| Status | Evidence and meaning |
|---|---|
| APPROVED | `authoring/characters/gait-rig-v50/approved-warrior-seed.png` is the unchanged shipped identity crop identified by that folder's README. SHA256 `750ffe25056760c6ab97c3e66a3488d15aec4c875e573d9a8cef65c8f0437e05`; copied reference has the same digest. This is approval of the inherited Warrior identity seed, **not approval of the modular Golden Swordsman or its motion**. |
| PROVISIONAL | Mapping that seed to the Golden Swordsman; measured identity locks; approximately 45-degree sprite camera; coordinated `candidates/directional-02` masters (37/40 internally); rig-walk/candidate-03 (38/40 internally). These are working structural/design references awaiting owner confirmation. |
| DEV_ONLY | All Swordsman modular masters, packed `swordsman-male-candidate`, internally passed painted clips, geometric `swordsman-proof`/`mage-proof`, and all new factory guides. No new source.approvedBy is permitted. |
| REJECTED | directional-01 camera/identity study; prior Walk attempts and simplified leg guide; the generated arm study. rig-walk/candidate-02 internal pass was withdrawn for inadequate rearward thigh extension. BasicAttack04 pass withdrawn for NE sword-angle singularity; BasicAttack05 rejected for NW angular detour. Retain the original provenance, comparisons and reports; a superseded candidate is not automatically owner-rejected. |
| MISSING | Owner-approved eight-direction Swordsman masters; complete Golden character; Death/Guard/Dash; female or future body variant; interchangeable alternate costume/sword, substantive offhand/headgear/back proof; approved final painted motion library; complete action runtime evidence and owner acceptance. |

`audit-inventory.json` retains exact provenance decisions for every candidate,
source digests, actual clip metadata, and all supplied pack manifest checks. The
supplied ZIP was fully extracted; 00_START_HERE, every spec, contract, schema,
research note, prompt and starter were inspected. They are specification/reference
material subordinate to the user's current bounded Phase 1/2 request. Bootstrap
and suggested AGENTS content were not executed or installed. The supplied master
prompt numbers phases differently; this report follows the user's phase numbers.

## Frozen registration, direction and sockets

Runtime authority: `docs/MODULAR_SPRITES.md`, `modular-sprites.js`, schema
`assets/characters/schemas/sprite-definition.schema.json`, and current packed
definition. Canvas: 320×320; root: (160,264); reference height: 176. Full RGBA
canvas for every part, no per-frame alpha fitting, mirroring or registration nudges.
Direction order: S, SW, W, NW, N, NE, E, SE. Legacy atlases have another row order;
the existing adapter resolves heading to a **direction name**, not an assumed index.

Required sockets: root (fixed ground origin), head (head attachment), hand_R and
hand_L (anatomical grips), back (back attachment), waist (belt attachment). Existing
extra foot/ankle/heel/toe sockets are allowed. S front places anatomical right on
viewer-left; N places it on viewer-right. Parts contain atlas refs, never a second
socket map, animation clock or canvas. Runtime weapons are already registered
into their full frame and must not be shifted by the hand socket again.

## Layers and runtime interface

BaseBody, Hair, Outfit, Weapon, Headgear, BackAccessory are required. Optional
Face, Offhand, Cape, CosmeticFX, Aura, ShoulderAccessory are supported. Current
default Headgear/BackAccessory are transparent. The gold cape belongs to current
Outfit construction; it does not yet prove an interchangeable back accessory.

Render slots map to logical layers. Every resolved drawOrder contains every slot
exactly once, back to front; a direction or pose may override it. WeaponBack /
Weapon front portions can share logical Weapon. BaseBody includes underlying
body and exposed identity paint; Outfit owns clothing. Existing painted master
separation is source masking/warping, not proof of independently authored complete
underlying surfaces for arbitrary costumes.

`AstraeonModularSprites.load` → ensure clips → compiled.sample(animation,
direction, elapsedMs, appearance) → draw or existing player adapter. Non-looping
clips hold their last frame. Body variants remain Swordsman presentation identity.
Cosmetic IDs resolve body-specific parts; setAppearance preloads and swaps
atomically. Equipment/stats never choose appearance. `allowDev: true` is required
for DEV_ONLY. `index.html?qa=1&swordsman=male` explicitly enables the development
candidate; ordinary player calls keep original art. No runtime 3D actor is needed.

## Existing action evidence

| Action | Retained best | Frames × directions | Status |
|---|---|---:|---|
| Idle | male/motion-candidates/Idle/candidate-03 | 8 × 8 | 93/100 internal, DEV_ONLY |
| Walk | Walk/candidate-28 | 16 × 8 | 91/100 internal, DEV_ONLY |
| Run | Run/candidate-01 | 12 × 8 | 92/100 internal, DEV_ONLY |
| BasicAttack | BasicAttack/candidate-06 | 16 × 8 | 91/100 internal, DEV_ONLY |
| SkillAction | SkillAction/candidate-02 | 14 × 8 | 91/100 internal, DEV_ONLY |
| Hit | Hit/candidate-02 | 8 × 8 | 92/100 internal, DEV_ONLY |
| Death / Guard / Dash | Idle-derived scaffold metadata | not produced | MISSING / PENDING_PRODUCTION |

Clip timing belongs to the definition (recorded verbatim in audit-inventory).
Existing shared source motion: `tools/swordsman-walk-cycle.py`, run-cycle.py and
action-poses.py. Walk has 1.12-second original cycle and virtual planted-foot
travel. Current source uses .70 leg calibration in painted output; Blender rig
proof itself uses 2.65 orthographic span. The painted upper body uses independent
measured per-direction landmarks. Therefore the current rig is reusable motion
input, **not a complete canonical character production rig**.

## Deterministic versus generative; smallest repair

`tools/build-swordsman-walk-rig.py` builds a fixed-length anatomical armature with
editable `rig-walk/candidate-03/walk-proof.blend`, 113 sampled keys, IK knees and
heel/toe contact diagnostics. It orbits the camera for directions and recalculates
camera shift; it does not expose the complete stable attachment/layer contract.
Older v50/v51 sources are studies, not approved replacements.

Current generation produces direction/identity paint probabilistically.
build-swordsman-production masks masters, warps UV surfaces and rigidly transforms
hair/sword against shared motion. Packing, normalization, full-canvas registration,
timing and metadata validation are deterministic. Current bests remain recoverable.

Smallest upstream addition: separate editable canonical skeleton/proxy surfaces,
fixed orthographic camera, named anatomical attachment transforms and root-only
eight-heading rotations; render neutral structural guides twice and compare pixels,
depth, masks and projected sockets. Use existing original motion later, after this
foundation is reviewed. Freeze technical registration now, mark inferred proportions
and exact camera/art fit PROVISIONAL. A single painted view cannot establish true
anatomical lengths or exact historical lens settings.

The owner clarified that Blender is installed. Windows installation registry
locates `C:/Program Files/Blender Foundation/Blender 5.2/blender.exe`; direct
execution confirms Blender 5.2.2 LTS, build d13f752e3b9c. It is outside PATH.
The game-dev CLI is absent; direct native Blender execution follows the repository's
authoring method and the user's explicit scope. No paid providers are needed.
Final identity/camera approval remains open; it does not block a neutral guide proof.

## Validation and evidence boundaries

Fresh baseline results at the audited SHA:

| Check | Result |
|---|---|
| python tools/validate-sprites.py | PASS: 5 definitions, 337 atlases, 32,304 frame refs |
| python tools/run-node-checks.py | PASS: 135 individual checks |
| node --test --test-isolation=none tests/world_streaming.test.mjs | PASS: 5 checks |
| python tests/modular_sprite_tools.py | 7 pass; 1 environment error: Windows WinError 1314 creating an escaping test symlink. Namespace guard not weakened; no code failure established. |
| python tests/swordsman_walk_motion.py | PASS: 8 checks, fixed lengths/contact/continuity/attack paths |
| swordsman_candidate_composition.py for six current clips | PASS: 592 exact packed composites |
| modular_sprite_browser.py with local Chrome | PASS: 432 frames, swaps, playback, adapter, responsive view |
| modular_runtime_browser.py | Recorded separately in baseline-results.json; ordinary player/WebGL/offline path, not new art approval |

Normal/quarter previews, all-direction comparisons, layer breakdowns and previous
in-game screenshots already exist in `docs/review/swordsman-production-v0.1` and
candidate directories. Historical validation-results.json counts only its earlier
scope; current asset namespace contains additional Mage/body definitions, explaining
the fresh validator's larger totals. Historical reports do not approve this branch.

Tools to retain: normalize-modular-strip.py (single shared transform),
pack-modular-sprites.py --deduplicate (untrimmed RGBA cells, gutters, optional exact
deduplication), validate-sprites.py plus Node metadata validator and JSON schema.
Non-deduplicated long clips exceed the 4096 atlas limit; use the existing deduplicate
path when appropriate, not a second format. Browser/game/cache suites remain
required for later shipping integration. No shipping asset changes in Phase 2.

RAGNAROK_REFERENCE is a pinned research study, not production pixels or Gravity
workflow proof. Pack vendor capability notes are research snapshots; no paid/vendor
integration is implemented. CURRENT_HANDOFF contains a separate world task and
historical camera/branch instructions; this user's explicit character branch/task
controls this work. World files and renderer are outside this bounded change.

## Latest-branch additions that supersede the pack snapshot

The base's newest commit adds `authoring/characters/true-modular/swordsman/male/`
and `tools/modular_character_engine.py` / `build_true_modular_swordsman.py`. These
author 11 independent source layers from original geometry (BodyCore, HeadBase,
Face, HairBack/Front, Outfit, Weapon, Cape, accessories/FX), with registered Idle
and Walk and cosmetic-swap evidence. They deprecate the old subtractive painter
as an authoring route, while retaining all historical candidates. Their identity
lock references unapproved `swordsman-production/master-composite.png`; it does
not establish newer owner-approved identity authority. Source rig knee poles
and 25-degree depth cue differ from the earlier anatomical gait/45-degree Blender
guide. Preserve both proofs; neither silently freezes final Golden proportions.
The new factory provides neutral 45-degree Blender structural evidence under the
existing 320px authoring contract; final fit/retargeting to this newer independent
layer authoring route remains open. No new painted candidate is promoted.

`docs/CHARACTERS_PATCH_001.md` and `wardrobe.js` introduce a uniform .5 runtime
compilation: 160×160 / root (80,132) / reference 88, derived from 320px authoring.
This is an existing presentation path, not a newer approved 320px source contract
replacement. Current Mage packages exist; `swordsman-male-001` and
`swordsman-female-001` do not. The creator's wardrobe load requests the absent
Swordsman URL. The modular runtime browser baseline waits for creator readiness
and times out. This pre-existing package gap explains that failure and contradicts
older documentation claiming ordinary calls still always use the legacy player.
The 18-clip wardrobe gate also differs from the newer Swordsman's 16 required
actions (Sit optional, Blink excluded). Fixing this belongs to later integration;
do not manufacture missing production clips to make the test green.

The nine Golden actions requested here remain the minimum factory target, not a
claim that broader latest-branch action coverage is already complete. The newer
proof has Idle/Walk only; the six older internally passed clips are historical
painted evidence, not transferable approval for the independent source renderer.

Decision: audit gate understood; no blocking contradiction for neutral authoring
evidence. Shipping/Golden integration remains blocked by the missing packages and
unapproved camera/identity fit. Proceed with
Phase 2 neutral rig/view foundation only. Stop before motion-library expansion,
equipment proof, stylisation or Golden acceptance.
