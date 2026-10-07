# Core Spine: eight-slot Action Loadout contracts

This implements the behavior, persistence and cooldown foundation for eight
learned skill slots in Patch 0.0.1. The whole patch/Core Spine is not complete.
Backbone v0.4 §8 is authoritative; current skill definitions, rank/Node logic,
resource costs and authored timings remain the existing foundations.

## Ownership

| Layer | Owner |
|---|---|
| Learned ranks, prerequisites, paid Skill Points and passives | Character / Skill Tree |
| Exactly eight assigned IDs or null | `action-loadout.js`, stored privately by Player |
| Current-class/rank authorization and authored Node compilation | `skill-runtime.js` |
| Eligibility, resource validation, tickets, transient cooldown clocks | `action-runtime.js` |
| Actual private SP mutation | Character setter called only at successful commit |
| Input vocabulary | `input.js`; no production bindings for slots 5–8 |
| Aim, authored anticipation extension, launch, contacts | game adapter and existing Timeline |
| Damage and HP application | Combat Runtime / Combat Resolution / existing contact consumer |
| Buttons, labels and existing cooldown treatment | Existing presentation; owner retains final UI decisions |

The core reads no DOM, storage, world, RNG, Date.now or performance.now. Runtime
uses owner callbacks and explicit simulation seconds. No damage formula,
prerequisite graph, rank transition, Node rule or animation definition moves
into the loadout system.

## Configuration and assignment

All API indexes are **zero based 0–7**, while developer controls display 1–8.
`AstraeonActionLoadout.slotCount` is 8. Player exposes:

```js
player.getLoadout();                       // immutable copy, exactly eight
player.getSlot(7);                         // invalid index returns null
player.canAssignSkill(7, 'rising-edge');    // detailed validation result
player.assignSkill(7, 'rising-edge', {now, inCombat});
player.clearSlot(7, {now, inCombat});
player.swapSlots(0, 7, {now, inCombat});
player.moveSkill(0, 7, {now, inCombat});
```

Assignment requires canonical persistent configuration, valid Skill Tree state,
valid slot, known active, loadoutAssignable, learned rank and current Base Class.
One ID may appear at most once. Reassigning the same ID in its own slot is a
no-op. Clear accepts null. Swap preserves both occupants; moving into an occupied
destination returns TARGET_OCCUPIED instead of deleting that occupant. Moving
an empty source rejects. Reordering an existing dormant ID is allowed; it stays
dormant. Invalid transitions never partially mutate configuration.

The pure model returns frozen transitions with ok/changed/loadout and details,
or structured errors. Player installs the next configuration only after runtime
accepts the configuration change. Detailed assignment errors are INVALID_SLOT,
INVALID_STATE, UNKNOWN_SKILL, NOT_ASSIGNABLE, WRONG_CLASS, NOT_LEARNED and
ALREADY_ASSIGNED. The existing public assignSkill preserves NOT_USABLE for the
four skill-eligibility errors, with a detailed reason; canAssignSkill exposes
the detailed code. No-op edits add no lock or ticket invalidation.

**Class dormancy policy A:** keep IDs, learned ranks and paid ledgers. An
incompatible stored ID reports WRONG_CLASS and cannot execute. Returning to its
class makes it usable subject to ordinary runtime checks. Switching classes
gives no refund and creates no ranks. The existing town-training resource refill
and archetype adapter remain unchanged; this is compatibility, not multiclass
gameplay. Each supported class currently has four actives, so tests move these
through all eight slots. A cross-class stored loadout may fill eight slots while
only the current class's four are executable.

## Runtime state and failure contract

`getActionSlotState(slot, context)` returns an immutable copied inspection:
slot, skillId, source (learned/legacy), sourceClass, learnedRank, node, action,
eligible, blockedReason, readyAt, cooldownRemaining, cost and resourceAffordable.
Empty/dormant slots have no compiled action; some metadata is absent. Invalid
slot/context/state/compilation returns `{ok:false,code}`. A valid inspection
returns ok:true even when ineligible. Learned is distinct from assigned, and
assigned is distinct from currently executable.

