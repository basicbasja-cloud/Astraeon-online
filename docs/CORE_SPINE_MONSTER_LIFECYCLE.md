# Core Spine — Monster Lifecycle / AI foundation

Patch **0.0.1 foundation only**, continuing Monster Loot. Save version **5**,
boot/page/cache **91**. Patch 0.0.1 and Core Spine are **not complete**.

## Responsibilities

| Boundary | Authority |
| --- | --- |
| Immutable mechanical MonsterDefinition | `monster-lifecycle-definitions.js` |
| Existing reward/drop reference definitions | Unchanged `monster-definitions.js` |
| Spawn ID and home | Game factory / supplied spawn definition |
| Instance and life identity | Existing Monster Loot registration / `newLife` |
| AI state, target, timing, attack authorization, death handoff | `monster-lifecycle.js` |
| Actual HP / transform | Existing actor, Combat HP application / navigation adapter |
| Enemy telegraph/contact geometry and damage source | Existing `enemy-combat.js` |
| Enemy contact calculation | `monster-combat-runtime.js` → existing Combat Resolution |
| Player HP / derived Stats | Existing Player / Character |
| Drop roll, entitlement, canonical reward commit | Existing Monster Loot / Player / Item authorities |
| Movement, collision, presentation, field budget | Contained adapters in `game.js` |

Lifecycle owns no inventory, gear serials, loot probability, progression/stat
formulas, learned skills, item clocks, renderer or navigation algorithms.

## Definition and spawn contracts

Definitions expose `id`, `rewardDefinitionId`, `stats` (HP profile), `movement`,
`perception`, `combat`, `lifecycle`, tags and non-final metadata. All are deeply
frozen. No current HP/target/position/timestamps live in definitions. Validation
rejects missing profiles, unknown reward definitions, non-finite/negative values,
zero HP/cadence/tolerance, invalid leash relationships, unsupported return policy
and non-JSON/cyclic metadata. Rejected registration allocates no loot identity.

Eight existing species and the current guardian retain their prototype HP
coefficients/speeds and reward references. Their names/art are compatibility
content, not approval of final monster design. The old arena control remains a
registered compatibility actor; town suppresses its hostile field AI.

Four isolated mechanical fixtures are generic/internal, not production content:

| Definition | HP | Speed | Detection | Attack range | Windup / cadence | Respawn |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| lifecycle-normal-a | 20 | 1 | 6 | 1.5 | .5 / 2 | 4 |
| lifecycle-normal-b | 24 | 1.2 | 7 | 1.8 | .6 / 2.4 | 5 |
| lifecycle-normal-c | 28 | .8 | 5 | 2 | .7 / 2.8 | 6 |
| lifecycle-tough-a | 60 | .7 | 8 | 2.2 | .9 / 3 | 8 |

These use existing material/consumable/no-drop/equipment proof reward references;
their rewards do not increment production kills/EXP/quest. No monster-specific AI
branch is required. All coefficients are **provisional**, authored and replaceable.
Common provisional home leash is 12, home tolerance .15, initial attack delay 1.8.
Production detection retains 8; cadence retains ordinary 2.8 / guardian 2.4.
Random initial attack jitter is replaced by explicit deterministic readiness.
Stationary ATTACK thresholds reuse the old melee chase reach (1.4, 1.5, 2.2,
1.6) and guardian close reach 3.5 so existing contact shapes can actually hit
after chase stops. Charge/projectile/field thresholds retain their existing
bands. This closes an unreachable-contact regression, not final aggro/balance.

Spawn input is `{id, home:{x,y}}`. Spawn IDs must be nonempty and unique within
an active population; home/position must be finite. Spawn serials increase on
the live controller's population creations. Definition ID, spawn ID, Loot's
`monster-N` runtime ID and `lifeGeneration` are distinct. Two same-definition
actors have independent HP, target, cadence, death and respawn. HP remains one
existing actor field, not a mirrored lifecycle resource.

## Explicit state machine and events

```text
SPAWN → IDLE → DETECT → AGGRO → CHASE ⇄ ATTACK
                           alive → LEASH → RETURN → IDLE
                       any alive → DEAD → RESPAWN_WAIT → SPAWN → IDLE
```

DETECT/AGGRO are explicit recorded transitions in the acquisition update. Legal
edges are declared once; `canTransition(from,to)` rejects unsupported edges.
Each immutable transition records from/to, reason, time, spawn/runtime/life ID.
Target-acquired/released, attack, death and respawn events are separate outputs.
History is bounded to 128 events; it is diagnostics, not a persistent ledger.

