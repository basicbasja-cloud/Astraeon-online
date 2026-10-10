# Fresh proportion and pose blockout

**PROPORTION_POSE_BLOCKOUT_UNAPPROVED / NO-SHIP.**

New, editable volume study based on the approved painted candidate-01. The owner
asked to follow the plan after Blender MCP and skills were installed. This is
the first narrow review checkpoint: body/head size, body proportions and relaxed
standing pose. It does not seek approval of painted style, finished identity,
grip, costumes, animation or the production factory.

Open `review.html` through the repository's local server. The unchanged concept
and the new source use the same 320-square frame and root (160,264). Buttons show
the comparison at 176 authoring pixels and 88 game pixels; the enlarged view
fits the available browser width. A same-frame overlay and manual landmarks
help locate differences. W/NW/N expose inferred depth; body-only SE shows the
connected underlying volume.

`source-blockout.blend` contains fresh lofted body volumes, a voxel union,
removable major clothing forms and provisional weapon geometry. No rejected
mesh, rig, painted cutout or MPFB body was imported. The body is one closed mesh.
Dense voxel quads are blockout geometry, not animation-ready edge flow.

The faceless head and broad hair mass are unfinished. The hand and blade guide
are provisional; no finger/thumb grasp or hilt occlusion is approved. Camera
elevation, joint locations hidden under clothing and rear anatomy are hypotheses.
Technical registration does not independently establish reference likeness.

Three form passes were inspected: initial volume, narrower split tunic with a
connected neck, then slimmer leg/boot forms and a cape edge that preserves the
observed silhouette. The initial blend and SE render are retained as history.
Final fitting cleanup reduces foot volume inside the boot and removes empty
collections left by iterations. Prior rejected source files are unchanged.

After an owner decision on this narrow checkpoint, refine the head silhouette,
costume structure and anatomical hands, author deformation topology and fit the
enabled Rigify skeleton. Review the actual grip in SE/W/NW/N before the coherent
source acceptance gate. Animation and factory expansion depend on that gate.

No paid generator, new image generation, external asset import, runtime package
admission or animation coverage was used or claimed.

## Rebuild

`tools/build-reference-fit-blockout.py` is executed as Python through the local
Blender MCP editing tool. It deliberately accepts only the owned disposable
connection-test scene or `ASTRAEON_REFERENCE_FIT_01`, then replaces that owned
scene. Output directories must already exist. It renders all checkpoint views
and saves an unapproved source with gear visible. Do not run it against another
owner scene. The script embeds the currently measured fit specification.

See `REFERENCE_ANALYSIS.md`, `fit-spec.json`, `validation.json` and `QA.md`.