Every execution context supplies finite nonnegative `now`. The game also supplies
actionActive, menuOpen and transitionPending; adapters can supply restricted.
Runtime validates current class, learned rank, compilation, finite/nonnegative
timing/cost/range/damage and finite nested numeric payloads. It rejects HP zero,
invalid resources, action/menu/transition restrictions, insufficient current SP
and unfinished cooldowns. Costs use existing Resolve/Mana/Focus compatibility
SP; regeneration, contact restoration and stat maxima retain existing owners.

Failure codes include EMPTY_SLOT, WRONG_CLASS, NOT_LEARNED, INVALID_SKILL,
INVALID_RUNTIME, INVALID_RESOURCE, DEAD, FORBIDDEN_STATE, RESOURCE, COOLDOWN,
INVALID_CONTEXT, INVALID_PACKAGE, STALE_PACKAGE, ALREADY_COMMITTED and
LAUNCH_REJECTED. The pure core is deterministic for fixed state/context.

## Preparation, launch and atomic commit

```js
const context = {now, actionActive: !!timeline.active, menuOpen, transitionPending};
const prepared = player.prepareAction(slot, context);
if (prepared.ok) {
  const executable = structuredClone(prepared.action);
  // Existing game adapter may extend anticipation while turning toward its aim.
  const receipt = player.commitAction(prepared, context,
    () => timeline.start(executable, origin, aim, now, {externalCooldown:true}),
    {castTime: executable.castTime});
}
// Or use requestAction(slot, context, synchronousLaunch, options) for both steps.
```

The package is frozen and registered in a controller-local WeakMap; a copied,
foreign or forged package cannot commit. Commit rechecks eligibility and current
resource, class, revision and compiled rank/Node signature. Configuration/reset/
death/map changes invalidate preparations. Rank/Node changes are caught by
compiled signature. Preparation spends nothing.

The trusted synchronous launch callback starts Timeline and returns exactly
true. False, non-true response or throw rejects before resource/cooldown mutation.
The adapter must not spend resources or perform unrelated state changes.
Reentry/configuration mutation inside launch is blocked. After acceptance the
private validated Character setter subtracts SP once and the controller starts
cooldown once, marks the ticket consumed, and returns resourceBefore,
resourceAfter, cost, readyAt and cooldownDuration. Overflow is rejected before
launch. There is no rollback of arbitrary side effects in an untrusted callback;
this local contract requires the shipped Timeline-only adapter and does not
claim server authority.

All original skill1–skill4 aliases and actionSlot1–actionSlot8 use this path in
game.js. Skills launch Timeline with externalCooldown:true, so Timeline neither
checks nor writes a second skill cooldown. Aim selection, opposite-facing cast
extension, effects, animation and contacts stay in existing orchestration.
Skill Runtime remains rank/Node authority. Damage contacts/projectiles/pulses
reach Combat Runtime → Combat Resolution → HP application. Guard/heal retain
existing self effects. The loadout never applies damage directly.

## Cooldown policy

Per-action clocks use action ID, not slot: moving, clearing and reassigning a
skill cannot bypass its cooldown. Duration is
`max(authored cooldown, actual launch castTime + activeTime + recovery)`;
anticipation can extend but cannot shorten authored castTime. Readiness is
`now >= readyAt`; remaining is clamped to zero. The caller supplies monotonic
simulation time; no wall-clock/offline clock exists.

Backbone §8 allows combat loadout changes and requires **all slots** to cool down.
A changed assign/clear/swap/move with inCombat:true adds one loadoutReadyAt lock
covering all eight, including empty/dormant slots. The provisional duration is
the maximum authored action duration among IDs in the old/new configuration,
not a new fixed timing constant. It includes retained dormant IDs (rank at least
one for duration compilation). Invalid compilation rejects the entire edit.
An edit cannot shorten an existing lock or individual cooldown. Safe edits add
no new shared lock and retain existing clocks.

The live developer adapter supplies `{now,inCombat:!canTuneNodes()}`. This uses
the existing town/cleared-camp safety policy, conservatively treating other
field configuration as in combat. It refuses edits during an active Timeline
with UNSAFE_CONFIGURATION; idle combat edits are allowed and lock all slots.
Node selection and paid reset retain their old safe-configuration gate.

Extension hooks: immutable controller config defaults
`{globalCooldown:0,inCombatChange:'maxAuthoredDuration'}`; optional compiled
cooldownGroup and groupCooldown. Effective readyAt is the maximum of individual,
group, global and loadout locks. No production skill has new group metadata and
no new global cooldown is enabled. resetActionCooldowns is a developer test
helper; it clears clocks and invalidates old tickets, not Timeline or assignments.
Authored durations remain provisional content values, not final MMO tuning.

