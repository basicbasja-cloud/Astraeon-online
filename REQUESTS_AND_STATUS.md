# User requests and current status

## Active continuation — 7 October 2026

Checkpoint audit finished and the six-walker experiment was reverted. The original
building-variety request resumed. Latest steering: local placement and tone should
be very similar to the supplied RO3 gameplay, while retaining Wayfarer's own theme.
Four current-source neighborhood views were inspected. A candidate adds varied
frontage treatment to 46 properties and adjusts the existing palette/light colors.
Latest steering also requires the RO3 camera baseline, more natural grass,
closer light/scale and improved trees. The candidate replaces uniform lawn bands
with curved planted pockets and gives 78 crowns fuller overlapping boughs,
retaining roots, physical footprints and original textures. Four side properties
now move 10 units inward to frame the square with continuous private terraces and
curbs. Latest feedback: grass must blend into stone, and the city may be too wide.
Native grass opacity now softens a 0.28-unit fringe over unchanged underlying
stone. Overall map width cannot be measured from the local reference frames;
plaza excess was directly visible and is being corrected. Cache 86 carries these
changes. All13 refreshed lighting/source stages and camera controls pass; actual final
gameplay capture, service walking, cache and performance review are running.
Visual acceptance remains open. Evidence:
`docs/review/wayfarer-capital-v76/property-frontages/`. No new push was requested.
The user explicitly authorizes resizing the whole city when needed to meet the
RO3 scale. That authorization includes reorganizing the current layout; no
additional confirmation is needed before a reversible local implementation.


Updated 7 October 2026 (Asia/Bangkok). The user requested a model-switch
checkpoint audit, authorized reverting the unreviewed crowd experiment, and then
asked to resume the original building-variety and neighborhood task using the
supplied RO3 beta frames. The restored pushed city checkpoint is `d7f9f15`.
Continue on `codex/world-pipeline-v3-proof`; RO3 visual acceptance remains open.
No PR, merge or deployment is requested. See the revision 76 checkpoint audit.

## Current implementation

The active architecture revision76 addresses the user's rejection of repeated
buildings:158 residential/commercial buildings, comprising37 retained originals
and121 additions across nine families. Fourteen paired plots were consolidated
into larger buildings. Council, Archive and Exchange have different massing;
public streets, plaza frontages and two inward-facing courts remain connected.
The pre-lighting geometry review found94 inner-neighborhood homes and a median
nearest visible gap of.96 world units, compared with3.84 in the first capital
draft. Source-matched structural checks pass; the full visual and ordinary gameplay
review remains pending.

The user's52 decoded Prontera RO3 beta gameplay frames are now the primary hard
visual reference for scale, materials, road edges, frontage and local adjacency.
Their README does not establish a complete global plan. Wayfarer keeps its own
geometric royal blueprint and original concept theme. A house count, architectural
family count, blueprint or geometry pass is not visual acceptance. Architecture
and foliage lighting finished; ground lighting is complete for the restored source.
The unchanged public street hierarchy is8-unit cross streets,9-unit district
streets,10-unit circuit and14/12-unit ceremonial axes. Twenty-eight local residents
and existing per-frame actor budgets remain.

Authority: `authoring/wayfarer-spatial.blend`, with its matching
`world/v3/wayfarer-spatial.json`. Bounds are 256 × 288 with 54,848 square world units of contiguous
land. Council Chambers, Grand Archive and Trade Exchange support the ceremonial
Hall–fountain axis. The native shoreline has defended walls, cliff courses,
waterline detail and bridge foundations. Original services, field destinations,
actor artwork, gameplay pace and progression semantics remain. The active
continuation calibrates new city camera defaults from the supplied gameplay.
Source74's continuous public-floor correction is already pushed as `7b72b3f`.

## Requirements and evidence

