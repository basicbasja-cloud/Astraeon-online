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
