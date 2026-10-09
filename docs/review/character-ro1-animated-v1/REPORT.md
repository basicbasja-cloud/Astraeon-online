# ASTRAEON painted Swordsman animated rescue proof

**ENGINE PASS · STRUCTURAL PASS · ANIMATED ART PROOF CREATED · OWNER VISUAL APPROVAL PENDING**

Open [the owner preview GIF](swordsman-owner-preview.gif) to watch motion without
running tests. It plays Idle S, Walk S/SW/W/NW/N/NE/E/SE, then BasicAttack in the
same eight directions. The complete sequence lasts19.8 seconds and loops.

Serve the repository with `python -m http.server 8012`,
then open `http://localhost:8012/character-review.html`. Its default is painted
Swordsman, Walk S, playback ON. Hair, sword, shield, circlet, cape, speed and
scale controls are visible. Diagnostic anchors and layer controls are collapsed.
The standalone GIF/APNG files also open directly without an HTTP server.

## Checkpoint and scope

- Branch: `character/ro1-reference-engine-v1`.
- Starting branch: the same current local rescue branch.
- Starting HEAD: `b277ac8875063935969ee7c2f1cfcbd732c4d57d`.
- Starting status: clean.
- Final HEAD: see the final Git command transcript and final task response;
  `git rev-parse HEAD` identifies the commit containing this report.
- Historical `swordman` proof `b43f9d2ba5820f7b0ec48f137e1014fddd2e8442`
  and its direct parent `c258c5034a49462381d15f425f103eddf85242c9` remain intact.
  No reset, deletion, force push or remote publication.
- Only Idle, Walk and BasicAttack were produced. No extended catalogue.

The prior engine-only checkpoint's raw-ACT production stop was superseded by
the owner's explicit request. This checkpoint supplies actual painted raster
animations, an autoplay browser player, all-direction animated boards,
equipment variants and actual world screenshots.

## Existing pipeline audit and deliberate reuse

The [historical audit](../character-ro1-engine-v1/audit.md) records inspection of
the handoff, architecture, Ragnarok reference, modular runtime, Python authoring,
blueprints, rigs, generated atlases and tests before the initial rescue.

Retained: canonical directions; deterministic validation and registration;
numeric MotionTemplate separated from AppearancePack; raster atlas construction;
semantic slots; direction/frame draw profiles; optional absent layers; attachment
transforms; immutable sampling/controller; asynchronous atomic appearance loads;
service-worker development bypass; review and isolation checks. The existing
`modular-sprites.js` optional bridge and legacy API remain intact.

Deprecated as production motion authority: `pose_for(...)`, invented gait/bone
movement, custom release timings and the broad procedural clip catalogue.
Intentionally not reused as production art: procedural SVG bodies, dummy colors,
historical proof atlases and unapproved generated review art. Historical source
and evidence remain preserved. New art is explicitly owner-review-required.

## RO evidence and confidence

Primary visual source: public ragassets renderer,
`https://assets.latam-tools.com.br/image`. Acquisition parameters include
`job=1`, `gender=male`, `head=1`, `headdir=straight`, `weapon=2`; body/camera
registration is fixed for each board. Research images are ignored under
`authoring/characters/private-ro-reference/RO_REFERENCE/{idle,walk,attack,ready}/`.
Each board contains APNGs, decoded keys, strips, eight-direction sheets,
phase labels, pose guides and provenance. None of these RO pixels enters a
tracked production atlas or a runtime dependency.

Repository-safe evidence:

- `authoring/characters/motion-templates/ro1-swordsman-male/rendered-reference.json`
  records35 inspected sequences, source URLs, hashes, frame hashes, action IDs,
  renderer delays and confidence.
- `reference-manifest.json` distinguishes SOURCE-DERIVED, ASTRAEON INTERPRETATION
  and UNKNOWN. `research-notes.md` separates current acquisition from historical
  format-only research and superseded stop conditions.
- ActEditor documentation, Ragnarok ACT/SPR format documentation/Research Lab,
  ragassets/zrenderer and inspectable client code establish action/layer/anchor
  behavior. The pinned roBrowser commit is
  `e4b5b53aa1f8b7e429bfa987ab321c96502ba1da`.
- Client `WeaponType.js`: SWORD view2. `Jobs/WeaponAction.js`: Swordman sword
  selector1. `EntityAction.js`: selector1 → ATTACK2/group10 → actions80–87.

