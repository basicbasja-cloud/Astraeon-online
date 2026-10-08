# ASTRAEON character rescue checkpoint — 2026-10-08

The reusable raster assembly engine and two dummy appearance packs pass their
engineering proof. **The RO1 Swordsman production proof is incomplete.** Actual
male Swordsman reference ACT/SPR data is unavailable; source poses, contacts,
attack selection and timing cannot be invented. No new production animation or
painted appearance pack was generated. This is a reviewable engineering rescue
checkpoint, with a documented reference intake gate.

- **ENGINE PASS:** independent MotionTemplate, appearance packs, four sampling
  modes, transforms, draw profiles, isolated swaps and second-pack reuse.
- **STRUCTURAL ASSET PASS:** DEV_ONLY dummy raster assets; separately, preserved
  eight-direction painted neutral candidates. This does not certify production
  Swordsman actions or modular painted layers.
- **VISUAL OWNER APPROVAL PENDING:** preserved painted turnaround is
  `REQUIRES_OWNER_VISUAL_REVIEW`; no production artwork is approved here.

Open [character-review.html](../../../character-review.html) through a local static
server. It shows synthetic keys, in-betweens, layers, anchors, order, playback,
cosmetic controls and 1×/2×/4× scales. It is development tooling, not game UI.

## Git and protected history

| Field | Value |
| --- | --- |
| Branch | `character/ro1-reference-engine-v1` |
| Starting checkout branch | `work` |
| Starting checkout HEAD | `3f8d41ceee91b4fe5dc6baa7b5c44014e3608355` |
| Verified source branch | `origin/codex/swordsman-visual-production-v0.1` |
| Source / new-branch starting HEAD | `c258c5034a49462381d15f425f103eddf85242c9` |
| Historical proof | `origin/swordman` at `b43f9d2ba5820f7b0ec48f137e1014fddd2e8442` |
| Verified graph | Historical proof's direct parent is source HEAD |
| Final HEAD | Reported with the final `git log`; this committed report cannot contain its own commit hash |

`git fetch origin` ran first in the repository. Because the configured fetch
refspec only included main, relevant heads were also inspected with ls-remote and
explicitly fetched. Remote lineage, not the initial `work` checkout, selected the
base. [Pre-edit receipt](git-start.json) records the clean initial status, source,
new branch and actual graph. No deletion, reset, force-push or protected-branch
update occurred. Work is committed locally in separate milestones; no push was
requested or performed.

## Existing pipeline audit

Read all four requested root documents; inspected current runtime, historical
authoring Python/build/tests, blueprint, authoring manifest, reviews and atlases.
The proof documents editable pose/source output that was not actually committed:
no pose-rig/poses.json, editable SVG strips, raster strips or individual composite
frames are present at b43f9d2. [Audit](audit.md) and [hashed artwork inventory](artwork-inventory.json)
record these distinctions instead of trusting filenames or newer timestamps.

Retained deliberately: canonical directions; deterministic root registration;
shared canvas raster baking/packing; review sheets; structural checks; cosmetic
hash isolation; immutable runtime sampling; atomic appearance loading; existing
direction/frame draw-order mechanism and legacy compile/load/draw interface.

Deprecated as production authority: analytic `pose_for(...)`, invented gait and
bone trajectories, independent action/frame/timing contracts, the 18-action
blueprint and old global release catalogue gate. These remain historical
engineering evidence. The old renderer protocol mixed costume and motion, so
its useful ideas were retained rather than importing that protocol.

Intentionally not reused: procedural SVG pixels/atlases, old invented animation
strips, whole-character subtraction as the new modular authoring strategy,
unapproved generated masters as approved source, empty atlases for absent parts,
or per-appearance body timing overrides. Historical art already on the clean
parent remains unchanged and is not consumed by the new proof build.

## RO1 evidence and unknowns

