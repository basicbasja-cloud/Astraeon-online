# Monster Box Item / Opening — working checkpoint

Branch: `backbone/monster-box-0.0.1`.
Parent: `backbone/monster-lifecycle-0.0.1` at
`05243a45737dbe5a493b7753f5517d7ea920243b` (latest fetched remote HEAD).

## Resume point

Step 0 completed with fetch/switch/ff-only pull and clean tree before branch
creation. Immutable canonical proof item and separate Box Content grammar/resolver
are implemented. No runtime or gameplay opening is connected yet.

One box, `monster-box-proof`; one separate table, `box-proof-basic`, with equal
weighted material/consumable/equipment outcomes and a material quantity range.
All new content/coefficients are provisional. This is not final balance.

## Verification / remaining work

- Parent baseline: historical 859 deterministic / 157 browser groups; not yet
  rerun on this task.
- Remaining: owned non-rolling preparation, commit-time RNG, canonical atomic
  source debit + rewards, stale/reentry/duplicate guards, hidden failed-roll
  retention, Player/Bag integration, isolated Loot proof, harness, comprehensive
  Node/browser suites and regressions, world/cache verification, final docs/push.
- Save version stays 5; no schema change planned. No lifecycle/combat/art/world
  edits are needed.

This is an incomplete working checkpoint, not an acceptance report. Patch 0.0.1
and Core Spine remain incomplete.