Inspected alternative attacks: group40 is the unarmed punch, group80 the selected
overhead/diagonal one-handed sword sweep, group88 a thrust and group96 the client
skill group. Group80 was chosen for the approved narrow one-handed sword, with
Ready actions32–39 supplying the recovery boundary. All eight directions of
Stand, Walk, selected Attack and Ready were inspected. Some neighboring RO
directions reuse rendered imagery; ASTRAEON has eight separate authored outputs.

| Observation | Evidence | Confidence / limit |
| --- | --- | --- |
| Stand actions0–7 | RENDERED_REFERENCE | HIGH; one unique stance per direction |
| Walk actions8–15,8 keys | RENDERED_REFERENCE | HIGH rendered phase sequence |
| Sword attack80–87,9 keys | RENDERED_REFERENCE | HIGH source imagery; MEDIUM anatomical retarget |
| Ready32–39 | RENDERED_REFERENCE | HIGH recovery boundary imagery |
| Walk75ms/key,600ms total | renderer-observed APNG | Not an exact ACT assertion |
| Attack100ms/key,900ms source | renderer-observed APNG | Not gameplay authority or exact ACT delay |
| Painted glove/head/cape transforms | ASTRAEON INTERPRETATION | MEDIUM; measured/retargeted on new artwork |
| Added poses and breathing | ASTRAEON_INBETWEEN | First-party refinement, not extra RO keys |
| Raw ACT intervals, original sockets/layer offsets | UNKNOWN | Raw male Swordsman ACT/SPR not inspected |

No source is classified ACT_EXTRACTED unless actual raw data supports it. No
claim of exact ACT attack timing. Client/version-specific equipment ordering,
foot-contact anatomy and pixel-perfect pose equivalence remain visual review
questions rather than fabricated extraction facts.

## Motion, smoothing and timing

The reusable `ro1-swordsman-male-v1` MotionTemplate has no costume artwork.
It supplies canonical S/SW/W/NW/N/NE/E/SE, root, anchors, pose intent, frame
classification, source identity, events, duration budgets and draw profiles.

| Action | Frames/direction | Duration | Reference keys | ASTRAEON in-betweens | Directions |
| --- | ---: | ---: | ---: | ---: | --- |
| Idle |9 |3000ms |2 |7 |8/8 |
| Walk |16 |600ms |8 |8 |8/8 |
| BasicAttack |16 |450ms |10 |6 |8/8 |

Idle's two landmarks reference the same unique standing pose; they are **not**
two distinct extracted breathing poses. Its seven refinements apply restrained
offline painted-raster breathing, with feet untouched, and small hair/cape follow.

Walk keys: passing-right-support → advance-left → contact-left → load-left →
passing-left-support → advance-right → contact-right → load-right. One authored
transition is inserted between each neighboring key, including loop closure.
Each75ms interval becomes38/37ms, preserving600ms total rather than slowing it.
The anatomical phase naming is a reviewed visual interpretation, not an ACT label.

Attack keys: raised ready → three preparation landmarks → weight commitment →
contact sweep → two follow-through landmarks → recovery intent → Ready return.
Expanded key indices are0,1,2,3,5,7,9,10,12,15. The9 source attack landmarks plus
the inspected Ready boundary have explicit source frame/action identity. Six
transitions refine acceleration, follow-through and recovery. The generator's
early cut was corrected at loaded key4; the incorrect overhead recovery tail was
replaced with a coherent overlapping chunk that settles at the waist.

450ms is a responsive **ASTRAEON presentation budget**, not the900ms renderer
duration relabeled as ACT timing. Key timestamps are0/20/40/60/80/170/220/250/280/370ms.
Presentation markers: attackAnticipation0ms, attackContact170ms,
attackRecovery250ms. They never execute damage or drive Combat. Existing Combat
remains downstream authority for eventual alignment.

Each in-between links valid neighboring reference-key IDs and an interval
fraction. Key order, pose metadata, total duration and timestamps validate.
The coherent painted strips are the body source, not procedural bone motion.
Authoring normalization uses one scale per strip and shared root registration;
overlap chunks convert source pixel units once from shared head landmarks and
retain frames8/9. No independently generated animation frames or runtime mirroring.

## Modular appearance and ordering

BodySpriteSet contains bald head/body, core class outfit, bronze shoulders,
waist details and boots. Painted hair, weapon, shield, circlet and cape are
independent raster sources. The body is reused unchanged by every appearance swap.

| Part | Sampling | Proof |
| --- | --- | --- |
| Body | BODY_SYNC |328 registered painted poses |
| Hair A / B | PHASE_SYNC | Silver tousled / silver side part with tied tuft; all3×8 |
| Sword A / B | ANCHOR_HOLD | Narrow steel/bronze default / broader alternate; all3×8 |
| OffHand | ANCHOR_HOLD | Teal/bronze shield on/off; no gameplay mechanics |
| Headgear | ANCHOR_HOLD | Independent circlet / None; not baked into hair |
| Cape | PHASE_SYNC | Rest/follow paintings sampled at four phase thresholds |
| Cosmetic loop | OWN_LOOP | Supported/tested engine mode; no new cosmetic catalogue |

