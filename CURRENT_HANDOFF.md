# Current character checkpoint: BasicAttack painted-arm anatomy repair

Continue `character/ro1-reference-engine-v1` from the commit containing this handoff. Starting checkpoint was `e0886e419212586161cd778d53e665a170a8f181`. The new review candidate surgically replaces 55 attack arm cells and retains 73. It repairs the SW/W/NW priority chain, NE6 extra/floating-arm issue and SW6 skull overlap, then registers the owned swords to the painted palms. No MotionTemplate, engine, ordinary gameplay, Head, Hair or Cape change. Costume A/B share the same anatomy/timeline/attachments. The requested sprite-gen skill is installed locally and supplies independent motion inspection; see its pinned receipt in the report.

Open [character-review.html](character-review.html) for clean BasicAttack autoplay, frame stepping, visibility toggles and optional joint/anchor overlays. [New report and all owner evidence](docs/review/character-basicattack-anatomy-repair-v1/REPORT.md). [Focused normal/half-speed GIF](docs/review/character-basicattack-anatomy-repair-v1/swordsman-basicattack-anatomy-repair-owner-preview.gif). Original pack remains selectable with `?registration=1`; previous evidence is intact. Tests: 303 JavaScript and 29 Python, plus 128 attack browser captures, 328 independent-layer swap checks and 200 unchanged Idle/Walk captures. Recovery13→14 remains brisk; retained torso/stance changes at15→0 and slow-view paint seams still require review. **OWNER VISUAL APPROVAL PENDING.** Do not expand actions or treat numeric checks as visual approval.

# Previous character checkpoint: dressed-body registration repair

Continue branch `character/ro1-reference-engine-v1`. The owner selected BodyWithOutfit + independent Head; separate BodyCore/Outfit is superseded. The new strict appearance pack reuses all painted source frames, extracts the existing Head pixels, and repairs skull/grip/shoulder registration. MotionTemplate and ordinary gameplay remain unchanged. Royal body B proves same-time costume swaps. The latest sword-alignment revision adds six weapon perspective phases, corrects the SW/W/NW blade arc, and reuses five bounded existing body poses for strike/held-fist continuity. Earlier rejected candidates are preserved. Open `character-review.html` for clean autoplay and development diagnostics. See [new animated review package](docs/review/character-bodywithoutfit-registration-v1/registration-report.md). **OWNER VISUAL APPROVAL PENDING**. The old animated proof is preserved as rejected evidence.

# ASTRAEON — animated character rescue checkpoint,9October2026

Branch `character/ro1-reference-engine-v1`; starting checkpoint
`b277ac8875063935969ee7c2f1cfcbd732c4d57d`. Historical proof on `origin/swordman`
`b43f9d2ba5820f7b0ec48f137e1014fddd2e8442` remains preserved. No World, map,
Blender, lighting, gameplay or Combat source changes are authorized here.

The owner reported that engineering alone did not show animation and superseded
raw-ACT-only gating. The active proof contains real painted ASTRAEON Swordsman
Idle, Walk and BasicAttack in eight authored directions, with independent Hair
A/B, Sword A/B, shield, circlet and cape. [Watch the owner GIF](docs/review/character-ro1-animated-v1/swordsman-owner-preview.gif).
[Autoplay player](character-review.html) defaults to Walk/S, overlays off.
[Report](docs/review/character-ro1-animated-v1/REPORT.md) records review and limits.

RO motion evidence is RENDERED_REFERENCE through public ragassets, with pinned
Swordman SWORD mapping selecting attack group80. Exact ACT delays are UNKNOWN.
Walk has8keys+8in-betweens/600ms. Attack has9attack keys+1Ready boundary+
6in-betweens/450ms. Idle uses one observed standing pose repeated at two cycle
boundaries, plus7ASTRAEON breathing refinements/3000ms. No RO imagery is shipped.
Private research boards remain ignored. Do not resume `pose_for` as authority.

Body is painted raster; hair, sword, shield, circlet and cape stay separate.
Root/head registration, diagonal facing and attack recovery were repaired from
visual captures. [In-world review](character-gameplay-review.html) loads the
unchanged actual world with an isolated memory save, existing Mage mechanics
and a presentation-only Swordsman override. Ordinary game boot remains unchanged.
The old selectable Swordsman still lacks `swordsman-male-001/sprite.json`; do not
invent18actions to satisfy the old wardrobe contract. Its repair is downstream.

ENGINE PASS / STRUCTURAL PASS / ANIMATED ART PROOF CREATED /
OWNER VISUAL APPROVAL PENDING. Structural tests do not approve identity or motion
fidelity. No Run, Sprint, Guard, Dash, Hit, Death, Cast, Pickup or wider catalogue
expansion before owner visual approval. Review the animations first.

Verified:257 JavaScript tests,15 Python tests,328 default and328 fully equipped
uncropped browser composites,1,640 isolated raster swaps,24 desktop world states,
8 exact attack-contact world captures, desktop/mobile player and world captures.
Normal Mage movement/Combat/offline regression passes. Headless software world
capture does not certify physical-device performance. The owner GIF runs19.8s;
APNGs preserve exact millisecond timings and transparent alpha.

