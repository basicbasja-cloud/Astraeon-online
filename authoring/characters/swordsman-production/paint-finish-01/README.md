# Painted finishing and RO pose study

The owner clarified that Blender should prove anatomy, pose, projection and
grip, then guide high-quality painted 2D sprites matching the approved art.
The previous `fantasy-base-01` bake is a technical scaffold. It is not the
completed Golden character or a demonstrated finished-art production factory.

`painted-se-style-pilot.png` demonstrates the missing painted finish using
the real SE Idle render and the approved concept as separate pose/style
references. The built-in image generator produced genuine transparent RGBA.
The pass improves face, hair and material rendering, but changes scale and
sword direction. It fails production registration and must not be admitted
to the existing atlases or treated as an animation frame.

`painted-se-ro-pose-pilot.png` is the second finishing trial, using the new
compact Blender stance as its edit target and the approved concept only for
identity/paint. It follows the bent holding forearm and downward-left blade
much better, but does not preserve canvas registration. Its alpha-224 opaque
height is 1.499 times the new guide's normalized height. It also contains
16,185 faint alpha pixels (1–15). The pose/finish improvement is a visual
observation, not proof of matching joint coordinates or a production pass.
It remains an unapproved composite study, with no separate painted layers.

`painted-se-registration-pilot.png` is a targeted third trial asking only for
uniform scale/position correction and alpha cleanup. It reduces the height
drift, but still measures 11.8% larger than the guide. The opaque bottom is
9.0% of canvas height too low. It therefore also fails registration, despite
retaining a similar painted pose. Prompt-only image edits have not established
repeatable frame coordinates in these trials; more blind full-motion image
generation would not resolve that requirement.

All three original generated PNGs are preserved without pixel changes. Prompts
are saved alongside them. `paint-study-audit.json` records their SHA256,
alpha bounds, normalized silhouette measurements and input roles. The first
style prompt did not retain its exact guide path; that provenance limitation
is explicit. The second trial's exact guide and approved-reference hashes
are included. No third-party paid job or image API CLI was used.

Open `review.html` to compare full canvases at 160/320/640 px, with optional
Blender joint or silhouette overlays and all eight guide headings. Framing
is not automatically corrected in the viewer. A larger or better-looking
painting therefore cannot hide the registration failure.

Reproduce the original pose guide with Blender 5.2 background mode, loading
`.character-tools/checkpoints/fantasy-base-01-native.blend` and running
`tools/build-ro-idle-pose-guide.py`. This writes a separate editable checkpoint.
Run `python tools/audit-painted-pose-study.py` for read-only raster inspection
and native-checkpoint hash assertions. These checks do not approve art.

The next guide is an original compact idle stance referenced to Ragnarok
swordsman silhouettes: narrower planted feet, relaxed shoulders, a bent
holding forearm and a naturally aligned wrist. The hand and sword remain
attached in Blender. This is a single pose trial, not completed RO-like
locomotion/attacks. See `pose-guide.json` and `tools/build-ro-idle-pose-guide.py`.
Eight guide views come from one real pose and the fixed camera; no view is
mirrored, independently repositioned or traced from proprietary sprites.

Reference: [official RO swordsman page](https://ragnarokonline.gungho.jp/gameguide/character/swordman/swordman.html).
The existing local RO sheets are visual references only and stay outside the
public package. Their body artwork, SPR/ACT files and motion curves do not
become ASTRAEON assets.

The finishing contract is:

1. Match the approved identity, palette and painted finish at actual game size.
2. Match the guide's camera, joints, ground anchor and weapon attachment.
3. Author consistent eight-direction poses and connected animation sequences.
4. Author complete registered body/outfit, head/hair, headgear, weapon and cape
   layers, including surfaces exposed by equipment removal. Cropping a finished
   composite cannot establish those hidden surfaces or correct registration.
5. Recheck motion consistency, alpha edges, occlusion, swaps and actual gameplay.

All studies here remain unapproved. A nice single painting does not prove a
repeatable layered animation factory. Raw generations and measured deviations
are retained so a failed art guide does not silently become production art.
