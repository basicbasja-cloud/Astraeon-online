# Street depth and painted material candidate, revision 77

The user rejected the prior city as flat/soulless and asked for larger, quieter
paving stones and architecture closer to RO3's painted style. This pass builds
on pushed checkpoint 4f6b275, not a rollback or replacement map.

Reference observations: supplied RO3 street 00:50 and house 03:35 have larger
readable stone joints, dark recessed glazing, marked lit/shaded facade planes,
nearby canopy/bench/stall layers and soft material grain. Fountain 00:35 places
street furnishings around activity while leaving walkable approaches. These
are artistic observations, not reconstructed RO3 engine/camera telemetry.

Candidate:
- 1.8× larger native public paving UV repeat; original image/resolution retained.
- Reduced paving/wall/clay-roof grain contrast, deeper blue window interiors.
- Lower fill and longer authored sun shadows; full native facade, original-alpha
canopy and 4096 floor lighting rebuilt together.
- Six tree/seat parklets with planted stone surrounds and conservative physical
proxies. Original tree materials reused; zero new image fetches.
- 398 tiny street-joint tufts retargeted to actual enlarged painted joints;
2 without local support removed; all 800 lawn tufts retained.

The planned new geometry budget is 7,000 visible triangles, authoring adds 5,640.
Existing buildings, roads, curbs, original colliders, all 8 services, 2 transition
portals and all 28 original residents remain unchanged. Of the eight plaza
citizens, one receives a small declared closing-leg turn around the new seat;
all other routes and actor records remain exact. An independent declared-delta checker
compares actual exported geometry against4f6b275 and checks physical clearance.
Historical v76 evidence remains available at its original source hash.

Status: native candidate, all source/transport checks, four paired views and
available mobile/cache/field regressions verified. Full RO3 baseline NOT MET. Do not call RO3 visual baseline met from structural counts.
Physical iPhone Safari verification remains PENDING.

The first ground bake completed its4096 image and native metadata but exhausted
workspace memory during the final JSON export. The repaired export preserves
the exact PNG hash and computed shadow geometry digest. Native parity passes.
See ground-save-recovery.json; the original failed log remains preserved. The
baker now uses a Float32 buffer and frees duplicate world/ray data before saves.

The first full traversal audit caught a southwest seat crossing the closing
leg of one visitor loop (the initial planner checked only open polylines).
The checker now covers complete closed loops. visitor-turn.json records the
precise original/after route; all static geometry and light remain identical.
