# BasicAttack body-art anatomy audit

Baseline: `e0886e419212586161cd778d53e665a170a8f181`, branch `character/ro1-reference-engine-v1`.
All frame indices in this package are **zero-based**. The 128 BodyWithOutfit cells were inspected without Head, Hair, sword or Cape, then with the independent Head restored for occlusion context.

| Direction | Main findings | Priority cells |
| --- | --- | --- |
| S | Compressed elbow at acceleration; shoulder/sleeve volume changes across contact. Low recovery hand fails to return to the raised ready silhouette. | 6–9, 14–15 |
| SW | Loaded upper arm becomes unreadable around the skull; contact substituted from frame 8 skips a pose; elbow collapses across the torso. Recovery stays low. | 4–9, 14–15 |
| W | Loaded elbow and forearm compression; large wrist transition into contact; sleeve folds obscure the elbow; substituted follow-through and repeated recovery interrupt progression. | 3, 6–12, 14–15 |
| NW | Rear sword arm shortens/compresses behind the shoulder during contact; repeated contact skips a distinct strike pose; recovery does not regain the raised ready arm. | 6–9, 14–15 |
| N | Sword-arm shoulder/forearm volume changes at contact; ready-return arm remains low. | 6–9, 14–15 |
| NE | Frame 6 has an isolated fist above the skull without a readable upper-arm/forearm connection. Rear contact and recovery need the same arm identity. | 6–9, 14–15 |
| E | Contact bracer/sleeve bend needs a distinct elbow; low recovery hand snaps to the raised next-cycle ready pose. | 6–9, 14–15 |
| SE | Contact elbow/sleeve compression and incomplete raised-arm recovery. | 6–9, 14–15 |

The source contains painted pose/projection variation. A gap hidden behind the reattached Head is not by itself proof of a severed limb; review must also follow shoulder, elbow, wrist and arm identity through adjacent cells. The issue is a combination of painted retargeting, compressed elbows/wrists and frame reuse, rather than principally weapon registration.

Repair priorities are anticipation, acceleration, contact and immediate follow-through, then recovery continuity. Preserve the RO-derived action phases, all 16 frame durations (450 ms), the 170 ms contact event, root, direction identities and independent face. No new actions, engine redesign, mirroring or neighbour-pose substitutions.

Debug joints are review annotations, including inferred occluded positions. They do not become animation or gameplay authority. Automated checks cannot approve anatomy.

**OWNER VISUAL APPROVAL PENDING.**
