# One coherent model-source job

Prepared 10 October 2026. **Awaiting account connection and spend decision.**

Input: `source/front-reference.png`, the corrected compact front A-pose reference
derived from the approved design. No sword, long cape or prop; these will be
independent equipment. The neck scarf remains. This reference is not an approved
runtime view or animation pose authority. Source hashes/prompts: `source-spec.json`.

The CLI dry run returned `valid: true`, no warnings and exactly one API call:

1. **image-to-model** — `POST /v3/generation/image-to-model`.
   CLI selects `tripo-v3.1`, wire model `v3.1-20260211` (default high fidelity).
   `texture=true`, `pbr=false`, `texture_quality=standard`, `face_limit=50000`,
   `model_seed=621018`. One candidate; no processing chain.

Estimated cost: **30 Tripo credits**, from the installed skill's approximate price
table for standard-textured v3.1 image-to-model. Proposed ceiling: **30 credits**.
No retries, extra texture pass, paid rigging, segmentation, animation or format
conversion is included. If the quoted charge changes, stop for a revised decision.
The CLI has no spending-cap flag in its documented `make` options; do not represent
this proposed conversation-level ceiling as a provider-enforced billing cap.
Failed/cancelled tasks are described as refunded by the provider workflow.

Expected provider files: GLB geometry/materials, texture images, `preview.png` and
`task.json`, under `provider/tripo-out/astraeon-coherent-master-01-<task-prefix>/`.
The dry run lists no explicit deliverables; these file expectations follow the
CLI's documented model-generation output. Inspect the actual result paths before
reporting delivered files.

Exact planned submission (not executed):

```powershell
npx --yes tripo-cli@latest make 'authoring/characters/swordsman-production/coherent-master-01/source/front-reference.png' -p texture=true -p pbr=false -p texture_quality=standard -p face_limit=50000 --seed 621018 --name astraeon-coherent-master-01 -o 'authoring/characters/swordsman-production/coherent-master-01/provider' --json --yes --no-open
```

After submission, wait for a terminal task result. Provider success alone is not
an accepted source. Inspect the mesh and textures in Blender, preserve originals,
and examine actual front/side/rear geometry, proportions, hands, materials and
disconnected surfaces. Stop for owner visual review before paid rigging or action
expansion. Generated rear surfaces and clothing/body separability remain unproven.

The original factory contract still requires a canonical body with concealed
surfaces, editable outfits/equipment, reusable motion, fixed camera/exact headings
and painted 2D PNG/JSON output. A successful generation does not establish these.
