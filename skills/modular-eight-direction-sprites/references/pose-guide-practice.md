# Pose guides, frame studies and generation discipline

Iteration 6, 2026-10-11. The user prioritizes attractive original fantasy sprites with correct anatomy over frame count, and permits references beyond Ragnarok. “No generation mistakes” is the target quality bar; prompts, source guides and automated tests cannot guarantee that a probabilistic image generator always satisfies it. The production method must include observable rejection and correction, not confidence language.

## What was actually studied

The [frame archive](../../../research/sprite-animation/motion-reference-v6/README.md) contains freshly decoded **136 RO samples**: male Swordman walk 8 × 8 views and weapon attack 9 × 8 requests, including paired attack duplicates. All 16 complete sequences were inspected in the two combined review boards. These are community renders of game assets, not captures of the original client or recovered source skeletons. They do not establish universal RO pose timing or every weapon/class rule.

Walking is an alternating weight-bearing sequence, not repeated independent leg swings under a fixed chest. The side views expose advancing/receding feet, bent swing knees and small upper-body changes; the front views preserve lane separation without turning every step into a wide squat. The image alone does not reveal a planted foot's world velocity or exact hidden knee rotation. To assess sliding, record character root travel and floor motion from gameplay or source animation too.

The attack example contains an extended raised/preparation segment, then a short drop into the stroke and an effect-covered follow-through. View reuse must keep the whole equipped character on the same source view. The large drawn sweep masks hand/face regions; it is not a reliable anatomical guide for those hidden joints or proof of an original blade mesh. Our blade-history ribbon should be evaluated for readability and timing, rather than copied because its existence can be measured.

