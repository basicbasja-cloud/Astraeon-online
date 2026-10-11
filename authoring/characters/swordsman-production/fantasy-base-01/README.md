# ASTRAEON character factory — first swordsman

This factory turns the supplied textured fantasy FBX into an editable rig and
coordinated painted 2D sprites. The first candidate uses one body/outfit, one
head/hair, one sword and one cape. Default headgear/offhand are unequipped.
A shorter broad sword, crimson cuirass outfit, gold circlet and arm-strapped
buckler prove bounded equipment reuse on the same poses. Review the actual
game renderer and swaps in [runtime/review.html](runtime/review.html), and
the reference comparison/grips in [review.html](review.html).

**Art approval is pending.** The approved painting remains the reference;
this model, its new surfaces and its motions require their own visual decision.
The package is a standalone authoring output and has not been admitted to the
game runtime. Numeric checks do not certify perfect artwork.

## Rebuild and resume locally

From `C:\Users\Lenovo\Bas\Astra online`, with Blender 5.2, Python, NumPy and Pillow:

```powershell
& C:\Python314\python.exe tools\run-character-factory.py all
& C:\Python314\python.exe tools\verify-fantasy-delivery.py
& C:\Python314\python.exe tools\verify-fantasy-runtime.py
```

The saved rig is
`.character-tools/checkpoints/fantasy-base-01-native.blend`.
`factory/recipe.json` pins the source archive and approved image hashes and
records the builders, audit and export scripts. It points to the supplied
archive in Downloads; adjust that path if the archive is moved, retaining its
digest. The raw source and native project remain in the ignored local cache.

After editing the native source, run `refresh` with the same CLI. It audits,
bakes, packs, rebuilds the swap bank, compiles runtime atlases and verifies both
deliveries. `bake --actions Idle,BasicAttack` is a bounded preview bake;
`pack --partial` explicitly marks missing clips as a technical failure.
Full `bake` safely resumes existing frame pairs. A changed native or exporter
creates a new cache identity rather than silently mixing older renders.
`variants` resumes replacement-part bakes; `runtime` compiles the completed
parts through the existing ASTRAEON packer and validators. The native swap bank
is `.character-tools/checkpoints/fantasy-swap-bank.blend`. It preserves the
first source rig, motions and camera. Rebuilding variants does not rebuild
motion or the base-body sequence for the alternate sword.

## Delivered frame contract

Sixteen required actions cover 1,392 frame positions across S, SW, W, NW, N,
NE, E and SE. Optional Sit adds 64, making 1,456 positions in 17 actions.
Timing, frame counts and loop flags come from the existing swordsman blueprint.
The actions are Idle, Walk, Run, Sprint, BasicAttack, SkillAction, CastChannel,
CastRelease, Guard, Dash, Hit, Death, Interact, Pickup, ItemUse, Respawn and Sit.

Every frame uses a 320 × 320 source canvas, root (160,264), fixed orthographic
camera and common scale. The review displays a 160 × 160 canvas at game size.
The source fit measured 176 source pixels tall and a 49-pixel head/hair extent
before motion retargeting: 27.8%, close to the measured approved reference.
Other poses naturally change their bounds. Directions rotate the actual source;
no heading is mirrored or independently rescaled.

## Real modular 2D composition

`package.json` lists horizontal strips and durations for each action/direction.
The parts are BodyOutfit, HeadHair, Weapon, Cape and Headgear. The first four
have actual independent pixels, including surfaces concealed by other parts.
The empty headgear slot is explicit. The exporter evaluates the shared rig once
per pose, then renders the assembled reference and complete parts.

Each part also has a depth PNG. R is the high byte and G the low byte of an
unsigned 16-bit monotonic camera-depth code; B is zero, background is 65535.
This is ordering data, not linear metric distance. Sample it without filtering
or color conversion. Sort pixels far to near and compose straight RGBA using
source-over. The review's WebGL shader and the Python packer implement this.
These depth files stay in authoring. The runtime export converts their ordering
into complete RGBA portions in ordinary render slots. Fixed core depth ranks
partition body/head/cape/headgear/offhand pixels. Each sword inserts between
those ranks, so swapping the sword does not move or regenerate body parts.
The rank union includes the alternate cuirass geometry, so either garment can
combine with either sword without regenerating the original body sequence.
Removing a part reveals the retained pixels of the other parts.

