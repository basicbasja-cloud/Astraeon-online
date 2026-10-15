# Research corpus and sources that can be proved

## Read the acquired evidence, not only a list of links

`research/sprite-animation/rpg-motion-foundation-v29/` is the broad corpus. Start with `SOURCES.md`, `sources.json`, `retrieval.json`, `DATASET-CONTRACT.md`, `MOTION-RECIPES.md`, `clip-inventory.json`, `corpus-summary.json`, `PAPER-METHOD-NOTES.md` and `PRODUCTION-PLAN.md`. Recorded scope: 92 source leads, 99 motion recipes across 11 families, 73 serialized animation records, 71 non-rest motion candidates, 639 evaluated source poses and 745 native capture frames. These counts are not 92 acquired full games or 99 accepted production animations. Failed fetches/located-only pages stay labeled.

`joint-tracking-ro-v30/` deepens actual RO action/direction/exposure and preset sampling. Read `README.md`, `RAGNAROK.md`, `METHODS-AND-PRESETS.md`, `KNOW-HOW.md`, manifests and acquisition receipts. `reference-reader.html` and overview boards in the corresponding cases enable visual review without inferring a motion from its name.

## Ragnarok findings that changed the pipeline

Community snapshot endpoint `https://assets.latam-tools.com.br`, not a complete official client archive. Retained audit records 1,340 requests, 1,275 decoded responses, 65 failures, 80 available class families and five gaps; 5,927 exposures include 5,642 timed and 285 untimed PNG observations. The index includes 290 job rows/85 families and larger item/skill/monster metadata lists; these are not all unique finished images or freely redistributable assets.

Observed stand/walk/sit have eight distinct directional sequences; most other actions have four; observed male primary attack has five and female four, freeze2 one. Therefore “only idle/walk are eight, everything else four diagonals” is too broad. Community/provider action order must be inspected per actor. Block12 is SKILL, not a third attack variant. Native provider facing order S,SW,W,NW,N,NE,E,SE differs from our order.

Observed male Swordman SE walk eight×75ms=600ms is a renderer probe, not a universal RO FPS. ACT delay is combined with renderer/action/speed rules. Source format and engine code establish timing semantics; a re-encoded GIF alone does not. Do not trace RO art into shipped original assets; extracted pixels are reference evidence, distinct from our paintover masters.

Primary format/engine leads:

* [RO ACT specification](https://ragnarokresearchlab.github.io/file-formats/act/)
* [roBrowserLegacy](https://github.com/MrAntares/roBrowserLegacy), observed commit recorded in v29 source catalog
* [ragassets](https://github.com/adsonpleal/ragassets), source parser/rendering evidence separate from game-pixel rights
* [Flare engine](https://github.com/flareteam/flare-engine) and [Flare game](https://github.com/flareteam/flare-game): native descriptors, eight-facing layering, per-file content licenses
* [Valyria Tear](https://github.com/ValyriaTear/ValyriaTear): animation/weapon-event and descriptor comparisons

Tree of Savior official class pages were retrieved as leads, but located/fetch-failed videos are not frame-by-frame analyzed captures. RO3 and every game in the world have not been exhaustively reverse engineered. Broader research remains valuable only when a specific new failure requires evidence, not as a replacement for validating our current pixels.

## Free presets actually acquired

[KayKit Character Animations](https://kaylousberg.itch.io/kaykit-character-animations) public Free1.1 archive was obtained through the anonymous free flow. `joint-tracking-ro-v30/kaykit-acquisition.json`, `preset-source/KayKit-License.txt` and retained GLBs document source and CC0 terms. Fourteen Medium/Large banks have 23-joint skeletons. 173 serialized clips/144 unique names produced 1,397 evaluated source poses; repeated names across banks are not new independent performances. Old legacy six-joint banks cannot establish full limb chains. Source poses are not retargeted production art or guaranteed contacts.

`continuous-arm-v43/reference/26.asf`, `26_09.amc`, `26_09.mpg` retain actual CMU skeleton/motion/video. The AMC has 740 samples at120Hz; 216 decoded video frames have differing timestamp evidence. Cross-modal alignment remains UNVERIFIED. Do not overlay them on an assumed shared clock and call it measured accuracy. CMU use/redistribution terms differ from CC0 and must be reviewed for the intended use.

Mixamo is a potential free-account workflow, not a fully acquired local preset bank in this delivery. No account login or external paid generator is necessary to inspect current work.

## Papers: selected methods actually read, no model training claimed

Seven primary PDFs have retrieval hashes/URLs in `rpg-motion-foundation-v29/paper-retrieval.json`; selected method/limitation sections were read. PDF/text caches are local-only where ignored; use that receipt to retrieve and verify, not a fabricated cache path in Git.

| Source | Knowledge used / limit |
|---|---|
| [PFNN](https://www.pure.ed.ac.uk/ws/files/35467734/phasefunction.pdf) | Phase/contact context and IK cleanup; not proof of a painted walk |
| [Robust Motion In-betweening](https://static-wordpress.ubisoft.com/montreal.ubisoft.com/wp-content/uploads/2020/07/09155337/RobustMotionInbetweening.pdf) | Temporal context/transition constraints; interpolating independent images is insufficient |
| [ReConForM](https://arxiv.org/pdf/2502.21207) | Morphology/contact/surface-aware retargeting; not executed neural inference here |
| [Skeleton-Aware Networks](https://deepmotionediting.github.io/papers/skeleton-aware-camera-ready.pdf) | Rest hierarchy/topology matters; no checkpoint reproduction here |
| [Learned Motion Matching](https://theorangeduck.com/media/uploads/other_stuff/Learned_Motion_Matching.pdf) | Context and transition quality, not just pose distance |
| [DeepMimic](https://xbpeng.github.io/projects/DeepMimic/DeepMimic_2018.pdf) | Pose/velocity/COM/task objectives are distinct; source rig is not a force simulation |
| [AniDoc](https://arxiv.org/pdf/2412.14173) | Reference/sketch correspondence; generation remains fallible and needs image QA |

CoTracker/TAPIR/DWPose documentation and limited experiments exist in v30; a tracker does not infer anatomical ownership through overlap. CoTracker license restrictions make it unsuitable as an automatically admitted commercial dependency. Retained limited point-tracking accuracy applies only to the visible subset and specific test images, not every sprite.

## Rights and portability

Open-source engine licenses do not license original game artwork. Keep third-party references out of our final runtime package unless separately admitted with their exact license. Original art masters, CC0 presets, reference-only captures and non-vendored downloads have separate scope. `LOCAL-CACHE-REPORT.json` lists historical local-only files absent from tracked delivery; acquisition receipts and primary links explain retrieval. No patent freedom-to-operate or commercial license audit is claimed. No persistent model training, universal generator correctness or finished sprite factory has been established.
