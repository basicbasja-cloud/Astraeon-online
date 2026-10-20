# Ragnarok open-source reference for Astraeon character assets

**Applied to:** Production Factory V3 Swordsman
**Reviewed:** 20 October 2026

## What the source code contributes

Open Ragnarok clients are useful engineering references for how a game keeps a
character's body, hair/head, accessory slots, weapon, palette, and action frames
composable. Goro's renderer keeps body, head, accessory tiers, weapon, weapon
light, and shield as separate sprite views; its actor appearance tracks hair,
weapon, shield, and headgear independently. Its action selection resolves an
ACT action from the action family and facing. OpenMidgard loads paired `.act`
and `.spr` resources for a character. These patterns support independent parts,
shared action timing, directional pose lookup, and replaceable equipment.

## Astraeon implementation

V3 already has the runtime primitives needed for that design:

- one shared clip timeline with explicit frame duration and eight unmirrored
  directions;
- distinct `BaseBody`, `Hair`, `Outfit`, `Weapon`, `Headgear`, and
  `BackAccessory` slots, shared root, and per-pose sockets;
- atlas records keyed by part/action/direction/frame and one common draw order;
- independently selectable cosmetics, with a transparent no-cloak part;
- an optional `CosmeticFX` slot for a separate sword-trail layer.

The old painted importer did not use those capabilities correctly: it packed a
whole-character image into `Body`, left the other slots transparent, and still
passed schema checks. The first attempt at independently generating each layer
also broke visual alignment. The owner redirected the authoring flow to match
the source-frame approach used by sprite-action systems: paint one complete
master per action/view/frame, cut parts from that exact master with one shared
pixel-label sheet, then reassemble and compare it pixel-for-pixel. The new
`cutout_master_sheet.py` extracts those parts without moving or repainting any
pixels; `import_layered_sheets.py` remains the downstream packer for reviewed
cutout sheets. CosmeticFX is an independent cutout and is never baked into the
sword.

The research branch's alpha-silhouette continuity audit is incorporated as a
diagnostic in `audit_sprite_candidate.py`. Its 0.88 adjacent-frame IoU threshold
flags frames for visual inspection; it does not determine whether a human attack
pose is good. The audit also reports body size/baseline movement, action timing,
weapon/effect visibility, the default back accessory, and whether a composite
tag remains.

## Reference repositories

- [Goro client source](https://github.com/kivutar/goro), including
  [`game/sprite_render.go`](https://github.com/kivutar/goro/blob/main/game/sprite_render.go)
  and [`game/world.go`](https://github.com/kivutar/goro/blob/main/game/world.go).
- [OpenMidgard client source](https://github.com/Sziadan/open-midgard), including
  [`src/session/Session.cpp`](https://github.com/Sziadan/open-midgard/blob/main/src/session/Session.cpp)
  and [`src/ui/UIEquipWnd.cpp`](https://github.com/Sziadan/open-midgard/blob/main/src/ui/UIEquipWnd.cpp).
- [ragnarokoffline.app](https://github.com/Flux159/ragnarokoffline.app) combines
  the open-source rAthena server and roBrowserLegacy client. Its setup requires
  game data to be obtained separately.
- The owner's [rAthena Ragnarok Online wiki reference](https://github.com/rathena/rathena/wiki/Ragnarok_Online)
  is an overview of Ragnarok systems; rAthena itself is server-side. Client
  sources are the relevant reference for sprite assembly and directional frames.

Use the open-source projects as hands-on references for character drawing,
frame conventions, layer order, body/head/hair separation, equipment placement,
and effects. If a repository includes source images or sprites with a license
that permits reuse, record that exact file and license before adapting it.
Project code being open-source does not automatically relicense official
Ragnarok sprites, sounds, maps, or GRF files. OpenMidgard asks for legally
obtained runtime data, and ragnarokoffline.app excludes Gravity-owned game
assets. The current Astraeon masters are original, then cut into same-frame
templates using the workflow directed by the owner.

ACT resources define animation frames as ordered sprite layers with per-frame
positions, transforms, tint, anchors, events, and timing. The ACT format does
not name a universal `Weapon Slash` layer. Goro's client instead keeps
`weaponLight` as a distinct humanoid layer beside `weapon`, resolves its motion
from the same facing/action/body-motion state, and draws layers in a facing-
dependent order. See [Goro's layer renderer](https://github.com/kivutar/goro/blob/main/game/sprite_render.go),
the [ACT frame and layer reference](https://github.com/rdw-archive/RagnarokFileFormats/blob/master/ACT.MD),
and the [rAthena ACT wiki](https://github.com/rathena/rathena/wiki/Acts).
Ragnarok stand/walk clips loop while attack clips play once. Astraeon's next
pass follows these patterns: 16-phase Idle/Walk cycles with no duplicated
endpoint, one-shot BasicAttack with a stable recovery pose, and a transparent
`WeaponLight` sheet synchronized to each action, direction, frame, and sword
position.

The first direction-specific stroke pilot is rejected: it crosses the body and
does not track the blade. It remains only as a diagnostic in the old 8-frame
paint job. The replacement must be drawn against the 16-frame attack guide and
reviewed for alignment and facing-dependent overlap before runtime admission.

## Review status

The older painted-v2 runtime candidate is still fused, has no visible weapon in
its independent Weapon slot, has no separate trail part, and uses a transparent
default Back slot. The current 8-frame review candidate has full-character
masters and per-frame cutouts for Idle, Walk, and BasicAttack, with exact pixel
recomposition. Its eight painted poses are below the smoothness bar. Separate
16-phase, eight-direction Blender pose guides now exist for all three actions;
they are low-detail references, not finished character art. The HeadHair label
includes a face-region heuristic that needs visual checking; hidden surfaces
and Headgear remain unpainted. Walk and BasicAttack continuity metrics are
below the research 0.88 warning. Neither the cutouts nor rejected trail pilot
has been admitted to runtime or previewed on the requested map. Before calling
the art modular and production-ready, repaint and review the 16-frame masters,
paint concealed surfaces, verify cloak/no-cloak and equipment swaps, and review
the composed animations in the requested map.
