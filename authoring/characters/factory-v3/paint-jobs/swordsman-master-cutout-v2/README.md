# Swordsman 16-frame repaint preparation

This paint job contains Blender pose guides for the next Idle, Walk, and
BasicAttack masters. These guides establish timing and pose; they are not
finished painted character art, a runtime character, or approved assets.

## Guides

Each sheet is an 8-direction grid with directions in `S, SW, W, NW, N, NE, E,
SE` columns and 16 chronological pose rows. PNG cells are 160×160; the source
rig is shown at low detail. Each GIF places all eight directions side-by-side
per frame and preserves the clip timing within GIF's 10ms duration units. Idle
and Walk loop; BasicAttack plays once and holds the recovery pose.

- Idle: [`idle-motion-guide-16.png`](guides/idle-motion-guide-16.png),
  [`idle-motion-guide-16-8directions.gif`](guides/idle-motion-guide-16-8directions.gif).
  The low-detail rig silhouette's mean last-to-first IoU is `0.969`.
- Walk: [`walk-motion-guide-16.png`](guides/walk-motion-guide-16.png),
  [`walk-motion-guide-16-8directions.gif`](guides/walk-motion-guide-16-8directions.gif).
  Mean last-to-first IoU is `0.852`; the weakest facing is `E` at `0.768`.
- BasicAttack: [`basicattack-motion-guide-16.png`](guides/basicattack-motion-guide-16.png),
  [`basicattack-motion-guide-16-8directions.gif`](guides/basicattack-motion-guide-16-8directions.gif).
  The original guide render used contact at frame 8. A later motion audit moved
  the candidate contact marker to frame 10 (phase `0.63`, 1239ms); recovery
  still begins at frame 13. Sampled poses and durations are unchanged, and the
  original timeline is archived beside the guide provenance. This one-shot
  does not loop. Its source timing is about 1.97 seconds.

The alpha IoU values are pose-guide continuity diagnostics, not human motion
or painted-art quality scores. Provenance JSON records the scene/timeline
hashes, frame phases, durations, and per-facing diagnostics. Rebuild the sheets
and GIFs with `tools/character_factory_v3/assemble_motion_guide.py` after
rendering the matching timeline with `blender/render_motion_preview.py`.

## Ragnarok reference applied

The client reference is frame-synchronized layers: ACT data carries per-frame
sprite placement and timing, and Goro keeps `weaponLight` separate from
`weapon`, selecting it with the same action, facing, and body motion. The first
`WeaponSlash` stroke experiment in paint job v1 crosses the character and does
not follow the sword. It is rejected and remains only as diagnostic evidence.
The replacement is an independently painted `WeaponLight` layer aligned to the
sword in each BasicAttack frame, with transparent frames outside the strike,
and facing-aware overlap reviewed before import.

A 16-frame single-SE full-master trial now has a looping review GIF so its
last-to-first seam can be inspected. It is rejected because sword pixels touch
or cross cell edges in frames 6–10; it has no `WeaponLight` and is not a runtime
asset. See [the rejection record](prototypes/basicattack-se-iteration-2/README.md).

A second, more compact low-diagonal SE attack trial has a recovery-locked loop
preview. It is also rejected: blade pixels reach the cell edge in frames 9–10,
with a detached fragment in frame 11, and no separate `WeaponLight` was made.
See [the compact trial](prototypes/basicattack-se-iteration-3/README.md).
An effects-only `WeaponLight` attempt was composited over and behind that
master, then rejected because its repeated curved marks cross the torso and do
not follow the blade. A separate tip-motion trace now follows the SE sword tip
in frames 6–12, but remains review-only because the base master still clips the
blade and the effect needs review at game scale.

### Broad SE sweep trail review

The owner supplied a rough 4×4 slash example. Iteration 4 uses it as a loose
shape guide for a broad low horizontal sweep with an original plum-gray to
lavender-silver to warm-ivory gradient, stored as separate
transparent `WeaponLight` frame images. The motion audit placed contact at
phase `0.63` / frame 10 / 1239ms, where the source clip's lateral sweep is
strongest; source curves and sampled poses remain unchanged. The GIF plays once
and holds the recovery pose for inspection:

- [One-shot SE review GIF](prototypes/basicattack-se-iteration-4/review/basicattack-se-weaponlight-one-shot.gif)
- [Four-by-four character and trail contact sheet](prototypes/basicattack-se-iteration-4/review/weaponlight-over-contact-4x4.png)
- [Behind-character contact sheet](prototypes/basicattack-se-iteration-4/review/weaponlight-behind-contact-4x4.png)
- [Transparent WeaponLight layer sheet](prototypes/basicattack-se-iteration-4/layers/WeaponLight/weaponlight-se-4x4.png)

This is still an art-direction prototype, not approved runtime art. It covers
only SE; the underlying character master has visible red fringe and clipped
blade pixels in the strike segment.

## Repaint requirements

- Paint one complete, high-detail 8×16 full-character master per action, using
  the pose guide and the owner-supplied swordsman images as references.
- Keep one camera, scale, root `(80,132)`, foot baseline, and palette across
  every direction and pose. Target a 112px visible character inside each
  160px runtime cell.
- Only after the full masters pass visual review, cut same-frame transparent
  `BaseBody`, `HeadHair`, `Outfit`, `Weapon`, `BackAccessory`, `Headgear`, and
  `WeaponLight` layers. Reassemble and compare against each master.
- Do not repeat the first ImageGen sheet attempt: it had red fringes, cells
  smaller than 160px, and weak pose variation. It was rejected and never
  imported.

The current eight-frame cutouts and rejected effect pilot remain in
[`swordsman-master-cutout-v1`](../swordsman-master-cutout-v1/README.md) as
diagnostics. None of them replaces the requested high-quality 16-frame art.
