# Source pilot implementation notes

Compatibility was tested against the actual installed Blender 5.2.2 LTS.
The pinned MPFB 2.0.17 source release initially failed through the legacy `mpfb`
addon name because its location service expects an extension package. Registering
a workspace-local Blender extension repository fixed this. The Blender 5.2 Eevee
enum is `BLENDER_EEVEE`, rather than the older `BLENDER_EEVEE_NEXT` name.

The compact source is reshaped from the core connected anatomical mesh. Arm
length is adjusted continuously, retaining shared vertices at the shoulder.
Fitted cloth copies the anatomical surface and weights. Hair, armor, shoes,
scarf/cape and blades are new local geometry, with actual side and rear surfaces.
The body and its concealed surfaces remain editable under reversible masks.
The initial face/eye proportions, scalp coverage, chest-panel fit, shoe coverage,
belt and tunic intersections were inspected and adjusted on this same source.
The face/hair and costume detailing still need artistic refinement.

The grip begins from two anatomical hand axes: the index-to-little-finger span
aligns with the hilt; the wrist-to-palm direction is rolled forward to avoid
folding the palm behind the hip. The blade's neutral character-space axis is
forward/down with a small anatomical-right component. All views rotate that
same geometry; there is no separate per-direction blade correction or mirroring.
Finger CCD uses bounded incremental rotations and records endpoint errors.
It has no claim of anatomically constrained animation or collision-free motion.

The first saved-file deformation probe found that MPFB defaults to Euler pose
rotation while the script had keyed quaternion fields. Static matrix-authored
poses rendered, but the keyed fields were inactive. Bones now use quaternion
rotation, including the socket bones. The saved-file test detaches the review
action temporarily, rotates the wrist, and confirms displacement of both the
skinned glove and attached blade. It restores the pose/action without saving over
the source. A separate check confirms the right-hand socket equals the actual
modeled hilt center.

Complete renders retain clothing/cape/body occlusion. The first hand close-ups
were obscured by the cape, tunic or opposite arm. Final diagnostic close-ups
isolate the right glove, right bracer and sword; they do not imply that the hand
should be visible through those surfaces in a complete sprite.

The review source pose is one frame. Endpoint fit, connectedness, distinct
headings, binding, render repeatability, swap independence and review controls
are technical checks. None declares final anatomy, style, motion or owner
acceptance. The existing runtime contract and global motion matrix remain intact.
