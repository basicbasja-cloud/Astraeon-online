# Patch 0.0.1 action direction decision

## Research evidence

Reviewed `origin/research/modular-sprites-full-body-2026-10-11` at `db59cc922ed1760243ffed9f07a81b891516db27`, especially `docs/character-factory/RESEARCH_2D_EIGHT_DIRECTION.md` and `RESEARCH_COHERENT_SPRITE_AUTHORING_V2.md`.

The retained RO research documents ACT indexing as `actionFamily * 8 + direction`. This establishes eight addressable facings. It does not establish eight distinct drawings for every action, or a universal four-direction attack/cast rule. Do not describe an Astraeon production choice as a verified RO asset rule.

## Current production policy

Physical sword and bow attacks retain the owner-requested four real diagonal views (SW, NW, NE, SE). Latest owner correction: all casting uses four diagonal views, including Mage Arcane Bolt/basic attack, CastChannel and CastRelease for all classes. General movement, reactions and non-casting utility actions retain eight. Male and female use the same action direction contract; artwork compatibility remains separately reviewed.

The table below is the current factory configuration, not a claim that the artwork is complete. A source-specific RO four-view exception requires actual ACT/SPR evidence before changing this policy.

| Class | Action | Authored views | Basis |
|---|---|---:|---|
| Swordsman | Walk | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Swordsman | Run | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Swordsman | Sprint | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Swordsman | Hit | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Swordsman | Death | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Swordsman | Interact | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Swordsman | Pickup | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Swordsman | ItemUse | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Swordsman | Sit | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Swordsman | Respawn | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Swordsman | Idle | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Swordsman | CombatIdle | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Swordsman | BasicAttack | 4 | Owner physical-attack convention |
| Swordsman | SkillAction | 4 | Owner physical-attack convention |
| Swordsman | CastChannel | 4 | Owner casting convention |
| Swordsman | CastRelease | 4 | Owner casting convention |
| Swordsman | Guard | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Swordsman | Dash | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Swordsman | SpinAttack | 4 | Owner physical-attack convention |
| Mage | Walk | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Mage | Run | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Mage | Sprint | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Mage | Hit | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Mage | Death | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Mage | Interact | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Mage | Pickup | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Mage | ItemUse | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Mage | Sit | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Mage | Respawn | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Mage | Idle | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Mage | CombatIdle | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Mage | BasicAttack | 4 | Owner casting convention |
| Mage | SkillAction | 4 | Owner casting convention |
| Mage | CastChannel | 4 | Owner casting convention |
| Mage | CastRelease | 4 | Owner casting convention |
| Mage | Guard | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Mage | Blink | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Archer | Walk | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Archer | Run | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Archer | Sprint | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Archer | Hit | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Archer | Death | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Archer | Interact | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Archer | Pickup | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Archer | ItemUse | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Archer | Sit | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Archer | Respawn | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Archer | Idle | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Archer | CombatIdle | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Archer | BasicAttack | 4 | Owner physical-attack convention |
| Archer | SkillAction | 4 | Owner physical-attack convention |
| Archer | CastChannel | 4 | Owner casting convention |
| Archer | CastRelease | 4 | Owner casting convention |
| Archer | Guard | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Archer | Dash | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Archer | TrapPlace | 8 | Eight-facing contract; RO indexing reference or Astraeon extension |
| Archer | ArrowRain | 4 | Owner physical-attack convention |

## References

- [Retained research](ro-action-direction-reference.md).
- https://ragnarokresearchlab.github.io/file-formats/act/
- Configuration: `../factory.json`.