| IDs | Requirement | Current implementation | Acceptance still required |
| --- | --- | --- | --- |
| R01, R20, R21 | Correct branch, continuation, checkpoint pushes and complete report | Architecture revision 76 checkpoint `d7f9f15` pushed to existing branch; reports maintained | Complete and push final browser evidence |
| R02 | Sharp native rendering | 1280 × 666 playfield at ratio1; no resolution reduction | Final native captures and physical-device check |
| R03, R19 | RO3 beta gameplay frames are the primary hard baseline; continue to acceptance | Per-reference review criteria in capital evidence | Rendered visual sweep; overall acceptance remains open |
| R04, R05 | Detailed, aged exteriors, wings and useful accessories | Original 37 assemblies preserved; 121 additions across nine massing families share native materials | Street and civic inspection |
| R06, R13–R15 | Owned building areas, visible curbs, closed loops without conflicts | Shared private paving, 42 boundary loops across 40 owned blocks; native curb faces checked | Native sidewalk/entrance views |
| R07 | RO3 scale and density | 158 buildings;94 inner homes; pre-lighting median gap.96 world units | Ordinary neighborhood walking |
| R08, R16 | Fountain, larger rounded square and symmetric approaches | Original tiered fountain at [128,144], rounded court and ceremonial cross | Lit plaza/axis views |
| R09, R12, R17 | Grounded, purposeful grass/flowers/props/trees | Owned planting retained; 78 trees grounded and clear of streets/solids | Root, planting and accessory inspection |
| R10, R11, R22 | Natural public stone, distinct private rectangles, no random floor pads | Continuous world-space public UVs; derived private blocks; zero public/private overlap | Floor seam inspection |
| R18 | Warm RO3 casts and contact shade | Architecture and original-alpha foliage complete;4096² ground bake resumed | Native light/shadow comparison |
| R23 | Expand the same town into a royal regional capital | Integrated formal blueprint, four gates, ceremonial axes and three substantial new civic buildings | Current playable views |
| R24 | Water/cliff/wall/foundations match city quality efficiently | Native detailed shoreline; shared materials, spatial batches and culled shadow receivers | Perimeter inspection and unchanged performance gate |

Latest requirements are also tracked explicitly:

| ID | Requirement | Current implementation | Remaining verification |
| --- | --- | --- | --- |
| R25 | RO1 placement principles and hard RO3 person-relative street scale | 158 buildings; 8–10-unit public streets; 14/12 ceremonial avenues | Ordinary walking and final visual acceptance |
| R26 | Some buildings face their own feature area | Three frontages at Artisans’ Court, four at Willow Court; wells, seating, planting and craft features | Ordinary entry into both courts |
| R27 | Nearby buildings face the fountain plaza | Ten actual door-plane directions verified; complete models and entrance contacts moved; updated casts | Ordinary plaza walking; overall art acceptance remains open |

## Current verification boundary

Saved native/export parity passes, including shared Hall transforms and bake
invalidation. The independent source check preserves 280,145 original transformed
vertices and 211,953 UV faces; public/private overlap is zero. All 78 tree roots
are grounded and clear of solids/roads; gardens do not overlap roads. All 904 cliff
faces point outward and 226 waterline faces upward. All 26 destinations and 28
complete patrols are clear. The current suite passes 96 individual checks across six files; four public
schemas pass.

Native street/civic/perimeter inspection, ordinary service/neighborhood walking,
field/save reload, cache86 migration/offline reload and isolated sound-on
performance are being completed. Historical 136-home captures and the 140-home
gap patch are diagnostics, not current visual acceptance. The cloud machine has
no physical GPU. Retain the existing native-resolution, FPS/frame-time and
moving-frame gates and report its actual result. Warrior artwork acceptance
remains separate and open.

Evidence: [capital review](docs/review/wayfarer-capital-v75/README.md),
[RO3 criteria](docs/review/wayfarer-capital-v75/ro3-review.md),
[current handoff](CURRENT_HANDOFF.md),
[source74 floor correction](docs/review/wayfarer-v74/README.md).
Historical paused report: [record](docs/review/wayfarer-v72/PAUSED_REQUESTS_AND_STATUS.md).

## Complete request transcript in chronological order

Original spelling retained. Repeated requests are retained rather than removed.
The initial resolution question included the town screenshot supplied in this chat.