```js
const lifecycle = AstraeonMonsterLifecycle.create({
  loot, getRewardContext: () => player.getMonsterRewardContext(zone), rng
});
lifecycle.register(actor, definitionId, {id: spawnId, home}, now);
const output = lifecycle.update(actor, {
  now, active: true, target: {id:'player', x, y, hp},
  attackAllowed: true, canRespawn: true
});
// Apply movementIntent via existing navigation; present attackIntent.
// At impactIntent, consumeImpact once before dispatching contact geometry.
```

Results/snapshots are immutable copies. Runtime state is private. Invalid HP,
position, definitions, context flags or backward/non-finite time reject before
transition/reward. Local actor/catalog/publisher adapters are trusted code, not
security against edited JavaScript, hostile accessors or a server transaction.

## Clock, perception and target policy

Caller supplies finite nonnegative monotonic simulation seconds. No Date.now,
performance.now, hidden RNG or frame/animation clock occurs in the core. Existing
game loop subdivides simulation into at most 1/60-second steps; no new timestep
engine is added. Menu/loading/hidden-tab/hit-stop pauses freeze this same clock.
Explicit paused updates emit no intent and leave timing/state unchanged.

Acquire only an existing finite-position alive target in an active combat context,
within inclusive detection range and home leash. One player target is supported;
there are no threat tables, parties, factions, vision cones or hearing. Acquisition
records DETECTED_TARGET / TARGET_ACQUIRED. Future perception may supply validated
eligibility before acquisition; full LOS semantics remain future work.

CHASE emits target ID/location/speed/stop distance. Existing collision/route
helpers decide how to move. Attack eligibility additionally requires current
range and the adapter's clear contact path / status restrictions. Leaving range
returns to CHASE and cancels a pending windup. Invalid/dead/disappeared/replaced
target, inactive gameplay or home leash releases offensive ownership.

## Attack authority and Combat integration

ATTACK emits one immutable owner-registered token with instance/life/target,
attack ID and explicit impact time. Before readiness it emits nothing. Windup and
cadence are separate from presentation. Next readiness is planned impact time +
cadence. A delayed update emits at most one request, never a catch-up burst; a
pending request cannot be duplicated. Subdivision may affect when observations
arrive, but cannot duplicate one attack/death identity.

`consumeImpact(token,context)` rechecks ownership, alive life, target, range,
context and due time, then consumes that impact once and advances authority time
to the accepted impact clock. A later backward update/death rejects. Registration
also rejects readiness overflow before allocating a Loot identity. Copied/foreign/cancelled
tokens reject. `canDeliver` checks source life/aggro generation/epoch and current
alive target for subsequent charge/projectile/hazard contacts. Death, leash,
target invalidation, loading and travel invalidate those deliveries.

The game uses existing EnemyCombat plans/contains/charge/shot/field geometry.
Gameplay impact uses the token deadline; animation only observes events. No
sprite-frame callback can deal damage or trigger death. Existing guardian phase
presentation/add spawning is retained as a compatibility consumer; no new boss
phase framework or final boss AI is implemented.

Enemy contacts now call the existing staged resolver with explicit authored
prototype baseDamage, physical category, guaranteed accuracy, no crit/Perfect
Dodge (retaining prior contact certainty), current Player derived defender Stats
and guard mitigation. Existing HP application then passes its result to Player's
canonical setter; existing hurt/invulnerability/death presentation remains.
This intentionally activates DEF mitigation on incoming damage. Warden Plate's
DEF enters once through Stats; its old additional flat reduction is not applied
again. Guard reduction .7 retains the prototype reduction amount but follows
the existing resolver's defense→mitigation order. There is no second AI damage
formula. Result damage can differ from the historical guard-before-plate path;
this is provisional incoming integration, not approved damage balance.

## Home leash, return and HP

Leash compares both monster and acquired target to immutable home, not merely
target distance. It clears offensive ownership, windup and attack leases, records
LEASH, then RETURN emits movement toward home. It never teleports an alive monster.
Within inclusive tolerance, RETURN reaches IDLE; re-acquisition is allowed on a
later update. No re-aggro occurs during return.

**HP is retained through leash/return**. Existing code did not heal at home;
this introduces no healing/reset exploit. Only a legitimate new life restores
full maxHP. Status restrictions retain the current freeze/stun/hit-reaction
adapter; they may delay movement, not make sprite completion the AI clock.

## Death, Loot and respawn

Authoritative Combat application reaches exactly actor.hp===0. `notifyDeath`
clears target/intents, enters DEAD and creates one immutable death event. It
invokes the existing Loot prepare/commit once using the already registered
instance/life. It never rolls another table or creates inventory itself. Repeated
notification returns duplicate:true/no new death event; dead updates cannot
reroll or trigger EXP, Job EXP, gold or quest credit. Reward failures are inspectable;
the existing Loot owner retains its claim policy rather than automatic rerolls.

