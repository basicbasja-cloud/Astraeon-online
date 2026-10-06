# User requests and current status

Updated 6 October 2026. The user resumed implementation toward the `RO3 Ref`
standard and then identified patchy floor rendering in the plaza screenshot.
The previous source72 stop was honored at that time; it no longer pauses work.

## Current outcome

Working branch: `codex/world-pipeline-v3-proof`. Source74 floor correction is pushed through `acd8fd3`; eleven native views
confirm coherent public stone and exact rendering with view culling.
Authority remains the saved Blender town and its matching JSON export.

The current native floor had two visible problems: coplanar rectangular backing
under the enlarged plaza, and inconsistent paving on public forecourts. Source74
removes 645.841m² of duplicate backing and fits public/private paving to closed
zone boundaries. Public stone has continuous world UVs and a shared tint.
Original art, full resolution, stairs, houses, plants, actors and gameplay stay
intact. Overall acceptance remains open. The active scope is now expansion into the
regional capital: original layout, Prontera-scale ambition, concept-art theme,
and hard RO3 quality throughout the city and its water/cliff defenses.

## Consolidated requirements

| ID | Requirement | Current work / verification | Remaining evidence |
| --- | --- | --- | --- |
| R01 | Correct branch and continuation | Correct branch; work resumed and checkpoints pushed | Complete current review |
| R02 | Fix blur; retain clear resolution | Native1280×800/1280×666 ratio 1; original artwork and1536² shadows | Final native screenshots |
| R03 | Hard reference all ten RO3 images | Reference review covers architecture, scale, paving, planting, composition and shading | Complete matching district sweep; user Golden acceptance |
| R04 | Detailed house exteriors and wings |37 houses preserve recessed windows, timber relief, steep roofs and wing details | Final frontage/residential inspection |
| R05 | Aged textures and useful accessories | Original weathered materials and27 goods stations retained | Final accessory and contact-shade inspection |
| R06 | Buildings own grounded private space | Closed zone edges, foundations and rectangular private paving; floor ownership check passes | Final entrance/lot images |
| R07 | RO3 scale and density |37 houses and prior density increase preserved through enlarged plaza | Whole-town visual comparison |
| R08 | RO3 fountain and square | Tiered water, four beds/benches; fountain centered at[54,52.75] | New lit plaza image |
| R09 | Grass at buildings, roads and selected joints | Foundation clumps, curb margins and selected rooted joint grass retained | Final distribution/contact inspection |
| R10 | Natural paving; road/lot distinction | Public irregular stone and private aged rectangles; continuous world UVs | Final floor images |
| R11 | Remove random PNG-like floor pads | No restored image pads; duplicate plaza backing removed natively | Final overlap/seam review |
| R12 | Sensible flowers/props and consistent quality |58 stranded flower groups rehomed into eleven owned clusters; all 798 parts verified | Final district sweep |
| R13 | Visible quality curbs at building edges | Seven textured/bevelled meshes define 19 logical closed boundaries | Final edge legibility review |
| R14 | Correct curb conflicts throughout town | Two curb/stair crossings repaired; expanded-town and boundary checks pass | Final native stair images |
| R15 | Closed loops around coherent building zones |19 loops; no open ends, intersections or public-path overlap | Final block composition review |
| R16 | Curved larger plaza and symmetric cross |538.194m² rounded court (+65.64%);8m symmetric approaches | Final lit plaza/axis images |
| R17 | Better integrated trees and foliage |64 trees retained; two whole groups moved off stairs onto flat margins with .015m embed | Final root/foliage inspection |
| R18 | Warm RO3 light and shade | Architecture/alpha foliage refreshed; source74 floor bake fresh at 1536², sun8/contact4 | Final lit reference comparison |
| R19 | Continue until visual test passes | Current schemas/parity,96 Node checks and native floor checks pass | Final captures, browser services/cache and isolated performance; no overall visual pass yet |
| R20 | Push each completed step | Three source73 implementation checkpoints pushed | Push current verified floor step and final evidence |
| R21 | All requests and status report | Current report plus preserved historical report/transcript | Update with final current results |
| R22 | Fix random floor from current screenshot |639 flat floors checked; coplanar backing removed; UV/zone ownership passes | Browser-only native capture retry |

| R23 | Expand this city into the regional capital | Original capital plan and native expansion active; Prontera is a loose scale reference | Expanded districts, navigation, source/export and native views |
| R24 | Same visual quality for water, cliffs, walls and foundations, with efficient rendering | Shared materials, native detail and spatial culling planned | Native edge views and resource measurements |

## Current verification

- All 96 individual Node checks pass.
- Four public schemas pass on source74.
- Saved Blender/export parity and shared Hall transform/bake invalidation pass.
- Seventeen destinations and ten patrols pass without repairs.
- Independent floor check verifies 639 surfaces and 35,359 UV corners; maximum
  rounding coverage difference .000231m²; residual plaza backing .00000506m².
- All architecture, plants, actors/services, stairs and unplanned floors preserved.
- Floor bake uses original cutout alpha,1536², sun8/contact4; cache versions 81.
- Native capture initially exceeded startup deadline during concurrent validation;
  browser-only retry underway. No gameplay/visual/performance gates are weakened.

Ordinary services, field transition/save reload, cache migration/offline reload
and isolated sound-on performance remain pending. Cloud SwiftShader does not
certify physical-GPU performance or user Golden approval. Historical results
remain available but are not reused as current acceptance.

Evidence: [source74 floor](docs/review/wayfarer-v74/README.md),
[source73 finishing](docs/review/wayfarer-v72/resumed/README.md),
[current handoff](CURRENT_HANDOFF.md). Historical paused report:
[record](docs/review/wayfarer-v72/PAUSED_REQUESTS_AND_STATUS.md).

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
