# Patch 0.0.1 Developer Tool contracts

This closes roadmap developer adapters only. Patch 0.0.1 / Core Spine are not
complete. No new gameplay foundation or final content is approved here.

## Access and presentation

`/?dev=1` loads `dev-tools.js` and publishes one coherent `AstraeonDev` namespace.
Only the exact parameter value `1` enables it. Normal, QA-only, `dev=0`, `dev=01`
and similarly named parameters do not load the module or expose mutations.
QA keeps its existing read-only inspection. This is local development isolation,
not authentication or server security.

`/tools/dev-console.html` embeds the actual same-origin game with explicit dev
mode. Create a disposable Swordsman or Mage there. The console has no shadow
character or sandbox gameplay authority. Existing specialized harnesses and
exact-dev APIs remain compatible; the new console is the roadmap entry point.

## Existing versus added / canonical authority

| Tool / command | Existing authority | Change |
| --- | --- | --- |
| `progression.setBaseLevel(n)` | Player -> Character -> Progression.setLevel | Reuse with validation/receipt |
| `progression.setJobLevel(n)` | Same, Base Job track | Reuse |
| `progression.addBaseExp(n)` / `addJobExp(n)` | Character -> Progression.grant | Reuse |
| `items.give(id,count)` | Item State.grantItemPackage -> Inventory / Capacity | Reuse atomic package |
| `money.give(n)` / `set(n)` | Existing Player gold field | Narrow validated Player publication helper |
| `skills.learn(id)` / `rankUp(id)` / `reset()` | Player -> Character -> Skill Tree | Reuse gates/refunds/loadout reset |
| `stats.allocate(id,count)` / `reset()` | Character paid allocation/refund | Reuse |
| `monsters.spawn(id,point)` | Existing enemy factory -> Lifecycle.register | Definition-aware dev adapter |
| `monsters.kill(instanceId)` | Existing hit -> Combat HP application -> Lifecycle death | Explicit policy/receipt |
| `world.teleport(point)` | Existing map loading, authored collision, transform/camera | Reconciled dev adapter |
| `inspect.stats()` | Player / Character / existing modifiers | Read-only grouped inspection |
| `inspect.effects()` | Existing modifier groups, equipment effects, runtime statuses | Limited real representation |
| `save.snapshot()` / `inspect.save()` | Existing Save.snapshot | Frozen read-only data |
| `save.wipeTestCharacter(confirmation)` | Exact current character save key | Scoped removal and stopped runtime |

`inspect.monsters()` and `inspect.maps()` are small supporting inspectors for
valid command identity and map/point inputs. They are not editors.

## Receipts and integrity

Mutation returns a structured immutable result with `ok`, `operation`, canonical
`before` / `after`, and `result` or stable `code` / `blockedReason`. No console log
is required to determine success. Busy/loading/no-character failures may return
only a structured failure. A pending async teleport blocks other commands through
the same owner. Preparation tickets are not introduced or persisted.

Successful commands call existing save and UI refresh. `persistence.ok=false`
with `SAVE_WRITE_FAILED` means the in-memory canonical mutation committed but
local persistence failed; it does not pretend to roll back. Invalid input and
supported preflight rejection do not partially mutate ownership or progression.
Publishers remain trusted synchronous local adapters, not a general database.

## Progression / Skills / Stats

Levels use configured Base 60 / Base Job 50 caps. EXP uses the existing curve,
multi-level point gain and cap policy. Setting a level resets EXP only as the
existing setter specifies; lowering rejects if it would reclaim spent points
into a negative pool. No raw level, EXP, Stat Point or Skill Point writes occur.
HP/SP follow Character's existing clamp behavior; the dev grant does not invent
healing. Normal monster-death reward resource behavior is unchanged.

Skill commands keep class, rank, Job, prerequisite and point gates. Use level/EXP
commands to obtain valid points first. No prerequisite graph bypass or imported
fake rank is added. Canonical reset refunds paid expenditure and clears loadout
through existing Player authority. Stat reset uses recorded paid spending,
recalculates Stats and clamps resources. Existing safe-configuration context
(town/camp and no active combat action) remains required for skill/stat changes.

## Items / money

Give validates known primitive item ID and positive safe whole count. Canonical
package preflight enforces capacity, weight, maxStack and serial feasibility.
Stack grant allocates no instance; non-stack units allocate exactly once per
accepted unit. No fake equipment objects, automatic equip or capacity bypass.
Global stored-ID reservation remains active. Metadata is ordinary canonical
default metadata; no item editor is supplied.