Required anchors: root, head, mainHand, offHand, back, waist, footL, footR;
weaponTip and fxOrigin are also supplied. Transforms are x/y pixels, clockwise
radians and positive uniform scale. Root is always(160,264) on320×320, reference
height176. Optional absent layers need no empty atlases.

Semantic profiles cover Shadow, GarmentBack, Body, HeadBase, HairBack/Front,
HeadgearLower/Middle/Top, MainHand, WeaponSlash, OffHand, GarmentFront,
BackAccessory and CosmeticFX; unused layers are filtered. Resolution is frame
override → direction override → default. Front/rear/loaded/rear-loaded/rear-strike
profiles are declarative. Rear cape stays over the back torso throughout; the
sword crosses the cape at contact/follow-through for readability. East cape
stays behind the visible face/torso. These are explicit ASTRAEON retargeting
decisions, not claimed exact ACT layer lists.

Hair/weapon/shield/circlet/cape swaps preserve action, clock, frame and unrelated
layer identities/pixels. An atomic loading delay can occur for uncached options;
body animation continues. No movement, collision, targeting or equipment authority
changes. A second DEV_ONLY blue-body pack with Hair B/Sword B uses the exact same
actual MotionTemplate; its exported animation demonstrates reuse without a
Swordsman-specific engine branch.

## Visual identity and review evidence

Identity source: `authoring/characters/gait-rig-v50/approved-warrior-seed.png`,
SHA256 `750ffe25056760c6ab97c3e66a3488d15aec4c875e573d9a8cef65c8f0437e05`.
The repository-designated owner-approved seed governs youthful proportions,
silver/lavender hair, bronze/ivory/navy outfit, teal waist, gold cape, boots,
narrow steel/bronze sword and painted rendering. Historical masters supply
orientation context, not automatic approval. New artwork is not promoted to
approved simply because its seed was approved.

Eight-direction identity turnaround: structural pass; visual owner approval
pending. [Compare the seed and turnaround](contact-sheets/approved-seed-vs-painted-turnaround.png).
Large and1×/2× reviews inspected all directions, key sequences, alpha/crop,
head/hair coverage, handedness, body/weapon relationship and recovery. Wrong
NW/SW/SE walk facing, cross-cell debris, partial scalp measurement, recovery
scale and equipment ordering were repaired rather than accepted as final defects.

Exact artifacts (relative to repository root):

- `docs/review/character-ro1-animated-v1/swordsman-owner-preview.gif`
- `docs/review/character-ro1-animated-v1/previews/Idle-eight-directions.gif`
- `docs/review/character-ro1-animated-v1/previews/Walk-eight-directions.gif`
- `docs/review/character-ro1-animated-v1/previews/BasicAttack-eight-directions.gif`
- `docs/review/character-ro1-animated-v1/previews/{Action}-{Direction}.apng`
  and matching GIFs for all24 action/direction pairs.
- `docs/review/character-ro1-animated-v1/previews/{Action}-alternate-equipped-eight-directions.gif`
  supplies Hair B/Sword B/shield/circlet/cape for all three actions.
- `docs/review/character-ro1-animated-v1/previews/second-pack-reuse-eight-directions.gif`
- `character-review.html` and `character-gameplay-review.html`.
- `docs/review/character-ro1-animated-v1/strips/{Action}-{Direction}.png`
- `docs/review/character-ro1-animated-v1/contact-sheets/`: neutral turnaround,
  all3 action boards, keys/in-betweens,1× gameplay, Hair A/B, Sword A/B,
  shield order, circlet, cape, layer decomposition and second-pack reuse.
- `docs/review/character-ro1-animated-v1/screenshots/desktop-autoplay-walk.png`
  and `desktop-{Action}-SE.png`; `mobile-autoplay-walk.png`.
- `docs/review/character-ro1-animated-v1/gameplay/{Action}-{Direction}.png`
  for all24 actual world states, `all-actions-eight-directions-gameplay.png`,
  `appearance-swaps-in-world.png`, `ordinary-movement-with-painted-proof.png`,
  and `mobile-in-world.png`.
- `docs/review/character-ro1-animated-v1/gameplay/BasicAttack-contact-{Direction}.png`
  and `BasicAttack-contact-eight-directions.png` inspect exact contact key7 in
  the actual world, without executing Combat or changing gameplay time.

