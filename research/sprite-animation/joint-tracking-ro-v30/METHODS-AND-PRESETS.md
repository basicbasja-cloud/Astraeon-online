# More animation, rig/preset and tracking research

The broad [v29motion foundation](../rpg-motion-foundation-v29/README.md) retains99action recipes across11families and92source leads, with acquired/captured/sampled/read/located states separated. This round deepens source ownership and actual-image checking. No old rejected own slash rig/sheet is a guide.

## Current presets actually acquired and evaluated

[Creator KayKit Character Animations](https://kaylousberg.itch.io/kaykit-character-animations) Free1.1 acquired through the public anonymous free-download flow with TLS verification, no account, payment or paid tier. [Receipt](kaykit-acquisition.json) records archive SHA/bytes; archive cache is excluded. [Exact bundled license](preset-source/KayKit-License.txt) states CC0. Fourteen source GLBs are vendored as research inputs with hashes, not integrated/shipped as our character art.

173serialized clips /144unique names acrossMedium/Large banks. Classification by name excludes14T-Pose records and6terminal/inactive `_Pose` records from motion-name candidates, leaving153candidates. Repeated names acrossbanks are not deduplicated performances. Filenames/marketingcounts/names do not establish loop, impact, contact or expressive quality.

Blender4.3.2 really imported every bank, set FPS30before import, muted NLA, bound each source action unambiguously and evaluated9selected native input timestamps per clip where available; shorter clips retain fewer. [Compressed samples](new-preset-samples.json.gz) contain1,397actual evaluated source poses with world joint heads, source SHA, hierarchy and rest matrices. This is source sampling, not retargeting to our character.

The current source has23joints perbank, including full bilateral upperleg/lowerleg/foot/toes, upperarm/lowerarm/wrist/hand/handslot, hips/spine/chest/head. This corrects the limit of older KayKit legacy6-joint banks (which cannot guide leg chains). No articulated finger rig: handslot location does not prove a sword sits inside a painted palm correctly. Contacts are unknown until independently checked against mesh/floor/support phases.

[12motion bone filmstrip](preset-source-bone-grid.png) uses one fixed projection/global scale and native sample times. It shows walk, optional forward dodge, diagonal slash, block hit, bow draw, casting, hurt, death, pickup, item, sit and chopping. This is a projection of source named bones, not detected skeletons in painted images. Death is noncyclic; don't add a final→first smoothness edge. Tool attacks/pickup have different planted-leg and upper-body demands; don't reuse one sword swing for all interact actions.

## Source reading and practical decision

[Method receipts](method-source-receipts.json) preserve retrieved content hashes/date. Mutable main/latest pages are byte-hashed snapshots, not pinned commits. Selected technical sections were read; full-text read and complete paper replication are not claimed.

| Primary source | Read finding | Factory application | Executed here |
| --- | --- | --- | --- |
| [CoTracker](https://github.com/facebookresearch/co-tracker) | point tracks plus predicted visibility; majority license CC-BY-NC with separate portions | never equate visibility/flow with anatomical ownership; not admitted as commercial factory dependency | docs only |
| [TAPNet/TAPIR/TAPNext](https://github.com/google-deepmind/tapnet) | point models/occlusion handling; coordinates distinguish(x,y) from(t,y,x); code/linked checkpoints Apache2.0, dataset/video rights separate | next bounded comparison candidate; explicit coordinate adapter, held-out painted set and checkpoint/license receipt needed | docs only |
| [DWPose](https://github.com/IDEA-Research/DWPose) and officialOpenCVbranch | SimCC axis decoding with CPUOpenCV DNN | inverse-map input crop into original image; keep model scores raw, own visible annotation authoritative | actual5image inferences |
| [RTMPose](https://github.com/open-mmlab/mmpose/tree/main/projects/rtmpose) | multiple runtimes and input/body conventions | checkpoint/input/output version must match, no silent resize-coordinate assumption | docs only |
| [Blender IK](https://docs.blender.org/manual/en/latest/animation/constraints/tracking/ik_solver.html) | target constrains a chain; pole target controls chain roll/elbow positioning | separate knee/elbow poles, rest-axis calibration, grip frame and floor constraints; targets alone won't fix acting | existing source sampling; no new target retarget |
| [Adobe Mixamo FAQ](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html) | royalty-free use for game/film projects; bipedal humanoid auto-rig/library scope | useful future candidate when account/source export available; preserve local downloads and exact clip settings | docs only; no Mixamo download claimed |
| [AMASS](https://amass.is.tue.mpg.de/) | common motion research portal | potential biomechanical reference, not blanket game/training license | portal retrieved, dataset not acquired |
| [RRL ACT/SPR](https://ragnarokresearchlab.github.io/) + pinnedroBrowser | native timing/layers/anchors and sprite encoding | frame parts/anchors/occlusion data with explicit part/action compatibility | selected docs/code plus actualROprobes |

DWPose is not a usable automatic approval detector on these tests: source medians6.99–9.18px versus3px provisional budget; painted accuracy unknown. Model weights134,399,116bytes with SHA in [receipt](pose-model-download.json), kept in ignored cache and not redistributed. Code license and checkpoint/dataset rights must be evaluated separately before admitting a model as dependency. Our image tracker is small local OpenCV point correspondence, not CoTracker/TAPIR inference.

## Production application before more art

Choose one motion family and one clear direction. Preserve external native source, sample known joints, inspect body-only acting and exact support phases. Establish style redraw, then label visible joints independently. Compare source-driven expectations and image observations without auto-relabeling. At overlap or lowconfidence return unknown; revise silhouette/depth and inspect next/previous images. Only after visible ownership, contacts, grip, native timing and acting pass should compatible interchangeable parts and remaining directions be made.

For many characters, freeze recipe/version/camera/joint schema/clock/part sockets and review evidence per character. Reusing a motion recipe does not transfer the previous character's anatomical approval. A full generation factory is still incomplete: no universal painted-joint detector, no error-free output guarantee, no new approved animation or full compatible replacement bank in v30.
