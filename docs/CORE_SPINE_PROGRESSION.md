# Patch 0.0.1 progression/stat/save foundation

This implements the progression/stat/save portion of Core Spine only. The
authoritative design remains `ASTRAEON_Backbone_Release_Roadmap_EN_v0.4.md`.
Combat's full staged damage pipeline, skill trees, action loadouts, item instances
and the rest of 0.0.1 remain future tasks. No Advanced Jobs are implemented.

## Boundaries and API

- `progression-config.js`: deeply frozen EXP curves, caps, rewards, stat costs,
  conversion coefficients, limits and current equipment compatibility values.
- `progression.js`: pure, immutable Base/Job transitions. Base cap 60, Job cap
  50; a supplied configuration supports a larger Base cap without adding a tier.
- `stats.js`: pure derived calculator, additive class conversion hooks, equipment,
  passive and temporary effect groups. No DOM, storage, RNG or clock input.
- `character-state.js`: private authoritative state, validated spending and
  resource clamps. Returned snapshots and definitions are frozen.
- `player-state.js`: adapter for legacy string equipment, companion HP and
  gameplay fields. `game.js` orchestrates existing gameplay through this adapter.
- `save-state.js`: versioned pure normalization, migration and serialization.
- `tools/progression.html`: plain developer presentation using the shared API.

`AstraeonCharacter.create(data)` provides `grantBaseExp`, `grantJobExp`,
`getBaseExpRequirement`, `getJobExpRequirement`, `setBaseLevel`, `setBaseJobLevel`,
`addStatPoints`, `addSkillPoints`, `allocateStat`, `resetStats`, `getPrimaryStats`,
`getDerivedStats`, `setCurrentHP`, `setCurrentSP`, `setModifiers` and `snapshot`.
`AstraeonPlayer.attach(save)` exposes these same operations on a persistent
game save. It recalculates legacy equipment/party changes before operations.

EXP, levels, point additions and allocations require safe integers. Allocation
amounts must be positive; the default cost is one point per stat increment.
Unknown stats, non-finite values, overspending and exceeding the allocation cap
throw without spending points. Reset refunds allocated increments once.
Skill Points are a persistent unspent pool; this task introduces no skill tree.

Level setters adjust the unspent pool by the configured reward difference. They
clear that track's EXP only when its level changes. Repeating the same setter
does not grant points or erase EXP. Lowering a level rejects if it would reclaim
spent points. A capped EXP grant discards surplus; no banking/conversion exists.

## Derived calculation

Start from character base + level coefficients. Aggregate primary stat bonuses
from equipment, passives and temporary effects, then apply the configured
primary conversions. Optional pure conversion hooks return additive derived
contributions. Add each group's derived flat contributions, then multiply by
`1 + sum(all rates)` and apply configured limits/rounding. A rate of `.1` means
+10%. No group has an implicit overwrite operation. Hooks receive frozen input.
Only the final immutable snapshot is consumed; definitions never accumulate
bonuses. HP/SP clamp when maxima decrease, and increasing a maximum does not
heal by itself. Existing gameplay Base level-ups still restore both resources.

Default coefficients preserve the prior unallocated level-1 damage and resource
capacities. They are provisional balance data. Melee/ranger damage consumes
physicalATK, Mage damage consumes magicATK, and maxHP/maxSP drive current resource
limits. HIT/FLEE/CRIT/ASPD/cast/DEF/MDEF/resilience/weight are ready as data; this
task does not activate new accuracy, timing, mitigation or weight mechanics.
Existing Warden Plate mitigation and ability timing remain in the playable game.

## Save version 4 and compatibility

Version 4 identifies authoritative progression/stat/resource fields:
`baseLevel`, `baseExp`, `baseJobLevel`, `baseJobExp`, `statPoints`, `skillPoints`,
`STR`, `AGI`, `VIT`, `INT`, `DEX`, `LUK`, `currentHP`, `maxHP`, `currentSP`, `maxSP`
and `resourceBase`. The existing storage key `astraeon-iso-v1` remains valid.

Canonical valid values take precedence over legacy mirrors. Legacy `lv/xp`
become Base progression; Job defaults to 1/0. Missing stat/skill pools start at
zero, with no retrospective level rewards. Primary stats default to 1.
Load never grants EXP or processes a level-up, even for a historical EXP value
above its requirement. Historical Base levels above 60 are preserved; subsequent
capped grants discard EXP without additional levels or points.

Legacy `hp/maxHp` and `energy/maxEnergy` become HP/SP. The first migration records
their capacity difference from the current baseline in `resourceBase`, accounting
for existing companion HP. This preserves actual historical capacities and
allows future primary/level/modifier changes without repeated migration bonuses.
`legacyBackbone` archives original old progression/resource values once. Both
fields persist; recalculation does not turn equipped or temporary bonuses into
permanent offsets. Active temporary effects are intentionally runtime-only.

Legacy fields remain serialized mirrors. In the running game they are getters
into private state; HP/energy writes use clamped setters. Levels, EXP, points,
primary stats and maxima cannot be assigned by unrelated gameplay code.
Current Resolve/Mana/Focus costs and regeneration use SP through the energy
alias. This is a compatibility bridge, not a new class resource system.

Inventory, equipment (including unknown slots), gold, quests, worldClaims,
discovery, chapters, skillNodes and valid historical/unknown fields retain the
existing normalization rules. Existing safe-spawn recovery still handles blocked
positions. Dungeon runs and runtime combat effects retain their prior lifecycle.
No load grants items, resets gear or repeats world claims. Round trips are
deterministic and idempotent. Malformed numeric values receive safe defaults;
fractional progression fields become integers, while HP/SP may remain fractional.

## Developer use and verification

Serve the checkout on localhost, then open `/tools/progression.html`. Its isolated
`astraeon-progression-dev-v1` key does not modify the playable character. It shows
progression, points, primary/derived stats and raw saves, with EXP, allocation,
reset, level/point/resource, save and reload controls. No formulas live in it.

For an explicit development session open `/?qa=1&dev=1`. After character creation,
`AstraeonProgressionDev` exposes the same operations plus `save()` and a full
persistent `snapshot()`. Mutations refresh the existing HUD; call `save()` before
reload. The API is absent without `dev=1`. Use disposable characters for testing.

```powershell
python tools/run-node-checks.py
python tests/progression_browser.py --url http://127.0.0.1:8011
python tests/cache_resume.py --url http://127.0.0.1:8011
```

Browser checks support `ASTRAEON_BROWSER` or `--browser`; reports/screenshots are
written outside the checkout. Boot/page/service-worker version 84 loads the new
modules together and precaches them, preventing cached code/schema mismatches.
No character, world, lighting, renderer or production UI artwork was changed.
