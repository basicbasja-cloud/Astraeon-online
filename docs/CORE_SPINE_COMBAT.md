# Core Spine: staged combat resolution foundation

This implements only the Combat Resolution foundation of Patch 0.0.1, plus
future-save protection and actual paid Stat Point accounting. Every combat
coefficient here is provisional. Nothing here declares the Core Spine complete.

## Ownership and dependency boundaries

| Module | Responsibility |
|---|---|
| combat-resolution-config.js | Frozen provisional defaults and pure override merger |
| combat-resolution.js | Plain-data validation, staged immutable results, pure HP application and future timing helpers |
| combat-runtime.js | Authorized action/stat snapshot adapter; injected sequence RNG and production RNG provider |
| combat.js | Existing definitions, Timeline and shape/projectile execution; skill launches now support an external cooldown owner |
| game.js | Existing contacts, HP assignment, rewards, status effects, presentation and persistence |

The resolver uses no DOM, storage, clock, Math.random, actor mutation or authored
skill mutation. Its inputs are cloned before freezing. Callers retain their own
mutable inputs. The production RNG provider alone uses Math.random. It is not
cryptographically secure or server authoritative.

```js
const input = {
 attacker: {level: 1, stats: attackerDerived},
 defender: {level: 1, stats: defenderDerived,
            resistances: {fire: .2}, mitigation: {guarded: true, shield: 10}},
 action: {damageType: 'physical', coefficient: 1.8, canCrit: true,
          accuracy: 'normal', penetration: {percent: .2, flat: 5},
          resistanceCategory: 'fire', tags: ['burn'],
          statusCandidates: [{kind: 'burn'}], onHitCandidates: [], procMetadata: {}},
 context: {mode: 'pve', sourceSkillId: 'rising-edge', sourceRank: 3, nodeId: 'qi'}
};
const result = AstraeonCombatResolution.resolveAttack(input, {
 config: AstraeonCombatResolutionConfig.configure({critical: {multiplier: 2}}),
 rng: AstraeonCombatRuntime.sequenceRng([.5, .5, .5])
});
const hp = AstraeonCombatResolution.applyCombatResult(currentHP, result, maxHP);
// Caller assigns hp.hpAfter only when hp.ok, then handles candidate side effects.
```

## Validation and normalized contracts

The [Action Loadout extension](CORE_SPINE_ACTION_LOADOUT.md) now owns skill
eligibility, explicit-time cooldowns and resource commit before this downstream
adapter. `Timeline.start(...,{externalCooldown:true})` delegates only skill
cooldowns; Basic Attack retains its Timeline clock. Resolver formulas, authored
payloads and timing definitions remain unchanged.

Both actors require a finite level >= 1 and a derived snapshot containing
physicalATK, magicATK, HIT, FLEE, CRIT, perfectDodge, DEF and MDEF. These fields
are non-negative; CRIT/perfectDodge currently accept percentage units [0,100].
Every nested numeric value must be finite, including unused metadata. Only
plain data/arrays cross the contract. Undefined optional data is allowed.
Snapshots may include other derived fields. Added damage types configure their
own required attack/defense keys and defense rule; current class IDs never
appear in the pure resolver.

Action coefficient defaults to 1. An explicit baseDamage substitutes for ATK,
then uses the same coefficient. Negative or overflowing damage is rejected.
Flat penetration is non-negative and percent penetration is [0,1]. Resistance
map values accept [-1,1] and are further clamped by config. Mitigation reductions
accept [0,1], shield amounts are non-negative, and eligibility flags are boolean.
Policies are normal/guaranteed/ignoreFlee; canPerfectDodge is independent.
Context mode supports pve/pvp metadata only, with no invented PvP modifier.

resolveAttack returns structured {ok:false, code, path, finalDamage:0} on invalid
input/config/RNG, including exhaustion/throwing providers. No HP/state mutation
has happened at any point. RNG draws are validated when consumed, because their
count depends on the actual path. Rejected late draws discard all pending damage.

## Stages and provisional rules

| Stage | Behavior |
|---|---|
| validate | Validate/copy normalized actors, action, context, config and provider |
| accuracy | Clamp base + (HIT − FLEE) × scale + levelDifference × levelScale; guaranteed or configured crit bypass skips draw |
| perfectDodge | Independent chance from defender derived perfectDodge, after accuracy success |
| baseDamage | Authorized coefficient × explicit baseDamage or selected derived ATK |
| critical | Attacker CRIT × configured scale; multiplier and partial defense ignore are independent config |
| defense | Percent penetration → flat penetration → clamp at zero → critical ignore → physical DEF/magical MDEF rule |
| resistance | Category lookup, missing neutral; clamp resistance then multiply damage by (1 − resistance) |
| mitigation | Positive attack defense floor → parry → guard → block → shield → decimal stabilization → rounding |
| hpApplication | Result declares pending HP damage; separate pure helper clamps application, reports applied damage/death/overkill |
| statusOutput | Output copied status/on-hit candidates for positive final damage; caller owns effects |

Miss and perfectDodge terminate early with zero damage and empty candidates.
Guarded/blocked/parried flags, absorbed amount, mitigated amount and final damage
are separate fields. Fully parried/absorbed outcomes remain zero even with a
configured defense floor. Shield consumption is a reported amount, never a
mutation of the shield. Rounding can also reduce small residual damage to zero.
mitigated reports reduction from damageAfterResistance to remaining damage;
it excludes defense/resistance reduction and subsequent integer rounding.

Default critical bypass is off. Turning it on requires a policy crit pre-roll
before accuracy. This selects bypass eligibility only: crit damage is applied at
the critical stage after Perfect Dodge. The normal RNG order is accuracy,
perfectDodge, critical; bypass order is criticalPolicy, optional accuracy,
perfectDodge. Guaranteed accuracy and disabled stages skip their own draw.
Enabled checks draw even at chance 0/1, making invalid providers detectable.
Trace records stage values and each consumed roll. Same input/config/roll stream
produces the same deeply immutable result.

