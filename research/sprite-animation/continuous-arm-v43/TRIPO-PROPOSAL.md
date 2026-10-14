# Optional controllable-mesh route — proposed, not executed

The complete painted critical-pose turnaround improves arm structure, but the first motion strip using that reference still swaps the reaching limb on lift. A source-controlled **skinned 3D mesh** would make the arm retain its identity while allowing a continuous elbow and proper perspective. A generated mesh still needs visual review, weights/correctives, matched family proportions, hand orientation and actual eight-view render QA; this route does not promise an automatic visual pass.

Proposed input: [front-only T-pose candidate](paint/model-front-candidate.png). This is new modeling reference, **not approved gameplay art**. The generated back repeats the front knee plates and is rejected for multiview submission; it must not be sent. No rejected arm rig or old attack enters this job.

Proposed public CLI: `tripo-cli@0.6.1`, MIT, source tarball retained and verified against npm SHA512 integrity. The package has been **read as data only**, not executed. Static inspection found the advertised dry-run branch before `newClient` and upload handling, but this is not an executed dry-run or a security guarantee for its dependency tree.

Proposed submission destination: `https://openapi.tripo3d.ai`. Exactly the front image above would be uploaded.

| Call | Configuration | Estimated credits |
|---|---|---:|
| `POST /v3/generation/image-to-model` | H model alias `tripo-v3.1`, wire `v3.1-20260211`, standard textured/PBR GLB | 30 |
| `POST /v3/animations/rig-check` | inspect riggability; stop if unsuitable | 0 |
| `POST /v3/animations/rig` | `v2.5-20260210`, Mixamo specification, GLB | 25 |
| Total | one candidate, no paid convert/retarget/re-roll | **about 55** |

The local follow-up would inspect rest axes and real bone/mesh names, adapt the pickup target using that mesh's measured limb lengths, apply reviewed local hand bases, then render all eight physical views from one action clock. Default logical asset groups remain **body with outfit + complete head**, optional equipment. Local corrections and QA are separate from provider acceptance. Keep original generation and rigged GLBs, preview, task IDs and per-step actual cost receipt in a fresh `skinned-character-v44/model/` folder, preserving published v43 evidence.

The exact pinned command proposal is in `tripo-proposal.json`. Before submission, an authorized dry-run must confirm model, all payloads and warnings. If any material parameter/step/cost changes, stop and update the proposal. Credentials, if absent, require the user's provider browser/device authorization; never request an API key in chat.

**Blocked action:** automatic approval rejected downloading/executing the CLI with a project-image argument, even in dry-run mode, because that specific destination/payload was not authorized. The rejected command did not execute. There was no image upload, provider job or credit charge. No workaround or indirect execution was attempted. An explicit user authorization is required for this optional external route. Local research and source validation continue independently.
