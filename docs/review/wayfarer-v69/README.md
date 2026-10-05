# RO3 town edges, aged paving and planted streets — source69

The curb follows the edge of the building zone. Houses own stone bases and
private paving; shared rectangular street stones have worn joints and selected
grassy patches. Rounded trees and grounded planting use original detailed art.
The supplied RO3 04_08_45/39/34 references guide these relationships; no reference
pixels or models are imported.

Branch: `codex/world-pipeline-v3-proof`. Parent source68: `27c65c1`.
Completed checkpoints `079f8f9` (curb/grass/house lots), `4aefbd7` (tree volume),
and `9bc6773` (coherent rectangular road paving) are pushed to origin. Final
city-detail source `e20dd3d` and pad-removal correction `159403e` are pushed;
review evidence is in `summary.json`.
Native authoring remains pass69; boot/page/static cache is74.

`comparison.html` contains native before/after images, the supplied reference and
six final views. `visual-test.json` records the scoped agent review. **Town Golden
accepted=false; locomotion accepted=false; cosmetics implemented=false.** The
agent review does not imply user acceptance or physical-device performance.

## Resulting source

- All37 ordinary houses have two staggered bevelled plinth courses and a cap,
  with490 private apron sections,420 stone rims and70 entrance gaps. Twenty
  planned sections crossing steps/slopes were omitted. Aprons rise.055 and rims
  .105. These910 native surfaces are walkable. The source68 house envelopes,
  density increase13.1%, one infill and tiered fountain remain.
- 629 bevelled stone street curbs (.12rise/.30width) outline the outside of the
  through-road union. Crossings, services, doors and steps remain open. Curbs
  separate the street from building-side paving. Roads, stairs and house aprons
  share aged rectangular stone art and world UV scale8, with native road tone
  slightly darker. The fine hexagon-like road repeat has been removed.
- 308 foundation grass strips and2464 rooted three-blade clumps follow house
  and paving margins.244 strips are fitted outside private rims;199 were widened
  toward.58–.82. Sixty-eight irregular roadside strips grow onto building-side
  paving. Their final shared1254² painted grass artwork has soft organic edges.
- The20 separate stone-image pads were removed after the user identified their
  stamped appearance. Continuous aged stone remains, with160 native three-blade
  grass tufts rooted in actual mortar/crack joints in20 selected building-side
  regions. Actual floor UV sampling verifies every root. There are no stone-image
  overlays in the current city; walkable floors and collision remain unchanged.
- Five inherited flower beds and22 orphan ground-flower groups are relocated to
  grounded planting islands on building-side curb edges. Raised flower boxes,
  formal fountain beds, owned entrances and nearby building-edge flowers remain.
  Twenty-seven painted grass islands tie the relocated flowers to their planting
  space. A separate native refit follows subtle paving slopes at every plant
  vertex instead of leaving a flat island floating above the ground.
- Trees have264 bark-textured trunk/branch parts,608 bowed leaf layers and280
  rounded crown tops. Original roots, trunks, branches, placement frames and
  collision remain. Crown extents are checked against preceding visible foliage;
  original-alpha leaf shadows are rebaked.
- Pierced main facades add147 recessed side/rear windows;11 formerly plain wings
  add64.455 original windows remain:666 windows/5994 unobstructed outward rays.
  Original hidden wall cores retain collision. All37 houses have weathered walls,
  base patina, lanterns, raised flowers, gutters and drains. Fourteen wing gables
  have timber relief. Twenty-seven goods stations have explicit native proxies.
- Eighteen formerly plain materials gain original shared metal wear, cloth
  weave, petal veins, produce rind, paper fiber or appropriate existing stone,
  glass and water art. Ordinary visible city surfaces have native textures;
  remaining plain colors serve fire/light. Native hues and geometry lighting are
  retained. Editable PNG masters and provenance live under `authoring/materials/`.
  Aged paving, planting grass and foliage are1254²; new prop surfaces,
  bark, curb stone and masonry are1024². Per-texture4× anisotropy preserves oblique
  detail. Gameplay buffers retain the existing resolution policy.
- Native `texture.alphaBlend` supports soft grass/patina. Building reveal uses
  hidden tall collision cores to qualify houses and visible facade triangles to
  reveal the player; the home fixture records faded owner `frontage-riverside`.

## Evidence and costs

`summary.json` records final outcomes, exact bake data and browser limitations.
`native-authoring.json` records saved Blender parameters and scene review data.

- `contact.json`:229376 quarter-unit samples,416 occupancy changes from27 goods
  colliders and7595 elevation changes from910 house surfaces/629 curb surfaces;
  zero unexpected changes.64501 low facade/accessory vertices fit occupied ground.
  Moving human height remains70*(92/76)/35≈2.42105 world units.
- `city-detail-check.json`:decorative paving/planting contacts, exact preservation
  of existing walkable floors and solids, relocated plant groups and material
  coverage. `curb-grass-check.json`:68 strips/272 vertices contact native ground.
  `tree-crown-check.json`:608 layers/280 tops,39217 preceding nonfoliage parts
  retained by the tree step and bounded crown extents.
- Main147/1323 rays, retained455/4095 rays and wings64/576 rays are separately
  recorded in `street-geometry.json`, `aperture-clearance.json` and
  `wing-clearance.json`. `house-life-check.json` records37 dressed houses and
  27 goods stations/1936 vertices fitting their native proxies.
- `traversal.json`:17 destinations and10 patrol loops clear, without route repair.
  Original navigation, spawn, actors, services, lights, portals and walkers remain.
- 95 individual Node checks across six files, four public schemas and saved
  Blender/export parity are recorded alongside ordinary services, field exit,
  save reload and offline cache evidence. No FPS thresholds are relaxed.
- `geometry-budget.json` distinguishes object geometry from terrain/decorative
  surface geometry. Additional facade relief and crown geometry have a measurable
  cost; those counts do not establish FPS.

Final views use native1280×666/1× buffers in a1280×800 DOM, distance160/yaw25°/
pitch46°. Source68 before views use the same camera/resolution. `curb-tree-trial/`
is the earlier hexagon-like-road trial, before the later path/planting corrections.
Fixtures establish appearance; `services/` checks ordinary input separately.
`performance.json` is isolated sound-on timing with unchanged frame/FPS gates.
Software timing does not certify physical hardware or painted gait continuity.

## Continue from the saved source

Use `authoring/wayfarer-spatial.blend`; historical migrations are not a town
rebuild recipe. All authoring changes are saved and exported into
`world/v3/wayfarer-spatial.json`. Once-only scene guards are intentional. Original
art masters and read-only checks make each step reviewable.

Geometry/light edits require sequential source save/export, corner bake,
original-alpha preparation and floor bake. The corner baker excludes vegetation;
leaf-only edits require the original-alpha floor bake. The ground baker indexes
nearby land polygons, with4096 full/indexed containment comparisons matching, and
precomputes UV projections checked against authored triangle corners. Do not
mutate source or bake during browser review/timing. Keep server8011 active.
