# New dedicated Swordsman candidate

Candidate: `fresh-2d/candidate-01`. State: **CONCEPT_APPROVED / PRODUCTION_DEV_ONLY**.
The owner approved the painted concept on 10 October 2026 and authorized iteration
until the next decision. Eight-direction source, layers, motion and release remain
unapproved. Exact approved image and statement are retained in the candidate's
`CONCEPT_APPROVAL.md`.
This is a fresh painted 2D source. The rejected mannequin and old motion frames
are not inputs. Preserve the inherited silver hair, gold cape, bronze armour,
ivory tunic and teal detail as identity vocabulary; this is not a claim that the
new rendering inherits approval from the old identity crop.

## First review deliverable

One complete elevated southeast standing view. Compact Ragnarok-inspired
proportions, about 3.7 heads tall, with readable painted volumes at game scale.
The anatomical right fist wraps one sword handle. Wrist, guard and blade form a
coherent grip; the blade rests outside the boots. Both legs support the pelvis.
The sword is a normal one-handed weapon, not a greatsword.

The raw generated PNG and exact prompts are retained. It is composite artwork;
there are no independently authored BaseBody, Outfit, Hair or Weapon layers yet.
No motion or eight-direction consistency is claimed. The actual generated canvas
is inspected and recorded; a prompt requesting a size or camera is not proof that
the resulting image meets that measurement.

## Requirements before expansion

| Gate | Concrete deliverable | Acceptance |
|---|---|---|
| Visual identity | One finished SE image plus honest small-scale preview | Owner accepts silhouette, camera, anatomy, sword and style |
| Turnaround | Eight independently authored views | Same identity, scale and anatomical handedness; no mirrored equipment |
| Source parts | Editable directional body/face/hair/costume/weapon parts, including hidden surfaces | Empty-slot and real alternate-item composites are correct |
| Motion pilot | Walk and BasicAttack in S, SE, N | Foot support, elbows, wrist grip, overlap, anticipation, impact and recovery read correctly |
| Complete character | All required actions in all eight directions, layered sprites and metadata | Visual review and existing packaging/runtime validation both pass |

## Motion and equipment coverage

Current wardrobe names: Idle, Walk, Run, Sprint, BasicAttack, SkillAction,
CastChannel, CastRelease, Guard, Dash, Blink, Hit, Death, Interact, Pickup,
ItemUse, Sit, Respawn. The Swordsman source contract excludes Blink and makes
Sit optional. Resolve this discrepancy explicitly before releasing a package.
Keep distinct impact, interrupt, loop and final-hold behavior. An absent action
cannot be filled with Idle and marked authored.

First weapon family: one-handed sword. First variation proof: a different sword
within the same family and an alternate actual costume. Two-handed swords,
spears, bows and staffs get compatible grip/stance/action families when introduced.
Costumes fit the approved body; sleeve and cape movement may require additional
art rather than a recolor. Each new body shape requires a fitting review.

## Authoring and game output

Recommended scalable source: Krita-painted parts, Spine direction/action template
and costume skins, then fixed-canvas component exports. Spine is a paid authoring
option and is not currently installed or required for the first image. Existing
ASTRAEON sprite runtime and tools remain the output contract.

Production target: 320×320 RGBA, root (160,264), reference anatomy height 176;
uniform 0.5 runtime compilation to 160×160, root (80,132), reference height 88.
A browser-scaled preview of raw art is not a normalized production frame.

## Bounded iteration

One candidate identity, with at most one targeted correction before route review.
No bulk motion, costume or weapon generation until this visual source is accepted.
Record visible shortcomings and approval separately from technical alpha/hash
checks. If it remains unsuitable, preserve it and change the production route
instead of repeatedly repairing the same source.

See [research and tool comparison](RESEARCH_2D_EIGHT_DIRECTION.md).