1. take and codex/world-pipeline-v3-proof branch as workspace and prepare everything before we continue to work

2. now continue from the handoff

3. why resolution bad ?

4. continue chasing building exterior detail ref from "RO3 Ref", Texture quality also, and the lighting shading also

5. House and building exterior detail and facade is based line ?, also the scale too

6. Hard ref to ro3

7. Continue the work until it pass visual test and add the work :hard ref the building density from RO3 too, also the water fountain.

8. The random green at road (like ro3) and the shapeness of the brick walkway (like ro3)

9. And some house are still less detail of facade and exterior (it look flat) hard ref from ro3 too

10. The another problem i found is The house texture is so flat and clean it like a non-render and the house not have a proper accessory (it look like just place in the floor and leave)

11. The green i mean the glass at the edge of building in ro3 make it feel lively

12. Look at the ro3 ref again and focus on the edge of building and road, there are some green grass and that make the road is not straight line even, and all building have their own space like a edge brick or something to make it not look like just place to the ground.

13. the road should have the edge to separate with building zone

14. the curb and the grass and the tree should have hi quality texture like the town

15. Continue the curb should be like ro 3 and the floor with grass too

16. When finish each step push to git too

17. Curb must be on edge building zone like ro3 and tree must be better too.

18. The road walk path is not fully perfect road right? They have some grass make it more beautiful, we can apply this to some area, and the walk path is not perfect brick alignment all so it make city look real

19. And as you screenshot, our walk path is many many hexagons and it conflict to the brick so it seem unnatural.

20. And all element of city have to be make sense like the flower should be at edge of building or walk path or some grass not on the middle of something not make sense, and the texture quality much be match with all city so they will not have anything leftout

21. Add don’t forget to push to git so the git have and updated everytime

22. Why the uneven pad is pad like a png random placement not smooth

23. Curb is not exactly see clearly, and please consider all element of ro3 ref for all aspect, the placement the color the town square, the tree , the green area, the facade, the architecture, the building, the walk path that not same like the building area.

24. Also the light color is more warm than us i think

25. The lighting and shade also should copy from ro3 ref

26. continue the job and don't forget to push

27. continue the job and don't forget to push

28. additional : as i see the screenshot of our town, the curb is not place correctly, it conflict with some part, you can see as the plaza.

29. and other area too. it should be work like separate the buliding area with the walk path

30. curb must be separate walk path and building area, so it will not have an open end, it will be the loop end or area, if cannot that mean our town blueprint is not okay

31. like in the plaza it should be a curve curb too

32. and can the plaza be more larger than rightnow ? and symetry road cross like to be more beutiful.

33. Please stop, all write a handoff and push all

34. now write all my request, and status report


34. read this and continue to work, I want it to meet the RO3 Ref standard .

35. also you can use all tools and skills if needed to make it perfect.

36. why the floor is random ? can we fix it ?

37. before improvement more, I want this city to be capital city of the region so can we expand the city to be like a prontera size, i also attached the prontera map, but we will not copy prontera blueprint but we will soft ref from them, but the theme is the concept art same, but not hard ref anymore just a theme

38. and water and cliff side detail like wall and under wall should be same quatily as the city but have some technic to reduce the resource use, because that zone player not care like city but the beautiful is to keep for not looking left out.

39. also our standard is same RO3 ref is our ultimate goal hard ref

40. Not like this, we should expand the old town and re organize them to be like real city

41. it messy make it more geometric since it capital city of region it should feel royal and impactful

42. and the city plan blue print too make it feel royal and respectful

43. and add the big building to support that feel too.

The active source75 blueprint supersedes the annex and organic layouts: one
integrated geometric capital, ceremonial axis, formal gardens and three large
civic buildings. All 37 existing houses are reorganized, with 135 new component-built houses. Native implementation is saved; final verification is in progress and RO3 remains the hard target.

44. User allowed higher housing density with Prontera as a soft reference, while retaining the original concept theme; then requested continuing the work. The first native source75 draft had 136 houses: all 37 existing assemblies reorganized and 99 component-built additions. The ceremonial avenues and major civic forecourts remain open. Verification is in progress; RO3 remains the hard visual target.