---

# Historical World handoff — preserved, outside this branch's task

# ASTRAEON — Wayfarer capital, verified art checkpoint v83

## Current verified checkpoint — layered painted crowns v83, 8 October 2026

Original World task ACTIVE. Same branch: codex/world-pipeline-v3-proof.
Verified v82 checkpoint 2932d57 is preserved, with complete native/JSON backup
at /tmp/astraeon-before-layered-crowns-v83/.
Source SHA256: 63e757ec6df1f533c77f0b8c2acf93da49cd3b3bf1a0fa5433d3bea953c304b3
Native SHA256: 686908bb25b4a25454108c588189485a01595e0b6076fb378a234057ed06d496
Cache 98, generation wayfarer-63e757ec6df1. Camera pitch 45 / yaw 35 / zoom 135 / FOV 15.

Eighteen selected plaza, avenue and river trees have fuller layered middle crowns,
three profiles and bounded uneven branch tips. Six candidates were rejected for
insufficient roof clearance. Only existing leaf X/Y coordinates changed. Every
leaf Z coordinate, face, UV corner, material and full painted foliage image is
retained. Lower boughs below 2.4m never expand into walking space. Each selected
crown remains 90 boughs / 720 triangles. Actual roof clearance is at least 0.48m;
crowns remain separate from neighboring trees. All roots/trunks/collision/tree
positions, 45,996 other parts, terrain/navigation/services/gameplay and original
37 houses are preserved. No added triangles, foliage textures or material variants.

All 13 native stages, 96 Node tests, five streaming tests, eight normal gameplay
captures, camera controls, WebKit touch traversal, cache/offline/save recovery and
ordinary field return PASS. Captures have zero errors or missing culling pixels.
Exact transport retains 965,811 authored draw triangles / 34,841,100 attributes,
75 chunks, 26,457,882 compressed bytes. Full fresh 4096 ground lighting
retains original alpha and eight sun/four contact samples. Emulated cold
16755.05 ms / warm 10298.94 ms; 34 unloads / 23 reloads.
Physical iPhone Safari PENDING. All eight city views and mobile warm/offline/
return images were manually reviewed against supplied RO3 gate 04:25 and house
01:40 frames; see the visual review for actual observations and limitations.

Native parity first exhausted the 8GiB memory limit while retaining duplicate
expanded worlds (exit -9). Diagnostic logs/progress are preserved. The checker
now compares sequential canonical full-value hashes and retains only the moved
Hall/court for the unsaved transform and stale-shadow test. The revised check
passed without rerunning authoring or lighting, and without quality cuts.

Full RO3 visual acceptance remains OPEN. Next original World action: address
remaining blank/repeated side and gable panels on selected new houses around the
inward-facing courts, using distinct owned frontage details and original painted
materials. Preserve original 37 houses, actual doors/uses/routes and the verified
roof forms/planting/camera. The plainer river crown/water remain on the art backlog.
Do not widen the six rejected trees into their roof envelopes.

Evidence: docs/review/wayfarer-capital-v83/checkpoint.json, layered-crowns/
visual-review.json and placement-plan.svg. The comparison page opens the v83
plaza beside the supplied RO3 gate frame. The one-shot author
tools/author-capital-layered-crowns-v83.py is APPLIED, with saved
capital_layered_crowns_v83=1. DO NOT rerun it or older
applied authors. No native/browser review jobs remain running after the final
seal. Preserve all diagnostic evidence and the v82 backup; do not reset, clean,
stash, discard, rebase, force-push or switch the working branch.

## Previous verified checkpoint — grounded frontages v82, 8 October 2026

Original World task ACTIVE. Same branch: codex/world-pipeline-v3-proof.
v80 and v81 were verified, manually reviewed and pushed as 0cc347f and 602c4fc.
Source SHA256: 3afd9c05c50595d5886b4b7f77b6fc43c12a1d227573bbb56821199bd2612382
Native SHA256: 4d09046b70ffd1e613bdaa977b020af414defc458a816d396623ff97b953cb0e
Cache 97, generation wayfarer-3afd9c05c505. Camera pitch 45 / yaw 35 / zoom 135 / FOV 15.

Twelve selected new houses retain their four distinct roof forms and gain 21
closed ground-side windows, real pale frames/reveals/sills and lower timber ties.
Closed glazing sits outside retained wall cores; these are not pierced ground
apertures. Six measured safe private-path drainage grates add small street
infrastructure. The first plan found six safe contacts rather than an arbitrary
12; no green, door, road, route or service clearance guard was relaxed.
All 904 original opaque bank faces gain continuous physical-station UVs and the
existing full city masonry image with quieter material variants. No new texture
images/materials, bank geometry, or texture-resolution cuts. Net +3,240 visible
triangles. All 45,723 old parts retained; original cores/roofs/doors/uses/terrain/
collision/navigation/gameplay preserved. The original 37 houses remain intact.

