# Fresh eight-direction character production research

Researched 10 October 2026. Branch: `character/production-factory-v2`.
Owner instruction: abandon the failed character approach and investigate a new
Ragnarok-preferred production method for motions, costumes, and weapons.
The attached factory pack is reference material; it does not override that request.

## Decision

Build the next candidate as **painted 2D artwork first**. Use an eight-view
turnaround with direction-specific body parts, a shared motion timeline, costume
skins, and explicitly authored hand grips and front/back equipment overlap.
Bake to ASTRAEON's existing layered PNG format. The recommended authoring tool
for scaling the approved artwork is **Spine**, with Krita for painting; a tool
purchase is not a prerequisite for the first visual candidate.

This is a workflow recommendation, not a claim that a finished character exists.
No researched tool has been tested here end to end for ASTRAEON's complete
eight-direction, all-action, interchangeable-equipment contract. No automatic
generator should be treated as having solved that contract from its marketing page.

The rejected mannequin, its proposed repairs, warped old composites, and geometric
SVG characters are excluded as new visual sources. Preserve them as historical
evidence. Keep useful runtime registration and packaging contracts.

## What Ragnarok actually establishes

ACT stores animation clips, frames, timing, events and sprite layers. Its anchors
position heads, weapons, shields and headgear relative to the body. This supports
separate artwork coordinated by animation metadata. It does **not** establish
that Gravity originally produced its characters using Blender, skeletal 2D tools,
or an automated eight-view generator. The research is community reverse
engineering, not a first-party account of Gravity's art department.
[ACT specification](https://ragnarokresearchlab.github.io/file-formats/act/).

The independent zrenderer implementation exposes body/job, head, headgear,
garment, weapon, shield, palettes, action, frame, and a canvas with an origin.
This is concrete evidence of compositional variation, rather than a single
complete character animation being repainted for every combination.
[Renderer source and usage](https://github.com/zhad3/zrenderer).

Action/direction indexing is documented by another renderer as
`action = animationType * 8 + direction`. Use this as a useful reference model,
not an excuse to replace ASTRAEON's named action/direction schema.
[ragassets source](https://github.com/adsonpleal/ragassets).

Ragnarok Research Lab reports measured ACT timing intervals of 24 ms; older
community tools often used 25 ms. ASTRAEON should keep explicit millisecond
durations and its gameplay events, rather than inherit an unrelated legacy tick.
[Timing experiments](https://ragnarokresearchlab.github.io/rendering/animation-systems/).

For the new art, carry forward readable compact anatomy, elevated game camera,
strong silhouette, controlled highlights, restrained detail and clear action keys.
These are our art-direction choices inspired by the requested reference, not
format requirements. A large detailed illustration is only useful if it survives
the actual game-scale preview.

## Tools compared

“Documented” below means described in a developer manual or original implementation;
“publisher claim” means advertised, without a local production test. The last
column is our assessment of fit, not the vendor's guarantee.

| Tool / route | Evidence-backed capability | Remaining work / limitation | ASTRAEON decision |
|---|---|---|---|
| **Krita** | Frame-by-frame painting, animated layers, timeline and onion skins | Drawing, direction consistency and equipment registration remain artist work; large animation documents consume memory | Preferred painted-art editor; small documents per action/view. [Manual](https://docs.krita.org/en/user_manual/animation.html) |
| **Spine** | Skins reuse animations across attachment sets; official eight-direction example; image sequences and automated exports | Must author the views, setup poses, grips, redraws and depth changes. A 2D bone rig cannot invent a hidden surface | Best researched scaling route for painted modular characters; bake PNGs to current runtime. [Skins](https://en.esotericsoftware.com/spine-skins), [eight-view example](https://esotericsoftware.com/forum/d/25378-animating-different-directions), [export](https://esotericsoftware.com/spine-export) |
| **Aseprite** | Tagged animation, separate-layer CLI exports, PNG sequences and JSON | Excellent sprite organization, but not an automatic eight-direction character or anatomy solution | Optional finishing/export editor if the approved look becomes deliberately pixel-authored. [CLI](https://www.aseprite.org/docs/cli/), [sheets](https://www.aseprite.org/docs/sprite-sheet/) |
| **Spriter** | Character maps replace/hide images; variations can be batch exported | Supplied manuals are old; modern compatibility and pipeline need a fresh pilot. Directional artwork still required | Lower-priority cutout alternative, not a reason to change runtime. [Maps](https://www.brashmonkey.com/spriter_manual/what%20are%20character%20maps.htm), [batch export](https://www.brashmonkey.com/spriter_manual/batch%20exporting%20animations%20from%20character%20files.htm) |
| **PixelOver** | Split painted artwork, bind 2D bones, animate and export; also imports 3D bones | Pixel-art-oriented output is a style choice; does not supply a correct eight-view modular character | Evaluate only if pixel treatment is approved. [2D tutorial](https://docs.pixelover.io/tutorials/bones_animation/), [export](https://docs.pixelover.io/manual/export/) |
| **Blender + Rigify** | Modular metarig construction and rig generation | An auto-rig is not a designed character, correct skin weights, finished sword animation or painted sprite | Installed Blender 5.2.2 LTS is available. Keep as optional pose reference after the new visual direction passes; do not resume procedural mannequin production. [Developer docs](https://developer.blender.org/docs/features/animation/rigify/) |
| **2DFactory** | Publisher documents multidirectional rendering, modular sheets, pivots, sockets and JSON; changelog states Blender 5.2 support | Needs a good model and authored motion first; exporter schema and camera conventions need adaptation; automatic crop must be disabled or reconstructed | Strongest researched Blender export shortlist if a later 3D source is deliberately chosen. Not an anatomy fix. [Publisher and changelog](https://superhivemarket.com/products/2dfactory) |
| **Sprite Render Kit / Get Sheet Done** | Publishers document sprite rendering and sheet automation | No reviewed evidence of a complete body/costume/weapon registration system for our contract; old SRK docs describe Blender scene/layer conventions | Export utilities only; lower priority than a modular exporter. [SRK docs](https://superhivemarket.com/products/sprite-render-kit/docs), [Get Sheet Done docs](https://superhivemarket.com/products/get-sheet-done/docs) |
| **DTWorldz Sprite Capture Studio** | Creator advertises 2/4/8-direction body/equipment captures with separate color and depth | Announcement is not a verified export contract; source-asset rights, supported clips, camera, dimensions and editable inputs need inspection | Promising targeted prototype; not selected without a sample passing our contract. [Creator announcement](https://www.linkedin.com/posts/deniz-traka_gamedevelopment-blender-artificialintelligence-activity-7500084750750199810-PTzM) |
| **Mixamo** | Adobe documents humanoid auto-rigging and an animation library | Realistic clips need proportion/style adjustment and hand/weapon correction; a library does not supply every game-specific skill | Optional motion reference, after a valid character source exists. [Adobe FAQ](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html) |
| **Cascadeur** | Posing, physics assistance, inbetweening and animation import/export | Still needs animation judgment; free tier cannot export FBX/DAE and is non-commercial | Optional animator aid, not required for the initial candidate. [Help](https://cascadeur.com/help/faq), [plans](https://cascadeur.com/plans) |
| **PixelLab** | Eight rotations, reusable skeleton templates, inpainting and outfit transfer are documented | Rotation, skeleton animation and outfit transfer have different size limits. Outfit transfer edits frames; independent equipment layers are not established by those docs | Good bounded draft experiment for pixel-style art. Do not select it as a proven paperdoll factory. [Rotations](https://www.pixellab.ai/docs/tools/create-8-rotations-pro), [skeletons](https://www.pixellab.ai/docs/tools/animate-with-skeleton), [outfits](https://www.pixellab.ai/docs/tools/transfer-outfit-pro) |
| **Scenario** | Eight-direction app; custom style and character model training | Vendor consistency claims do not establish exact joint locations, frame timing, detachable equipment, or complete motions | Potential style/reference assistance; avoid training before approved data exists. [Eight directions](https://www.scenario.com/apps/8-direction-sprite-generator), [character training](https://help.scenario.com/articles/4280773511-train-a-consistent-character-model) |
| **Host-native image generation** | Available in this session for a fresh raster character design | Generated raster is a visual candidate, not editable layered art, rig data, an animation proof or an approval | Use for one new visual candidate; preserve raw output and prompt. No batch of motion generation before review |
| **ControlNet + IP-Adapter / ComfyUI** | Spatial conditioning and image-reference conditioning documented by original authors | Hardware/setup cost, temporal drift, occlusion and part registration still require measurement; conditions are not hard geometric guarantees | Research fallback, not the first rescue route. [ControlNet](https://github.com/lllyasviel/ControlNet), [IP-Adapter](https://github.com/tencent-ailab/IP-Adapter) |
| **Wan-Animate** | Original project accepts a reference character and driving video for animation/replacement | Video output does not prove clean alpha, loops, eight views or separable costumes/weapons | Motion visualization only until a sprite-contract pilot proves more. [Original repository](https://github.com/Wan-Video/Wan2.2) |
| **EbSynth** | Publisher describes propagation from painted keyframes across video | Paint propagation does not create missing directional art or a modular body; overlap and reveal still need repair | Optional paintover experiment after motion is already correct. [Publisher](https://ebsynth.com/) |
| **Tripo** | Developer docs provide generated models, rigging and animation operations | Mesh editing may discard binding; model segmentation does not establish rig-compatible interchangeable costumes. A 3D mesh still needs sprite rendering and visual finishing | Excluded from the immediate 2D-first candidate; later optional model-source experiment only. [Rig docs](https://docs.tripo3d.ai/animation/rig-v1-0-20240301.html), [current rig API](https://developers.tripo3d.ai/en/docs/animations-rig) |
| **RO ACT/SPR tools and renderers** | Read/render existing layered sprite formats | Reading Ragnarok assets does not create an original ASTRAEON character or establish reuse rights | Study composition/timing and original code; do not vendor game artwork. [Formats](https://ragnarokresearchlab.github.io/file-formats/act/), [renderer](https://github.com/zhad3/zrenderer) |

## Important limitations verified in the shortlist

PixelLab's specific eight-rotation Pro tool documents a maximum 168×168 frame,
with its own direction ordering. Its skeleton tool documents 16/32/64/128/256
square canvases. Outfit transfer at 171–256 px handles up to three frames per
request and is documented for Aseprite/Pixelorama extensions. Do not generalize
one tool's limit to every PixelLab API or equate a transparent composite with
an independently authored Outfit layer. See the three PixelLab manuals above.

Spine's official animator recommends a turnaround template for directions,
with skins representing appearance changes. Use named direction/action
animations on shared logical bones and direction-specific attachments. Adjust
the animation per direction when projection changes, rather than blindly copy
all transforms. [Animator explanation](https://esotericsoftware.com/forum/d/10436-multi-directional-character).

Spine can export fixed crop bounds, image sequences and named skins, with saved
export settings. Our adapter would render selected component groups on the same
timeline and canvas. **Exact ASTRAEON layer composition remains an integration
test**, especially where one weapon crosses both sides of the body in a frame.
[Export manual](https://esotericsoftware.com/spine-export).

Current page snapshots show Spine Essential $69 and Professional $379 (discounted
from $99/$449). Meshes/IK require Professional; the editor trial is not a production
save/export license. Cascadeur lists Indie $19/month or $8/month billed annually,
with a revenue condition; its free tier is non-commercial and exports CASC only.
These are observed prices, not a budget authorization. No purchases, provider
jobs, account creation or installations were made. [Spine pricing](https://esotericsoftware.com/spine-purchase),
[Cascadeur pricing](https://cascadeur.com/plans).

## How to support all motion, costumes and weapons

Separate **body shape**, **animation family**, and **equipment appearance**.
“All weapons” cannot mean one identical sword swing for a dagger, greatsword,
spear, bow and staff. Share locomotion where the grip/posture is compatible;
author different stance, attack and skill timelines for each weapon family.
An alternate sword within one family can share grips; a two-handed weapon needs
both hand contacts, appropriate shoulder poses and a different motion contract.
This is our production design, rather than a vendor promise.

Each item has its own authored art, fitting profile, attachment transform,
front/back overlap policy, coverage and compatibility manifest. Each costume
shares the body's joints but retains real sleeves, boots, folds and exposed-skin
rules. Palettes can supply inexpensive color variants; recoloring is not a
different costume silhouette. Longer coats, capes and skirts require their own
secondary motion or pose substitutions. Bulkier body variants need a fitting
pass; they are not automatically compatible because bone names match.

Author hidden limb surfaces where equipment can be removed. Keep skin under a
removable sleeve and hands under gloves. Render test combinations with an empty
slot, alternate costume, alternate sword, headgear and back item. Changing one
slot must not alter unrelated body geometry, timing, camera or anchor.

During a swing, a blade can pass behind the torso while its handle remains in
front. A single fixed layer order is insufficient for that frame. Split the
source into front/back pieces or use an agreed mask/pass scheme, then map to
the existing runtime's supported slot/draw-order facilities. Do not create a
new runtime dependency merely because the authoring tool has one.

## Concrete production gates for the new candidate

1. **One visual identity:** one finished elevated SE view, with a complete
   costume and a believable single-handed sword grip. Inspect at 320 authoring
   scale and 160 runtime scale, on light/dark backgrounds. This first image is
   a composite art candidate, with no claim of modularity or accepted motion.
2. **Eight-view source:** independently author S, SW, W, NW, N, NE, E, SE. Lock
   head/body proportion, palette, camera, ground and anatomical right hand.
   Mirroring is prohibited for this asymmetric equipment contract. Inspect a
   static turnaround before animating.
3. **Layer pilot:** independent BaseBody, Hair, Outfit and Weapon art in all
   views. Empty-slot tests and one actual alternate sword/costume must pass.
   Isolated colored markers and subtraction from a flattened composite cannot
   satisfy this gate. Accessory slots may be explicitly empty until real art exists.
4. **Motion pilot:** author Walk and BasicAttack for S, SE and N first. Review
   normal speed, quarter speed and keyed poses. Require planted-foot readability,
   plausible elbows/wrists, a stable grip and correct blade overlap. Add the
   other views only when these different projection cases work.
5. **Nine-action core:** Idle, Walk, Run, BasicAttack, SkillAction, Hit, Death,
   Guard, Dash in every direction, each with its own appropriate timing.
6. **Complete current game contract:** resolve the broader 18-entry wardrobe
   contract explicitly. The current Swordsman blueprint requires 16, with Sit
   optional and Blink excluded; the global runtime also names both. No copying
   Idle into an absent action and declaring completeness. Preserve a matrix
   of required, optional, unsupported and authored states.
7. **Equipment expansion:** add one item at a time against approved motion,
   with family compatibility and extreme-pose checks. Expand body variants
   only after one complete dedicated character passes.

Owner visual approval is distinct from structural test success at each gate.
A successful hash/pixel comparison cannot override the owner's rejected arm,
sword or overall anatomy. All new artifacts remain `DEV_ONLY` until accepted.

## ASTRAEON adapter contract

Preserve existing named actions, durations, pose IDs, sockets and draw ordering.
Author full 320×320 RGBA frames at root `(160,264)`, reference anatomy height 176.
Compile the current patch's uniform 0.5 scale to 160×160, root `(80,132)`, reference
height 88. Equipment can extend beyond the anatomy bounds. Do not resize each
frame/direction independently or anchor on the changing alpha bounding box.

One registered canvas covers every exported component and action. Source exports
must carry action, direction, frame/pose ID, duration, equipment family, sockets,
overlap order, source hash and approval state. Empty frames are explicit. Bake
with the existing packer/validator; do not ship Spine data, Blender scenes, or a
third-party engine plugin as a substitute for ASTRAEON's sprite definition.

The adapter is a future implementation requirement. No new adapter or playable
character package was implemented as part of this research.

## Scope and effort controls

The current patch specifies 192 frames per direction across 18 action names:
1,536 composite frame positions across eight directions. Its current 16 required
Swordsman actions total 1,392 positions. The machine-readable
[coverage matrix](new-production-matrix.json) distinguishes all three contract
states and marks the new candidate's motion coverage as empty. The final count and
class applicability must be reconciled with the Swordsman blueprint first.
Layer and variant counts then multiply the export workload. They do not justify
making thousands of independent AI generation calls.

The first visual milestone has **one candidate**, not many parallel redesigns.
Allow at most one targeted art correction before a route review; do not endlessly
patch a rejected source. Later work proceeds only from accepted art with saved
editable source. Tool discovery is complete enough to choose a route; further
research must answer a concrete unresolved question rather than restart browsing.

If the new 2D candidate still cannot reach the requested art standard, the honest
fallback is an original layered turnaround commissioned from a character/sprite
artist using this brief, followed by automation of exports and validation. More
scripts cannot replace missing art quality. This is a fallback recommendation,
not a message to an artist or a spending decision.

## Local skills and execution evidence

Reviewed the installed `game-asset-production`, `sprite-pipeline` and `imagegen`
skills. The useful common rules are capability discovery, explicit dimensions,
source/provenance retention, an approved seed before expanding animation, and
visual review after normalization. Sprite-pipeline recommends generating a strip
together to reduce drift; that does not establish modular layers or guarantee
eight-direction continuity. Its normalizer must also be checked against our
fixed-root contract before adoption.

The game-dev CLI is unavailable locally; native Blender is installed and was
verified earlier. The researched commercial products, their plugins and remote
AI services were **not** installed or benchmarked. A failed web fetch for some
Blender manual pages was supplemented with official developer documentation.
Scenario's official public skill repository was discovered as workflow reference,
not installed or adopted as instructions.
[Scenario skill catalog](https://github.com/scenario-labs/skills).

This is a broad, task-focused survey of original documentation, source projects
and publisher material across painted animation, skeletal 2D, 3D baking, motion
libraries, AI sprite generation, conditioning, video transfer and RO formats.
It is not an exhaustive inventory of every tool on the internet.

## New visual artifact produced after research

One fresh painted Swordsman identity candidate and one bounded correction were
generated with host-native image generation. Raw sources, prompts, hashes, alpha
inspection and a browser review are retained under
`authoring/characters/swordsman-production/fresh-2d/candidate-01/`.
The selected `candidate.png` is **DEV_ONLY / OWNER_REVIEW_PENDING**. It is one
composite view, not a normalized frame, source-part library or motion proof.
The blade still passes in front of the leg area; exact projection and proportions
are unverified. No further automatic correction loop or motion expansion was run.

The local review page loaded in Chrome with no JavaScript errors and displayed
88/176 px silhouette previews on contrasting backgrounds. This validates the
review page only. It does not establish acceptable anatomy or game integration.
