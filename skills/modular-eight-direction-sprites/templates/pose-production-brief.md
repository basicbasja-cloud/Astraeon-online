# Ordered guide-to-art request

Fill this once per character/action/view; attach the **complete ordered** source guide strip and approved identity/turnaround. This template is not approval of v4/v5 or a guarantee from an image model.

- Character identity/style source: [approved asset ID/hash, or explicitly unapproved study]
- Rig family and approved proportions: [ID]
- Action and requested facing: [action, aim facing]
- Authored view and whole-character view map: [view, map]
- Native canvas / capture canvas / fixed root anchor: [dimensions and coordinates]
- Pose guide source and SHA-256: [actual baked-source guide JSON; do not substitute inferred hidden joints]
- Exact ordered pose keys: [index, phase, duration, contacts, guide image]
- Dominant anatomy: anatomical **right** holds the sword for every pose; blue means right, orange left. Screen position does not change ownership.
- Shape/occlusion conditioning: [ordered silhouette, visible-piece IDs, common-range depth; exact encoding and actual backend support]
- Camera/floor evidence: [source shot and timestamps, moving/fixed/unknown camera, contacts observed vs source-known vs estimated]
- Palm/finger guide: [source/image showing wrist basis, hilt contact, thumb and finger wrap; or unverified]
- Item shape and grip socket: [weapon ID, weapon.right → right.hand, length, grip surface]
- Full-body acting: [hip load/rotation, chest opposition, knee bend plane, head response, free-arm balance]
- Walk-specific targets: [stance/release windows, travel speed, world-contact root/floor data, swing clearance and view lane spacing; or action not walk]
- Complete part requirements: [body/head/hair/costume/armor/weapon/back content and hide rules]
- Effect: [off during anatomy review; later contact arc/emission/recovery expiry on the same action clock]

Draw/produce one coherent aligned ordered strip for this view. Preserve character scale, camera, identity and root registration. Use pose holds deliberately. Do not recenter or independently scale individual frames. Do not flip the asymmetric character. Keep the original sword on its right-hand chain even if that chain crosses the torso. A guide's hidden joints are aids, not outlines to expose through clothing.

Review each completed image at native size and in motion, with FX off. Reject switched ownership, twisted drawn palms, detached grips, deformed torso, reversed knee bends, wide-legged gait drift or identity changes. Compare visible joints to the appropriate guide; separately inspect occluded intervals and recovery continuity. Bone/PNG/browser tests cannot automatically approve those drawings. Repair against the same strip/source, then rerun export checks. Do not multiply equipment/actions from an unapproved seed.

For full redraw/repair practice, read [conditioning and redraw](../references/conditioning-and-redraw.md). At a grip repair, review elbow and wrist continuity, the palm/hilt seam and adjacent keys; measure preservation outside the declared repair region. Complete hidden parts remain a separate requirement from a successful flattened drawing.