All 13 native stages, 96 Node tests, five streaming tests, eight normal gameplay
captures, camera controls, WebKit touch traversal, cache/offline/save recovery and
ordinary field return PASS. All captures have zero errors and missing culling
pixels. Exact transport: 965,811 authored draw triangles,
34,841,100 attribute values, 75 chunks, 26,452,383 compressed bytes.
Full fresh 4096 ground lighting retains original alpha and eight sun/four contact
samples. Emulated cold 18431.25 ms / warm 11894.65 ms;
34 unloads / 23 reloads. Physical iPhone Safari PENDING.
All eight city images and mobile warm/offline/return images manually inspected
against the supplied RO3 house 03:35 and gate 04:25 frames. Side windows visibly
occupy the blank walls; bank masonry now connects to the city's material language.

Full RO3 visual acceptance remains OPEN: some other new-house side/gable panels
repeat or remain blank, formal tree silhouettes need closer layered-crown work,
and the river crown/water are plainer than city frontage. Next original World
action: compare selected formal tree crowns at matching actor scale against RO3
gate frames, then author layered branch silhouettes inside safe root/roof envelopes
using the existing full-resolution painted foliage. Retain the unique house forms,
planting, camera and gameplay; require fresh full lighting and ordinary captures.
Court-side and river-crown gaps remain on the subsequent original art backlog.

Evidence: docs/review/wayfarer-capital-v82/checkpoint.json, grounded-frontages/
visual-review.json and placement-plan.svg. The comparison page opens current v82.
One-shot author-capital-grounded-frontages-v82.py is APPLIED; native flag
capital_grounded_frontages_v82=1. DO NOT rerun it or older applied authors.
No native/browser review jobs remain running after the final seal. Preserve
/tmp/astraeon-before-grounded-frontages-v82/ and all diagnostic evidence. Do not
reset, clean, stash, discard, rebase, force-push or switch the working branch.

## Previous verified checkpoint — occupied windows / natural edges v81, 8 October 2026

Original World task ACTIVE. Same working branch codex/world-pipeline-v3-proof.
SourceSHA256:01983f97781fb1f6d02bebda134a33d678ff75102d0a99b04e2b218bf0b74207.
NativeSHA256:4af92fcb4edcf991f2f351da27669692ab528fbbb8f780f3b79708e22566bba1.
Cache96, generation wayfarer-01983f97781f. Camera45/35/135/FOV15 retained.
142 pierced upper openings on12 distinct new houses have wider glazing, pale
frames and quieter blue glass.25 connected soft property-path green patches
add25.131m² and2141 triangles, no new image assets. Original roof forms,37 old
houses, old ground uses/doors/solids/terrain/navigation/gameplay remain exact.
One-shot author-capital-property-life-v81.py is APPLIED; DO NOT rerun.

All13 native stages /96 Node tests /5 streaming tests /8 ordinary captures with
zero errors or missing culling pixels /camera /WebKit /cache-offline /field-return
PASS. Source transport has962,571 authored draw triangles /34,724,460 attributes,
75 chunks,26,374,440 compressed bytes. Full fresh4096 ground shade with original
alpha and8sun/4contact samples. Emulated cold17788.67ms/warm11086.55ms,
34 unloads/23reloads, no monolithic boot or errors. Physical iPhone Safari PENDING.
All8 city views and3 mobile/offline/return images manually inspected against
RO3 house01:40/03:35 and gate01:00/04:25. Windows and green ingress visibly improve.

Native author first hit memory exhaustion before saving; original v80 native/
source SHA was verified unchanged. Candidate author now uses compact sealed
fingerprints instead of two live worlds. Foliage saved full shade then hit a
second duplicate-export memory peak; its full rerun PASS after releasing completed
world/ray buffers. Exporter now reads UV/light corners once, with exact native/
source preservation proved. Failed logs remain; no image/sample/quality cuts.

Evidence:docs/review/wayfarer-capital-v81/checkpoint.json and property-life/
visual-review.json. No native/browser jobs remain running. Full RO3 acceptance
remains OPEN. Exact next original World action: v82 planned occupied closed west
side glazing/timber on selected new houses, real private-path drains, continuous
shared city masonry on existing opaque river bank. The scoped v82 pass was
subsequently applied and verified; see the current checkpoint above. Its native
flag guards the one-shot author.
Do not shortcut bakes or alter original house layouts to meet the reference.

Pre-v81 full backup:/tmp/astraeon-before-property-life-v81/; v80 pushed checkpoint
0cc347f is preserved. Original art work continues immediately from this result.

## Previous verified checkpoint — original neighborhoods v80, 7 October 2026

Same working branch codex/world-pipeline-v3-proof. Original World art task ACTIVE;
full RO3 visual acceptance remains OPEN. Do not reset/discard existing work.
SourceSHA256:b999c59228786b93f4f6be9c5836f24cb38e108c7c1bd60000cab11414236f85.
NativeSHA256:77f5a7e0c89a18032f08443d881a2b8047f1c569d8779c2a5455ecbea2f8e5ee.
Cache95, immutable generation wayfarer-b999c5922878. Camera45/35/135/FOV15.