Fresh inspection covered RagnarokResearchLab ACT, SPR and timing notes;
RagnarokFileFormats ACT/SPR documentation; roBrowser Action/Sprite/EntityRender;
ActEditor direction selection and anchor drawing; zrenderer ACT and component
composition; ragassets ACT/composition/direction documentation. Pinned revisions,
URLs, source snapshot hashes and fact-level attribution are in the
[reference manifest](../../../authoring/characters/motion-templates/ro1-swordsman-male/reference-manifest.json)
and [research notes](../../../authoring/characters/motion-templates/ro1-swordsman-male/research-notes.md).

Established technical behavior:

- Action indexing `group * 8 + direction`; documented named order
  `S SW W NW N NE E SE`. Actual camera-relative selection remains client behavior.
- ACT has variable frame counts, ordered transformed layers, events, action
  interval floats and version-dependent attachment points. Layer transforms
  include offsets, mirror, tint, scale and rotation.
- SPR separates palette-indexed and truecolor imagery; indexed zero is
  transparent; 2.1 supports zero-run encoding. Truecolor uses ABGR in inspected
  parsers. No sprite pixels were downloaded, copied or committed.
- Body/head composition aligns parent/child ACT anchor0; this is not a set of
  named anatomical hand/foot sockets. Head/headgear standing slices can be head
  orientations rather than temporal breathing keys.
- Weapons and shields are separate components. Inspected clients put shield
  behind body at direction indices2..5. Garment/component ordering can depend on
  job, action, frame, priority and Lua/IMF rules. A fixed universal order is not
  established.
- Internal mirror support exists in ACT. Final ASTRAEON output forbids direction
  mirroring and requires eight authored/reviewed directions.

Unknown / not established: actual male Swordsman per-direction counts, delays,
gait/contact sequence, standing weight, sword attack group, anticipation/contact/
recovery poses, body/head/weapon/shield/garment/headgear trajectories and exact
job/action/frame order. Idle0..7 and Walk8..15 are documented **candidate** mappings;
the actual job files must confirm them. Attack may use groups5/10/11; source
revisions disagree about group12. No group was chosen arbitrarily.

Timing sources disagree: older community code multiplies stored interval by25ms;
ResearchLab documents24ms. Intake records raw values and requires an explicit
24/25 profile plus client-build provenance. No actual Swordsman duration is known.

`tools/extract_ro1_reference.py` inspects private ACT2.0–2.5 and SPR dimensions,
emits bounded numeric metadata/hash provenance, and emits no imagery. Synthetic
binary tests are not evidence of actual Swordsman motion. Unsupported/truncated
input rejects rather than guessing. It does not infer named actions, anatomy or
phase labels. A separate observed-pose annotation step remains necessary.
Private/raw paths and ACT/SPR files are ignored; runtime has no RO asset dependency.

## MotionTemplate and smoothing

[Architecture](../../CHARACTER_ASSEMBLY_V1.md), [motion schema](../../../authoring/characters/schemas/motion-template.schema.json),
[transform schema](../../../authoring/characters/schemas/attachment-transform.schema.json)
and [appearance schema](../../../authoring/characters/schemas/appearance-pack.schema.json)
define the new contracts.

Flow: private reference extraction → evidence/pose annotation → MotionTemplate
→ explicit pose/anchor/order timeline → replaceable ASTRAEON appearance packs
→ raster assembly → runtime composer. Costume artwork is absent from the motion
contract. The RO draft has empty actions, `REFERENCE_DATA_REQUIRED` and prohibited
runtime use; compiling it fails. Its status is deliberate, not a finished motion
template mislabeled as missing optional art.

RO keys must retain source hashes/action/frame/direction identity, orientation,
limb phase, contact intent, attack phase, silhouette, anchor/root metadata, event
metadata and landmark order/timestamps. Every expanded frame is `referenceKey`
or `astraeonInbetween`. In-betweens reference two neighboring key IDs and an
interval fraction; they cannot invent source phases or new visual event branches.
Last-to-first interpolation is permitted only for looping actions.

Smoothing uses an explicit insertion schedule per key interval. It subdivides
selected intervals, linearly interpolates position/scale and follows the shortest
rotation arc. It preserves positive integer timing, total duration and all key
timestamps; it never doubles every frame or action duration automatically. This
is an authoring aid, not a replacement for observing body poses or painting a
coherent strip. There is **no RO-to-expanded phase map yet** because actual keys
are missing. The synthetic proof demonstrates that such a map can be validated.
Foot planting and cloth follow-through in painted production remain unverified.

