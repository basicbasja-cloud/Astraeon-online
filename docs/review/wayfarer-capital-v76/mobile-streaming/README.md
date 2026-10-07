# Mobile loading interruption

## Baseline

Preserved World checkpoint: 67ea7e7 (starting HEAD d7f9f15). Same authored
city; source receipt in recovery-source.json. Physical iPhone Safari PENDING.
Chromium iPhone13 emulation on cloud SwiftShader, local uncompressed HTTP;
these times are not physical-phone or deployed-network measurements.

Detailed first playable: 70392 ms; 82 page
resource entries; 96,011,778 reported page-transfer
bytes. Service Worker traffic may not all appear in page Resource Timing.
Static precache inventory: 139,617,220 bytes. World payload:95,574,459
bytes; isolated parse1,504 ms after body-read2,211 ms. Content import1,674 ms
(includes compile1,339 ms). Renderer mount49,340 ms, including whole-city
reveal preparation/warming44,726 ms. Observed sampled JS heap peak
1,118,533,439 bytes; synchronous peaks may
be missed. First original Response.json profile separately retained. No errors.

Bottlenecks: giant JSON/full geometry import; construction/warming of all
static and reveal meshes; entire-world SW install139.6 MB; shared4096-square
RGBA floor/mask canvases and CPU RGBA readbacks. Static precache also includes
unused older atlases and the legacy court. Full objects account for94.9 MB of
95.6 MB; gameplay solid parts1.51 MB before removing render-only attributes,
terrain0.68 MB. Preserve stable authored collision/elevation/service metadata
separately from streamed render geometry.

Architecture decision: derive deterministic spatial render chunks from the
unchanged native export, retaining exact Float32 draw attributes, full authored
lighting/UVs/materials. Keep compact authoritative current-zone gameplay data
for navigation, destinations and saves. Runtime binary buffers avoid repeated
JSON numbers and per-triangle construction. Spawn-local chunks precede first
playable; distant chunks and future zone manifests are lazy. Shared assets stay
shared; chunk geometries and reveal resources have explicit unload ownership.
Static SW cache becomes shell-only, large content uses bounded on-demand caches.

Status: baseline complete. Implementation and mobile acceptance pending.
Original plaza refinement is paused at the exact point recorded in
CURRENT_HANDOFF.md; RO3 acceptance pending.

## First real-map streaming checkpoint

Normal boot now reads WorldManifest -> selected ZoneManifest ->0.97 MB exact
authored collision/elevation/service metadata -> nearby indexed Float32 buffers.
75 immutable32-unit spatial render chunks,27.21 MB compressed total. Default
spawn boots10 chunks/2.09 MB compressed/8.28 MB decoded, not the whole city.
No native/export/atlas change. Construction/reveal copies are local; every chunk
unload disposes its geometries and invalidates chunk-owned reveal ranges.
Shared materials/textures stay shared. Distant content is requested after first
playable; current/future zone manifests are selected lazily. Existing court-legacy
path remains. Return transitions protect the arrival chunks before mutation.
Camera changes wait behind a loading overlay if new visible chunks are missing.

SW87 static shell42 resources/~2.38 MB, no maps/atlases. Runtime world cache
32 MiB/180 entries; runtime assets64 MiB/100 entries; deterministic oldest-access
eviction, serialized writes, fetch deduplication, old-version cache cleanup.
Diagnostic monolithic source is not cached. Offline and migration tests pending.

Verified:75 chunk digests,73,728 collision/elevation samples identical, all
932,983 original visible draw triangles/33,664,539 attribute values numerically
exact, metadata/solid/floor geometry exact. Numeric signed zeros normalized only
for the comparison. Four streaming contract cases pass: future zone exclusion,
in-flight deduplication, retained lifecycle/reload, retry/failure and spawn-local
real-map boot. Three ordinary910x512 captures preserve city appearance, culling
pixel differences zero. Timestamp-dependent water/actors differ in image pairs;
visual-comparison.json is diagnostic, not a claim of identical capture times.
The reveal path was subsequently corrected to exclude terrain from occluders and
clear owner mask IDs in reveal copies; fresh reveal/camera review is still due.

Candidate2 mobile Chromium/SwiftShader: first playable24.94 s, UI8.58 s, mount
1.71 s, heap150.7 MB observed. Page encoded resource bodies38.74 MB include some
after-first-playable prefetch. SW responses make page transferSize underreport
network traffic;447 KB is NOT the actual initial transfer claim. Baseline encoded
resource bodies129.78 MB; baseline detailed first playable70.39 s, render mount49.34 s. True network and strict critical
cutoff measurements still needed. No physical iPhone acceptance claimed.

Next: browser repeated traversal/unload/reload and memory samples; cold/warm
load including offline-cache/save migration; reveal, court-legacy and camera
regressions; request failures; first-playable network accounting. Asset retry
hardening and remaining measured memory costs may require small fixes. Mobile
acceptance pending. Original RO3/plaza work stays paused at recorded resume point.
After future native/export changes, regenerate transport with
node --max-old-space-size=6000 tools/build-world-streaming.mjs, run
node --max-old-space-size=4000 tools/check-world-streaming.mjs, and bump boot/index/
SW cache version before gameplay evidence. Never accept stale transport.

## Cache correctness checkpoint (version88)

