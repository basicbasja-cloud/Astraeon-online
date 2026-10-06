# Historical source72 request/status report

Superseded by the resumed work in REQUESTS_AND_STATUS.md.

# User requests and status report

Recorded 6 October 2026 (Asia/Bangkok). Covers all task requests visible in this
chat, including repeated push instructions and the latest stop/report requests.
Implementation remains paused. This update documents the work; it does not resume
geometry edits, bakes or visual testing.

## Current outcome

All implementation through source72 is committed and pushed as `deda35b` on
`codex/world-pipeline-v3-proof`. Native source and JSON export are saved. The
latest plaza/curb geometry and traversal checks pass, but the requested complete
RO3 visual result is **not yet verified or accepted**. Lighting bakes are stale,
cache remains78, and current native browser review is pending.

Authority: `authoring/wayfarer-spatial.blend` and `world/v3/wayfarer-spatial.json`.
Continuation instructions: [CURRENT_HANDOFF.md](CURRENT_HANDOFF.md).
Current evidence: [source72 review](docs/review/wayfarer-v72/README.md) and
[machine-readable status](docs/review/wayfarer-v72/status.json).
Historical source69/70/71 reports describe earlier snapshots, not current visual
acceptance. An earlier screenshot pass missed curb-placement problems identified
by the user and was superseded by those corrections.

## Consolidated requirements and status

“Implemented, review pending” means work is saved, not that it visually matches
RO3. Numeric counts below describe authored work and checks; they do not establish
reference fidelity. No overall completion percentage is claimed.

| ID | Your requirement | Saved work and present status | What remains |
| --- | --- | --- | --- |
| R01 | Use `codex/world-pipeline-v3-proof`, prepare the workspace and continue the handoff. | Completed: correct branch/workspace, native save/export and handoff available. Development server8011 was kept alive at the last verified check. | Wait for an explicit continuation; implementation is paused. |
| R02 | Investigate bad resolution and maintain clear visual quality. | Native1280×800 view with1280×666 scene at pixel ratio1 retained; no deliberate resolution downgrade. Historical original texture art is1024²/1254² and the ground atlas1536². | Current apparent sharpness has not been established by a source72 capture. The user's initial blur concern is not closed solely by keeping buffer dimensions. |
| R03 | Hard reference all aspects of the town to `RO3 Ref`, including placement, color, architecture, scale and overall composition. | Implemented in successive native passes using the ten supplied reference images; original art/assets were authored. | Compare every final district view against those references; no source72 visual acceptance yet. |
| R04 | Add detailed building exteriors and facades; eliminate flat houses and plain wings. | All37 ordinary houses retained; historical additions include666 total windows,436 facade band/diamond parts,124 shutters, wing windows/timber relief, weathered walls and base patina. Source72 preserves that detail while moving five whole house groups. | Inspect every frontage/wing at final scale, especially any house still reading as flat. Counts alone do not prove visual quality. |
| R05 | Make house textures aged and rendered, with proper exterior accessories. | Saved wall/brick/limewash/patina textures, lanterns, upper flowers, drains and27 goods stations; shared prop material work covers metal, cloth, petals, rind and paper. | Final weathering, accessory placement and contact-shade review after fresh bakes. |
| R06 | Buildings must own grounded space, brick edges, foundations and building-side paving rather than sit loosely on the floor. | Houses retain bevelled plinth courses/caps; native private aprons fit the revised blocks. Source72 replaces old lot rims with shared closed building-zone boundaries. | Final grounding and public/private transition review, including door/service approaches. |
| R07 | Match RO3 building scale and density. | Earlier source68 recorded a13.1% density increase and one infill. Current37 ordinary houses retain dimensions; five are repositioned to fit the larger plaza without dropping house count. | Confirm current spatial density and scale visually against RO3 after the plaza enlargement. Historical density work is not a current acceptance result. |
| R08 | Match the water fountain and its town-square setting to RO3. | Native tiered fountain retains celestial figure, water levels, four cascades, four formal beds and four benches. Whole group is centered at[54,52.75]; benches received sage color in earlier work. | Review fountain detail, water appearance, scale and court composition in the final lit scene. |
| R09 | Grass at building and road edges should make the city lively; selected paving joints may have grass. | Source72 fits308 foundation strips/2464 clumps,160 actual-mortar tufts,20 new soft curb-margin strips and four civic green islands. | Inspect natural distribution, edge softness, texture cohesion and floor contact throughout town. Grass is understood from the user's clarification; “glass” in the original request meant grass. |
| R10 | Walkways should have natural irregularity rather than perfect brick alignment or a dense hexagon repeat. | The earlier fine hexagon-like repeat was replaced. Public streets/court use larger irregular rounded stones; private building paving/stairs use aged rectangular stone. Actual-joint grass was refitted for source72. | Verify stone scale, variation, sharpness and the road-versus-lot distinction at final viewing distance. |
| R11 | Remove the random PNG-like uneven pads and make wear blend smoothly. | All20 separate stone-image pads were removed in source69; integrated floor materials and native joint grass remain. Source72 does not restore those pads. | Check final floors for any remaining visual seams or stamped appearance. |
| R12 | Every flower/prop must have a sensible place, with matching texture quality across the city. |27 ground flower groups follow nearby house owners and private curb margins; formal fountain beds and owned displays remain. Shared textures were added to formerly plain city materials. | Full visual sweep for isolated flowers, mismatched materials or accessories stranded by later layout edits. |
| R13 | Curbs must be clearly visible, high quality and placed at the building-zone edge. | Seven final native curb meshes use textured stone, dark fascias,0.36m width,0.20m rise and0.035m bevel. Old conflicting independent courses/rims are hidden and nonwalkable. | Verify clear legibility, material quality and correct side of every road in screenshots. |
| R14 | Fix curb conflicts in the plaza and all other areas. | Source72 independent native checker passes with no public-path overlap, curb/solid-volume overlap or curb intersection. Eighteen retaining-wall parts fit the widened Hall opening. | Final native visual review plus final saved-source parity check; automated geometry checks are narrower than whole-town visual acceptance. |
| R15 | Curbs must form closed loops around coherent building areas; redesign the blueprint if necessary. | Blueprint redesigned: three shared district blocks plus four civic islands produce seven meshes and19 logical closed outline loops. Native boundary topology has zero open ends. Flush entrance crossings retain continuous boundaries. | Review whether every resulting block reads as a coherent building zone to the player. |
| R16 | Make curved plaza curbs, a larger plaza and a beautiful symmetric road cross. | Rounded court28×19.5m with3m corner radius; footprint538.194m² versus324.915m² (+65.64%). All four approaches are8m wide with matching opposing lengths; fountain recentered. Civic planted islands are cut out of actual paving. | Final lit screenshots of the curve transitions, cross symmetry and usable open space. |
| R17 | Improve trees, curb/grass/tree texture quality and integrate them with the town. |62 conifers use textured curved branch tiers; two broadleaf accents retained. Five full tree groups and owned beds move with the blueprint. All64 trunk contacts measured. | Visually inspect foliage/shade and two inherited contact outliers; moved roots preserve earlier offsets, which does not prove all roots are correct. |
| R18 | Match RO3's warmer lighting and shading. | Warm sun[1.18,1.05,0.79], warm fill[1.04,1,0.90], strengths0.65/0.44 and soft cast/contact-shade settings retained. Source72 bake code now respects actual floor holes. | Source72 architecture, foliage and floor bakes have not run. Current floor atlas is stale; export uses geometric fallback. Final warm-light comparison remains open. |
| R19 | Continue until the visual test passes. | Partial: current geometry/world/traversal checks pass. Earlier visual review was superseded by user corrections. | This requirement remains unfinished. Fresh bakes, native district captures, reference comparisons and corrections are required after the user resumes. |
| R20 | Push each completed step and keep Git updated; stop, write a handoff and push all. | Completed for the paused snapshot: all implementation pushed as `deda35b`; remote matched and working tree was clean. Stop/handoff honored. This report is a subsequent documentation-only checkpoint. | Continue pushing each completed step after work resumes. |
| R21 | Write all requests and a status report. | This document includes the consolidated requirements, evidence, unfinished work and the complete chronological request transcript below. | No implementation change is implied by this reporting request. |

