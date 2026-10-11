# QA verdict: licensed anatomy source fitting

**NO-SHIP. Owner approval: absent. Runtime admission: absent. Motion coverage: empty.**

Evidence: latest eight `*-final-static.png` frames, `SE-final-static-large.png`,
matching SE/W/NW/N grip crops, weapon-only/hand-masked crops and full-canvas
holdouts, five equipped layers per direction, equipment-removal and complete
body-only frames. Earlier renders document internal fitting failures, not passes.

The actual mesh remains connected and closed: 6,287 vertices, 6,324 faces,
6,242 quads and 82 triangles; zero boundary/nonmanifold edges. A nonmutating
simple triangle-join test leaves 74 triangles, so automated joining does not
establish acceptable joint topology. No new armature was created.

The glTF inspection has at most four influences; **this FBX source has up to six
positive influences**, with inherited sums about 0.0845–1.2795. Static fitting
normalizes the blend during interpolation. Those raw groups have not passed
weight normalization or deformation QA and must not be described as a certified
four-weight bind. Subdivision is a study surface modifier, not retopology.

Source fixes: forearm armor fitted inward and then given anatomy clearance,
continuous navy sleeves beneath the separate plates, body-derived garment clearance,
toe smoothing, a back-mounted cape, a stylized skin/eye pass, source-surface
eyelids, and an anatomical palm frame whose roll locates MCP finger roots before
curl. Finger rolls follow the donor's actual axes. A thinner handle and continued
distal curl make SE/W overlap more credible; the corresponding weapon-only
holdouts remove those covered pixels. These are static source corrections;
there are no FK controls, animation tests, or validated contact mechanics.

Lighting is shared by all headings and reduced from the initial overbright
study lights; it is not corrected independently per frame.

Latest internal refinement: the plain guard is hidden and replaced by hooked
quillons, a central relief and a pommel. Weapon diagnostics include those source
objects and keep the old hidden guard inactive. Belt frame/pin placement clears
the leather backing and refitted shirt; garment emblems follow evaluated surfaces.
Boot soles establish a shoe outline; bronze/leather shading now converts intended
paint colors to linear shader inputs and samples the source UV paint atlas without
bleeding into neighboring swatches. Lips, brows, cheek tint and native eye shading
are refined. These are improvements, not an owner-approved likeness result.

The additional semantic bake separates body/outfit from head/hair and exports
weapon/cape across all eight headings. Headgear is unequipped. Head/body masking
uses 1,286 head-region polygons on the unchanged closed body. Numeric recomposition
is recorded separately under `modularLayerProof`; it does not validate substitution,
deformation or motion coverage.

Major visual gaps: the face/hair identity and painterly finish still differ
substantially from the approved concept; boots, collar and costume construction
need authored detail; metal is too uniformly shaded; cape silhouette differs;
NW complete-character blade visibility remains inadequate. Inspecting only an
isolated grip cannot certify an occluded full-character frame.

The Ranger garment test exposes skin/intersections and is inactive. Current
body-derived garments avoid that test's gross gaps but need seam and deformation
review. Visible-only equipped layer reconstruction measures this combination
alone, not all outfits/weapons or action coverage. Do not publish or expand the
class/action matrix on the strength of these numeric checks.
