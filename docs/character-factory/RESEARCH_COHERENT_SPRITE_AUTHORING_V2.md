# Coherent eight-direction sprite authoring: revised research

Researched 10 October 2026 on `character/production-factory-v2`.
Supersedes the earlier immediate painted-cutout recommendation. Scope: the
approved original ASTRAEON design, eight directions, actions and interchangeable
costumes/equipment. This is a research checkpoint, not a production approval.

## Finding and correction

The source must be a coherent character authored in a common drawing or modeling
space. Independently generated anatomical tiles assembled around calculated
joints failed owner review. Matching dimensions, bones, alpha layers and sockets
did not establish matching anatomy, perspective, shading, overlap or style.

The earlier research identified useful tools for rigs, skins and exports, but
underestimated creation of compatible source art. I applied those capabilities
too early. Export tests cannot replace that proof. Do not reuse the failed
mannequin, turnaround or painted limb atlas as a new approved source.

**Recommendation for this factory contract:** a new, coherent modeled and skinned
character as the master authoring source, animated under a fixed camera with
exact headings, followed by source-native layered painted 2D finishing. This
preserves the original request's deterministic rotation and costume-independent
motion requirements. It requires an actual character asset that passes visual
review. It does not revive the rejected mannequin or turn image cards into a
coherent 3D character. Gameplay output remains painted 2D sprites.

Coherent frame-by-frame painting is the closest researched route to the RO
costume-authoring evidence and a valid finishing method. Krita can author those
layers; Spine can optionally organize drawn sequences and appearance variants.
Pure independent drawing alone does not establish the requested rotating
master rig or exact projection. Our automated generator has not demonstrated
complete compatible source creation. A tool purchase is not the missing
source-art deliverable.

## Stronger Ragnarok evidence

