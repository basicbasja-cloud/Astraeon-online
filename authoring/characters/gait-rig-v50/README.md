# Controlled gait reference — authoring only

`walk-reference.blend` contains an original articulated mannequin, eight walk keys plus a loop closure, an orthographic sprite camera and studio lighting. `build-gait-rig-study-v50.py` recreates it independently of the town source. Nothing in this folder is a runtime asset.

Two-bone leg IK keeps each thigh and shin 0.57 world units. The stance foot retracts 0.70 units relative to the hip over a 0.62 duty fraction. Virtual root travel of `0.70 / 0.62` units per full cycle cancels that retraction exactly. The source verifies evaluated Blender ankle positions against analytic targets; maximum error in this run is 2.11e-8 world units. Guide red is the anatomical right leg (viewer-left in front view), blue is anatomical left (viewer-right). The short cape exposes both legs deliberately.

`S-eight-pose-guide.png` assembles the actual eight rendered poses with a shared camera, scale and fixed root origin. **Do not normalize each pose to its lowest boot:** projected foot travel is part of the gait. Any final sprite registration must preserve one root coordinate and scale across the full strip.

`approved-warrior-seed.png` is an unchanged crop from the shipped walk atlas, used for identity. The illustrated eight-pose generation from the rig is retained as `painted-eight-study-rejected.png`. It does alternate leading legs, but it does not preserve the rig's precise stance progression and foot retraction, so it is not approved or installed. No test of bone mathematics certifies generated art.

Remaining work: a convincing complete illustrated gait with actual planted-foot travel, stable costume and eight facings; normal walking, running and sprinting for every starting archetype; correct shared scale/anchors and actual gameplay video approval. Preserve the shipped character identity while resolving these. Repeated image-generation edits that merely exchange leading boots do not satisfy the gate.
