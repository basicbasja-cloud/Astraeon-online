# Inventory Capacity / Weight foundation — working checkpoint

Branch: `backbone/inventory-capacity-weight-0.0.1`.
Parent: `backbone/monster-box-0.0.1`.
Authoritative starting HEAD: `1e32ce4e17ae516b504a65e7a0a03db634ac62d4`.

Step 0 fetched, switched/pulled ff-only, confirmed clean and created the required
branch. No stale checkpoint reset or unrelated merge.

Resume: canonical capacity integration and 142 new deterministic checks pass.
Full Node final precision checkpoint: 1152 / 0; focused final cases: 142 / 0.
Initial focused browser: 63 groups / 0, both classes, no runtime/HTTP errors.
All previous 1010 deterministic assertions are retained (12 import-only additions).
Final browser sequence is running: new Capacity 63 / 0 and Box 33 / 0 passed.
World validator passed all four schemas. Remaining previous browsers/cache and
final documentation/audits remain.
Runtime integration checkpoint: `7ea67e1bacf9de1d41696a94e8b71d336b7416af`.
No complete acceptance claim yet.
Production provisional policy: 100 slots, 1000 weight; existing authored zero /
unconfigured weights retained. Milliweight integer arithmetic, per-dimension
no-worse over-limit rule; no persistent capacity counters or gameplay penalties.

Evidence directory: `D:\Astraeon\backbone-verification\inventory-capacity`.
Tests: `node-precision-final/report.json` (1152/0). Earlier new test rejected
`itemRewards:null`; implementation now rejects it without weakening assertion.
Review added a positive-subprecision weight rejection so tiny authored weights
cannot silently round to zero. Browser fixture numbers and production zeros are
unchanged. Current HEAD: use `git rev-parse HEAD`.