## Death, transitions and persistence

| Event | Configuration/ranks/paid ledger | Cooldowns | Preparations |
|---|---|---|---|
| Death/respawn | Retained | Retained on simulation timeline | Invalidated |
| Town/field/dungeon/class change | Retained; incompatible class dormant | Retained | Invalidated |
| Ordinary save | Serialized as configuration | Never serialized | Never serialized |
| Reload/new attached controller | Restored | Fresh empty clocks | Fresh ticket registry |
| Skill debug reset | Existing paid refund, clear ranks/slots once | Retained | Invalidated |
| Developer cooldown reset | Unchanged | Cleared | Invalidated |

Menus/loading/hidden-tab pauses freeze the existing simulation clock. Cooldowns
advance during ordinary death simulation; cancellation never refunds accepted
cost/cooldown. Existing respawn HP/SP restoration and death penalty remain; no
new resource awards are introduced. Reload resetting transient clocks is an
explicit 0.0.1 policy, not offline persistence.

Current save version is **5** after the [item foundation](CORE_SPINE_ITEMS.md)
schema change; this loadout extension originally shipped additively in version 4.
Key remains `astraeon-iso-v1`. Skill Runtime's existing
normalizeLoadout delegates to the pure model: exactly eight dense slots, known
assignable actives only, first valid duplicate occurrence wins, remainder empty.
Wrong-class IDs stay dormant. A known but unlearned stored ID is retained safely
and blocked NOT_LEARNED, never auto-learned. Unknown/passive IDs become null.
This path is deterministic/idempotent and leaves the unrelated historical
`loadout` field alone. Existing future-save rejection, Stat refund ledger,
inventory/equipment/quests/world normalization remain intact.

## Basic Attack, Potion and returning saves

Basic Attack is outside the eight slots, requires no learned rank and retains
its Timeline cooldown/combo/contact resource behavior. Potion retains its separate
utility action, inventory decrement and healing. Input exports separateActions
identities for attack, potion, dodge and interact as a later item/input extension
boundary. The item foundation now adds owned instances and canonical Potion
consumption; new potion cooldown rules and a full item action framework remain
future work. Backbone's later combat-item/scroll/weapon slot types remain future
action adapters. One active skill configuration is sufficient; future
presets can supply a new configuration through the same transition boundary.

Returning saves with legacySkillControls:true get authored fixed actions in
**empty first-four slots only**, compiled at original runtime rank with existing
Nodes. Explicit assignments take precedence; dormant assignments do not fall
back. This legacy source uses the same eligibility/SP/cooldown/commit controller
without learned/paid maps or granting points. A fallback and assigned copy of
the same action share its ID cooldown. Slots 5–8 never gain fallback actions.
Unsupported prototype Base classes retain the old first-four archetype fallback;
new Swordsman/Mage characters have no fallback. Debug skill reset opts out of
the returning shortcut as before.

## Developer tooling and verification

`tools/progression.html` uses isolated `astraeon-progression-dev-v1`. It supports
learning/rank/Node inspection, all assignments, invalid attempts, clear/swap/move,
compiled/cost/eligibility/cooldown display, execution through a real empty-fixture
Timeline, explicit monotonic set/advance time, reset clocks, save/reload.
It models execution without world damage; playable browser acceptance covers
actual field contacts. Harness reload creates new Timeline/controller/time zero.

Exact `?dev=1` enables the live APIs; add qa=1 for read-only inspection. In
addition to prior APIs, getLoadout/getSlot/canAssignSkill, clearSlot/swapSlots/
moveSkill, getActionSlotState/getActionRuntime/resetActionCooldowns and
executeActionSlot are available. Normal URLs expose neither progression nor
combat developer mutation APIs. Existing first-four desktop/touch buttons and
bindings are retained; no production controls or labels for 5–8 are added.

Run the commands in README, including `tests/action_loadout_browser.py`. The
[verification report](CORE_SPINE_ACTION_LOADOUT_REPORT.md) records checkpoints,
all regression counts, disposable Swordsman/Mage smoke and remaining scope.
Boot/page/SW version 88 precaches the action and item core modules and supports offline
saved-character boot. No visual acceptance is inferred from these checks.
