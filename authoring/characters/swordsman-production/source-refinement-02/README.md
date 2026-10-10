# Fresh source refinement 02

10 October 2026. Branch `character/production-factory-v2`.

Internal source study, **NO-SHIP**. The painted concept remains approved; this
geometry, inferred depth, grip and equipment assembly have no owner approval.
The owner asked to continue the authorized work while answering questions.
No approval is inferred from those questions or from technical validation.

Open `review.html` through the repository's local review server. It compares the
unchanged concept with the new source at a common scale, provides an overlay,
eight exact headings, full-context and isolated hand diagnostics, visible weapon
passes, a five-layer equipped assembly, and separately baked source variants.
The editable source is `source-refinement.blend`.

The fresh volume study in `reference-fit-01` was developed into a coherent source
with physical face and hair, fingers curled around the complete hilt, an opposing
thumb, fitted garment shells, armor, tunic panels, cape and preliminary seams.
No rejected pilot mesh, image-card rig, generated limb tile or rejected turnaround
was imported. The approved concept and both preserved checkpoint manifests were
checked unchanged; see `validation.json`.

## What the layer proof establishes

Five full-canvas visible-only passes reconstruct this exact equipped SE view:
BaseBody, Hair, Outfit, Weapon and BackAccessory. Every pass uses the same camera,
320 canvas, root (160,264), source geometry and pose. A holdout material on other
geometry removes covered pixels, including the grip-covered hilt, while retaining
the complete physical sword in the source. `layer-proof-validation.json` records
zero coverage-pixel differences and mean opaque RGB error of about 0.374 out of
255, measured by in-memory alpha composition. This is a measured approximation,
not an exact pixel identity or proof of painted quality.

These equipped passes do not contain hidden body surfaces and cannot support
arbitrary costume switching by simply removing the Outfit PNG. The separately
baked outfit-removal image comes from complete source anatomy. The alternate
blade test changes blade geometry only, preserving the grip, hilt and guard.
Headgear and offhand are absent. No general combination exporter, depth-split
runtime assembly, animation strip or production package is claimed.

## Geometry and remaining work

The bare body has 87,356 vertices and 87,362 quad faces in one closed component,
with no boundary, non-manifold edges or loose vertices. It is a voxel volume
source, not authored deformation topology. There are zero armatures, no fitted
finger controls, no skinning and no motion coverage. Retopology and topology QA
must precede the fitted rig.

Each glove is a closed static volume built around the actual grasp paths.
Nearest-limb garment classification was replaced for gloves after it produced
wrist holes and stray thigh patches when the blade angle changed. The right
glove has 9,434 vertices, the left 7,252, each in one closed component; see
`glove-topology.json`. This establishes closed static surfaces, not rig quality.

Head and hair likeness, scarf and costume fitting, seam cleanup, sculpted detail
and rear-view readability need further work. Structural materials are not the
approved painted finish. At constant scale the silhouettes range from 173 to
190 authoring pixels across headings; no independent direction resizing was used.
Manual registration and mesh closure do not prove visual matching.

NW/N complete diagnostic and production frames contain no visible weapon pixels
because the torso and cape occlude them. W has 38 visible production pixels.
The isolated hand views expose physical contact but do not resolve complete-view
readability. Keep both sets in review. Blade-tip depth was refined from -0.15 to
-0.40 meters, retaining the reference SE tip projection. A deeper -0.75 trial
made the side-view blade too horizontal and was discarded internally. The
current inferred angle remains a source study, not owner-approved projection.

## Reproduction

The local safe-mode Blender MCP executes these repository scripts in the owned
ASTRAEON tool scene, never a user source scene:

1. `tools/build-reference-fit-source.py`: constructs the fresh static source,
   saves it and renders the eight headings and SE large/body views.
2. `tools/inspect-reference-fit-grip.py`: produces four same-frame diagnostic
   sets and the production-frame visible weapon pass, restoring source state.
3. `tools/bake-reference-fit-layer-proof.py`: produces five equipped SE passes,
   outfit removal and alternate blade; restores source state.

These are authoring scripts with an explicit workspace output path. No paid
generation, new image-generation call, source asset import or runtime admission
was used. `provenance.json` pins script hashes and method references.