## Verification report for the paused source72 snapshot

| Check | Result | Evidence / limit |
| --- | --- | --- |
| Native save and JSON export | Completed | `patrol-author.log` confirms both after seven native route repairs. |
| Closed boundaries / geometry conflicts | Passed | `boundary-check.json`:19 logical loops, zero open ends, zero public-path overlaps, zero curb/solid-volume overlaps, zero curb intersection area. |
| World tests | Passed | `world-tests.log`:20 pass,0 fail, including actual floor-face containment and a closed-band hole fixture. |
| Destination and patrol traversal | Passed | `traversal.json`:17 reachable destinations,10 clear patrols, no additional repairs required. |
| Tree-floor contacts | Measured; visual review pending |64 contacts; five moved roots keep prior offsets within0.00001m. Inherited offsets at plaza-oak-east-root(-0.525m) and garden-v4-tree-7-trunk(-1.03826m) require inspection. |
| Public schemas | Earlier source72 snapshot passed | Four passed earlier; final saved snapshot still needs a rerun. |
| Blender/export parity | Pending | No final source72 parity check recorded. |
| Architecture / foliage / floor lighting | Stale | Source71 atlas is historical; no source72 rebakes. |
| Cache | Pending update and test | Remains78; stable source72 needs a coordinated bump and migration/offline checks. |
| Native browser visual review | Pending | No final source72 district screenshots or accepted visual test. |
| Ordinary services, field transition, save reload | Historical pass only | Merchant/Artisan/Housing Keeper checks passed on source70; rerun for source72. |
| Performance | Current snapshot unverified | Prior isolated SwiftShader result failed; do not reuse it as a source72 measurement or physical-GPU result. |
| User visual acceptance | Not obtained | No user Golden acceptance; source72 visual requirements remain open. |

No new tests, geometry changes or bakes were performed to prepare this report.

## Remaining work when you resume

1. Check final schemas and saved Blender/export parity; inspect tree-contact outliers.
2. Bake architecture, then foliage, then floor shadows, keeping original alpha and resolution.
3. Update cache78→79 together and verify migration/offline reload.
4. Capture all ten native district views and compare against all ten RO3 references.
   Review facade depth, scale/density, house-owned space, street/lot distinction,
   closed and curved curbs, fountain/cross composition, grass/flower ownership,
   texture cohesion, trees and warm lighting. Correct failures and capture again.
5. Verify ordinary services, field transition/save reload and isolated performance.
6. Push each completed step. Claim a visual pass only with current evidence;
   user acceptance and physical-GPU verification must be recorded separately.

The commands and guarded native-authoring sequence are in `CURRENT_HANDOFF.md`.

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
