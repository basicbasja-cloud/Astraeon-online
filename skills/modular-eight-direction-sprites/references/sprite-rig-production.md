# Sprite rigs, directional equipment, and repeatable production

Study iteration 4, 2026-10-11. This addresses the user's rejected hand switch, rejected effect, and request for deep rig research. The [original rig proof](../../../research/sprite-animation/silver-scarf/rig-proof-v4/README.md) exercises these ideas with editable geometry and exported sprites. It establishes a bounded technical workflow, not mastery or approval of the character's look and acting.

## What Ragnarok actually separates

[Ragnarok Research Lab ACT documentation](https://ragnarokresearchlab.github.io/file-formats/act/) describes directional actions, frames, sprite layers, transforms, delays and anchors. These are recorded poses and attachment metadata, not a general-purpose bone rig. The [archived ACT specification](https://github.com/rdw-archive/RagnarokFileFormats/blob/master/ACT.MD) includes reverse-engineering hypotheses; distinguish those from verified implementation behavior. Neither establishes one universal RO FPS.

The pinned [roBrowserLegacy EntityRender implementation](https://github.com/MrAntares/roBrowserLegacy/blob/1370afa878ba296a6ea35f5b76eb904a2611537b/src/Renderer/Entity/EntityRender.js) resolves body, head/headgear, weapon, shield, robe and weapon trail through related actions. Around lines 745–855 it chooses action and facing together, uses the entity's elapsed animation time, and adjusts child positions against body anchors. Around lines 375–465 it applies direction-sensitive ordering; the trail is a distinct attachment. [EntityView](https://github.com/MrAntares/roBrowserLegacy/blob/1370afa878ba296a6ea35f5b76eb904a2611537b/src/Renderer/Entity/EntityView.js) resolves the separate asset families. This is an open community renderer, not proprietary client source.

Classic head-style assets can include the face and hair together. Independently replacing hair over a complete bald head is a useful extension for this game, not proof that every historical RO hair was an isolated scalp layer. The transferable contract is related pose time plus anchors and direction-aware visibility. Do not copy modulo fallbacks that silently select an unsupported replacement action.

## Three viable rig pipelines

| Method | Editable source | Direction handling | Main failure to inspect |
|---|---|---|---|
| Authored cel layers | Complete drawings per supported pose | Eight explicit view banks | Inconsistent anatomy, incomplete hidden parts |
| Directional 2D cutout/mesh rig | Named bones, full painted pieces, corrective attachments | Authored view banks and pose/draw-order changes | Rubber deformation, flat rotation, missing far-side content |
| Modular 3D rig rendered to 2D | Complete meshes, bind data, materials, shared skeleton | Eight camera-relative orientations | Unwanted model look, seams, shading mismatch, export visibility |

All can produce the same 2D part contract. A 2D rig does not reveal the back of an image; a 3D source does not automatically match RO's painted sprite appeal. Rigging solves repeatability and attachment. Acting, silhouette and style need their own review.

The [NotSlot directional sword tutorial](https://notslot.com/tutorials/2020/04/spine-8-direction-character-part-4) demonstrates coordinated attack posing and direction-specific changes. Its example assigns the sword to the left hand, so it cannot establish this game's right-hand invariant. Its warning about replacing a flat sword view is relevant: realistic equipment needs appropriate directional silhouettes. Five views plus mirroring are unsuitable for our asymmetrical loadout unless mirrored anatomy and equipment are explicitly corrected.

## Keep bones, slots, and render pieces distinct

[Spine skins](https://esotericsoftware.com/spine-skins) and the [mix-and-match example](https://esotericsoftware.com/spine-examples-mix-and-match) show how replacement attachment selection can be separated from animation. [Slots and draw order](https://esotericsoftware.com/spine-slots) separate hierarchy from rendering order. Read their linked dependency rules before assuming every skin adds only an image.

Use three contracts:

- **Anatomy:** `right.upperarm → right.forearm → right.hand → weapon.right`. Right means the character's right, independent of screen position or camera orientation.
- **Equipment:** a sword item selects geometry/drawings, material and grip compatibility for the weapon slot. One cape item can contain multiple pieces; one glove item can supply both hands.
- **Visibility:** front/back pieces, frame-specific masks or depth choose which pixels are visible. One scalar order cannot put the same sword both behind a forearm and in front of a torso within one image.

Coverage is deliberate: a closed helmet can suppress the hair slot; underneath it the head remains complete. Cropping the visible hair out of a flattened character would leave missing scalp/face content when that item changes. Inspect each part alone and combinations with covering items removed.

## IK, bind poses, and weights

[Spine IK documentation](https://esotericsoftware.com/spine-ik-constraints) explains one/two-bone targets, bend direction and reach handling. Keep a two-bone target outside the constrained subtree, choose a stable pole/bend side, and inspect near-straight limbs where the solution becomes ambiguous. Do not silently stretch the sword arm to repair an unreachable pose.

[Skin constraints for different proportions](https://esotericsoftware.com/blog/Skin-constraints-for-different-proportions) demonstrates why constraint order matters when proportions change. Apply changes that reposition the torso/hip before solving dependent limbs. A helmet for the same head family is a cosmetic swap; a different arm length is a rig/fit change requiring different checks.

[Spine weights](https://esotericsoftware.com/spine-weights) distinguishes binding from attachment selection. Weight sums, bind positions, mesh topology, triangle ordering, smoothing/pruning and seam matching affect the result. Test a dedicated animation spanning maximum bend/twist ranges. A setup-pose fit is insufficient. Automatic weights are a starting point; prune tiny influences only after confirming deformation remains acceptable.

For conventional linear blend skinning, a vertex uses `v_pose = Σ weight_i · M_pose_i · inverse(M_bind_i) · v_bind`. Normalize weights and preserve the bind transform. Rigid equipment should follow a defined socket without deforming its blade; cloth and flesh may need blended weights or corrective shapes. The current proof uses rigid segmented weights, not a finished smooth skin. Joint seams, cloth deformation and appealing shoulder volumes remain production work.

The SIGGRAPH paper [Bounded Biharmonic Weights, Jacobson et al. 2011](https://igl.ethz.ch/projects/bbw/bounded-biharmonic-weights-siggraph-2011-jacobson-et-al.pdf) was read for its formulation, implementation and limitations (§3–5). It minimizes a biharmonic energy with interpolation and bounded-weight constraints; its faster independent solves normalize afterward. The paper reports locality empirically rather than proving every desired property. It also acknowledges bind-time cost, 3D volume discretization, lack of linear precision and possible foldovers/self-intersections. Better weights do not guarantee collision-free motion. BBW is researched here, **not implemented** in this proof; no claim is made about Spine's proprietary automatic-weight algorithm.

The [Godot 4.3 cutout tutorial](https://docs.godotengine.org/en/4.3/tutorials/animation/cutout_animation.html) provides another cutout workflow and hybrid drawing context. That documentation version is now marked unsupported. It is background reading, not evidence of integration against the current game's engine version. Blender manual pages attempted through the web tool were unavailable; local Blender 4.3.2 behavior was tested directly instead.

## Sword ownership and blade-derived effects

Check ownership at three levels: the named parent, the actual vertex weights, and reopened baked animation. Then inspect visible wrist–grip–guard continuity at each gameplay-scale pose. A right-hand socket assertion cannot approve a drawing that visually attaches to the left arm.

The proof uses actual continuous blade-base/tip samples to make a swept ribbon, with a separate variant for each weapon geometry. History ends at the current attack time, has a short lifetime, tapers with age and clears on interruption. It is not a decorative crescent fitted loosely to the body. Held sprite keys and effect history share authored action time; there is no independent effect clock.

[Unity Trail Renderer documentation](https://docs.unity3d.com/Manual/class-TrailRenderer.html) identifies emission, lifetime, point spacing and sampled gradients as independent controls. Those principles informed the study; the implementation here is an original blade-edge ribbon, not Unity's component. One depth per pixel cannot fully describe translucent ribbon self-overlap or multiple transparent surfaces. The current FX experiment still requires visual refinement and a production transparency strategy.

## Batch contract for a part catalog

Every item must declare rig family, compatible proportion family, supported action/direction/pose coverage, grip family, coverage rules and output sampling convention. Export all items from the same camera, scene time, scale and ground root. Do not center or resize according to each part's bounds. Preserve blank frames explicitly.

Validate in stages:

1. Reopen editable source; check named ownership, weights, binding and actual baked keys.
2. Verify every required tuple resolves. Missing diagonal attack hair is a failure, not a request to mirror the south idle image.
3. Compare independently composed opaque parts against independently rendered whole-character references, including crossed limbs and replacement geometry.
4. Test native-scale normal/quarter-speed playback, body without weapon/FX, occlusion, swap phase, interrupted effect lifetime, and rapid turns during asset loading.
5. Evaluate additional body proportions and action families before calling the pipeline a factory. Measure loading, memory and rendering in the real game before shipping it.

The proof covers one rig, eight facings, eight attack keys, 17 item passes and 48 logical loadouts. It checks tuple coverage for all 3,072 loadout/pose combinations; it does **not** claim visual review of every combination. Only 96 selected combinations have full-scene reference comparisons. The browser harness uses one-facing strips and serialized facing loads to bound its cache. This CPU compositor is a test fixture, not a mandate for the game's renderer.

## Failures found by executing the study

- Painted v3 was rejected for apparent third-pose hand switching, its effect and flattened parts. Correct file timing did not prevent those failures.
- The first original rig windup hid the raised grip behind the head. Moving the hand target outside the head silhouette improved readable ownership without changing its anatomical parent.
- Manually posing while the scene's evaluated action time stayed at frame 1 made rendered poses repeat. Matching scene time to the pose before rendering fixed this; distinct image hashes caught the freeze.
- First independent render comparison found four hard-shading-boundary pixels different across 96 references. The initial report is preserved. Shading input quantization did not remove the discrepancy. A fixed shared capture offset also failed to remove it (six pixels remain in the final export after adding complete bare feet). Independent full-scene owner/alpha tests found no visibility mismatch. Exact color remains a separately failed gate; investigate source topology and renderer precision rather than patching pixels or weakening the result.

## Remaining gates

The authored model is a technical prototype, not approved final RO-inspired art. Its segmented limbs, broad head silhouette, clothing and ribbon require artistic review and refinement. No individual approved turnaround exists yet. Walk, idle variations, hurt, cast, death, further weapon grips, shields, additional body families and real-game transitions remain unfinished. The evidence supports continued rig-based iteration; it does not support a claim of mastery, mass-production readiness, or ACT/SPR binary compatibility.