Recovered v79 now applied and verified:280.056m² extra owned green,168 sparse
three-blade roots,16 formal crown variants, full1254² original painted foliage,
warmer clay. Twelve new houses have four actual roof/massing designs, and ten
unequal-spaced owned garden trees bring total94. All37 original assemblies,
old doors/solids/terrain/nav/gameplay, original84 tree contacts, and retained
new-house ground uses remain exact. Net v80 addition16,906 visible triangles.
Do NOT rerun one-shot author/partition/dormer corrections; their saved flags
are applied. All8 new dormer windows clear actual main roofs by at least11.5cm.

All13 native stages,96 existing Node tests,5 streaming tests,8 ordinary gameplay
captures/culling comparisons and camera controls PASS. Exact transport preserves
960,430 authored draw triangles /34,640,961 attributes;75 chunks,24 active images.
Full fresh4096 floor light was baked with8 sun+4 contact samples and full original
alpha. Compact independently verified v79 baseline makes declared delta repeatable.
Mobile WebKit iPhone13 emulation cold15079.30ms/warm12873.50ms,34 unloads/23 reloads;
no monolithic load or browser errors. Cache95 migration/offline original4096 floor,
save/progression retention and ordinary touch field-return PASS. Physical iPhone
Safari remains PENDING. No native/browser jobs remain running.

Evidence:docs/review/wayfarer-capital-v80/checkpoint.json and unique-neighborhoods/
visual-review.json. Eight actual city scene captures and mobile/offline/return
images were manually inspected against RO3 house01:40/03:35 and street00:50.
This is a verified improvement, not complete RO3 art acceptance. Next original
World action: larger upper glazing proportions and varied facade detail on
selected new houses, plus connected planted ingress along real property edges.
Keep clear2.2m door approaches, public streets, uses and closed patrols. Do not
randomly rotate every building or scatter props as a substitute for architecture.
Keep authoring/native/source/light/stream/cache/evidence synchronized.

Full pre-v80 v79 backup:/tmp/astraeon-before-unique-homes-v80/; pushed v78 backup:
/tmp/astraeon-before-painted-landscape-v79/. Earlier checkpoints preserved below.

## Current verified checkpoint — selected frontage placement v78, 7 October2026

Same working branch codex/world-pipeline-v3-proof. Starting checkpoint3cc2c65
remains preserved. The original World art task is ACTIVE; do not stop at this
checkpoint. Full RO3 visual baseline remains OPEN.

Current sourceSHA256:67c6ff1f94bdaaa8a278437306beab0b3d94026a106b77e436f93b660dba57d9.
NativeSHA256:58a7b8c5519f37a1edb284404dd5cf6bd520313788db898c2997614c3491af4a.
Boot/cache94, immutable generationwayfarer-67c6ff1f94bd.
Nineteen actual owned fronts now have deliberately selected entry-gable, garden-
hip, eave-gallery or artisan lean-to roofs, braces, blue/gold lamps and elevated
herb pots. Two other plaza candidates were rejected for existing use conflicts.
Added4,659 native triangles and38 slender collision posts, all outside2.2m door
approaches and public roads. Original parts/solids/doors/gameplay/terrain are
exact, except explicitly enlarged clay roof UVs2.4→3.4; original images/resolution
remain byte-exact. Source74 preservation allows only that declared UV multiplier
and still checks every original vertex/face and other UV.

All11 native pipeline stages and96 individual Node tests PASS; full fresh4096
ground bake also proves the repaired low-memory baker completed normally.
Exact stream conversion PASS:935,370 authored draw triangles and33,715,851
attribute values,75 chunks/24 active images. Five streaming tests PASS.
Eight normal910×512 gameplay views each have0errors and0changed pixels between
ordinary/exhaustive culling. Three ordinary-control camera studies are saved.
WebKit iPhone13 emulation cold21322.06ms /warm10883.48ms,
34unloads/23reloads, no monolithic boot, no visible missing chunks, duplicate
geometry or blocked ordinary touch traversal. Physical iPhone Safari PENDING.
Final cache/offline/field tests must be repeated on the upcoming current art
source; v77 has prior verified results.

Evidence:docs/review/wayfarer-capital-v78/checkpoint.json;frontage-placement/
contains all native/bake/delta checks, owned-frontage-plan.svg, eight views and
visual-review.json. Mobile evidence ismobile-streaming/ordinary-touch-v78/.

Exact next original World action: use the reviewed camera candidate45°pitch /
35°yaw /135distance /FOV15. It reveals front entrances/corners and adjacent
properties, with more reference-like character framing. Do NOT blindly resize
the entire map: local street/character proportions are plausible, global RO3
dimensions are not established. Private paved aprons still have overly thin
planted bands in artisan/merchant shots. The next v79 scripts propose bounded
95cm inward growth of selected actual owned lawns, preserving paved doors/work
bays/courts/closed routes, sparse new edge blades and16 formal park crown
variants. New foliage candidate authoring/materials/wayfarer-conifer-v79-source.png
is original host-native ImageGen art; its1254² RGBA lossless export is exact,
alpha coverage.58367, original v70 source preserved. Candidate is NOT YET
adopted in the runtime. Its provenance/prompt and draft v79 scripts are untracked
continuation work and must be preserved. Do not rerun v78 one-shot author.
Rebuild foliage/4096 floor light after v79 adoption, independent declared delta,
native parity, exact stream/cache and normal gameplay/mobile before acceptance.


