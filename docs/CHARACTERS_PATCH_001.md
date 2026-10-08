# Characters for patch 0.0.1

Work branch: `codex/swordsman-visual-production-v0.1`, starting at `1b8b1c7`.

Open `character-studio.html` to select Swordsman or Mage, male or female body,
class hair or silver tied bob, and Traveler attire or Astral Court costume.
All clips can be played, paused, scrubbed, and viewed at game size in eight
named directions: S, SW, W, NW, N, NE, E, SE. No runtime direction mirroring.

The game creator and Character → Appearance use the same layer compositor.
The save stores `appearance` separately from equipment, inventory, stats,
skill nodes, and progression. Existing saves without appearance retain their
previous art until the player applies an appearance in town or at a safe camp.

## Shared anatomy

All four character packages use the same original anatomical rig and pose
registration: 320×320 authoring canvas, root (160,264), 176px reference body
height, and a 48×50 skull envelope. Hair volume and costume silhouettes may
extend beyond that anatomy. Runtime sheets use one uniform 0.5 scale for all
frames, directions, classes and layers: 160×160 canvas, root (80,132), 88px
reference height, 24×25 skull envelope. Physics and combat coordinates remain
in world units. No frame is individually fitted, stretched, trimmed or mirrored.

## Motion contract

| Motion | Frames per direction | Playback / game use |
| --- | ---: | --- |
| Idle | 8 | Loop; standing |
| Walk | 16 | Distance-driven; deliberate movement |
| Run | 12 | Distance-driven; normal movement |
| Sprint | 12 | Distance-driven; sprint |
| BasicAttack | 16 | Swordsman strike |
| SkillAction | 14 | Swordsman attack skill |
| CastChannel | 12 | Loop; cast anticipation |
| CastRelease | 10 | Cast release and recovery |
| Guard | 10 | Loop; defensive skill |
| Dash | 10 | Swordsman evasion |
| Blink | 10 | Mage evasion |
| Hit | 8 | Damage interrupt |
| Death | 12 | Fall, then hold last pose |
| Interact | 8 | NPC / world interaction |
| Pickup | 8 | Gathering / loot |
| ItemUse | 8 | Flask / food |
| Sit | 8 | Inn, house or safe camp rest |
| Respawn | 10 | Town recovery |

Each complete body has 1,536 directional poses and eight separately baked
part surfaces: BaseBody, native Hair, silver-bob Hair, native Outfit, Astral
Court Outfit, Weapon, empty Headgear and empty BackAccessory. All parts use
the same frame clock, root and sockets. Empty accessory slots are intentionally
transparent, with atlas deduplication; they are not missing character motions.

`hair.silver-bob.001` and `costume.astral-court.001` are stable cosmetic SKUs.
The current offline prototype lets players preview and wear both cosmetics.
A future store must check purchases and ownership on the server; the local
appearance IDs are presentation data and do not establish paid entitlements.

## Scope and references

The supplied Ragnarok Walking NPC and Female Novice sheets were inspected
for eight-direction staging, body/head proportions, motion readability and
layer separation. Their pixels are not shipped. Paint comes from the existing
original Swordsman masters and newly generated original ASTRAEON masters.
Source art, registrations, whole strips, per-frame contact sheets and provenance
are kept under `authoring/characters/patch-001/`.

Read-only scope checks included the `backbone-design`,
`backbone/skill-tree-0.0.1`, `backbone/action-loadout-0.0.1`, and
`backbone/action-item-0.0.1` branch descriptions/docs. Swordsman (legacy class
ID 0) and Mage (12) are the two new creator choices. Their existing four skills,
basic attack, evasion and items reuse these body motion families. Nodes and
spell effects remain separate from body paint. This work does not merge or
replace those branches' progression systems. Existing Ranger saves and town
training remain compatible with the previous renderer.

## Rebuild and inspection

```sh
python3 tools/rebuild-characters-001.py --masters
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 tools/rebuild-characters-001.py --character swordsman-male-001 --pack
# Repeat for swordsman-female-001, mage-male-001 and mage-female-001.
python3 tools/rebuild-characters-001.py --pack-existing mage-male-001
python3 tools/validate-sprites.py
python3 tools/run-node-checks.py
```

Generated source PNGs are stored inside the repository, so reproducing the bake
requires no provider call. `--pack-existing` repacks complete source strips
without rerendering poses. The source rig scripts require Pillow, NumPy and
SciPy; validation also uses jsonschema and Node.

Visual candidates are explicitly tagged `DEV_ONLY` /
`REQUIRES_OWNER_VISUAL_REVIEW`. Production coverage and technical validation
are not a claim of owner art approval or guaranteed frame-perfect visual quality.
Original branch approval records are preserved.

## Checkpoints

- Creator, wardrobe persistence, original source masters and full Mage packs:
  implemented; browser inspection underway.
- Swordsman full action bake: underway at this checkpoint.
- Full coverage, composition, live game and responsive validation: underway.
