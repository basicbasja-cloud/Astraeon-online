# Natural motion: rejected proof → external source study → new blocking

Iteration 7 follow-up, 2026-10-11. The user explicitly says the original conditioning board still looks unnatural. This is a **failed naturalness review** of that source posing/model presentation, not a request for more texture polish. Preserve its technical evidence; do not promote or multiply it as an approved motion/art seed.

## Primary instruction studied

[Anthony Wong's posing lesson](https://www.animationmentor.com/blog/tutorial-building-appealing-character-poses-for-animation/), article text: use a clear line of action, meaningful weight shift, readable silhouette and shoulder–hip counterpose. Avoid distributing all expression inside the outline or polishing a bad base pose. Evaluate the destination camera while retaining credible off-axis structure. Foot-roll controls change the contact pivot. The embedded video was not downloaded/viewed here.

[Wayne Gilbert's mechanics breakdown](https://www.animationmentor.com/blog/animation-tips-tricks-what-makes-or-breaks-a-good-body-mechanics-shot/), article text: decide the causal sequence through the body, including preparation and lead/follow. Breakdowns explain how the action reaches its next pose, rather than inserting generic interpolation. Which hip carries the weight, how the knee turns and how the shoulder assists are deliberate acting decisions. This was a text study, not capture of its illustrated motion.

[Natasha Krinsky's combat lesson](https://www.animationmentor.com/blog/tutorial-animate-sword-fights-battle-sequences/), article text: weapon mass changes acting and timing. Study representative reference, block its meaningful events, then retime for a game. Check strain, grip slips and intersections; spacing communicates resistance and release. The lesson's embedded video and game rigs were not downloaded here.

## Real source rig sampled this time

[Quaternius' Universal Animation Library](https://quaternius.itch.io/universal-animation-library) author page specifies CC0, a free Standard subset, and root-motion/non-root-motion variants. Current changelog notes corrected sword elbow twist, export speed and directional starting-foot sync. A GitHub 2025 mirror was inspected as a discovery lead; **it was not used as the sampled rig**, because it predates those listed corrections.

The current free Standard archive was downloaded directly through the author's public download page with no account/payment. Its bundled README/license and glTF names were inspected. The selected **`UAL1_Standard_RM.glb`** contains 43 named clips and a 65-bone skeleton including fingers. Blender actually imported it and sampled **Walk_Loop: 41 source samples / 1.333333s**, **Sword_Attack: 47 / 1.533333s**, at the real glTF input timestamps. All 88 source poses were inspected in dense SE diagrams. Eight-view diagrams are camera projections of source-known coordinates; their eight equally spaced columns are overview samples, **not approved production key choices**.

Set Blender FPS **before import**, and sample by glTF seconds × scene FPS. An initial inspection at Blender's default 24 FPS produced fractional frame ranges; changing only a presumed integer frame index would mis-time the action. The committed sampler sets 30 FPS before import, mutes all imported NLA tracks, explicitly assigns the chosen action, evaluates the scene and preserves the actual source timestamps. Last samples are endpoint poses with **no invented hold**.

World root travel is retained in JSON. Root-relative guide diagrams subtract the measured source root explicitly; they do not center per-frame image bounds or pelvis. Walk root displacement is `[0,-1.3000,0]`, attack `[0,-1.5005,0]` in imported source units. The attack is a travelling/lunging move, not proof that our compact attack needs that distance. Deleting that translation while keeping its planted-foot schedule would change mechanics.

The [measurements](../../../research/sprite-animation/source-motion-v7/mechanics-measurements.json) show source walk pelvis-height excursion about 0.0526 units and shoulder–hip yaw difference about −8.91° to +7.69°. The attack has much larger pelvis and shoulder–hip changes. These describe the sampled animation, **not target constants for a chibi rig**, center-of-mass simulation, or verified sole-ground contact. Bone toe/ball landmarks are not mesh contact patches. No sword mesh or surface grip was supplied in this sampled file; finger joints alone do not prove hilt contact.

## Specific changes needed before the next original pose passes

The rejected proof moves multiple targets through shared smoothstep intervals; it can satisfy bone lengths and declared contacts while still looking mechanical. It has one chest segment, pose-target hand placement, no articulated fingers, and no independently animated cloth/hair. Successful attachment and export checks did not measure a convincing line of action or the order of force through the body. The review boards remain failed/unapproved.

Create a new original blocking action using the source studies as reference. Keep the technical registration/part contract, but re-author these decisions:

- **Support and line of action:** choose which foot accepts the load and draw the line through that support, hips and chest. Do not treat fixed toe targets as evidence of balance. Preserve a deliberate stance width; a turned knee should follow the thigh/foot plane.
- **Torso distribution:** distribute bend/twist across pelvis and multiple spine/shoulder controls. Separate when the hips start, when the chest catches up and when the arm releases. Increasing twist numbers on one rigid chest is insufficient.
- **Shoulder–elbow–palm relationship:** move the clavicle/scapular region as the arm raises; inspect elbow direction, wrist basis, thumb side and the actual hilt surface. Review the free arm's job instead of mirroring the sword arm.
- **Feet and travel:** choose whether this is a compact cut, stepping slash or lunge. Repose support/release and rear-foot roll to that action. For walking, capture root speed and floor registration, stance contact, passing knee and swing clearance; do not bend both knees outward simply to keep every foot visible.
- **Phase-specific spacing:** select load/coil, launch, strike, follow-through and braking/recovery keys from actual changes in action. Use deliberate sparse holds. Generic ease-in/ease-out on every joint at the same times can remove weight and snap.
- **Secondary motion:** add cape/hair lag and settle after base mechanics pass. Keep amplitude restrained at native size, with independent joints/replacement drawings where needed. Secondary jitter cannot repair a weak primary pose.
- **Projection and native silhouette:** inspect front, side, back and all diagonals. Source-human proportions are not our final chibi proportions. Use separate per-view drawings/correctives when a sound 3D pose reads badly in a sprite, while retaining anatomical ownership and complete replacement content.

Review one plain original walk and one plain original attack in motion at native size, with FX disabled, before restoring costume details or mass-producing parts. The present work provides a repeatable source-study method; it has **not** yet retargeted this library, fixed the original character or obtained a naturalness/art approval.
