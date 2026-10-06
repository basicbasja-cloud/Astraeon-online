# Source74 — coherent public floor

The user identified random rectangular patches in the source73 plaza capture.
The legacy continuous rectangular floor and enlarged irregular-stone plaza
shared elevation .025m, causing coplanar competition. Old public forecourts also
retained rectangular paving and roads used a different tint.

The saved Blender correction removes 645.841m² of duplicate backing beneath the
actual plaza and four approaches. Flat paving follows the closed private-zone
geometry: public areas share the existing irregular-stone artwork, world UVs
(x/8,y/8) and native plaza tint; private lots retain aged rectangular paving.
Stair treads and the fountain steps are unchanged. No replacement texture,
runtime pad, resolution reduction or character change is introduced.

The independent checker verifies 639 floors and 35,359 UV corners. Maximum
coverage difference after export rounding is .000231m²; residual backing overlap
is .00000506m². All architecture, plants, actor/service/navigation metadata and
unplanned floors are preserved. All 96 Node checks pass.

Floor shadows are refreshed with original cutout alpha, 1536² resolution,
eight sun samples and four contact samples. Architecture and foliage geometry
are unchanged, so their completed source73 lighting stays valid. Page, loader
and service-worker versions are synchronized at 81.

`plaza-before.png` is the superseded image used for diagnosis. Final schemas and saved Blender/export parity pass, as do 17 destinations and
ten patrols. Final native captures, browser checks and isolated performance are
pending. The first capture exceeded its startup deadline during concurrent
validation; the browser-only retry uses a bounded 240-second startup deadline.
Movement, image quality and performance thresholds are unchanged.
This report does not claim user Golden acceptance or physical-GPU performance.

## Native plaza review

`native/plaza.png` is a fresh1280×800 capture, with 1280×666 scene at ratio 1,
zoom 160/yaw 25°/pitch 46°. The public floor is visually continuous across the
plaza and approaches; the former rectangular patches are absent. The fountain
keeps its intentional pale stepped foundation. Curbs and private lot paving
remain distinct, and no console/page errors were recorded. This resolves the
reported plaza-floor defect; it is not an overall town/Golden acceptance.

## Bounded rendering work

Opaque scenery now batches in 16m spatial cells so Three.js can cull offscreen
meshes. Each native part retains every vertex/face, UV, lighting value and
picking owner. Blended materials remain grouped to preserve ordering. In the
default-camera movement scenario, submitted triangles fall 563,143→230,526;
draw calls rise 70→169. This is a submission improvement, not a certified FPS
pass. The short isolated SwiftShader samples still fail the unchanged gate:
baseline 0.756 FPS/p95=1500ms (five frames), candidate 0.876 FPS/p95=1283.3ms
(six frames). They cannot establish a statistically reliable FPS speedup or
physical-GPU performance. No frozen rendered-root pairs were observed, but the
required >100 moving pairs were not attained at this software frame rate.

The capture tool optionally renders the same state exhaustively and with
ordinary static frustum culling, reads native framebuffer pixels, compares them
and restores renderer flags before taking the screenshot. This checks graphics
preservation only; gameplay service checks use ordinary input. Plaza, avenue,
market and shop frontage currently have zero differing pixels and no errors.
The remaining views and cache/services checks are in progress.

Eleven final native views are complete and inspected. Each reports zero pixel
differences with frustum culling and no errors. Capital expansion supersedes the
remaining small-town review, while hard RO3 quality remains required.