An original 2022 interview with Japanese RO operations staff describes manually
authored pixel art for costume equipment: eight directions, animation frames,
different human/Doram appearances, and additional combat-ready/incapacitated
variants. Staff discuss simplification, size adjustments and repeated exchanges
with Gravity's 2D team. This establishes substantial deliberate artwork creation
for the discussed assets. It does not identify the original body-authoring
application or prove that every historical RO asset used the same technique.
The interview's eight-frame example is not a universal action frame-count rule.
[Staff interview, costume discussion](https://www.4gamer.net/games/001/G000183/20221219027/index_2.html).

ACT reverse engineering documents clips, timing, sprite layers, and body-relative
anchors for heads, weapons, shields and headgear. That is a playback specification,
not an art creation workflow. Preserve the documented uncertainties.
[ACT specification](https://ragnarokresearchlab.github.io/file-formats/act/),
[original reverse-engineering notes](https://github.com/rdw-archive/RagnarokFileFormats/blob/master/ACT.MD).

I inspected zrenderer source as well as its README. `sprite.d` computes an offset
from the selected parent action/frame anchor and subtracts the child anchor.
`renderer.d` handles frame selection and special head/accessory cases. This
corroborates coordinated registration. It is community implementation evidence,
not Gravity's source code.
[Anchor implementation](https://github.com/zhad3/zrenderer/blob/main/source/sprite.d),
[frame selection](https://github.com/zhad3/zrenderer/blob/main/source/renderer.d).

ActEditor source includes layer drawing, anchors and reference controls. It is
useful for studying ACT editing; it does not draw missing anatomy or action
frames. ASTRAEON already uses layered PNG/JSON, so ACT conversion is not required.
[ActEditor source](https://github.com/Tokeiburu/ActEditor).

The owner's weapon sheet shows omission of pixels covered by the hand. Treat
this as a concrete visual reference, not proof of a universal automatic RO
masking system. The owner's body/head/hair/headgear/weapon/cape description
is reference information; it does not silently change ASTRAEON's runtime slots.

## Source drawing and runtime modules have different boundaries

Runtime modularity does not require independently painted rigid limbs. A complete
body pose can be one coherent image while head/hair, sword and cape are separate
coordinated frame sequences. Body and costume can be drawn together for fitting
in an editable source, retaining meaningful layers and the hidden surfaces
needed for supported removals. All layers describe the same pose and projection.

Proposed source groups:

- **Body:** connected neck, torso, pelvis, arms, hands and legs. Every pose must
  read as a complete figure. Concealed surfaces must exist where substitutions
  can reveal them.
- **Outfit:** clothing fitted to that body, including cuffs, trousers, gloves
  and boots as appropriate. A replacement breastplate is not a full second outfit.
- **Head/hair:** a registered authoring group; retain editable hair separation
  where the runtime requires independent Hair selection.
- **Weapon:** an authored view for the actual grip and action pose; omit covered
  hilt pixels in that exported frame when necessary.
- **Headgear/cape:** registered to the same pose, with folds, reveals and overlap
  changes authored where needed.

These are our proposed boundaries. Their validity comes from complete-character
and removal tests, not from matching a tool's default skeleton.

## Tools supported by concrete evidence

| Tool/route | Evidence inspected | Useful capability | Missing ASTRAEON proof |
|---|---|---|---|
| Krita | Official animation workflow and PNG export | Animated painting layers, key poses, onion skins and drawn inbetweens | Our coherent source, views, grips and action coverage |
| Spine drawn sequences | Original Dragon JSON and region manual | Coordinate deliberately drawn frames as attachments/sequences | Our independent modules, views and exports; no local editor test |
| Spine designed multi-view rig | Official animator's source ZIP and explanations | Authored turnaround poses, attachment switching, appearance skins | Source art must already fit; sample does not prove our no-mirror/projection requirements |
| Aseprite | Official per-layer/tag/frame CLI export | Reproducible sprite export and finishing | Source painting/animation; approved painted style must be retained |
| Blender genuine skinned source | Official skinning docs and shipped-game accounts | Coherent geometry, reusable motion, deterministic multi-angle renders | Approved model, weights, materials, cloth and grip |
| ACT/SPR tools | Format research and original editor/renderer code | Study registration and existing playback | Original character art; no need to change runtime |
| PixelLab | Current vendor tool manuals | Static rotations, animation and outfit transfer through distinct tools | Removable layers, exact grip/projection and all required actions |

[Krita animation](https://docs.krita.org/en/user_manual/animation.html),
[Krita export](https://docs.krita.org/en/reference_manual/render_animation.html),
[Spine sequences](https://en.esotericsoftware.com/spine-regions),
[Aseprite CLI](https://www.aseprite.org/docs/cli/),
[Blender skinning](https://docs.blender.org/manual/en/latest/animation/armatures/skinning/index.html).

### Actual Spine project inspection

The official Dragon example demonstrates drawn frame-by-frame wing animation.
I parsed its stable 4.2 JSON: two nine-image sequence attachments with sequence
timelines. This proves Spine supports deliberately drawn frames as well as bone
animation. It does not prove an eight-direction modular human factory.
[Dragon example](https://en.esotericsoftware.com/spine-examples-dragon),
[original JSON](https://github.com/EsotericSoftware/spine-runtimes/blob/4.2/examples/dragon/export/dragon-ess.json),
[local inspection receipt](research-v2/spine-dragon-inspection.json).

The official eight-direction ZIP contains 131 entries, 114 PNGs, several native
Spine projects and art folders for five named directions. Its bundled
`8direction-chara.json` fails standard JSON parsing at line 50, where a separator
between skin objects is missing. The native complete `.spine` file was not
tested in the editor. Do not claim a local import/render pass or independent
eight-view/no-mirroring compatibility. Archive inspection took place in memory;
no sample artwork was vendored or used as ASTRAEON source.
[Official project download](https://esotericsoftware.com/files/projects/twitch/twitch-8-direction-chara.zip),
[inspection receipt](research-v2/spine-eight-direction-inspection.json).

The official animator recommends turnaround poses as the base for directional
animations, reserving skins for appearance changes. Staff also discuss when
separate directional skeletons are appropriate and why torso turning during a
sword action complicates rig organization. These are authored workflows, not
automatic conversion of a concept into correct attacks.
[Animator explanation](https://en.esotericsoftware.com/forum/d/12414-keyable-skin-switching),
[rig tradeoffs](https://en.esotericsoftware.com/forum/d/24092-best-practices-of-rigging-8-directional-character-in-spine-2d/2).

### Shipped-game production accounts

Hades developer `kid_zomb`, marked as a developer on Steam, confirms that many
characters including Zagreus were animated/rendered in 3D during production,
then exported as thousands of frames from many angles for a 2D runtime. This
establishes a shipped multi-angle route; it does not establish costume modules
or disclose all source tools.
[Developer response](https://steamcommunity.com/app/1145360/discussions/0/1738883810796606862/).

Dead Cells artist Thomas Vasseur describes a model sheet, simple 3ds Max model
and skeleton, convincing timed key poses first, then PNG/normal-map rendering.
He discusses animation reuse, armor additions, retiming and pixel flicker/detail
tradeoffs. This is firsthand evidence, but a side-view pixel-art game is not a
local proof of ASTRAEON's painted eight-direction paperdoll requirements.
[Artist's production account](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-).

Tree of Savior art director MAGGI describes fixed quarter-view choices and
hand-drawn textures. This supports compatibility between a painted look and
structured rendering; the interview does not specify a complete modular sprite
export workflow.
[Original interview](https://treeofsavior.com/page/news/view.php?n=337).

### AI features must be evaluated separately

PixelLab's eight-rotation Pro manual specifies eight static views and a current
168 x 168 maximum per frame. Its automatic-animation manual specifies four
directions and <=64 x 64. These are different tools; this is not a claim that
all its animation endpoints have that limit. Outfit transfer edits input frames
in size-dependent batches, without documenting independently removable outfit
layers. None establishes exact hands, projection or complete modular action art.
[Rotations](https://www.pixellab.ai/docs/tools/create-8-rotations-pro),
[automatic animation](https://www.pixellab.ai/docs/tools/create-animations-automatic),
[outfit transfer](https://www.pixellab.ai/docs/tools/transfer-outfit-pro).

Other AI/model/video/paint-propagation tools from the first report remain
auxiliary candidates. No reviewed evidence establishes a complete compliant
ASTRAEON source. No paid job, tool purchase, model download or installation
was performed in this checkpoint.

## Grip and overlap specification

The hand owns visible fingers and palm. Register the weapon grip to the actual
hand pose. Covered hilt pixels can be omitted in the exported weapon frame or
excluded with an explicit hand mask. Retain the complete editable weapon source
for other poses; visibility changes with the pose.

Hilt omission cannot fix wrong blade direction. Define wrist, grip, guard and
blade-tip positions from a shared pose. Review W/NW/N as complete figures,
hand/weapon close-ups and isolated weapon views. Blade direction is action-specific:
it follows the approved pose and attack arc rather than pointing forward in
every animation frame.

A sword or cape crossing both sides of a figure may require front/back sublayers
or a changing draw order. Globally placing a whole item above/below the body
cannot handle every crossing. Use existing runtime front/back equipment support
where appropriate. This is our proposed compositing specification, inferred
from the constraints and owner's references, not Gravity's internal specification.

## Small proof before another factory build

1. Establish how a new coherent editable modeled/skinned source matching the
   approved design will be obtained and authored. Preserve the requested master
   rig, fixed camera and reusable motion. If available capabilities cannot create
   acceptable source art, identify the missing artist/model deliverable explicitly
   before another generation attempt. A painted-frame editor is downstream of
   that pose authority, not a replacement for it.
2. Author one coherent standing source with the concealed surfaces it needs.
   Review dressed and equipment-free figures at 176 px authoring height and
   88 px runtime height against the approved concept.
3. Prove W, NW and N alongside SE early. Require consistent proportions,
   handedness and independent view surfaces. Rotate the same coherent character
   under the fixed camera at the exact headings required by the original request.
   Painted finishing must follow those pose/projection guides.
4. Demonstrate original sword, alternate sword, no sword, no cape and removed/
   replaced outfit on the same poses. Show source layers and correct neck,
   cuff, waist and grip boundaries. Obtain owner visual acceptance.
5. Then author attack anticipation, strike and recovery keys in SE and N;
   prove grip, torso turns and depth changes. Approve key poses/timing before
   completing a whole clip. Follow with Walk contact keys.
6. Expand to all eight views and the agreed action matrix. Complete costumes
   need fitting and deformation/redraw work. Weapon classes can require new
   grips and actions. Shared timelines do not create all item artwork.
7. Build packaging automation around the accepted source/export convention,
   using the existing lossless PNG/JSON pipeline, shared clock and sockets.

Technical invariants: S/SW/W/NW/N/NE/E/SE; 320 x 320 authoring canvas; root
(160,264); reference height 176; uniform 0.5 runtime scale; named clips and
explicit durations; mandatory BaseBody/Hair/Outfit/Weapon/Headgear/BackAccessory
slots. Full-canvas layers need no second socket translation. No per-frame
crop/fit, silent mirrors or invented coverage. [Runtime contract](../MODULAR_SPRITES.md).

Show each visual gate to the owner before expanding work. A failed gate requires
source-route diagnosis, not another bulk bake of an abandoned candidate.
Record technical verification and visual approval separately.

## Limits and current result

This is targeted follow-up research into source-authoring failure, not an
exhaustive list of every internet tool. Manuals establish features; inspected
projects establish data structures; creator accounts establish shipped precedents.
None is a local end-to-end ASTRAEON test. The original RO authoring software
remains unverified.

Only the concept is approved. Turnaround and cutout pilot are rejected. No
complete motion/costume/weapon package has passed owner review. The interrupted
pilot is excluded from coverage. The next production decision is how to obtain
and author a coherent editable master source, before choosing another exporter.