## Current verified checkpoint — street depth v77, 7 October 2026

User requests larger, quieter paving and RO3 painted architectural character in
Astraeon's own theme. This pass is complete and verified; full RO3 visual baseline
is still NOT MET. Preserve this work. Recovery checkpoint4f6b275 was pushed before
this pass. The same working branch remains codex/world-pipeline-v3-proof.

Current sourceSHA256:461fc1142ab22989a3f8d3f3281924eebf7a0b5b714c110e7553c09ad2025275.
NativeSHA256:9d109706c685e9a26b2d02f2ac218b9c493868aed34f4a5cebf8a0e35bfa84e3.
Default/cache version93; immutable streamed generationwayfarer-461fc1142ab2.
Paving is1.8× larger (native repeat5.76 vs3.2) with.58 grain contrast. Wall/clay
roof grain is.56 and recessed glazing is deeper blue. Original image bytes and
resolution remain intact. Six original tree/seat parklets add5,640 visible
triangles, no additional image assets.398 joint tufts align with the enlarged real
painted cracks; two without a suitable local crack were removed, all800 lawn
tufts remain. All original building geometry, colliders, services, portals and the28
original residents are exact. One of the8 plaza citizens has a declared small
closing-leg turn around the southwest seat; total residents remain36.

All native/light/delta/architecture/assembly/density/traversal/schema checks pass,
as do96 individual existing Node tests and5 streaming contract tests. All26
destinations are reachable and36 closed patrol loops have zero blocked samples.
Exact transport verifies930,711 authored draw triangles /33,548,127 attributes
and73,728 collision/elevation samples.75 chunks,24 static images, compressed
geometry25,409,430B, decoded111,030,012B. Four source-matched gameplay views have
zero browser errors and zero pixel changes with ordinary vs exhaustive culling.

Current mobile WebKit: cold20,729.35ms /warm11,661.58ms,34 unloads /23 reloads;
no full-world boot request, missing visible chunks, duplicate geometry or blocked
player. Native full4096 ground atlas is verified offline and saved character
survives cache migration/reload. Ordinary touch field entry releases all city
geometry and returns/reloads correctly. Physical iPhone Safari remains PENDING.
Public Pages was observed atversion92 before this new checkpoint push; do not
assume93 deployed solely from a successful branch push.

Evidence: docs/review/wayfarer-capital-v77/checkpoint.json;street-depth/ contains
all bakes/checks, preserved failed logs, exact fixes, four view PNGs and
visual-review.json. Ground save hit memory exhaustion during final JSON export,
after the image/native metadata were saved. The recovered atlas is byte-exact
SHA91b133d6441f2fcd3f70d50919065a4567ee87bf8addc1431225347263b05342 and digest
bdb1e2bdfde4a46bb18890669939598391054a19fdeea2865f5d0af45ab400f1. The baker now
uses a Float32 buffer and frees duplicate world/ray data. The new field test
uses ordinary on-screen approach steps for the closer camera. Neither fix
lowers production art quality.

Exact next original World action: audit character-relative roof, window, door
and street proportions against RO3 house01:40/03:35 and street00:50. Work on
frontage-riverside[70.5898,200.3634],north-garden-house[88.54,199.0227] and nearby
capital-townhouse-083/-085/-089. The west street still repeats tall gable masses;
plan original contrasting roof/frontage silhouettes and meaningful owned use
areas, preserving road/entrance clearances. Do not substitute more scattered
NPCs or claim baseline met from counts. Whole-city resizing remains authorized
when paired image evidence warrants it; do not blindly scale from a crop.
Do not rerun one-shot author/visitor scripts. Read actual Git/status before
resuming; archived v76 evidence remains tied to its prior source hashes.

## Latest visual feedback — 7 October 2026

The user rejects the current flat, soulless feel versus RO3. Camera, warmer
paving, grass and eight citizens are a verified checkpoint, not visual acceptance.
Next original World work must address street-scale layering, meaningful owned
frontage/feature areas, facade/window depth, stronger light-plane contrast and
canopy/contact shadows. Compare specific RO3 scenes and create a bounded native
street-detail pass; do not substitute additional scattered people for this work.
Whole-city resizing remains authorized. Preserve the existing checkpoint before
new native changes and keep the source/lighting/streamed transport synchronized.

## Current state — RO3 refinement resumed, 7 October 2026

This section supersedes the historical recovery/resume instructions below.
Branch: codex/world-pipeline-v3-proof. Existing mobile gate passed on the preceding
city; physical iPhone Safari remains PENDING. Original World work has resumed.

