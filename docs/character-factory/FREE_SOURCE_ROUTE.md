# Free source-authoring route

Checked 10 October 2026 after the owner asked, "We don't have a free way ?"
No paid generation is authorized. The prepared Tripo plan is on hold.

## Recommended local route

Blender plus MPFB/MakeHuman core character assets is a route with no provider
credits or software license fees. MPFB creates coherent humanoid meshes, supports
shape adjustment, standard rigs and independent clothing assets. Its core mesh,
targets, skins and rigs are CC0; the addon code has a separate GPL license.
Check each third-party asset separately rather than assuming it has the core
asset license. [Free-use FAQ](https://static.makehumancommunity.org/mpfb/faq/is_it_really_free.html),
[core license](https://static.makehumancommunity.org/about/license.html),
[authoring and rigging workflow](https://static.makehumancommunity.org/mpfb/docs/getting_started.html).

Use the coherent mesh as an anatomical/topological foundation, then author our
approved compact silhouette, anime face, hair, clothing, armor and equipment in
Blender. The generic base is not the approved ASTRAEON character. This route saves
provider fees but requires modeling, skinning and painted finishing work. It is
not a demonstrated automatic conversion of the approved image.

The first installation/compatibility and visual-source proof must be small.
Keep tools in a dedicated authoring workspace where possible; preserve source
licenses and hashes. No global addon installation, asset download or new source
mesh was performed during this feasibility check. MPFB's official getting-started
page specifies Blender >=4.2; our installed version is 5.2.2, but an actual load
and generation check is still needed before claiming compatibility.

Next gates: establish the connected body and finger topology; reshape it against
the approved design; prove hand grip and fixed-camera difficult views; author
meaningful clothing/equipment sources; then expand motion and export. Do not
resume either rejected model or image-card assembly. Reuse only the existing
runtime contracts and accepted design reference.

## Local AI alternatives

TripoSR has MIT-licensed code/weights and image-to-3D inference. Its README reports
about 6 GB VRAM with default settings, while its code supports a CPU fallback.
That does not establish performance, quality, detachable layers or riggable hands
on this PC. [Original project](https://github.com/VAST-AI-Research/TripoSR).

The PC reports AMD Radeon 780M integrated graphics, Ryzen 7 8840HS (8 cores/
16 threads), and 14,806,622,208 bytes of usable system RAM (~13.8 GiB). Windows
reports 2 GiB for AdapterRAM, which is not a complete account of shared GPU memory.
No NVIDIA GPU was reported. The usual CUDA setup is therefore not a straightforward
local fit. CPU/AMD alternatives require a bounded compatibility/performance test;
do not install several large model stacks as a speculative rescue.

The official hosted TripoSR demo listing currently reports a runtime error in
the retrieved page. It is not a verified available free generation service.
[Official demo listing](https://huggingface.co/spaces/stabilityai/TripoSR/tree/main).

## Cost boundary

The free recommendation means no additional provider credit charges. It does
not mean no work, compute time or iteration. Paid Tripo generation remains
optional and unsubmitted; the pending 30-credit plan must not run unless the
owner explicitly returns to and authorizes that exact job.
