# Checkpoint audit — 7 October 2026

The user requested an audit after switching models, authorized reverting messy
work, and then asked to resume the original architecture and neighborhood task
using `RO3 Ref/Prontera_RO3_Beta_Reference`.

The restored city is the pushed checkpoint `d7f9f15978b0ca6347fe5f80302d147544bd4626`
on `codex/world-pipeline-v3-proof`.

- World export SHA256: `ad5956f55b4a4d1fb00c665754f5bc28f13b001a7f1456bf0e6c3e01894155dc`.
- Native Blender SHA256: `b6bf486e4261bb6c247c4a2facaae8186d07aac7e96ce403ecbca4db3a09fbc3`.
- 158 buildings, nine new architectural families, three distinct civic additions,
  and 28 ambient walkers. These counts do not establish RO3 visual acceptance.

## Reverted work

The intervening model described redistributing residents but actually added six
new walkers, taking the total from 28 to 34. Their paths were tiny loops arranged
around a single camera view. It also changed the density check to require 34.
No gameplay images of that candidate were produced. The supplied multiplayer
crowd is not evidence for an exact ambient-NPC budget.

An independent semantic comparison proved that removing those six records made
the candidate world identical to the Git checkpoint. Buildings, roads, floor
surfaces, materials, lighting, existing routes and existing actors had not changed.
Both native and exported city files and the original density check were restored.
The two experiment scripts and their authoring report were removed. A recoverable
copy is in `/tmp/astraeon-model-switch-plaza-experiment-20261007`; that scratch
archive is not part of the project or the resumed city.

## Retained review evidence

All retained screenshots identify the restored world hash in their manifests.

| Capture | Actual position | Evidence |
| --- | --- | --- |
| `../beta-default/street-west.png` | [80, 201] | Ordinary 910×512 gameplay street view |
| `../beta-default/plaza-frontages.png` | [128, 132] | North plaza approach; unsuitable as the sole fountain comparison |
| `../diagnostics/plaza-correct-anchor/plaza.png` | [128, 150] | Actual named Plaza route point, matching the fountain approach |

Each capture reports no runtime errors and zero changed pixels between ordinary
culling and exhaustive submission. They establish capture integrity, not visual
equivalence or performance acceptance. Projected player geometry bounds include
sprite padding and must not be treated as measured character artwork height.

The retained three-line capture-tool fix resolves `plaza-frontages` to the named
Plaza route point. It changes review placement only. The previous north-approach
capture remains explicitly labeled with its original position.

## Verification and continuation

`native-parity.log` verifies that the saved Blender file reproduces the restored
export. Its stale-bake message comes from the deliberate unsaved caster movement
used to verify bake invalidation; the saved source contains its matching 4096²
ground-shadow atlas. `traversal.json` verifies 26 reachable destinations and 28
clear patrols. The existing `../node-final/report.json` matches this exact world
hash and records 96 passing checks. The repeated public schema audit passes (`schemas.log`). `integrity.json` records
byte equality with the checkpoint and the verification results.

Resume the user's architecture request: assess whole-building silhouettes,
rooflines, useful storefronts, local courts, curb ownership and character-relative
spacing in actual gameplay views. Inspect the supplied house/street/civic frames
before altering geometry. Full neighborhood, court, civic, shore, ordinary walking,
cache and performance review remains open. The RO3 baseline has not been accepted.