Second plaza inset is APPLIED: four whole fronts16 units inward total, joined
terraces/curbs and all entrances preserved. Rounded planting contacts were
retessellated within the unchanged12,500 guard. Current93 lawns use14,177
triangles, including8,386 feather triangles. Native warmer stone/neutral shadow
lighting, original-image lawn normalization and1,200 small grounded grass tufts
are authored and checked. The new gameplay camera is45°/10°/110, FOV15, selected
from fresh ordinary-control paired studies. Eight original plaza citizens were
added; all28 existing residents remain (36 total). No new character art, static
triangles or collision objects were added for the activity.

Current export SHA256: 1a4efa50e8cb607bb40d4c15d12d834131b8cd7ca6ed699858ce5826b2afb771
Current native SHA256: 3afb39aef2fdfa9952aff49e71bf9a7f02d71f79f4517fef9d06acd04965fbac
All15 native/source stages pass. The first three lighting stages are reused from
the fully verifieda8872a1d source: plaza-life-check reconstructs that export byte
for byte after removing only the eight declared citizens, and checks its bake.
Transport regenerated and checked:75 chunks,25,237,098 compressed bytes,
925,077 authored draw triangles/33,345,303 draw attribute values exact;
73,728 collision/elevation samples exact. Cache92. All prior generations/evidence
are retained. Latest captures run under property-frontages/ro3-plaza-life/.

Next: inspect those fresh views, exercise the selected camera and current city
through ordinary mobile traversal/field/save/offline checks, update acceptance,
then commit/push a documented milestone. Do not rerun one-shot authors.
Whole-city resizing/reorganization remains authorized if broader screenshots
justify it. Native art/composition must be reviewed against the supplied RO3
frames; passing counts or route tests alone does not claim artistic equivalence.

## Historical mobile interruption — superseded by the current state above

User recovery request explicitly authorizes checkpoint commits and pushes on the
existing branch, then profiling and streaming of the current real city. This
supersedes earlier no-push instructions. No checkout/reset/clean/stash/restore
was performed. Starting HEAD: d7f9f15978b0ca6347fe5f80302d147544bd4626.
The recovery-source.json receipt records the preserved authored files.

Original World resume point: first plaza inset (10 units), grass feathering,
frontages/tone/trees and camera are saved; all 13 source stages pass for export
e97f4333 and native59118c. Three gameplay captures and camera checks are preserved
under property-frontages/diagnostics/plaza-inset10/. Actual plaza still looks too
open; RO3 acceptance remains pending. The second six-unit inset is planning ONLY.
Its planner stopped at the 12,500-face grass guard (plaza-inset16-planning.log);
no native/export changes were applied. Preserve the unfinished iteration-2
scripts. On resuming: inspect tessellation/count accounting before changing any
guard, complete the second planner or choose a reference-supported correction,
then native parity/lighting and fresh gameplay captures. Continue service and
neighborhood walking, field/save/cache/offline and sound-on performance checks.
Do not rerun one-shot authors or regenerate saved art for streaming.

Baseline profiling is complete; evidence and measured secondary costs are in
mobile-streaming/README.md and baseline-mobile-detailed.json. First real-map chunk boot, exact draw/semantic transport checks and three
streamed city captures now pass. SW89 uses a shell-only static cache and bounded
on-demand world/assets caches. Runtime source and native authored files remain
the recovery receipt hashes. Streaming/mobile acceptance is still pending.
Offline saved-character reload, migration, current authored textures and ground
bake now pass. Cache clone/overwrite races were fixed; see cache-resume evidence.
WebKit Safari-engine six-leg ordinary touch traversal and cold/warm reload pass:
51 unloads/31 reloads, repeated-location retained buffers exactly stable; physical
iPhone remains PENDING. Chromium ordinary field-gate entry/return and zero city
geometry in the field pass. Candidate3 server audit:33.47MB before readiness,
18.12s observed gameplay,177MB sampled heap; no monolithic request. All96 original
Node checks and5 streaming contracts pass. Exact next infrastructure action:
finish service/neighborhood walking, court-legacy, camera and transient failure
checks; update available-environment acceptance and resume original World work.
See mobile-streaming/README.md.
Available-environment mobile gate PASS; overall optimization PARTIAL because
physical iPhone Safari remains PENDING.8 services/10 neighborhood stops,
ordinary field entry+saved reload, court-legacy Canvas boot/walk, current camera
controls/aspect/inverse, and actual HTTP503 chunk retries all pass. All sampled
owned geometry bytes independently match loaded manifests; repeat visits exact.
See mobile-streaming/README.md for objective metrics, scope and physical URL.

Original World task RESUMED automatically. Exact action: inset16 needs13,125
unfeathered faces; retained91-lawn boundary union has no micro-holes. Improve
curve tessellation without increasing12,500 guard, apply second6-unit inset,
then native RO3 daylight/paving/grass-blade and rooted stone-joint ingress pass.
Refresh original-alpha lighting/native parity, regenerate exact streamed chunks,
bump cache version and compare actual gameplay with supplied RO3 frames.
Current authored recovery source remains e97f4333/native59118c before these
new edits. Retain archival source-specific evidence; no art acceptance claimed.