APNG preserves exact millisecond subdivisions and transparent alpha. GIF rounds
cumulative centiseconds; identical adjacent pictures may coalesce while preserving
duration. Source frame counts/classification remain in the MotionTemplate.
PNG frame scratch exports are ignored/reproducible; owner movies, strips, boards
and captures are tracked. No RO research imagery is included in those artifacts.

## Browser/gameplay boundary and limitations

The DEV_ONLY world review runs the unchanged actual game through an isolated
in-memory save. Existing Mage mechanics supply boot/movement/Combat; only the
player presentation callback composes the painted Swordsman. It never writes
the owner's stored character. Actual WebGL world screenshots, including mobile,
were captured and inspected, rather than inferred from DOM assertions.
Proof action/direction selectors are independent of gameplay dispatch. Exact
frame inspection freezes presentation only; normal review defaults to playback.

This is not installation into the ordinary selectable Swordsman catalogue.
The clean parent already lacks `assets/characters/swordsman-male-001/sprite.json`;
the legacy wardrobe also expects a broader action family. That preexisting
creator failure was recorded. The new proof does not invent those actions to
silence the old catalogue contract. Normal Mage boot/movement/attack, Combat,
offline service-worker boot and visual-cache isolation pass.

Headless SwiftShader world playback is slow on this large existing town scene;
captures prove composition, not physical-device frame-rate quality. The isolated
review player and GIF/APNG exports provide a direct, responsive way to judge
the full cycles. Physical iPhone Safari and owner device playback are unverified.

Known visual review questions: exact seed face/fringe likeness and ornamental
detail density; continuity of painted costume details across source strips;
contact-foot skating at owner gameplay speed; reduced-phase cape/hair follow;
whether every painted attack silhouette adequately matches the rendered key.
These are owner acceptance questions, not an automatic production approval.
There are no accepted cropped default/equipped frames or missing atlas references.

## Validation and reproduction

- JavaScript suite: current final count is recorded in `validation.json`; all
  MotionTemplate/assembly, old movement/Combat/world and new painted checks pass.
- Python:15 passed (reference parser/schema/intake plus real RGBA atlas,
  registration, shared-scale, identity-source and eight authored view checks).
- Browser composer: all3 actions visibly change pixels;328 default poses
  uncropped;1,640 appearance swaps leave unrelated raster pixels unchanged.
- Equipped composer:328 Hair B/Sword B/shield/circlet/cape poses uncropped.
- World review:24 actual desktop states plus8 exact-contact captures, mobile capture, appearance mechanics
  isolation, normal movement and unchanged owner storage.
- Protected gameplay/world paths unchanged against the historical clean parent.
- Engine and structural tests cannot approve artwork. All new painted assets
  remain REQUIRES_OWNER_VISUAL_REVIEW; dummy reuse assets remain DEV_ONLY.

Commands from repository root:

```sh
python tools/build_painted_swordsman.py
node --test tests/*.test.cjs tests/*.test.mjs
python -m unittest discover -s tests -p 'test_*py'
python -m http.server 8012
# In another terminal:
python tools/export_swordsman_review.py --url http://localhost:8012
python tools/export_swordsman_variants.py --url http://localhost:8012
python tests/swordsman_painted_browser.py --url http://localhost:8012
python tests/character_assembly_game_regression.py --url http://localhost:8012 --output /tmp/astraeon-normal-game
```

Do not rebuild atlases while browser/raster tests read them. Reference acquisition
is a separate optional research step; the painted build/runtime needs no private
RO assets. Inspect `browser-review.json`, `variant-review.json`,
`gameplay/browser-review.json` and `gameplay-regression/report.json` for evidence.

Files added: coherent painted source canvases/provenance, independent appearance
pack/second dummy pack, painted atlases, normalization/calibration/compiler,
exporters, autoplay/world review pages and presentation scripts, raster/painted
browser/engine tests, animated/contact/capture evidence and this report.
Files modified: RO motion evidence/schema/validator/template/manifests,
character review page, historical fixture test URL, README/architecture/handoff/
reference/engine documentation, ignore rules. No world, Blender, terrain,
buildings, lighting, economy, inventory or Combat authority rewrite.

**STOP.** Do not expand Run/Sprint/Guard/Dash/Hit/Death/Cast/Pickup/Interact/
Respawn or skills. Recommended next action: owner watches the GIF/player and
approves or requests bounded repairs to identity, gait, sword arc and layering
in these three actions. Further action families require separate owner approval.
The Swordsman and character catalogue are not claimed fully finished.
