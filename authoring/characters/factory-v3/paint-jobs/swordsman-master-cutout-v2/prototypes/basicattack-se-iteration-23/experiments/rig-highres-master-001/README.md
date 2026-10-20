# High resolution master pose fit pilot

**Rejected. Review evidence only; not runtime art.** The pilot tested whether one detailed frame-499 composite could be deformed to four Rokoko poses while retaining a stable character.

## Finding

The selected source image and the motion guide do not share a compatible pose. A fixed root and a high-resolution source do not fix that mismatch: the torso and limb segments would need large stretches or compressions. The full-body triangulation also folds across the character. The resulting poses visibly distort the armor, arms, and sword, so this method is rejected for this source master.

The audit compares each arm and leg segment after the shared height scale with its target guide length. The permitted range is `0.78–1.12×`, matching the V3 motion prompt's limb-length bound. Torso length is recorded separately: preserve the painted proportions instead of stretching the sprite to the mannequin's torso length.

| Guide frame | Torso ratio (diagnostic) | Largest arm change | Smallest arm change | Flipped triangles | Limb fit |
|---:|---:|---:|---:|---:|---|
| 480 | `1.691×` | `1.582×` | `0.479×` | 9 | Fail |
| 493 | `1.724×` | `1.479×` | `0.659×` | 12 | Fail |
| 499 | `1.737×` | `1.105×` | `0.509×` | 4 | Fail |
| 511 | `1.709×` | `1.338×` | `0.560×` | 4 | Fail |

Every tested frame fails the limb-strain gate; the whole-body mesh would also stretch the torso by `1.691–1.737×`, and it flips 29 triangles across the four poses. The screen comparison is [here](pose-pilot-001/review/highres-master-guide-comparison.png), with the machine-readable details in [the audit](pose-pilot-001/review/highres-master-guide-pilot-audit.json).

## Authoring decision

- Do not warp this frame-499 image across the Rokoko sequence.
- Do not treat stable canvas registration, uniform output height, or high source resolution as proof of character continuity.
- Build the next high-detail master from the exact matching motion-guide pose, then cut same-frame `HeadHair`, body/outfit, `Weapon`, and `BackAccessory` layers. Use the shared mesh only when its pose preflight passes and adjacent-frame review shows no folds or silhouette jumps.
- Keep the Rokoko motion guide as the pose source. This pilot provides no reason to alter or approve the motion itself.

## Reproduction

Run `tools/character_factory_v3/warp_highres_master_to_rokoko.py` with the iteration-22 high-resolution frame-499 composite, this experiment's source landmark JSON, and frames `480,493,499,511`. The script writes the output images and pose-strain audit under `pose-pilot-001/`.