Gameplay remains downstream authority. Visual event data cannot call Combat or
apply damage. Presentation timing will need an explicit, reviewed mapping to
Combat once the actual reference action exists; it is not installed here.

## Layers, sampling, anchors and ordering

BodySpriteSet combines body, class/core clothing and boots. It is not dozens of
runtime armor pieces. Separate appearance slots support HeadBase, Hair, MainHand,
OffHand, Headgear, Garment, BackAccessory and CosmeticFX as appropriate.

Semantic layers: Shadow; GarmentBack; Body; HeadBase; HairBack; HairFront;
HeadgearLower/Middle/Top; MainHand; WeaponSlash; OffHand; GarmentFront;
BackAccessory; CosmeticFX. Optional absence is null, without empty atlases.

| Sampling mode | Implemented behavior | Dummy proof |
| --- | --- | --- |
| BODY_SYNC | Exact expanded body frame | Body and garment |
| PHASE_SYNC | Explicit normalized **time** thresholds | Three hair phase paintings versus nine Walk body frames |
| ANCHOR_HOLD | One/few authored direction views; optional phase view selection | Sword, shield, headgear |
| OWN_LOOP | Independent cosmetic clock/frame delays | Cosmetic loop |

Required anchors are root/head/mainHand/offHand/back/waist/footL/footR; weaponTip
and fxOrigin are optional. Every transform has finite x/y, clockwise radians and
positive uniform scale. Root equals the fixed registered root in every frame.
Small attachment raster cells use authored pivots and optional local transforms;
full canvas parts use shared registration. No runtime humanoid skeleton, vector
puppet or 3D character was introduced.

Resolved draw order: frame full override → frame named profile → direction named
profile → default profile. Profiles validate as permutations; absent layers are
filtered. GarmentBack/Front share one independent garment selection. No
`if class === "Swordsman"` branch is needed for the shared engine.

## Dummy assembly and reuse proof

Two DEV_ONLY packs use one synthetic MotionTemplate, with blue/coral body,
skin circle head, purple hair, red weapon, yellow offhand, cyan headgear, green
garment and a cosmetic loop. Sources bake to raster atlases; review uses the
actual runtime raster composer. Eight directions are explicit, with no mirroring.

Hair A→B, Weapon A→B, OffHand on→off, Headgear A→B/none and Garment on→off are
visibly different in **every** sampled direction/frame. The same Body references
and pixels remain unchanged; all unrelated layers remain identical. UI swaps at
Walk/SW/frame5 preserve action, direction, elapsed time and frame. The controller
has no movement/collision/targeting/gameplay state authority. Failed or superseded
preloads keep the prior complete appearance; retry works.

The second coral pack reuses all motion without an engine branch, and renders all
144 frames. Different Body/Hair/MainHand selections prove next-class appearance
reuse only; no Mage production artwork or class-specific motion is claimed.

Browser inspection initially found a fully occluded weapon swap at W/frame5.
The synthetic fixture's orientation range was corrected, then the whole matrix
passed. This was a debug fixture correction, not an invented production attack.

## ASTRAEON identity and production actions

Identity authority: unchanged repository-designated approved seed
`authoring/characters/gait-rig-v50/approved-warrior-seed.png`, SHA256
`750ffe25056760c6ab97c3e66a3488d15aec4c875e573d9a8cef65c8f0437e05`.
The reference copy is identical. Historical README/identity-lock documents that
designation; this task discovers no additional owner sign-off.

The eight painted neutral masters are historical first-party generated review
candidates, not owner-supplied by their actual provenance. Shared320px alpha
canvas, root convention, eight directions and uncropped edges pass read-only
structural verification. Same-person identity, proportions, costume/hair, camera,
sword dimensions, handedness and painterly fidelity need owner visual review.
They do not establish RO standing pose or a modular production BodySpriteSet.
No procedural Swordsman is used as the appearance authority.

