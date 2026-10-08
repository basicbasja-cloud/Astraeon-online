# Inventory Capacity / Weight foundation — working checkpoint

Branch: `backbone/inventory-capacity-weight-0.0.1`.
Parent: `backbone/monster-box-0.0.1`.
Authoritative starting HEAD: `1e32ce4e17ae516b504a65e7a0a03db634ac62d4`.

Step 0 fetched, switched/pulled ff-only, confirmed clean and created the required
branch. No stale checkpoint reset or unrelated merge.

Resume: canonical capacity integration and 128 new deterministic checks pass.
Full Node: 1138 pass / 0 fail, retaining all 1010 previous checks. New browser
acceptance is running; all previous browser/cache/world verification and final
documentation remain. No complete acceptance claim yet.
Production provisional policy: 100 slots, 1000 weight; existing authored zero /
unconfigured weights retained. Milliweight integer arithmetic, per-dimension
no-worse over-limit rule; no persistent capacity counters or gameplay penalties.

Evidence directory: `D:\Astraeon\backbone-verification\inventory-capacity`.
Tests: `node-foundation/report.json` (1138/0). Earlier new test rejected
`itemRewards:null`; implementation now rejects it without weakening assertion.
Current HEAD: use `git rev-parse HEAD`.
