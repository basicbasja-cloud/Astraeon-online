# New source evidence and application notes

This is an original analysis of retrieved sources. It explicitly excludes our prior slash posing as motion reference. See retrieval.json for per-source HTTP/commit/file receipts. “Retrieved” does not mean a whole page/video was read or all clips accepted.

## Actual-source findings

### 1. Quaternius UAL2 Standard

Creator [distribution](https://opengameart.org/content/universal-animation-library-2) and bundled license identify CC0. The exact downloaded Standard GLB contains **43 named animation records**, a **65-joint skin**, and 67 nodes. A_TPose is excluded; two Dash clips are now included for optional research, giving42active overview candidates. The advertised full library count belongs to another acquisition scope.

The new file includes Chest_Open, Consume, OverhandThrow, Walk_Carry_Loop, lay/get-up, farming, shield/sword actions and reactions. Real source channels/times were read and Blender evaluated nine native key-time samples per included clip. This is new external motion data, not the old own rig. Contact/weapon/palm surfaces are still unmeasured; bone samples alone do not approve motion adaptation.

Application: first test interaction/reaction/carry families alongside melee so the factory architecture stops assuming every action is a slash. Do not transfer full-scale adult motion to our proportions without contact-aware adaptation.

### 2. Legacy KayKit 1.2 versus current pack

The [creator OGA page](https://opengameart.org/content/kaykit-character-animations) provides the exact legacy1.2 archive/CC0 license and three animated previews. That GLB contains **30 records**, including four Dash and BasePose; BasePose is excluded, leaving29candidates including optionaldash.

Actual skin has **six joints**, not a legged humanoid chain. Good for gesture/hand-slot/simple silhouette examples, inadequate for validating our hip–knee–ankle ownership. The [current creator page](https://kaylousberg.itch.io/kaykit-character-animations) describes a newer category/rig-size library; its free package has not been downloaded here, and its count is not added to acquired motions.

Application: always audit the actual skeleton and version. “Walk” in a clip name is insufficient for leg validation. Same creator does not imply same rig/content.

### 3. Real GIF clock and preview boundaries

All three creator GIFs were decoded: **250+250+245 = 745 exposures**, 10s each. Native GIF delays and repeated poses remain. Some clips contain title changes and multiple actors at once; they are not continuous single-actor ten-second actions. Preview2 includes a HOP label followed by CLIMBING; preview3’s ending contains WAVE then a title transition. Those boundaries must be annotated before extracting action intervals.

Application: build shot/label intervals before assigning semantics or loop seams. Use fixed per-actor crop only after actor/shot review. The full montage is evidence, not an anatomical motion dataset by itself.

### 4. Isometric Hero author archive

Fresh [creator archive](https://opengameart.org/content/isometric-hero-and-heroine) supplies separate body/head/equipment PNGs. Actual selected atlases are 4096×1024: 32 frame columns ×8 directional rows of128px cells. Original diagnostic boards use clothes+male_head1 only, credit Clint Bellanger and retain cell IDs.

Eight action boards include shared hit/death rows: 272 action-cell uses, **256 unique grid cells**. Native PNG clock is unknown. These are diagnostic composites; engine draw order, world support and exact cardinal mapping are not recovered.

Application: sparse action poses can be legible at game scale and reuse separate appearance parts. Draw-layer semantics and hidden replacement content still require a target adapter; we keep source art out of our original shipping assets.

### 5. Flare runtime/descriptor separation

Pinned current content descriptors provide eight facing indexes and action definitions. The unpacked default file explicitly identifies itself as a demonstration template, not an engine-loaded file. Actual male item descriptors were separately read. Values include stance4/800ms/back_forth, run8/533ms/looped, swing/cast/shoot4/400ms, hit2/133ms and die6/800ms.

[Engine](https://github.com/flareteam/flare-engine) parser and avatar implementation are separately pinned. These values are source-specific, not a recommendation that our attack must be400ms or that the old author PNG uses the same clock.

Application: distinguish body keys, repeated exposures, display cadence and gameplay events. An action can have few drawings with different playback semantics.

### 6. The Mana World action names and fallbacks

Fresh pinned human-male.xml actually provides stand, walk, attack, attack_bow, sit, ride variants and dead. Four direction rows are present. Walk has six-frame sequences with80ms delays; attack has four with80ms and an end marker. Several ride/spawn aliases point to the same static seated frame bank; dead directions share one frame.

The paired hair XML inherits its base animation. See [client data](https://github.com/themanaworld/tmwa-client-data).

Application: explicit fallback names are not evidence of newly drawn motion. Coverage reports need unique frame/sequence IDs, supported directions and static versus moving semantics, including inherited items.

### 7. LPC compatibility and attribution

Pinned body.json declares animation families including spellcast, thrust, walk, slash, shoot, hurt, watering, idle, jump, run, sit, emote, climb, combat and one-hand variants. Body families and credits/licenses differ. The [generator](https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator) supports item-level output/credits.

Its recursive tree response is **truncated**; do not claim complete repository asset enumeration from the61,027 returned entries. Specific definition files were retrieved separately.

Application: a machine-readable action/item/body compatibility matrix is part of production. Four-direction mechanics from LPC do not prove our eight views, art quality or asymmetric wardrobe compatibility.

### 8. Wesnoth timing plus gameplay branches

Three actual unit configs were read. White Mage includes18 idle images, healing/magic frame families, staff melee, separate halo timing and hit/miss sounds. Female idle is explicitly a static placeholder; names alone overstate coverage. See [AnimationWML](https://wiki.wesnoth.org/AnimationWML).

Application: body, effect and sound need coordinated clocks while unique body drawings can be sparse. Male/female/item coverage may differ even within a single unit definition. Hex-game facing must not be mislabeled as our compass map.

## Research and documentation synthesis

| Primary source | Read scope this round | Practical lesson | Unexecuted work |
| --- | --- | --- | --- |
| [ReConForM](https://arxiv.org/abs/2502.21207) | abstract/method summary | contacts relate morphology and surfaces, not only matching joint angles | full solver/local benchmark |
| [Skeleton-Aware Networks](https://deepmotionediting.github.io/retargeting) | author method/demo text | topology/rest structure matters in transfer | model inference/our retarget |
| [PFNN](https://www.pure.ed.ac.uk/ws/files/35467734/phasefunction.pdf) | selected phase/contact/runtime sections | contact labeling needs correction; root and contact-aware IK are separate | paper experiment |
| [Learned Motion Matching](https://www.ubisoft.com/en-us/studio/laforge/news/3NWqwcMU9lMfumgfPAEfka/learned-motion-matching) | author overview | retrieval conditioned on motion context; useful transition research | source database/runtime |
| [Robust Motion Inbetweening](https://www.ubisoft.com/en-us/studio/laforge/news/1ERUZiYmmtUBYZ4KvVvmFP/robust-motion-inbetweening) | author overview | endpoint/transition context matters; more frames is not automatic acting improvement | trained inference |
| [DeepMimic](https://xbpeng.github.io/projects/DeepMimic/index.html) / [AMP](https://xbpeng.github.io/projects/AMP/index.html) | author project abstracts | reference motion, style and dynamic feasibility are separate | physics training |
| [AniDoc](https://github.com/robbyant-research/AniDoc) | pinned README | color/sketch video conditioning; documented14-frame preprocessing can discard native timing | inference/oursheet quality |
| [ToonCrafter](https://arxiv.org/abs/2405.17933) | abstract | cartoon interpolation is a candidate, not a replacement for corrected keys | inference/hidden anatomy QA |
| [Sprite Sheet Diffusion](https://arxiv.org/abs/2412.03685) | abstract | sheet consistency is a research topic, not a zero-error promise | model/reproduction |
| [Spine skins](https://esotericsoftware.com/spine-skins) and export | documented slot/skin/timeline concepts | logical items and draw attachments have different roles | target runtime implementation |
| [Godot AnimationTree](https://docs.godotengine.org/en/stable/tutorials/animation/animation_tree.html) | state/root-motion documentation sections | transitions and movement must be tested together | in-game integration |
| [Larian animation slots](https://docs.larian.game/Animation_set_resource_panel) | weapon/state slot listing | weapon-specific families, sitting/lying, cast stages and fallbacks | original actor implementation |

### Research dataset rights findings

[LAFAN1](https://github.com/ubisoft/ubisoft-laforge-animation-dataset) identifies CC-BY-NC-ND4.0. [AMASS](https://amass.is.tue.mpg.de/license.html) and [BABEL](https://babel.is.tuebingen.mpg.de/license.html) restrict commercial use/training and redistribution. We read documentation/license pages and **did not acquire their motion datasets**. HumanML3D’s code repository does not override originating AMASS rights. They inform methods/schema, not our commercial reusable source asset bank.

### External skills as research

Pinned Scenario sprite skill warns about source-frame ordering and alpha; pinned sprite-gen motion QA describes image-region motion checks; Phaser skill covers runtime animation state/events. Read as data, not activated instructions. No external skill was installed/executed and no provider job was submitted. Region/format QA does not establish anatomical side or convincing acting.

## Open source quality gap

ToS class pages, Supergiant project text, RO ACT spec and engine sources were retrieved. The new ToS YouTube lead could not be fetched through the current network path. No new RO3/Hades/ToS full frame study was performed in this round. Do not fill this gap with a title, thumbnail or prior rejected own poses.

The next quality-comparison dataset needs retrievable fixed-camera/full-body gameplay intervals for locomotion, bow, casting, hit and death at a resolution where grip/occlusion is readable. Acquire clips through available permitted delivery, retain source origin/clock and do the frame annotation before saying these games support our recipe.

## Additional breadth and deeper paper reading

Source discovery now totals92leads, including creator CrossCode GIF/workflow/press pages, Children of Morta postmortem, DOFUS CUBE developer notes, actual pinned DevilutionX player code, OpenDiablo2 and OpenTESArena. These are newly retrieved production/game reference leads; no whole-video/frame study or locally executed engine is implied. Official RO trailers remain inaccessible through this fetch path; the RO3 landing page is sparse and does not establish observed animation quality. RO class3 footage is not automatically the separate RO3game.

Seven primary PDFs were retrieved. [Targeted method notes](PAPER-METHOD-NOTES.md) expand selected sections on phase/manual contact correction, root-aware transitions, surface/morphology contacts, skeleton topology, motion matching context, imitation rewards and correspondence-guided redraw. This is deeper than the earlier abstract pass but still not complete-paper reproduction or model inference.
