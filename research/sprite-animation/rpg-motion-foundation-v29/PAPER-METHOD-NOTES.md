# Targeted primary-paper reading — application to our factory

Seven primary PDFs were retrieved and converted to local text. The following are original notes from selected methods/limitations sections, not a claim that every paragraph, supplement, model or experiment was reproduced. Exact PDF hashes/URLs are in paper-retrieval.json. Full third-party PDFs/text remain in ignored local-cache/.

## PFNN — phase and contact need explicit evidence

The [paper](https://www.pure.ed.ac.uk/ws/files/35467734/phasefunction.pdf) labels foot phase from heel/toe velocity, explicitly acknowledges heuristic failures and manual correction, outputs contact channels, and uses two-joint IK after prediction to mitigate foot sliding. Root position/rotation is updated separately.

Our application: label support intervals and gait phase separately from frame ordinal; verify automatic contact candidates with actual visible/source surfaces; test controller movement alongside in-place sprites. A low-velocity ankle is a contact candidate, not ground truth. An animated source with IK is not automatically a correct painted boot. We have not executed PFNN or imported its training motions.

## Robust Motion In-betweening — destination alone is not enough

The [primary PDF](https://static-wordpress.ubisoft.com/montreal.ubisoft.com/wp-content/uploads/2020/07/09155337/RobustMotionInbetweening.pdf) conditions transitions with time-to-arrival and scheduled target noise, evaluates world/root-aware motion, and notes failures with unrealistic/out-of-distribution conditions. Controlled style changes are outside its stated scope.

Our application: preserve duration, current motion context and landing state in start/stop/turn/combo recipes; reject inserted drawings that stall at an intermediate key. Compare at equal total action duration before deciding that16frames are better than8. Correct sparse keys first. No trained transition model was executed here and LAFAN1 is not an unrestricted commercial source bank.

## ReConForM — morphology-aware contact relates surfaces

[ReConForM](https://arxiv.org/abs/2502.21207) uses transferred rigged mesh key vertices, pairwise distance/direction/penetration descriptors and floor/sliding relationships. Constraint relevance changes over time according to proximity/contact. Its thresholds are characterized relative to the particular character, not copied pixel budgets.

Our application: when changing body proportions, preserve palm/hilt, sole/floor, seat and interacting-limb relationships using actual target surfaces. Keep both pose rotations and contact constraints. Separate contact-cleaning from camera placement; never translate the whole actor just to hide foot drift. Source-surface selection and optimization are still future work, not implemented merely by sampling world bone heads. No ReConForM solver is run.

## Skeleton-Aware Networks — compatible skeleton structure is an assumption

The [paper](https://deepmotionediting.github.io/papers/skeleton-aware-camera-ready.pdf) builds pooling/unpooling/convolution operators using skeletal adjacency and a common primal structure for topologically corresponding skeletons. Different rest proportions and hierarchy need explicit treatment.

Our application: define bone correspondence, rest axes, parent order and anatomical sides before transfer. Our6-joint legacy KayKit source is not equivalent to the65-joint humanoid source for leg analysis. A target with no leg chain cannot gain verified knee/ankle data from a clip name. This motivates schema rejection and per-source adapters; it does not authorize inventing missing joints or imply paper inference is executed.

## Learned Motion Matching — transitions depend on motion context

The [paper](https://theorangeduck.com/media/uploads/other_stuff/Learned_Motion_Matching.pdf) distinguishes matching features from full pose data, describes search/step/decompression and blending, then replaces components with learned networks. Feature vectors can include foot positions/velocities and trajectory context.

Our application: for sparse sprite state changes, select a compatible outgoing phase and incoming pose/velocity/support context, rather than matching only a still silhouette. This is our proposed adaptation, not motion matching executed on2Drasters. Blending coordinate transforms does not automatically create anatomically correct inbetween artwork. Retrieval and memory-efficiency gains do not certify item contact or damage feel.

## DeepMimic — pose, velocity, endpoint and task are separate

The [paper](https://xbpeng.github.io/projects/DeepMimic/DeepMimic_2018.pdf) combines reference-motion imitation and task goals in physics-based control. Its imitation terms distinguish pose, velocity, end-effector positions and center-of-mass; reference-state initialization exposes different motion phases during training.

Our application: do not use “bones end near the target” as a complete action score. Assess temporal progression, support, hand/weapon relationship and intent independently. We cannot measure real COM or force from painted pixels; our visible hip/lean metrics are proxies. We are not training a physics controller and source-skeleton diagrams are not damage physics evidence.

## AniDoc — correspondence-guided redraw, not an anatomy oracle

The [paper](https://arxiv.org/pdf/2412.14173) uses design-reference/sketch correspondence guidance, point tracking in training and semantic matching at inference. Sparse-sketch inference interpolates point trajectories; low-level feature matches across color/sketch domains can fail. Its implementation README separately documents14-frame preprocessing.

Our application: establish correct motion lineart/owner/occlusion first, then test style/color transfer. Retain exact source-time mappings when adapting to a model-required input length. Do not treat linear point interpolation as a verified limb path through an occlusion or assume a temporally consistent color sequence has correct anatomy. No AniDoc inference or training was performed here.

## Research conclusions we can act on now

The immediately reusable pieces are phase/contact/identity schemas, exact clocks and source transforms, explicit morphology/rest mappings, an independent image review, and state/event contracts. Learned interpolation/retarget/style tools are experiments to evaluate against these pieces. None supplies a universal promise that every generated RPG action will be correct.
