# Pre-repair visual audit

Starting branch: character/ro1-reference-engine-v1, fc7be02d56ac9c020652225af6fe6bff79b7e4fc. Clean existing clone; no reset, rebase or unrelated merge.

Inspected actual existing 16-frame normal/slow GIFs and 384-frame owner GIF through decoded samples; all eight full composite strips; body-only and joint boards; contact and grip before/after boards. Historical evidence is retained. Six phases reviewed at frames 0,4,6,7,10,14, with adjacent frames and loop boundary checked in strips.

| Direction | Ready / anticipation | Acceleration / contact | Follow-through / recovery | Full-body and occlusion |
|---|---|---|---|---|
| S | Recognizable face and neck; planted lead boot; raised elbow compressed | Arm crosses torso with weak elbow distinction | Wrist changes markedly; return lifts too abruptly | Keep front torso/stance; open shoulder-elbow silhouette; sword face needs depth |
| SW | Distinct front diagonal but upper arm buried against collar | F6 to F7 skips downward; elbow collapses across torso | F7 reused F8 erases transition; F14 return too high | Preserve pelvis/boots; near shoulder and support arm must separate; cape behind torso |
| W | Side-biased torso, head/neck readable; arm tight to skull | Short upper arm, folded wrist; large hand jump | F10 reused F11; F14/F15 sourced F13 cannot explain return anatomy | Keep stance; articulate elbow outside chest; gradual shoulder and forearm recovery |
| NW | Rear diagonal and asymmetrical boot stance present | Rear upper arm compresses; F7 reused F8 skips contact | Wrist drops while upper arm hardly changes, return skips | Cape hides shoulder chain; retain rear torso, show near elbow outside cape |
| N | Rear shoulder width readable, neck under hair/collar | Strike reaches screen right; elbow needs depth | Tip rotates more than hand; abrupt ready return | Symmetric rear differs from NW; cape overlap must not hide visible hand |
| NE | Rear diagonal, support shoulder visible | F6 fist/forearm reads disconnected beside head | Hand falls rapidly then rises at return | Repair near arm chain; keep independent head/hair and stance |
| E | Side torso and pelvis coherent, wide stance | F6/7 forward extension strongest existing pose | Hilt angle changes abruptly; recovery discontinuity | Preserve good extension; no mirrored W substitute; glove above handle |
| SE | Front diagonal has coherent lead knee and torso twist | Arm crosses chest; retain visible upper arm | Downward arc then sharp return | Preserve costume and face; distinguish S with shoulder/pelvis depth |

All rows include shoulder, upper arm, elbow, forearm, wrist, hand, grip, tip path and sword perspective. Head/neck, torso twist, pelvis, support arm, legs, cape and hair were checked in the full composite. Hidden joint positions are estimates, not measured 3D anatomy.

## Internal board review

`pre-repair-technical-board.png` was inspected before new art. It exposes the six phase silhouettes in all eight projections. The biggest change needed is continuous arm-chain articulation through contact/recovery, not a new MotionTemplate. Keep the 450ms duration and 170ms presentation contact. Preserve good torso/leg/head pixels. Re-author failing limb regions and local shoulder seams; do not infer success from coincident anchors.

Status: repair work required. No owner visual approval.
