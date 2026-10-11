# Free motion source and retargeting decision

11 October 2026, `character/production-factory-v2`.

The owner authorized free preset animation downloads and Ragnarok pose
references. The owner confirmed that “90 degrees” means the sword/grip axis
perpendicular to the forearm, with a naturally aligned wrist.

## Selected source

Quaternius Universal Animation Library Standard 1 and 2 supply the donor
motions. Their creator pages state CC0, commercial use and retargetable
humanoid rigs. The free download flow unlocks Standard; Pro/Source tiers cost
money and were not downloaded. No account, upload, checkout or payment was used.

- [Creator library 1](https://quaternius.com/packs/universalanimationlibrary.html)
- [Creator library 2](https://quaternius.com/packs/universalanimationlibrary2.html)
- [Library 1 download and changes](https://quaternius.itch.io/universal-animation-library)
- [Library 2 download and changes](https://quaternius.itch.io/universal-animation-library-2)

The included `License.txt`, archive hashes, source URLs and file inventory are
retained in the candidate's `factory/`. Creator credit: Quaternius; the creator
pages also credit animator Gonzalo Furnier. This license applies to donor
motions, not the owner's separate fantasy archive or approved concept.

## Actual mapping

| ASTRAEON action | Preset source |
|---|---|
| Idle | Idle_Loop |
| Walk | Walk_Loop |
| Run | Jog_Fwd_Loop |
| Sprint | Sprint_Loop |
| BasicAttack | Sword_Attack |
| SkillAction | Sword_Regular_B + Sword_Regular_B_Rec |
| CastChannel | Spell_Simple_Idle_Loop |
| CastRelease | Spell_Simple_Shoot |
| Guard | Held middle section of Sword_Block |
| Dash | Sword_Dash |
| Hit | Hit_Chest |
| Death | Death01 |
| Interact | Interact |
| Pickup | Farm_Harvest |
| ItemUse | Consume |
| Sit | Sitting_Idle_Loop |
| Respawn | LayToIdle |

Only rest matrices and skeleton samples are transferred. Neither donor
mannequin meshes nor their body proportions, weights, finger poses, cameras or
materials enter the fantasy source. Rest/pose rotation differences correct
different bone rolls. The target retains its fitted lengths and source paint.
Pelvis translation scales to the target legs; the fixed game action durations
and frame counts resample the presets rather than preserving donor durations.

The right hand keeps its custom finger curl and a neutral local wrist. A single
forearm pronation offset calibrates the grip orientation for all clips. The
hilt axis is perpendicular to the forearm in bind space and the audit measures
the result on actual poses. Enlarged head/body floor contacts and continuous
cape floor deformation address the target's proportions during the fall.
These are native geometry/pose corrections, not patches painted over sprites.

The first trial used Sword_Idle for Idle. Its deep combat stance obscured this
character's face, so the neutral Idle_Loop was selected. The first fall trial
penetrated the floor and clipped N/NE. That trial is not the delivered bake.

## Ragnarok reference scope

Retain the earlier research in `RESEARCH_COHERENT_SPRITE_AUTHORING_V2.md` and
the owner's weapon sheet: coordinated body/outfit, head/hair, headgear,
weapon and cape registration; real eight headings; hidden hilt pixels belong
to the holding hand. Ragnarok is a reference for pose readability and layer
composition. No Gravity sprites, textures or proprietary animation files are
copied into this package. Preset availability does not certify a style match.

## Remaining visual gate

Technical checks measure timing, geometry, registration and composition.
Owner review must still judge facial likeness, painted finish, weight and
motion readability. Do not describe a passing numeric audit as perfect art.