## Active continuation after the audit

The original building-variety task has resumed. The user clarified that local
placement and tone should be very similar to RO3 while keeping Wayfarer's own
theme. Four source-matched neighborhood captures of the audited checkpoint are
in `docs/review/wayfarer-capital-v76/streets/`.

An authored candidate now changes 46 property frontages: 18 recessed shops,
17 recognizable work fronts, and 11 residential entry/shutter treatments.
The two projecting oriel homes retain their existing sheltered entry volume;
redundant new porch geometry was removed before lighting. Urban geometry,
collision cores, actual door leaves, services and walkers passed the authoring
preservation guard. Existing materials supply all new meshes; no new textures.
Warm clay, warmer timber, neutral paving and cooler light/shadow colors form a
separate, guarded tone pass. Cache version 86 exposes the updated native export
and floor atlas to returning clients.

The historical checkpoint hashes below describe the audit, not this candidate.
The user also requested the RO3 camera baseline, natural grass placement,
closer light/scale and better tree quality. The selected pitch/orbit study is
55°/20°; camera distance is still subject to gameplay comparison. The runtime
uses a single default for initial projection and resets, with a canonical sprite
axis to preserve aspect ratios under orbit.
The user explicitly authorized resizing/reorganizing the entire city if the
reference comparison requires it. There is no pending permission request.
The four side properties of the plaza now move inward by 10 units, with complete
meshes, colliders, actual doors and entrance contacts. Continuous private terraces
and closed curbs replace 314.4 square units of surplus public plaza paving. Main
road widths, the fountain, city bounds and shore stay fixed. The existing plaza
resident is rerouted around the closer fronts; population stays 28. A larger
resize remains authorized if further comparison establishes the need.

Curb-aligned lawns expand into curved planted pockets, with 2.2-unit clear entrance
paths. Latest user feedback specifically requests grass blending into stone.
The lawns now have native SurfaceOpacity point attributes: opaque interiors and
a 0.28-unit translucent fringe reveal the existing paving. This uses the original
texture and existing feather shader; no extra texture or physical obstacle. Seventy-eight evergreen
crowns have 90 overlapping boughs each, three fullness profiles and original
full-resolution textures. Roots and collisions are unchanged. Landscape budgets separately bound the original 23,050 added triangles and the
13,679 triangles needed for the planted edge. Exact current totals are recorded
in landscape-authoring.json; count/resource checks do not establish visual parity.

The final candidate passes all13 refreshed lighting/source stages through
`tools/review-capital-frontages-v76.py`. Export SHA256:
`e97f4333ac193196cf61b68765f3218d9fc98d1c12433c03b875187f5c3ce114`.
Saved native SHA256:
`59118c5925570f6f674673ba975cf44defe3bf312f7f21639165fd741b332db6`.
Native area-accounting metadata was separately synchronized and parity repeated.
Camera mouse controls/resets, sprite aspect and ground inverse checks pass.
Receipts/logs: `docs/review/wayfarer-capital-v76/property-frontages/`.
Current-source gameplay captures, ordinary service/neighborhood walking, field
travel, save/cache/offline reload and sound-on performance review are in progress.
Compare current gameplay with the preserved checkpoint and supplied RO3 frames. Do not claim the RO3 baseline from geometry alone.
Source authoring scripts are one-shot guarded; do not rerun them on this city.
Rollback source copy: `/tmp/astraeon-before-property-frontages-v76/`.

Checkpoint audited on 7 October 2026 (Asia/Bangkok). The user authorized reverting
the intervening model's unreviewed crowd experiment, then requested continuation
of the original building-variety and neighborhood task using the supplied RO3
beta frames. Continue that task after the audit; no additional push is requested
by this continuation.

## Restored checkpoint

The native city and export exactly match pushed commit `d7f9f15` on
`codex/world-pipeline-v3-proof`.

- Native: `authoring/wayfarer-spatial.blend`, SHA256
  `b6bf486e4261bb6c247c4a2facaae8186d07aac7e96ce403ecbca4db3a09fbc3`.
- Export: `world/v3/wayfarer-spatial.json`, SHA256
  `ad5956f55b4a4d1fb00c665754f5bc28f13b001a7f1456bf0e6c3e01894155dc`.
- 158 residential/commercial buildings: 37 originals and 121 additions across
  nine massing families; 14 paired plots consolidated into larger buildings.
- Three distinct civic additions; 28 existing ambient walkers.

The discarded candidate added six walkers (28 to 34) despite describing a
redistribution. The world comparison proved this was its only content change.
Both city files and the density checker were restored; experiment scripts and
report removed. A recoverable scratch copy is at
`/tmp/astraeon-model-switch-plaza-experiment-20261007`.
See `docs/review/wayfarer-capital-v76/checkpoint-audit/README.md` for the audit.

## Active task and reference

Make whole buildings visibly different and use land efficiently, with convincing
neighborhoods and balanced spacing. RO3 is the hard visual target; the concept
supplies timber, clay, ivory, blue and gold theme. Keep one original geometric
regional capital. Prontera informs hierarchy and local urban relationships.