See [1× identity comparison](identity/gameplay-1x.png), [2× comparison](identity/review-2x.png),
[diagnostic](identity/diagnostic.png), [provenance/verification](identity/identity-review.json)
and [blocked production build](../../../authoring/characters/builds/swordsman-male/build-manifest.json).

| Production action | RO reference keys | ASTRAEON in-betweens | Total frames / duration | Eight directions |
| --- | --- | --- | --- | --- |
| Idle | Unknown; none extracted | None produced | Unknown; 0 new production frames | Not built |
| Walk | Unknown; none extracted | None produced | Unknown; 0 new production frames | Not built |
| BasicAttack | Unknown; sword action unresolved | None produced | Unknown; 0 new production frames | Not built |

For comparison, the **synthetic engine fixture**, per direction:

| Fixture action | Synthetic keys (zero RO keys) | In-betweens | Total frames | Duration |
| --- | --- | --- | --- | --- |
| Idle | 2 | 2 | 4 | 600ms |
| Walk | 4 | 5 | 9 | 800ms |
| BasicAttack | 3 | 2 | 5 | 600ms |

All three fixture actions have eight directions. These counts are engineering
data only and must never seed the production Swordsman reference contract.
Painted default/alternate hair and weapons, production shield/headgear and cape
action variants were not generated. Their engine counterparts are debug assets.

## Browser, gameplay and visual evidence

[Browser report](browser/browser-report.json): 144 frames per pack, 864 visible
isolated swaps, 2,592 unchanged-pixel comparisons. UI frame preservation, speed,
direction rotation, layer toggles, unapproved-runtime rejection, failed preload,
retry and superseded preload pass. No unexpected HTTP or page errors; one
alternate-hair request was deliberately aborted for the failure test.

Captures: [desktop1360×1000](browser/desktop-review.png),
[phone portrait390×844](browser/mobile-390-844.png),
[phone landscape844×390](browser/mobile-844-390.png),
[second pack](browser/second-pack.png). Phone captures use Chromium viewport
emulation, not a physical phone or Safari. The diagnostic panel scrolls internally
on narrow screens; document width and 1× gameplay view remain usable.

Automatically generated contact sheets: [neutral eight directions](browser/neutral-eight-directions.png),
[Idle all directions](browser/Idle-eight-directions.png), sixteen per-direction
Walk/BasicAttack strips, [hairA/B](browser/hair-A-B.png), [weaponA/B](browser/weapon-A-B.png),
[offhand ordering](browser/offhand-ordering.png), [headgearA/B](browser/headgear-A-B.png),
[garment on/off](browser/garment-on-off.png), [decomposition](browser/layer-decomposition.png),
[key/in-between classification](browser/reference-key-vs-inbetween.png).
All animation images are explicitly labeled synthetic/DEV_ONLY.

1× debug rendering uses a70px body reference inside128px canvas; identity review
also includes gameplay scale. These prove registered raster composition, not
painted temporal quality. Actual painted production in-game captures for the
24 action/direction combinations cannot run before production actions exist.
No new art was installed into ordinary game boot.

The old `tests/modular_runtime_browser.py` fails at its default Create click:
the clean parent already lacks `assets/characters/swordsman-male-001/sprite.json`.
The default Swordsman creator is disabled. This is recorded, not hidden as PASS;
the old wardrobe also insists on an18-action catalogue, incompatible with this
three-action rescue's future opt-in. Neither is broadly rewritten or filled with
invented clips to make the gate pass.

The focused [ordinary-game report](ordinary-game/report.json) records that
baseline and checks existing normal Mage UI boot, movement, Combat attack,
unchanged appearance and offline reload after opening the new review page.
New motion/assembly modules are absent from game boot. DEV review metadata/
atlases use the existing service-worker bypass and do not enter gameplay caches.
Protected gameplay, map, world, Blender and boot paths are byte-unchanged from
the source checkpoint. See [default creator](ordinary-game/default-creator-baseline.png),
[normal Mage](ordinary-game/mage-normal-gameplay.png) and
[offline reload](ordinary-game/offline-after-character-review.png).

## Validation and acceptance gates