45. User found the city soulless and lonely in playable screenshots, then identified excessive building gaps. The active refinement concentrates homes along neighborhood streets, narrows secondary streets to 4–5 m, keeps ceremonial axes broad, and adds local resident routes. There are 140 homes (37 preserved originals, 103 additions); 51 new modules move, including 32 transferred from the perimeter. New density lighting and browser review are pending.

46. User clarified that characters must walk through real neighborhoods, using Prontera/RO3 gameplay screenshots as the reference. The preceding narrow-street revision organizes continuous street-facing rows and shared back courts, with 172 homes and 118 homes in the inner neighborhoods. Median visible facade gaps were .80 world units.
47. User requested small building gaps and curbs around residential/building areas to form the edge of walking paths. Shared owned-block paving and continuous curb boundaries replace individual island aprons inside neighborhoods.
48. User reaffirmed RO3 Ref as a hard reference. It governs street scale, density, curb placement, materials and final visual quality; Prontera's map remains a soft scale reference and Wayfarer retains an original blueprint. Lighting and playable verification of this revision are pending.

49. Continue the work until we meet the baseline. RO3 remains the hard target; continue actual rendered inspection and ordinary playable verification without treating structural checks as visual approval.

50. Please look at ro1 prontera for the example of blueprint and building placement plan, as i can see right now the steets look so narrow and you have to recheck all ro3 ref or the scale, please hard ref it. All ten RO3 references were re-inspected. The current revision keeps 172 complete houses, uses 8–10-unit public streets, removes five redundant through lanes and reorganizes 163 whole assemblies. Close frontage gaps and shared back courts remain; actors and building models are not rescaled.

Two owned inward-facing courts now give selected blocks their own purpose.
Artisans’ Court turns three complete homes/shops toward a shared well, craft
tables, noticeboard, benches and planting. Willow Court turns four frontages
toward a gathering well and planted seating. Main public widths remain 8–10
world units. Two existing local residents walk court routes; the total remains
28 and per-frame actor budgets are unchanged. Both courts are ordinary reachable
route destinations and are included in the service/neighborhood walking review.

51. Can some area have like a area zone of their own like not face the street but face their own zone for some feature to be there. Initially implemented two owned courtyards with nine inward-facing complete models, shared features, side-passage entry and local resident routes; the later square revision leaves seven courtyard-facing models.

The square now has ten complete nearby building frontages oriented toward the
fountain plaza, with doors, awnings and accessories moving together. Three
neighboring assemblies shift slightly to keep full visible gaps and street
clearance. Two edge homes join the square frontage; Artisans’ Court keeps three
inward-facing models and Willow Court keeps four. Trees and lamps are grounded
clear of the revised buildings, and one existing local resident walks the
square perimeter. Lighting and playable evidence are being refreshed again
for this latest native geometry.

52. Can you change the building near square plaza to be face with the plaza so it look more like a plaza center of life. Ten nearby complete frontages now face the fountain square, with three neighboring assemblies shifted to preserve clearance and an existing resident routed around the square. Both owned courts remain.

The actual-door audit found one retained infill home whose model front differed
from its placement heading. Its whole assembly rotates clockwise to face the
square and shifts .4 world units for roof clearance. Original indexed shape and
UVs remain. `frontageOffset` records that model’s geometric front, and the source
check verifies all ten actual door-plane directions. Final lighting and saved native/export parity pass. Browser
evidence is being captured for this corrected source. The first checkpoint’s
views are historical in `diagnostics/pre-entry-correction/`.

53. It doesn’t feel like ro3 ref, maybe because we reuse the same building again and again? Can we make new and efficiently the area that we use, not so dense but not so loose, so it make it feel like a real city, you can research the prontera on web or other capital city inreal world or game similar theme to use it for our ref

Revision 75 is visually rejected for architectural repetition. Revision 76
replaces the 135 repeated additions with 121 buildings across nine architectural
families, consolidating fourteen paired plots into larger buildings (158 total,
including the 37 originals). Three civic additions receive different massing.
Research: official RO1 Prontera map/guide, Colmar tourist-office heritage,
Blizzard’s Stormwind tour. RO3 remains the hard reference and native gameplay
review is required; previous geometry passes are not visual acceptance.

