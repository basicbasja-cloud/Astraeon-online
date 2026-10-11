# Proposed asset contract

This is a design proposal for project adoption, not an existing engine standard. Example numbers are illustrative. Preserve a project's valid established conventions.

## Coordinate and direction conventions

Use an explicit direction array. The original diagnostic study uses this example order; it is not proof of the newest game's storage or view mapping:

| Index | Facing |
| --- | --- |
| 0 | S |
| 1 | SE |
| 2 | E |
| 3 | NE |
| 4 | N |
| 5 | NW |
| 6 | W |
| 7 | SW |

Document whether these labels denote world azimuth or projected screen-facing art. For a conventional screen vector with x right and y down, `atan2(dx, dy)` produces zero at S and positive angles toward SE/E. Quantizing that angle to 45-degree sectors yields the order above. Near zero speed, retain the last facing; optional hysteresis prevents direction jitter around sector boundaries.

For isometric games, choose sectors in the coordinate space that matches the authored view azimuths. A projected world vector is foreshortened, so equal screen-angle sectors need not match equal world-yaw sectors. Record the projection and direction mapping instead of copying the screen-space formula blindly. Also distinguish movement direction from facing: strafing and backward walking can preserve aim facing.

Source coordinates use a top-left origin, x right, y down, with pixels as units. Declare whether positions refer to pixel centers or continuous image edges. Anatomical `hand_left` and `hand_right` are character-relative and never renamed because their screen positions change.

Define a logical frame and a ground-root anchor. Example: frame 128 × 128, anchor `(64,104)`. The ground root is a stable origin, not the lowest opaque pixel or the average of the currently visible feet. Lean, bounce, jumping, and authored pose offsets remain motion relative to that origin.

Keep intentional root translation separate from normalization. With trimmed frames, drawing is conceptually:

```text
draw_top_left = root_screen
              + shared_root_motion
              + display_scale * (trim_offset_in_source - root_anchor_in_source)
```

Socket-bound pieces additionally apply the documented socket-to-piece-pivot transform. Do not also apply the socket transform to a piece already drawn in full-frame body coordinates.

## Required data groups

| Data group | Required contents | Purpose |
| --- | --- | --- |
| Package | Schema version, rig ID/version, art style, projection, source canvas, coordinate convention, direction order | Defines the shared interpretation |
| Clips | Action/grip ID, frames, positive duration per frame, loop rule, pose-phase landmarks | Defines the authoritative pose timeline |
| Base poses | Direction/frame keys, optional root offsets, sockets, contact/event markers | Defines fitting and attachment reference |
| Item definitions | Item ID, gameplay slots, compatible rigs/bodies/grips, supported poses, render pieces | Defines valid replacement scope |
| Appearance rules | Occupied/conflicting slots, hair/body coverage, visibility policy | Resolves combinations |
| Render pieces | Piece ID, placement mode, image/frame bindings, palette/material references | Keeps gameplay items independent of rendering splits |
| Ordering | Per-facing defaults, action/frame overrides, masks/depth policy if used | Resolves occlusion |
| Atlas frames | Atlas file, source rectangle, original logical size, trim offset, rotation, blank/alias state | Reconstructs registration after packing |
| Provenance | Creator/source, asset license, attribution, derivative history, tool/model/version | Makes reuse and regeneration reviewable |

A clip's direction coverage can be explicit. If an action intentionally supports fewer directions, declare that behavior and its runtime policy. A request for all eight directions cannot be satisfied by an undeclared four-direction fallback.

## Gameplay slots versus render pieces

Possible appearance slots include `body`, `head`, `hair`, `headgear`, `torso`, `legs`, `feet`, `hands`, `main_hand`, `off_hand`, and `back`. Choose only those the game needs. Gameplay equipment slots are a separate contract. For Astraeon, preserve the five existing authoritative slots and aliases in the [technical brief](astraeon-technical-brief.md); hats and wings must not silently become new combat slots.

Possible render pieces include `hair_back`, `hair_front`, `cape_back`, `cape_front`, `arm_left_back`, `arm_left_front`, `hand_right`, `weapon_back`, and `weapon_front`. Their usefulness depends on the base's poses. Do not mandate dozens of limb pieces for a simple paper doll.

One equipped item can provide several pieces and reserve several slots. Replacement of the item commits all its pieces and visibility effects together. A helmet may select a helmet-compatible hair variant or apply a pose-specific mask; hiding all hair is acceptable only if it is a deliberate art rule.

Define the base's role: complete body underneath clothing, segmented anatomy, or replacement anatomy included in equipment. Mixing these conventions without explicit coverage produces duplicated hands, exposed skin, or gaps.

## Compatibility

An item is compatible only when its rig/body family, source scale, projection, supported action/grip, frame timing, sockets, and required directions agree. Palette consistency and seam overlap require visual checking too.

