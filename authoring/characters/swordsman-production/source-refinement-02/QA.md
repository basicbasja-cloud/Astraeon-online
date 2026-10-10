# Source refinement QA

**NO-SHIP / INTERNAL SOURCE STUDY / OWNER UNAPPROVED** — 10 October 2026.

Technical observations from live Blender 5.2.2 LTS and local rendered files:

| Check | Observation | Limit |
| --- | --- | --- |
| Bare-body topology | One closed component, 87,356 vertices, 87,362 quads; zero boundary/non-manifold/loose elements | Voxel topology is not animation-ready topology |
| Production framing | Eight exact headings, fixed orthographic camera, 320 canvas, root (160,264) | Side/rear depth and camera elevation are inferred |
| Static grip | Four fingers and opposing thumb are modeled around a complete hilt; glove/hand coverage masks weapon pixels in SE/W/NW/N | No fitted finger controls, weights or movement test |
| Back-view context | NW/N weapon visibility is zero in complete production frames; W has 38 visible pixels | Physical contact does not solve visual readability |
| Equipped layers | Five SE passes reconstruct direct render with zero coverage mismatches; mean opaque RGB difference ~0.374/255 | One exact combination, visible-only layers; antialiasing differs |
| Gloves | Two closed static volumes, one component each, zero boundary/non-manifold/loose elements | Rough shape and bracer seam still need art cleanup |
| Source reuse | Outfit removal and shorter/wider blade separately re-baked at same framing and grip | No complete second outfit or class variation |
| Preservation | Approved image hash plus 50 rejected-pilot and 19 first-checkpoint files unchanged | No approval inferred for new source |
| Rig / motion | Zero armatures, no skinning, empty action coverage | Factory and runtime package incomplete |

Layer masking uses the [Blender Holdout shader](https://docs.blender.org/manual/en/3.4/render/shader_nodes/shader/holdout.html)
with transparent film. Its behavior was tested locally on these rendered images;
documentation alone is not acceptance evidence. Diagnostics restore materials,
visibility and the production camera. The saved source keeps the original blade.

Known visual defects: approximate head/hair likeness; simple scarf, armor and
boots; rough glove/bracer seams; jagged edges where fitted surface classification meets neighboring
garments; missing sculpted folds/detail; rough cape emblems; unapproved rear
depth; back-view sword obscuration. Lighting and colors are a structural preview,
not painted sprite art. No quality score or final candidate acceptance is given.

Browser review includes actual direct renders, common-frame layer stacking,
shared-scale controls and unchanged reference. Screenshots are retained under
`screenshots/`; browser operation is separate from visual acceptance.

Before rigging: refine the remaining source defects, review the physical source
and grip against the approved concept, author deformation topology, and validate
it. Then fit body/finger controls and equipment sockets, test deformations and
motions, establish combination-aware depth handling, and finish the painted
2D layers. Do not bulk-bake the class/action matrix from this checkpoint.