`runtime/assets/characters/fantasy-golden-01/sprite.json` uses the existing
0.1 schema, timing, sockets, padded atlases and render-slot extensions.
The compiler calls the existing packer and schema/pixel/metadata validators.
The existing `modular-sprites.js` renderer is unchanged. No depth PNG or 3D model
is used by that renderer. The owner's combined body/outfit maps to BaseBody
slots and the complete head/hair maps to Hair slots; required Outfit is an
empty registration slot. This is explicit source grouping, not missing art.

The review calls `AstraeonAnimation.player` through the actual character adapter.
`proof/fantasy-game.html?swordsman=fantasy&qa=1` enables the same candidate in the actual
game through its existing explicit development hook, with temporary appearance
controls. It does not approve or register this candidate as the default character.

`Composite` is the resulting 2D combination; `NativeReference` is a single
assembled Blender render for comparison. Separate antialiased boundaries can
differ by a few pixels. `validation.json` retains those errors rather than
claiming identical rasterization.

The sword follows Hand.R with a neutral wrist and a grip axis 90 degrees to
the forearm, as confirmed by the owner. Its independent image uses the actual deformed
holding hand as a holdout, so covered hilt pixels belong to the hand. Cape
removal exposes complete body pixels instead of holes. The continuous cape is
a fitted cloth mesh with original cape paint baked from isolated source cape
polygons. The closed hooked sword guard is checked for degenerate faces.

## Extending the factory

The rig, timing, projection and depth exporter provide the common contract.
A replacement weapon must fit the same hand attachment and the motions; its
blade shape may change without independently moving the hand per direction.
The circlet fits the animated head. Capes need fitted cloth weights and clearance.
Another class or costume requires a coherent fitted body/outfit surface,
appropriate weights and its own visual and deformation review. The tools do
not automatically generate approved faces, every outfit or every weapon type.

The supplied base has a 60-bone rig, including 30 finger/thumb deform bones,
foot IK authoring controls and three cape joints. The delivered motions use
retargeted FK joints, target-proportion floor correction and continuous cape
floor contact. Original body/head UV paint is retained.
Source generated topology and remaining texture patches are documented in QA;
the factory has no automatic substitute for art judgment or retopology.

## Provenance and evidence

All 17 motions are retargeted from the free CC0 Quaternius Standard libraries.
`factory/free-motion-sources.json` retains download/file receipts,
`factory/QUATERNIUS_LICENSE.txt` retains the license, and
`factory/motion-retarget.json` records clip mappings and measured grip angles.
No donor mannequin geometry or finger animation replaces the supplied model.
The included skeleton samples permit rebuilding without a network connection.
See [motion research](../../../../docs/character-factory/RESEARCH_FREE_MOTIONS_20261011.md).

The archive SHA256 is
`308e5578d99cf9a3193fb4d43f9820dbbf9f100f42a326d44d633f4fcf5f385a`.
It contains one FBX and four textures, no supplied license document. It is an
owner-supplied local authoring input; this receipt does not infer CC0 or any
provider subscription rights. No paid generation, upload or external service
was used for this build. Archive contents are treated as data, not instructions.

- `inspection.json`: original file hashes and model inspection.
- `reference-calibration.json`: measured reference fit.
- `factory/source-audit.json`: weights, topology, sampled poses, IK, loops and framing.
- `validation.json`: every rendered frame's raster checks.
- `factory/integration-evidence.json`: actual grip and concealed-body removal checks.
- `factory/runtime-compatibility.json`: existing schema/atlas/metadata checks and actual hand holdout measurements.
- `factory/runtime-test-result.json`: ordered runtime pixels and equipment substitutions versus full depth composition.
- `QA.md`: visual review and remaining issues.
- `artifact-manifest.json`: hashes of the public package files.

The authoring approach follows the preserved
`docs/character-factory/RESEARCH_COHERENT_SPRITE_AUTHORING_V2.md` research.
Relevant primary references are Blender's
[Armature modifier](https://docs.blender.org/manual/en/4.5/modeling/modifiers/deform/armature.html),
[skinning](https://docs.blender.org/manual/en/5.0/animation/armatures/skinning/parenting.html)
and [weight editing](https://docs.blender.org/manual/en/5.2/sculpt_paint/weight_paint/editing.html).