Treat `one_handed_sword`, `two_handed_sword`, `bow`, `staff`, and `dual_wield` as possible pose families. An item artwork swap within a family can preserve phase. A family change may require another body/arm pose or a gameplay transition.

Allowed policies for unsupported combinations: reject with an actionable authoring error; choose an explicitly approved variant; or use a declared pose mapping reviewed for that combination. Do not silently omit required equipment during attacks.

## Minimal frame bindings

An untrimmed reference grid can use one sheet per piece and clip:

```text
items/iron_helmet/headgear/walk.png
items/iron_helmet/headgear/idle.png
items/iron_helmet/headgear/attack_onehand.png
```

Rows follow the direction array; columns follow clip frames. Thus an eight-frame clip has eight columns and eight rows. A two-frame idle has two columns and eight rows. Actions with differing frame counts do not need identical sheet widths.

This is the simplest one-to-one export convention. A part can instead declare a phase map or a body-pose-to-source-image table. For example, a three-entry head map can hold image A at phases `[0,.28)`, image B at `[.28,.42)`, and image A at `[.42,1)`. The head still resolves an attachment transform for every body sample. Source image reuse must not discard duration-bearing body poses or restart a part clock. Prove coverage and phase alignment before accepting nonidentical frame counts.

For a sheet with cell width W and height H, direction index d and frame f map to `x=f*W`, `y=d*H`, `w=W`, `h=H`. Retain a logical binding even when the image is blank. Duplicate images may be aliased without deleting their duration-bearing frame entries.

Packed atlases replace that formula with explicit rectangles and trim metadata. Disable rotated packing initially unless the loader handles the rotation flag. Do not infer original canvas or pivot from the packed rectangle dimensions.

## Occlusion model

Specify a facing default as an ordered list of piece IDs, from back to front. Allow an override key `(clip, direction, frame)` when a pose crosses that ordering. An invisible piece can remain listed but skip drawing.

If a frame needs `A behind B` and `A in front of B` in different regions, one whole-image position is insufficient. Split A into pieces or define validated coverage/depth composition. A cyclic whole-piece ordering constraint is an authoring failure, not a sorting algorithm problem.

For multiple piece sets, use either fully enumerated per-appearance order or consistent ordering categories with explicit insertion rules. Validate that every visible piece has exactly one placement in the final list and that masks reference the intended rig/pose.

## Runtime behavior

```text
sample = authoritative_clock.sample(action, direction, elapsed_or_gait_phase)
appearance = resolve_equipment_and_coverage(equipped_items, rig, action_family)
pieces = resolve_pose_images_and_part_maps(appearance, sample)
order = resolve_default_and_override_order(appearance, sample)
draw(pieces, order, shared_root_transform)
```

The renderer reads one pose sample. It does not advance a different timer for each sleeve, boot, and weapon. For durations that vary by frame, use cumulative duration intervals; for gait driven by distance, convert the shared gait phase through the same declared pose map.

On a cosmetic swap, preserve action, direction, current frame, subframe progress, and shared root. Preload required images, check compatibility, then commit the item, its pieces, masks, and palette changes atomically. A failed load keeps the previous complete appearance or uses a deliberate placeholder.

When changing direction mid-loop, preserve normalized phase only when direction clips represent matching phases. Do not interpolate two unrelated drawn poses by default; cross-fades can double silhouettes and weapons.

Animation event markers support authoring and debugging. Combat damage and authoritative gameplay events must follow the game's simulation rules; texture-loading completion should not determine when a hit happens.

## Validation coverage

Structural validators should find missing poses, nonpositive durations, invalid frame aliases, atlas bounds errors, unresolved render pieces, duplicate ordering entries, incompatible rig IDs, and coverage-rule conflicts.

Preview QA should exhaust the pose matrix for the base and every newly admitted item. Combine each new item with a reference outfit and stress items in neighboring slots. Use pairwise combination coverage where exhaustive outfits are too numerous, plus manually chosen cases for overlaps involving three or more parts. Pairwise coverage is a cost-saving strategy, not proof that every combination works.

Measure socket drift against an approved pose reference, not a constant screen point. Inspect planted-foot stability relative to ground/root and the simulation's displacement. Blanket recentering can hide bad registration while introducing foot sliding.

## Proposed acceptance criteria

- All declared pose bindings resolve or have reviewed explicit aliases.
- Cosmetic replacement leaves the sampled pose unchanged.
- No unexplained seams, clipping, disappearing pieces, or handedness changes at native scale.
- Direction/action/frame order matches reviewed occlusion examples.
- Packed output reconstructs the authoring composite within the chosen pixel/alpha tolerance.
- Runtime sorting and memory meet measured project budgets.

Pixel-art comparison can often use exact reconstructed pixels; painted images may need a specified tolerance for exporter/compositor differences. Choose the tolerance from the pipeline, not from an arbitrary score claimed to prove artistic quality.