54. Pause now i have to add ref

Paused on 7 October 2026 UTC. Stopped the review and active ground bake;
preserved local changes. Await the new reference before continuing or pushing.

55. Already add in https://github.com/basicbasja-cloud/Astraeon-online/tree/codex/world-pipeline-v3-proof/RO3%20Ref/Prontera_RO3_Beta_Reference please use it for ref

Imported the two reference commits without discarding local work. Inspected all
four chronological contact sheets and opened representative source frames at
original resolution. The52 beta frames are now the primary RO3 gameplay visual
reference. Resume the native review; do not infer a complete city plan from them.

## Mobile infrastructure interruption — 7 October 2026

User recovery request explicitly authorizes checkpoint commits and pushes on the
existing branch, then profiling and streaming of the current real city. This
supersedes earlier no-push instructions. No checkout/reset/clean/stash/restore
was performed. Starting HEAD: d7f9f15978b0ca6347fe5f80302d147544bd4626.
The recovery-source.json receipt records the preserved authored files.

Original World resume point: first plaza inset (10 units), grass feathering,
frontages/tone/trees and camera are saved; all 13 source stages pass for export
e97f4333 and native59118c. Three gameplay captures and camera checks are preserved
under property-frontages/diagnostics/plaza-inset10/. Actual plaza still looks too
open; RO3 acceptance remains pending. The second six-unit inset is planning ONLY.
Its planner stopped at the 12,500-face grass guard (plaza-inset16-planning.log);
no native/export changes were applied. Preserve the unfinished iteration-2
scripts. On resuming: inspect tessellation/count accounting before changing any
guard, complete the second planner or choose a reference-supported correction,
then native parity/lighting and fresh gameplay captures. Continue service and
neighborhood walking, field/save/cache/offline and sound-on performance checks.
Do not rerun one-shot authors or regenerate saved art for streaming.

Active priority: baseline profiling -> chunked spawn boot/runtime streaming ->
bounded on-demand caching -> mobile/emulated acceptance. Physical iPhone Safari
is pending unless actually available. After sufficient available-environment
acceptance, resume the above World point automatically. No new art/layout work
during this interruption. Baseline/development evidence belongs in
 docs/review/wayfarer-capital-v76/mobile-streaming/.

Mobile insertion: checkpointed initial real-capital chunk loading, exact draw and
collision transport checks, and three streamed city captures. No art changes;
mobile acceptance and repeated traversal/cache verification remain pending.
Original RO3 task remains paused at the documented plaza planning guard.

Additional visual request received during mobile interruption: match RO3 lighting,
screenshot tone and feel more closely; polish other elements, including grass
particle/fine-blade detail and natural green ingress between paving stones along
walk paths. Incorporate this into the original visual task immediately after the
available-environment mobile gate. Keep camera comparison consistent, natural
planting restrained and clear routes. Do not substitute streaming for this work.

Mobile checkpoint: available WebKit iPhone13 emulation passes cold/warm and
six ordinary traversal legs,51 unloads/31 reloads, no duplicates or runtime
errors, exact repeated-location owned geometry bytes. Chromium actual field
gate release/return and offline save/migration checks pass. Candidate3 local
HTTP-body audit33.47MB before readiness; no full map.96 existing Node checks
and5 streaming contracts pass. Physical iPhone Safari PENDING. Remaining
infrastructure checks: court-legacy, camera, transient browser failure, finish
service/neighborhood walk. Then automatically resume original plaza enclosure
planning and the additional RO3 daylight/fine grass/natural ingress request.

Available-environment mobile gate completed:8 services/10 neighborhood stops,
field/save flow, court-legacy Canvas, current camera and503 retries pass.
Physical iPhone Safari PENDING, overall optimization PARTIAL; exact preserved
World task automatically RESUMED. Native inset16/RO3 lighting and natural grass
are active next. No art was changed during optimization.