DEAD emits no movement, detection or attack. Next update explicitly records
RESPAWN_WAIT. Readiness is death simulation time + authored delay. Respawn requires
active context and a caller policy allowance. At the exact boundary, `respawn`
restores existing maxHP/home, calls Loot.newLife, increments the shared generation,
clears target/cadence/death/claim linkage and records SPAWN→IDLE. Failed newLife
restores pre-respawn HP. No reward is granted during respawn.

Field policy permits per-life respawns. Dungeon actors remain waiting until the
existing room/population retirement; dungeon clear rewards stay separate. Existing
replacement spawns coexist under provisional bounded population data: initial 7,
max 8 runtime entries/alive actors, refill below 7 at the existing 12-second gate.
The extra entry preserves replacement identity compatibility; same-instance
respawns use the shared alive budget. This is **not final spawn density**. No
duplicate actor/slot entry is added by per-life respawn; no infinite corpse list.

## Player death, context and persistence

Actual player death releases every target immediately and cancels pending windup,
charge, shot and hazard deliveries. No monster loot is created. Monsters remain
valid lives in RETURN until the existing player respawn retires the population
and returns to town with its existing 8-gold loss. Town has no hostile field AI.

Loading immediately invalidates offensive leases before awaiting assets; failed
loading resumes the current population with fresh acquisition. Successful field,
town and room transitions retire old lifecycle and Loot registrations. Menus
freeze simulation and pending deadlines; they grant no free attacks or respawns.
No stale source callback can damage the player after retirement.

Save version stays **5**, with unchanged migrations and future-save guard. Player
progression/items/instances/serial/gold/quests persist through existing authority.
Targets, AI states, attack timers, death events and unresolved enemy lives do not
persist. Reload rebuilds fresh actors from current population definitions; it
does not replay committed deaths or grant reward on load. Later new gameplay
kills remain legitimate rewards. Durable encounter identity/AI persistence is
explicitly future work; existing dungeon runs also remain transient.

## Developer tools, limits and next boundaries

`tools/monster-lifecycle.html` is an isolated in-memory sandbox: four fixture
definitions, target positioning, deterministic advance, damage/kill, death/Loot
inspection and respawn/new life. No playable storage key is read/written.
Exact `dev=1` enables live definitions/inspection, safe disposable player placement,
Combat-HP damage and repeat-death inspection. QA exports readonly lifecycle and
incoming Combat evidence. Normal URLs expose no live mutation API or debug UI.

Boot/page/cache v92 loads/precache all three modules. Unchanged Loot v90 URLs are
also actually precached to retain the previous explicit cache contract; scripts
are executed once using current boot URLs. No persistent schema/artwork changes.

Current limits: one target, no threat system, no final balance/density/perception,
no navigation rewrite, no full status/monster skill framework, no durable AI save
or server security. Movement can be blocked by existing authored collision; no
new teleport/pathfinding escape rule is invented. Presentation mappings can later
observe IDLE/CHASE/RETURN/ATTACK/DEAD without changing authority. Capacity and
Equipment closure are documented below; Shop/Storage/Town Services remains the
next separate roadmap task.

See [verified handoff](CORE_SPINE_MONSTER_LIFECYCLE_REPORT.md). The subsequent
[Monster Box foundation](CORE_SPINE_MONSTER_BOX.md) operates downstream of Item
ownership with a separate content-table contract. It introduces no lifecycle
states, respawn policy, monster attacks or death/claim changes. The subsequent
[capacity foundation](CORE_SPINE_INVENTORY_CAPACITY.md) checks canonical rewards
downstream of Loot; this lifecycle owner has no slot/weight arithmetic. A rejected
reward cannot generate another death or roll. Existing life/retirement boundaries
still expire transient uncommitted claims. Recommended next Backbone task:
**Shop / Storage / Town Services foundation**, following completed Equipment Slot
Closure and the Quest observer integration below.

## Quest death observer boundary

The [Quest foundation](CORE_SPINE_QUESTS.md) observes this existing authority
without modifying Lifecycle. A narrow bridge validates the exact owned death
event and current runtime/life/death identity, obtaining MonsterDefinition ID from
the same owner. Duplicate event objects give no additional Quest Kill credit;
respawned new lives legitimately count. Loot resolution is never Kill evidence.
Only the existing player-owned combat/death path delivers the observation.
Quest durability does not serialize the Lifecycle event history, alter AI or
introduce listeners that travel/reconstruction could duplicate.