The existing save/cache test exposed two runtime-cache races: a queued write
cloned a body after the client consumed it, and delete-before-replace briefly
removed otherwise valid offline entries. The worker now retains response clones
immediately, replaces entries atomically, and handles hits by updating an
in-memory access inventory. Inventory accounting scans once rather than for
every write. Assets and chunk cache byte/count limits remain enforced.

`cache-resume/report.json` passes shell-only precache, on-demand authored
materials/chunks, old-version removal, legacy-layout migration, same-layout
blocked-position recovery and offline saved-character reload. The test fixture
now runs once at document initialization so normal pagehide saves cannot
overwrite an intended migration fixture. Original gameplay progress checks
remain. The offline ground image is still4096x4096 and matches its preserved
SHA256; compact semantics/source provenance are exact. No runtime errors.

Unused Canvas-town building sheets now load only when an original field/legacy
scene requires them. All original assets are retained. Authored material texture
promises are awaited for every incoming chunk; failed textures/materials can
be retried without installing partial geometry. Existing six Node regression
files and four streaming contracts pass. Safari-engine WebKit cold boot works;
ordinary traversal and field/service/reveal checks remain in progress. Physical
iPhone Safari remains PENDING. Mobile acceptance is not yet declared.

## Available-environment mobile evidence

WebKit26.5 with iPhone13 emulation: cold26.47s, warm7.87s; six ordinary
touch journeys through the real capital,51 unloads and31 reloads, no blocked
actor samples, missing visible chunks at checkpoints, duplicate chunk meshes or
runtime errors. Retained buffers peaked60,382,120 bytes, then returned to the
exact same60,382,120 bytes at the plaza and30,269,852 bytes at arrival on
repeat visits. Shared texture growth settled at44 during these two passes.
These are buffer ownership measurements, not a physical Safari memory report.
WebKit's emulation reports Apple GPU; the host remains Linux/cloud, not iPhone.

Chromium iPhone13/SwiftShader candidate3: first observed gameplay18.12s,
renderer mount1.49s, observed sampled JS heap177.0MB. Shell precache2,383,616
bytes. A disposable server counted every HTTP response body write, including SW
install/runtime traffic:33,467,533 bytes and98 requests before the runtime's
spawn-visible-ready marker. It counted the same bytes before the first observed
gameplay frame. No monolithic world request. The preserved baseline did not use
this server audit, so its page-transfer numbers are not directly comparable.
Original detailed boot70.39s/mount49.34s/observed heap1,118.5MB; original shell
precache139,617,220 bytes. Physical network timing and HTTP header bytes are
outside this body accounting. Spawn still10/75 chunks,2,090,118 compressed
bytes/8,284,388 decoded bytes. Timing varies with the cloud renderer.

The ordinary mobile field-gate check passes: original field artwork is deferred
until needed, city decoded geometry reaches zero in the field, return reloads
10 exact chunks, character/gold preserved, no runtime errors. Offline/save checks
passed separately. Five streaming contracts now include the lazy diagnostic
nav grid. All96 original Node checks pass individually. Service/neighborhood
walking, camera/reveal checks and transient browser-failure checks are ongoing.

Physical iPhone Safari: PENDING. On the published branch build, check a fresh
load at https://basicbasja-cloud.github.io/Astraeon-online/ , retain the saved
character on a warm reload, walk arrival -> plaza -> both neighborhoods ->
arrival repeatedly, enter/return from Goldenfield, and inspect sunlight,
plants, occlusion and collisions. Record Safari/device/iOS, network, cold/warm
time, crashes and sustained frame pacing. Do not clear an existing player's
save. Cloud/software timing and emulation cannot satisfy physical-device FPS,
thermal or Safari memory-pressure gates. All authored materials, geometry and
art resolution remain intact; visual RO3 acceptance is still pending.

## Optimization acceptance and automatic World resume

Available-environment gate: PASS. Overall optimization acceptance: PARTIAL
solely because physical iPhone Safari FPS/thermal/memory-pressure validation is
PENDING. All8 current services and10 neighborhood stops open/reach through
normal input, original field entry and saved-character reload pass at1280-wide
native CSS resolution; no page or resource errors. Court-legacy remains the
original Canvas diagnostic and passes ordinary boot/walk. The current55°/20°
camera, orbit/tilt/distance/reset, sprite aspect and ground inverse pass. A real
HTTP server injects two503 spawn-chunk failures; the actual SW/runtime retries
twice, installs unique meshes and reaches play with no lingering failure or
page error. Compact966,013-character gameplay metadata parse24.3ms in this
fault run, versus original monolithic isolated parse1,503.8ms. Largest critical
asset is2,100,118 bytes (original authored street texture), versus original
95,574,459-byte monolithic world request. No texture or geometry downgrade.
Memory ownership audit independently totals every loaded manifest: all sampled
owned geometry bytes match, and repeat visits match exactly. Browser/GPU/texture
memory beyond those owned buffers remains a real-device measurement limitation.

Version89 is publicly served at the recorded URL. Checkpoint0a681b3 preserved
the verified mobile loop, field and audit evidence. Original World task is
resumed automatically: the inset16 planner currently needs13,125 unfeathered
faces versus its12,500 limit. The existing feathered91-lawns mask itself has no
micro-holes; boundaries are retained exactly. Improve curve tessellation/count
accounting while retaining the original budget, then apply the recorded second
six-unit inset. Follow with reference-informed native daylight/paving and fine
grass rooted near the actual stone seams, fresh source-matched bakes, transport
regeneration and gameplay comparison. Hard RO3 art acceptance remains PENDING.