[King Lucas art director Antonio Pastor](https://www.devilishgames.com/en/2016/12/14/how-to-animate-a-king-who-has-lost-his-daugthers/) describes changing a timid walk, using fewer attack frames to strengthen the hit, avoiding mirrored weapon ownership, and exporting segmented art through Spriter. The two walking GIFs and a shading comparison were extracted and inspected completely. The stronger walk has clearer leg opposition and larger torso/helmet motion; this is a side-view acting reference, not an eight-view body contract. Its 30 ms GIF delays are illustration-container timings, not a target for our attack.

[Fyna's developer](https://www.indiedb.com/games/fyna/news/devblog-20-animation-improvements-2) shows a rough rig/reference followed by drawn animation with improved cloth/hair detail. Both 11-sample GIFs were decoded. They contain zero-delay samples, so the study explicitly leaves total playback time unknown. Their use here is guide-to-final redraw practice. The developer's process description does not mean our finished drawings are automatically anatomy-safe or interchangeable parts.

[Tree of Savior's developer](https://treeofsavior.com/page/news/view.php?n=2276) specifically says hair is implemented in 2D and requires many motions; this supports budgeting item-by-action authoring, not an assertion that every other part uses our renderer. Its [earlier optimization article](https://treeofsavior.com/page/news/view.php?n=438) explains the sorting/batching tradeoff for translucent particles. It does not validate our alpha-depth FX composition. The [Wakfu lead animator's portfolio](https://ntamak.artstation.com/projects/bKQDPG) was located as a primary art lead; its embedded trailer and full pose library were **not** extracted here. Final Fantasy Tactics/Disgaea remain candidate acting/style comparisons, not completed motion studies.

## Two distinct kinds of skeleton information

**Observed image landmarks:** keep the original crop registration and time; annotate the visibly identifiable shoulder, elbow, wrist, pelvis, knee, ankle and grip. Mark ambiguous/occluded landmarks unknown or estimated. Screen-left is not an anatomical-hand label. A 2D pose estimator can reverse owners or hallucinate joints on stylized chibi art; don't use its output as ground truth. Our extraction tool intentionally provides empty annotations rather than fabricating these joints.

**Authoritative source guides:** sample a baked rig action at chosen sparse pose keys and use the exact export camera. The current adapter reopens `.blend`, samples bone matrices, projects all eight facings, checks limb segment lengths and compares the right wrist to the actual weapon bone origin. Blue denotes anatomical right, orange left, yellow blade, green declared contacts. Occluded joints remain source-known and visibly labeled as such in JSON. Toe/heel contacts come from analytic targets, not independent foot-mesh measurements. Hand-frame axes are orientation aids, **not finger/palm surface validation**.

[Adobe's Mixamo documentation](https://helpx.adobe.com/creative-cloud/help/mixamo-rigging-animation.html) requires login and describes wrist/elbow/knee/groin placement and rig mapping. No Mixamo account was accessed, FBX downloaded or animation retargeted in this iteration. A later FBX study needs a recorded action, anatomical bone map, coordinate conversion and source license; generic human motion must be reposed to our body proportions and reviewed. “Mixamo-like” in a filename is not evidence of those checks.

Use the [ordered guide-to-art request template](../templates/pose-production-brief.md) to record the exact source, anatomy, contacts, part requirements and review status without turning an unapproved guide into an approved art seed.

## Gate the art before multiplying it

1. Establish the original character's approved proportions and eight-view neutral turnaround at **native game size**. Keep hair, costume, face and clasp identities stable. The v4 rig and v5 visual board remain unapproved studies.
2. Block one walk and one right-handed attack as plain silhouettes/rig guides. Give each key its contact, weight-bearing side, hip/chest orientation, limb chains, grip and recovery role. Decide frame holds after motion review. Fewer convincing poses are preferable to more incorrect ones.
3. Review the limb chain in every facing, including crossed arms. Check shoulder → elbow → wrist → palm → hilt, with sword axis and grip area. A coincident bone origin catches detached attachments; it cannot catch a twisted drawn palm or wrong finger wrap. Add palm/finger guides or explicit close-up drawing references before approving the grip.
4. For walking, inspect hip → knee → ankle alignment and the anatomical bend plane. Use floor/root information for stance sliding; review swing-leg toe clearance and perspective lane width. A skeleton's constant segment lengths alone cannot reject an ugly bow-legged drawing.
5. Use the approved character and the **complete ordered guide strip** together for assisted generation/drawing. Keep one fixed camera, canvas, scale and root. If a generator crosses/changes hands or deforms legs, reject or repair that frame against the same guide; do not normalize the mistake away through cropping or mirroring. No separate random frame prompts may independently establish anatomy or character scale.
6. Finish hidden body/hair/back costume source content, then test item swaps against the same action/view key. Flattened painted masks do not become complete interchangeable source items. Prefer editable layered drawings or complete geometry with reviewed draw-over refinement.
7. Review the native sprite with FX disabled, then check effect exposure and occlusion separately. Native contour/palette cleanup is still required for a rig-derived image to gain the desired appeal.
8. Only expand equipment and action counts after the above tests and artistic acceptance. The release path must remain blocked while the body, motion, trail or game-renderer tests are unverified.

## Export observations applied this iteration

[Aseprite CLI](https://www.aseprite.org/docs/cli/) documents split layers, all-layers, JSON metadata and frame durations. Empty frames and duplicates need timeline entries; do not casually use ignore-empty or merge away their pose identity. The tools were studied, not installed or executed here.

[TexturePacker alignment guidance](https://www.codeandweb.com/texturepacker/knowledgebase/keep-animation-alignment-with-trim) explains preserving original positioning through exported metadata. Its [settings](https://www.codeandweb.com/texturepacker/documentation/texture-settings) distinguish Trim from Crop and describe alpha handling/paired-map layouts. We retained full fixed cells in this adapter. A future trimmed color/depth pair must reconstruct the same logical canvas and anchor exactly, using one common layout; copying only the packed color PNG would break our compositor. TexturePacker was not invoked.

## Current completion bar

The reusable CLI now builds, checks and packages the technical proof, with 64 original skeleton guides and external frame-study extraction. It still has no original walk clip, approved native anatomy/style set, finger-contact proof, complete action family or production-game rendering run. Exact-color reconstruction still differs at six pixels. These are concrete next work items, not reasons to label the package “ultimate” or a no-error generator.