Gold helpers validate safe nonnegative whole amounts and current plain writable
wallet, including overflow. Malformed current gold rejects rather than silently
repairing it. There is no DevGold ledger. Gold change stales existing authorizations
through their current canonical identity checks.

## Monster spawn / kill policy

Spawn accepts a known Lifecycle MonsterDefinition ID and `{zone,x,y}`. The zone
must be the current valid hostile field, coordinates finite/in bounds/unblocked,
and the existing population actor budget must allow it. Town, remote-map and
dungeon spawn reject. Existing enemy factory creates the actor and Lifecycle
owns its spawn/runtime/life state. Mechanical fixtures use the existing generic
species presentation/attack orchestration; no new monster content or AI is added.

Kill accepts exact runtime instance ID, or the selected target when omitted.
It uses `hit(actor,actor.hp)`, which invokes existing Combat HP application and
normal `kill` -> Lifecycle notification. It is an explicit developer lethal
application, not a simulated ordinary attack or new damage formula.

Policy is **normal player-owned death reward behavior**: Loot resolves once,
Base/Job EXP/gold/kill counters use its existing reward profile and commit, and
eligible active Quest Kill observes the exact Lifecycle death. Capacity still
applies. A successful death may report a rejected reward in `result.reward`;
this is not a partial loot success or permission to reroll. Same life already
dead rejects `ALREADY_DEAD`. Respawn retains existing new-life semantics. Kill
does not fabricate Quest progress or bypass Loot authorization.

## Teleport reconciliation

`{zone,x,y}` uses current numeric zone IDs and authored bounds/collision. It may
bypass ordinary travel unlock/grind/gold cost, but not map/position integrity.
Cross-map movement loads existing map assets through `prepareZone`, exits transient
dungeon state, rebuilds current population and records existing discovered map.
It does not generate rewards or reset player inventory/Quest/Storage.

Both same-map and cross-map movement invalidate prepared action/Action Item/Box/
Quest authorizations, service sessions and monster offensive target/attack state.
They clear timeline/projectiles/fields, held input, target/navigation selection
and reposition through existing `centerCamera` / player transform. Cooldown and
durable state policies remain existing behavior. Dead/loading/invalid point rejects.
The legacy Lifecycle point helper remains unchanged for perception/leash fixtures.
It validates current collision and calls existing transform/camera authority. It
intentionally lets AI observe the moved player instead of releasing its target.
It is not the roadmap map-teleport command; use the coherent `world.teleport`
for complete general travel reconciliation.

## Read-only inspectors / status limits

Derived stats are the Character result, never a second calculation. Inspection
shows primary, equipment, passive (including learned/party) and temporary modifier
groups. Effects inspection shows existing equipment effects, guard/invulnerability
timestamps, current combat action tags, projectile/field counts and monster burn/
slow/frozen/stunned timestamps with simulation time. Timestamps may have expired;
the inspector shows existing state rather than inventing a general status ledger.
There is no full Status Effect system in this milestone.

Save snapshot is the canonical serializable Save v5 data: progression, allocation,
skills/loadout, inventory/equipment/gold, Quest, Storage and map/position. It contains
no WeakMap tickets, sessions, NPC capabilities, subscriptions, DOM or actor refs.
Calling an inspector does not grant rewards, save, or publish ownership mutation.

## Wipe scope / persistence

Confirmation must be exactly `WIPE ` plus the loaded character name. Only
`astraeon-iso-v1` is removed. Quality/settings, other dev keys and unrelated origin
storage remain. The old runtime is stopped and save/pagehide writes are disabled;
reload is explicitly required before a new character. This is not a reset-all
origin command. Normal URLs have no wipe API. Save version remains 5; no persistent
dev fields, tickets, permissions or schema migration are added.

## Non-goals / next step

No gameplay redesign, world/Character art, final UI, item/skill/monster/map editor,
GM/RBAC/network server, advanced classes, PvP tools, status framework, botting or
Auto Battle. The next separate stage is **0.0.1 Integration Gate**. Do not start
it automatically. Verification and exact resume identity are in
[CORE_SPINE_DEV_TOOLS_REPORT.md](CORE_SPINE_DEV_TOOLS_REPORT.md).