Default executable fixtures: accuracy base 1, HIT/FLEE scale .005, level scale 0,
accuracy clamp [.05,1]; Perfect Dodge/CRIT scale .01, max chance 1; crit multiplier
1.5, defense ignore .3; flat DEF/MDEF scale 1 (configurable ratio alternative);
resistance clamp [-.6,.8]; guard/block .7, parry 1; positive defense floor 1,
floor rounding after six-decimal stabilization. Penetration defaults zero.
These are not approved production formulas or class balance decisions.

## Playable and skill integration

learned skill + validated rank + existing authored action + compatible single
Node → SkillRuntime.compile → CombatRuntime.buildInput → resolver → HP helper
→ existing game contact/status/reward/VFX paths. Rank/job/prerequisite/loadout/Node
validation stays in the existing foundations. Automatic passives reach damage
through Player.getDerivedStats; the resolver never derives STR/INT/LUK itself.

All ordinary player Timeline contacts, projectiles and field pulses now use
physical or magical resolution. Existing presentation archetypes select the
adapter damage category outside the resolver. Enemy actors currently receive
neutral configured DEF/MDEF/FLEE/resistance data unless m.combatStats is provided;
this is a compatibility adapter, not authored monster balance. Timelines,
animations, hit stop, shapes, movement, VFX and camera settings are unchanged.

Incoming enemy attacks retain hurtPlayer and the existing timed guard/plate
mechanics. That orchestration uses invulnerability/time and historically applies
guard before plate; replacing it would change behavior beyond this foundation.
A future incoming adapter should snapshot defender stats and guard state, call
the same resolver, consume mitigation, then use the existing hurt/death/respawn
presentation. No claim that incoming enemies already consume DEF/MDEF here.
Burn/ignite/chain/delayed Node proc damage keeps its existing calculation; the
shared hit function now applies its numeric result through the safe HP helper.
Action-area spirit healing remains its original shape effect. The candidate
boundary does not move the full status framework into the calculator.

resolveAttackInterval uses base interval × referenceASPD/ASPD with a configurable
minimum; resolveCastDuration uses base duration × castTimeModifier and its
minimum. These future helpers do not alter any playable animation timing.

## Save protection and actual Stat refunds

The combat extension originally added statPointSpending in version 4; current
save version is 5 for [canonical item ownership](CORE_SPINE_ITEMS.md). The
independent integer Stat expenditure total remains unchanged. Skill Point
accounting keeps its separate existing map.
Allocation commits primary value, unspent balance and exact cost into the ledger
atomically. Reset refunds the stored expenditure, zeros it and resets stats;
repeated reset cannot refund twice. Reopening with a tuned pointCost preserves
the original expenditure, including allocations made under different costs.

Valid v4/earlier saves without the ledger migrate once using the historical
initial=1, cost=1 rule. Today's configurable pointCost is never used to invent
historical credit. Explicit malformed ledgers give zero credit; unallocated saves
give zero credit. The canonical snapshot/private Player getter/save preserve the
ledger. This is local compatibility accounting, not protection against a manually
forged save or a final respec economy. A future schema changing the historical
stat baseline must author its own migration rather than reinterpret this rule.

Save.normalize and snapshot reject saveVersion > 5 with UnsupportedSaveError.
Normal boot displays the unsupported-save path and returns before character
creation, mount, autosave or pagehide/visibility save listeners are registered.
Original storage bytes remain untouched, including across reload. No production
respec UI or replacement character flow is introduced.

## Developer inspection and verification

tools/combat.html resolves editable JSON fixtures, config overrides, supplied
rolls and separate HP application through the same modules. It has no saved game
state. Only exact ?dev=1 enables AstraeonCombatDev.inspect/results/setPolicy;
setPolicy overlays disposable live combat inputs and never persists test data.
Normal URLs expose neither CombatDev nor ProgressionDev mutation APIs.

Run the documented static server, full Node suite, combat_browser.py,
skill_tree_browser.py, progression_browser.py, cache_resume.py and world validator.
Cache/boot/page version 90 includes the three combat modules for offline boot.
Browser tests cover the actual playable classes, ranked Node contacts, passive
stats, deterministic miss/dodge/crit/defense, HP/death/respawn, progression/rewards,
save parity and future-save preservation. See CORE_SPINE_COMBAT_REPORT.md for the
verified checkpoint and limitations. Test passes make no visual acceptance claim.

## Action Item execution extension

The [Action Item contract](CORE_SPINE_ACTION_ITEMS.md) supplies validated current
HP/SP effects, non-mutating prepare and exact-once atomic effect/debit execution.
Potion/Ration remain canonical stacks outside learned slots 1–8. Full resources
reject without consumption. Item/function clocks are provisional, explicit-time
and separate from skills. Existing Stats/Combat/Progression/ownership authorities
and save version 5 remain intact; clocks are runtime-only. See the
[verification handoff](CORE_SPINE_ACTION_ITEMS_REPORT.md) for lifecycle evidence.

## Monster Loot integration extension

The [Monster Loot contract](CORE_SPINE_MONSTER_LOOT.md) adds per-life exact-once
monster rewards using the existing canonical ownership and Progression/Stats
contracts. Item/gear/currency rewards, Base/Job EXP and quest credit are planned
before synchronous publication. Existing formulas, learned skills, action slots,
Action Item execution and save version 5 remain unchanged. Claims are runtime-only;
boot/page/cache version is now 90. See the [loot verification handoff](CORE_SPINE_MONSTER_LOOT_REPORT.md).
