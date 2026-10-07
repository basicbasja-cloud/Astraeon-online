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
