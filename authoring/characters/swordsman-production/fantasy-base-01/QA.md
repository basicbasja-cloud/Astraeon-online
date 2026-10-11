# QA verdict — fantasy swordsman candidate 01

**Release verdict: NO-SHIP — owner art review is pending.**
The factory produces a dedicated, reproducible candidate with editable source,
motion strips and genuine independent parts. This is not a declaration that
the supplied model has reached the approved painting's finish.

## Evidence and scope

Inspect `review.html` at game and authoring size, with the approved reference
registered beside the new source. The SE/W/NW/N grip close-ups and Idle, Walk,
BasicAttack and Death stress renders are refreshed from the final native.
Actual Blender camera inspection also confirms the 60-bone source hierarchy.
The final package, source audit, raster validation and integration evidence
identify the same native digest.

The corrected guard has a closed hooked profile rather than collapsed faces.
The actual hand masks covered hilt pixels. Independent hand/weapon depth
coverage is tested, while projected centers remain diagnostics. These checks
do not prove aesthetically perfect anatomy or contact at every finger surface.

| Area | Result | Practical assessment |
|---|---|---|
| Shared headings and registration | Match | Eight genuine rotations; common camera/root/scale. |
| Head-to-height proportion | Close source fit | The pre-retarget fit measured 49/176 pixels (27.8%); motion naturally changes projected bounds. |
| Costume identity and palette | Close | Gold scarf/cape, bronze armor, ivory/teal tunic and olive pants retained. |
| Face and hair likeness | Needs art review | Source hair and face paint retained; the generated mesh simplifies facial features and fine hair contours. |
| Painted material finish | Gap | Some gray texture patches and broad faceted shading remain; the approved illustration has richer metal/leather highlights and cleaner contours. |
| Grip and sword orientation | Needs art review | Shared hand attachment, finger joints and covered-hilt omission are present; W/NW/N are explicit stress views. |
| Body/head/cape separation | Technically tested | Concealed body survives cape removal; complete module pixels and depth determine overlap. |
| Motion | Presets retargeted, unapproved | All 17 CC0 clips retain blueprint timing; the owner must judge stance, readability, secondary motion and personality. |

## Technical gates

`factory/source-audit.json` checks normalized weights, at most four influences,
no unweighted vertices or invalid bones, unit pose scales, active IK target
reach, neutral wrist/perpendicular grip, loop endpoints, sampled framing and nondegenerate weapon
faces. Source boundary/nonmanifold counts are retained, including ornamental
single-sided cloth trim; the generated input is not certified retopologized.

`validation.json` checks all delivered frame positions for border clipping and
compares the independent 2D combination with the single assembled native
render. The thresholds are mean opaque RGB error ≤4/255, mean opaque alpha
error ≤3/255 and ≤64 coverage mismatch pixels per frame. Shared antialiased
boundaries can differ; maximum errors remain visible in the report.

The integration suite checks original input/concept digests, matching native
receipts, complete blueprint timing and atlas dimensions, actual NW/N concealed
body exposure, covered hilt pixels at sampled projections, loop endpoints and
nondegenerate weapon faces. Its retained verdict is
`factory/test-result.json`; detailed removal/grip measurements are in
`factory/integration-evidence.json`.

## Next art decision

Review this specific candidate against the approved painting, especially the
face, gray material patches, stance and rear grip. Approving the concept or
providing the FBX did not approve these new poses or outputs. Further source
polish can retain the same factory, rig and motion contract.

The bounded reuse proof adds a shorter broad sword, a crimson garment with a
fitted closed cuirass and bronze border, a circlet and an arm-strapped buckler
across the same poses. These variants remain unapproved.
Other class bodies, garment shapes and weapon families require fitted sources
and their own checks. Runtime delivery uses the existing modular renderer,
schema, ordered slots and packer; depth remains in authoring. The candidate is
selected only by the explicit development review, not admitted as default art.

Files named `*-source.png` show the original supplied input; `*-fitted.png`
and `rig-fit.json` retain earlier build-stage inspection. They are historical
diagnostics, not final production strips. Use `atlases/`, `package.json`, the
final source audit and the named motion/grip proofs for the delivered candidate.

Projected bone-center alpha is retained as a diagnostic, not a coverage gate:
in Walk NW frame 9 the nearer weapon surface has depth 47534 and the holding
hand 47642 at the rounded center. A blanket empty-center test incorrectly
rejects that legitimate foreground overlap. The integration gate now checks
actual opaque hand-covered weapon pixels using independent hand, unmasked
weapon and depth renders. It retains residual edge disagreement and requires
less than 5%, alongside the full-runtime holdout check.

## Owner hand feedback and motion replacement

The owner rejected the unnatural hand and clarified that the grip should be
perpendicular to the forearm while the wrist stays naturally aligned. The
arbitrary wrist rotation was removed. The right wrist now remains neutral;
the audit records grip/forearm angles and wrist rotations on real poses.
All 17 actions now use CC0 presets retargeted onto the supplied character.
Source receipts, sampled skeleton data and per-action adjustments are retained.
The rig's IK controls remain editable, while preset clips use FK rotations.
Body/head floor correction and cape floor contact handle the enlarged source
proportions during death. Neither those repairs nor the numeric 90-degree
check constitute owner approval of the grasp or motion.

## Final framing correction

The strict equipment compiler detected two alpha-1 antialiasing pixels at the
bottom of HeadHair in Death N frames 10–12. Death now settles by 0.05 source
units along negative Y over its clip, shared across all headings and parts.
The source pose is corrected; the boundary test is unchanged. The repair
records evaluated geometry, rig matrices and camera digests for every frame
of all 16 unchanged actions before reusing their bake caches. Death is
rendered again for both the source and equipment bank. See
`factory/death-framing-repair.json`.


## Sealed technical results

The source audit/raster checks and all five source integration tests pass.
The unchanged existing modular renderer suite passes 39 tests. The repaired
compiler resolves equal-depth body/outfit ties consistently: all 480 sampled
combinations across Idle, Walk, BasicAttack, Guard and Death now have maximum
RGBA error 0 against source depth composition. No equipment border pixels
are clipped. Runtime hand holdout covers 13,176 opaque overlap pixels, with
346 residual edge pixels above alpha 96 (2.626%, below the 5% bound).
The alternate garment changes depth at 374 pixels in Idle SE.

`factory/browser-review.json` records desktop/narrow layouts, playback and
scrubbing, costume/weapon/headgear/offhand/cape swaps, and actual-game
click-to-move Run followed by Idle. Fresh runtime/game console errors are
empty. Browser JPEG evidence is in `renders/browser/`. The explicit factory
game path selects the candidate through the render adapter and retains the
existing gameplay/save inputs. This is technical playback acceptance only.

The owner Golden art decision remains pending before other classes or weapon
families are expanded. The simplified face, faceted surfaces, material patches,
stance, grasp and final game-scale readability still need art judgment against
the approved painting. No numeric test promotes these outputs to final art.
