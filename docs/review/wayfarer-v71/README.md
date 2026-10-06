# Town-wide curb placement correction — source71 / cache78

The source70 screenshot review missed curb-placement conflicts identified by
the user. Curbs were authored against individual road segments, which left
courses inside the open plaza and crossing paths and caused overlapping junction
blocks. Source71 clips the actual native curb footprints against133 public
path/court/stair footprints and preceding curb courses.

31 blocks are trimmed and103 conflicting blocks suppressed;526 active native
curb blocks remain on the building side of public paths. Matching vertical
fascias follow each trim. Historical meshes remain in the editable Blender
source with suppressed surfaces hidden and nonwalkable. Six roadside grass
strips inside public areas are suppressed. Fourteen verge contact fits remain
within their existing footprint, avoiding floor-height transitions.

The independent saved-source checker tests every active curb against public
paths, solids, private aprons and other curbs, and checks actual grass triangle
contact against the native floor. All original object geometry, actor/service
metadata, materials and navigation stay exact relative to the source70 snapshot.
Curb visibility, floor extent and verge geometry deliberately change. The current
1536² ground-shadow atlas is rebaked; architecture and foliage caster geometry
and its existing corner lighting stay exact.

Evidence: `boundary-check.json`, `traversal.json`, `world-checks.log`,
`schema-check.log`, `export-parity.log`, and the before/after overhead maps.
The native checks pass: zero curb/public overlaps, zero curb intersections,
zero curb/solid/apron overlaps, zero roadside grass/public overlaps and1550
grass contact samples.19 world tests, four schemas and17 routes/10 patrols pass.

Native screenshots, visual decisions, ordinary-input service checks, offline
cache78 migration and isolated sound-on timing are being completed. User Golden
acceptance and physical-GPU performance remain unverified. Keep server8011 alive.
