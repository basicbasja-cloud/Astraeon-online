# Source rig motion study

The sampler imports a locally supplied Quaternius UAL Standard root-motion GLB and evaluates the actual glTF time accessors for two named clips. It does not estimate a skeleton from an image, run Mixamo, or retarget the action to our character. The names/layout supported here are explicit; another rig requires a new checked anatomical map.

See the [executed study and commands](../../../../research/sprite-animation/source-motion-v7/README.md), [natural-motion practice](../../references/natural-motion-practice.md), and archived source/license/provenance. `draw-source-study.py` produces fixed-camera root-relative diagrams with original world root coordinates retained in the JSON; `measure-source-motion.py` reports geometric ranges only. Neither certifies physical support, source foot soles, original grip surfaces or natural final sprite acting.
