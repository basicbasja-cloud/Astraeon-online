# Source of truth for game-motion paintovers

2026-10-12, v19. The user explicitly authorizes original-character paintover trials of RO and other games, including additional frames. This extends research input use; it does not approve new drawings or replace the accepted v17 original upright source.

## Evidence has different authority

| Evidence | Authoritative for | Unknown / not established |
|---|---|---|
| Captured raster plus SHA, ordinal, PTS, exposure, fixed canvas | Exactly what the retrieved file displays | Hidden bones, anatomical ownership under occlusion, world contact, source engine timing |
| Pinned native atlas descriptor | Source cell/order/repeated IDs/declared clock in that code revision | Executed engine behavior, source anatomical skeleton |
| Native ACT/SPR with decoded transforms/anchors | Images, layers and anchors actually present in those files | Anatomical bone rig unless separately provided |
| Manually observed visible contour/landmark | Scoped visible surface with uncertainty | Hidden hip center or anatomical side merely inferred from cloth color |
| Reconstructed pose / inserted frame | Our authoring decision and its exact pixels | A frame recovered from the source game |
| Exact user-approved original rig GIF and bound source | Approved v17 W source motion at its stated clock | New art, a different action/facing, replacement parts |

There is no one magic reference that proves all these layers. A practical source of truth is the linked contract retaining their boundaries. Never overwrite observed evidence with the reconstructed hypothesis, and never promote an unknown to PASS.

## What RO actually provides

Re-read primary [ACT format](https://ragnarokresearchlab.github.io/file-formats/act/) and [client timing study](https://ragnarokresearchlab.github.io/rendering/animation-systems/). The documentation's author reports24ms ticks rather than the historical25ms conversion. This is third-party reverse engineering of a studied client, not our reproduced universal-client experiment. Our archived8×75ms community APNG is still8×75ms: we did not retrieve this Swordman's exact native ACT and must not assume its interval count and silently replace75 with72.

Pinned RagLite revision `d1ce2b1e2136c46b1409d5c6701f64d7c3cddaf9` was inspected at [RagnarokACT.lua](https://github.com/RagnarokResearchLab/RagLite/blob/d1ce2b1e2136c46b1409d5c6701f64d7c3cddaf9/Core/FileFormats/RagnarokACT.lua): it declares24ms, reads optional anchors from2.3, U/V scales separately from2.4, and image dimensions from2.5. It reads ticks per **clip**, multiplying each clip's duration per displayed frame; its default for older files is4ticks. Those are implementation facts, not recovered joints. [KeyframeAnimation.lua](https://github.com/RagnarokResearchLab/RagLite/blob/d1ce2b1e2136c46b1409d5c6701f64d7c3cddaf9/Core/NativeClient/KeyframeAnimation.lua) advances integer frames, preserves accumulated remainder and wraps the selected clip. We read three files and their blob hashes; did not execute its Lua suite or reproduce a client.

ACT layer positions and head anchors make an attachment system possible. They do not make a 2D raster's hip joint an authoritative anatomical bone. Classic replacement head/body/weapon content and our complete independent hair/clothes requirement remain distinct.

## Safe interpolation experiment

1. Bind original observed keys/order/clock before generating. Keep all duplicates and non-loop cuts explicit. Choose one complete loop or a bounded action, not an arbitrary clip containing room changes.
2. Paint one coherent full key sheet in our own identity. It is an experimental draft until proximal chains, contact, registration and acting are reviewed. A pose trace prompt is not an exact pose tracer.
3. Freeze those authored key files. Request separate midpoint drawings, with the intended left/right pair and wrap pair identified. A midpoint is a new authored hypothesis, not a captured source timestamp.
4. Interleave exact key copies at even zero-based indices. The gate rejects a newly generated key substituted into the control. Keep one shared scale/canvas; no individual pose fitting, cropping or head pinning.
5. Compare8/16 at equal total duration. Preserve a precise raster clock separately from GIF quantization. Here600ms means16×37.5ms in APNG; GIF can represent only30/40ms approximations. Uniform50ms16-frame GIF800ms is an **explicit retimed control**, paired with100ms8-key800ms.
6. Review all edges and the wrap; verify sole/hip/limb continuity independently. A small head jump does not certify correct knees or contact. Unknown hidden joints stay unknown.
7. Promote only with reviewed original geometry or explicit art evidence, actual hidden-part coverage and scoped acceptance. Do not turn a flattened third-party pose paintover into a complete modular package by labeling masks as parts.

Neural interpolation isn't ground truth either. [FILM](https://film-net.github.io/) handles large raster displacement/disocclusions; it does not guarantee anatomical side identity. [ToonCrafter](https://doubiiu.github.io/projects/ToonCrafter/) supports sparse sketch guidance and explicitly reports semantic-content and appearance/disappearance transition failures. Neither model was run here. Our inserted drawings use imagegen and retained controls, not an unreported research-model backend.

## Executed cross-game findings

[v19 actual study](../../../research/sprite-animation/reverse-paintover-v19/README.md) includes2 RO key attempts,8 midpoint draws and6 Valyria drafts. First RO attempt fails equal-cell foreground cuts. Second is more upright but registration/pose/proportions still differ from its guide. Inbetweens reopen the stride at midpoint4 and vary boot/body size. The actual16-frame loop hair-region jump is22.32px versus18.95px for the8keys; the20px warning remains provisional. This disproves automatic improvement from additional generated frames in this experiment.

Valyria's pinned native walk repeats atlasID13 at exposures1/4. Its six130ms exposures contain five distinct source cells. The generated intermediate phases widen more than the source, and its loop jumps27.93px in the calibrated silver-hair region. Raw generated neutral poses are pixel-different; we preserve that result, not silently substitute an identical drawing to conceal generator drift. Future body/cloth phase reuse must be explicitly authored.

King Lucas's13-frame developer GIF was inspected as another acting/volume comparison, not paintover-generated in this iteration. Its [art director](https://www.devilishgames.com/en/2016/12/14/how-to-animate-a-king-who-has-lost-his-daugthers/) documents Adobe Animate→Spriter→Unity, non-mirrored direction work, and export-deformation repair. It informs modular authoring and mechanical review; its proportions are not our template. Earlier ToS shots and other game studies remain separate evidence, not an inferred shared rig.

## Checker improvement: incomplete image measurements

The initial v19 palette ROI began at y70 and clipped some hair. Those metrics are invalid evidence, retained separately. `palette_patch_probe` now refuses a measured component touching its ROI boundary, returning `INCONCLUSIVE_REGION_TOUCHES_ROI` without a centroid-step score. We remeasured with one whole-clip ROI `[80,10,370,240]`, visually reviewed these images and added actual-image regression cases. This is a calibrated surface-region diagnostic, not a semantic head/leg detector. Recalibrate for every different character/facing/palette; the tool cannot determine all hidden anatomy from pictures.

`scripts/reference-truth.py` checks capture hashes/canvas/order/clock, observed versus inferred points, protected authored keys and loop-pair correspondence. `--require-production` fails closed for all current paintovers. Diagnostic success means the provenance contract is intact, not that the animation is correct.

The next production exercise should transfer the reviewed compact motion into complete original rig/part authoring, then redraw against actual source owner/depth/contact passes. External raster studies remain an observation lane. The approved v17 original source can provide actual bones; this RO experiment cannot supply hidden RO ground truth.