[Node report](node-checks/report.json): all222 tests pass, including87 new assembly
tests and135 existing motion, modular, locomotion, golden and world checks.
Ten Python tests pass for bounded ACT/SPR inspection, schemas, raster alpha,
registration and byte-deterministic rebuild. Browser evidence covers both dummy
packs plus isolated swaps; focused normal gameplay regression is separate.
[Coverage map](validation-coverage.md) explicitly separates engine checks from
blocked production-only assertions. Passing fixtures never certify artwork.

| Gate | Result |
| --- | --- |
| 0 | Research inventory complete; actual reference pose/timing manifest blocked |
| 1 | PASS, eight-direction dummy swaps/order/root/two-pack reuse |
| 2 | Preserved neutral candidate structural PASS; owner visual/RO standing review pending |
| 3 | BLOCKED, no actual Idle/Walk/BasicAttack production animation |
| 4 | NOT RUN for painted production; all variants pass debug assembly |
| 5 | Engine desktop/mobile review and ordinary Mage regression captured; production in-game capture blocked |

Reproduce locally (serve repository on8011 first):

```sh
python3 tools/build_assembly_debug.py
node --test tests/character_assembly.test.cjs
python3 -m unittest discover -s tests -p 'test_ro1_reference_intake.py'
python3 tools/run-node-checks.py --output /tmp/astraeon-node-checks
python3 tests/character_assembly_browser.py --output /tmp/astraeon-assembly-browser
python3 tests/character_assembly_game_regression.py --output /tmp/astraeon-assembly-game
python3 tools/review_character_identity.py
```

## Files and remaining work

Added engine modules, three JSON schemas, private reference inspector, reference
manifest/notes/blocked motion draft, two debug appearance packs, synthetic motion
and build manifests,23 debug raster atlases, debug bake tools, Node/Python/browser
tests, identity verifier/source record, blocked Swordsman build record, standalone
review page/script, architecture and audited visual/test evidence. Modified only
`.gitignore`, the optional runtime bridge in `modular-sprites.js`, and root
README/ARCHITECTURE/RAGNAROK_REFERENCE/CURRENT_HANDOFF documentation. Final
[changed-path inventory](changed-files.json) lists every added/modified path.

DEV_ONLY: every new debug atlas, appearance pack, synthetic key/action and related
contact sheet. Owner-review-required: preserved painted neutral comparison and
future painted output. No new production-approved or shipped appearance exists.

Known visual problems: production visual identity/choreography not validated;
hair/weapon alternates are only colored debug shapes; planted-foot/cloth motion,
alpha fringe, painterly detail at game scale and temporal flicker remain untested
for production. The neutral candidates are flattened historical paintings, not
new independent modular layers. Good structural registration is not art approval.

Known technical problems: default Swordsman creator missing asset and old
18-action wardrobe requirement predate this branch; no new ordinary-game
production adapter/install was attempted before the proof exists. ACT intake
does not convert image indices into anatomical pose guides automatically.
Observed annotation, root convention conversion, perspective-critical weapon
views and a Combat presentation adapter remain necessary after source intake.

Known reference uncertainties: selected client timing24/25, actual sword action
group and version-specific component priorities. No actual body/equipment
trajectories or source action counts have been measured.

Next necessary input is lawfully obtained **local** male Swordsman body/head/sword
ACT+SPR, identified client build, and weapon/action mapping; shield/garment/
headgear ACT plus priority rules help establish their relationships. Keep inputs
under ignored private paths. Inspect with the supplied numeric extractor, label
actual observed keys/contacts, and populate the template with evidence. The owner
must also review the preserved eight-view identity or provide the authoritative
replacement artwork. Continue coherent painted modular strips only after those
gates, then validate all swaps and capture the three actions in-game.

What must not expand before owner approval: production actions beyond Idle,
Walk and BasicAttack; full catalogues, advanced classes, final cosmetic catalogues
or gameplay gear authority. Never promote synthetic keys/procedural art to solve
the missing-reference gate. After the three-action proof receives owner approval,
complete the actual-reference RO core family first; ASTRAEON-only Run/Sprint/
Guard/Dash/Cast/Blink/Respawn extensions belong to a later approved phase.

This checkpoint does not claim a finished Swordsman or character catalogue.