The primary direct reference is `RO3 Ref/Prontera_RO3_Beta_Reference`: 52 original
910×512 frames and four contact sheets, from remote commits 797e7a4/e546c30.
The reference README limits inference of a complete map or absolute dimensions.
`prontera-beta-review.md` and `reference-and-design.md` record observations and
supporting official Prontera, Colmar and Stormwind research. A count of building
families or a crowded multiplayer screenshot cannot establish art acceptance or
an exact ambient-NPC budget.

## Current implementation and evidence

The Council is a hipped palazzo/clock pavilion; Archive a reading nave with
low galleries and stair tower; Exchange a clay-roofed market hall/colonnade/belfry.
Original Hall, shrine, services, field destinations, actors and pace remain.
Keep 8–10-unit streets, 14/12-unit ceremonial axes, owned-block curbs, two inward
courts and ten actual plaza-facing entrances. Layout ID stays valid; exported
`architectureRevision:76` identifies the mesh revision.

At the restored checkpoint, public stone repeats at 3.2 world units; private
pavers stay at 8. Its eighty-four planted block-edge pieces preserved streets
and all 158 actual door approaches; the active landscape replaces those pieces.
Architecture and original-alpha foliage lighting and the 4096² ground bake are
complete. The parity test intentionally moves an unsaved caster; its stale-bake
message proves invalidation and does not describe the saved export.

Geometry, retained assemblies/floors, density, doors, routes and public schemas
passed for the restored hash. The existing Node report has 96 passes and no
failures for that same hash. The checkpoint audit repeats native parity, route
checks and schemas. It records each result in its own folder.

Ordinary 910×512 captures now exist in `beta-default/`. The original
`plaza-frontages` shot used [128,132], north of the fountain. A correctly placed
Plaza route capture is in `diagnostics/plaza-correct-anchor/`, at [128,150]. The
capture tool now resolves future `plaza-frontages` views to the named route point.
These images have no runtime errors and zero culling-pixel differences. Their
manifests retain exact source/camera/position values. Sprite geometry rectangles
include padding and are not measurements of visible character artwork.

The side-by-side viewer is `prontera-comparison.html`. Broader street, court,
civic and shore captures, ordinary neighborhood/service walking, field/save
flow, cache85/offline reload and native-resolution performance remain pending.
The hard RO3 and broader Golden visual baseline has not been accepted. Inspect
actual rendered architecture before selecting additional geometry changes.

## Safe continuation

Authority is the native Blender file; always keep its export in parity. Do not
rerun the one-shot architecture author on the edited city. Plans and guarded
finishing companions are in `tools/*architecture*v76.py`. Original assemblies,
component groups and separate collision cores must stay intact.

Shapely2.1.2 is at `/tmp/astraeon-curb-geometry`; use it through `PYTHONPATH` for
geometry planners/checkers. Its ABI differs from Blender's Python. Shadow alpha
cache: `/tmp/astraeon-ro3-72/composition-alpha.json`. Lighting must follow caster
or floor geometry changes. The native ground atlas is
`assets/wayfarer-ground-shadow-v75.png` under cache83.

Use one browser at a time. Chromium local sockets need the network sandbox
capability. Existing server: 127.0.0.1:8011, log
`/tmp/astraeon-capital-server.log`. The cloud uses SwiftShader without a physical
GPU; retain the existing FPS/frame-time/moving-frame requirements and report
software-renderer limitations accurately.

`tools/review-capital-architecture-v76.py` can resume and bound stages with
`ASTRAEON_ARCH_REVIEW_FROM` and `ASTRAEON_ARCH_REVIEW_TO`. Start with a bounded
visual architecture sweep, then address findings against particular reference
frames. Preserve source-specific historical images and never use earlier results
as acceptance of changed geometry. No PR, merge or deployment is requested.

Additional visual request received during mobile interruption: match RO3 lighting,
screenshot tone and feel more closely; polish other elements, including grass
particle/fine-blade detail and natural green ingress between paving stones along
walk paths. Incorporate this into the original visual task immediately after the
available-environment mobile gate. Keep camera comparison consistent, natural
planting restrained and clear routes. Do not substitute streaming for this work.

User reaffirmed whole-city resizing on7 October2026: if gameplay screenshots
still do not meet RO3, estimate scale from local building/actor, street-width
and adjacency relationships and resize/reorganize the whole city as needed.
This remains authorized; no additional permission is required. Full map bounds
are not established by the incomplete beta footage. Do not constrain the
solution to the plaza inset if broader comparison warrants a city-wide change.

### Camera angle steering — 7 October 2026

The user explicitly reaffirmed that camera angle is important. Continue the RO3
comparison with pitch, yaw and distance alongside city spacing; compare visible
roof/façade balance, street depth and person-relative framing. Current55°/20°/125
is a candidate calibration, not immutable or measured RO3 telemetry. Whole-city
resize remains authorized if fresh screenshots justify it.
