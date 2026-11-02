# Swordsman Walk: native source replay and five painting experiments

**No action, cutout, variant or character is accepted by this checkpoint.**
The owner authorized all required work and reports to issue #2. Posting permission
is resolved. Production remains at the source-accurate complete-master gate;
failed artwork has not been segmented, imported or expanded into other views.

## Concrete results

One original Mesh2Motion Walk job was replayed twice in Blender4.3.2:16 actual
samples ×8 real cameras, with the retained GLB, renderer, camera and source
timing unchanged. All136 decoded PNGs (128 poses plus8 contact sheets) match
pixel-for-pixel between these two runs. Raw PNG file hashes differ because
Blender embeds Date/Time/RenderTime metadata. The new sealing tool removes only
PNG metadata and preserves **every RGBA byte, including RGB beneath zero alpha**.
Both sealed128-pose packages, their unchanged manifest and their seal reproduce
as **130 byte-identical files**. This is one source job, not six fitted characters
or a passed motion/contact test.

[Sealed source package and hashes](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-walk-guide-sealed-20261102/capture-seal.json)
· [source manifest](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-walk-guide-sealed-20261102/manifest.json)
· [verification and tool versions](verification.json)

Five live image-generation/edit attempts were made and retained with their exact
prompts, references and raw result hashes:

| Attempt | Scope and result |
| --- | --- |
| [Whole sequence](../../../../authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-male-walk-sw-20261102/) |16 SW poses from the retained guide and tall matching-direction identity. Unapproved pose/weapon/temporal consistency; native1254px output despite requesting at least1536px. |
| [Four keys](../../../../authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-male-walk-sw-keyposes-20261102/) |Source slots0/4/8/12 from the new replay, rendered together at greater per-pose detail. Sword endpoints/orientation do not consistently match source. Hidden ankle and contact association remain unresolved. |
| [Marked key correction](../../../../authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-4keys-marked-20261102/) |Explicit ankle/wrist/prop target rings; output still needs geometry review and was not adopted. |
| [Single complete-frame repair](../../../../authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-sw12-single-20261102/) |A full-body crop edit, not separately generated limbs. It changes anatomy/details beyond the proposed repair and was not composited into the master. The earlier foot diagnosis was too strong; see correction below. |
| [Sword-only correction](../../../../authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-4keys-weapon-edit-20261102/) |Marked endpoints help shorten the bottom-row blades, but the endpoints still miss the requested guide.164,528 visible RGBA pixels change outside deliberately generous weapon review windows, so this is not a preserved local edit. |

All five outputs are1254×1254 RGBA. Model version and seed were not exposed by
the image tool; generation itself cannot be claimed as bit-reproducible. Saved
inputs/results and the deterministic processing are reproducible. No output was
upscaled and described as newly authored768px detail.

## Inspect the actual geometry

- [16-pose guide/draft/control comparison at source cadence](full-normal.gif)
  and [3× slow](full-slow.gif). Normal preview is1,670ms after GIF quantization;
  the source cycle is40 source frames at24fps (1,666.667ms).
- [Four-key sampling preview](key-sampling.gif): this deliberately skips twelve
  samples and is **not** a finished or smooth Walk clip.
- Original four-key comparisons: [00](key-00.png), [04](key-04.png),
  [08](key-08.png), [12](key-12.png).
- Marked correction: [00](paint-attempts/marked-key-00.png),
  [04](paint-attempts/marked-key-04.png), [08](paint-attempts/marked-key-08.png),
  [12](paint-attempts/marked-key-12.png).
- [Single-frame crop edit](paint-attempts/single-edit-12.png).
- Sword correction: [00](paint-attempts/weapon-edit-key-00.png),
  [04](paint-attempts/weapon-edit-key-04.png),
  [08](paint-attempts/weapon-edit-key-08.png),
  [12](paint-attempts/weapon-edit-key-12.png).
- [Visible tip comparison](paint-attempts/weapon-tip-target-comparison.png)
  and [change map](paint-attempts/weapon-edit-change-map.png): red changes are
  outside the generous weapon windows; blue changes are inside, without any
  implication of correct ownership.

The last output's visible core tips were manually inspected at native pixel
scale. Their guide-endpoint distances are approximately1.05/4.65/3.15/2.09 runtime
pixels for0/4/8/12, with a conservative3-raw-pixel annotation uncertainty radius
recorded in [the receipt](paint-attempts/receipt.json). These are weapon endpoint
diagnostics, **not** the plan's separate≤1 runtime pixel sole-contact test.
No painted contact point or anatomy score is invented from a bounding box.

**Correction to the intermediate diagnosis:** the conspicuous right-side feature
in key12 is a bent knee/shin, not a clearly located ankle. The ankle is occluded
by the supporting leg. The claim that the lifted ankle was visibly far out to
the right is withdrawn. Neither a numeric large ankle error nor a contact pass
is certified. The single-frame edit remains a study, not an adopted fix.

The retained16-pose guide-contact image and the newly replayed contact image are
not raster-identical (56,237 RGB pixels differ). They must not be described as
byte-identical references. The first painting used the retained image; all later
four-key and marked references were built directly from the newly replayed
frames. The numerical tip check concerns the last four-key output only. The
guide's `head` control is a bone origin, not an annotated painted crown; wrists
and foot-bone origins likewise are not interchangeable with palm/sole landmarks.

## Reproduction and preservation

The authoring transform is fixed for every cell: source crop
`[420,520,1116,1216]` maps to a348px square at`[210,260]` on the full768px canvas.
Fractional1254/4 cell boundaries are sampled uniformly with premultiplied alpha.
The source camera and root remain unchanged. No per-frame fitting, limb warp,
frozen leg, mirrored view or fabricated frame is used. Inspection boards crop
one shared authoring viewport for readability; draft frames retain their full
768px canvas.

From the repository root, into fresh output directories:

```sh
blender --disable-autoexec -b -t 2 --python-exit-code 1 \
  --python tools/character_factory_v3/render_patch001_guides.py -- \
  --job authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-male-walk-sw-keyposes-20261102/source-job.json \
  --output /tmp/walk-native-replay

python tools/character_factory_v3/seal_source_guide_replay.py \
  --source /tmp/walk-native-replay --output /tmp/walk-sealed

python tools/character_factory_v3/prepare_walk_reference_controls.py \
  --guide-folder /tmp/walk-sealed \
  --key-sheet authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-male-walk-sw-keyposes-20261102/generated-sheet.png \
  --output /tmp/walk-reference-controls

python tools/character_factory_v3/review_swordsman_walk_locked_guides.py \
  --guide-folder /tmp/walk-sealed \
  --full-sheet authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-male-walk-sw-20261102/generated-sheet.png \
  --key-sheet authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-male-walk-sw-keyposes-20261102/generated-sheet.png \
  --output /tmp/walk-review

python tools/character_factory_v3/review_walk_paint_attempts.py \
  --guide-folder /tmp/walk-sealed --output /tmp/walk-paint-attempts

python -m unittest discover -s tests/character_factory_v3 \
  -p test_source_guide_sealing.py -v
```

Fresh rebuilds match130 sealed source files,44 primary review files,12 additional
review files and8 reference-control files byte-for-byte. The six actual marked
reference PNGs were also compared to the exact inputs used for generation and
match. Three focused tests pass: metadata-only changes with hidden RGB/partial
alpha preserved; late missing input produces no output; failure after writing
the first frame removes only the owned output and preserves inputs/prior work.
Existing outputs are refused. The full historical factory test suite was not
rerun for these isolated new tools.896/896 protected baseline hashes still match;
no canonical renderer, production binding, original painting or runtime asset
was changed.

## Coverage and the remaining prerequisite

| Character | Newly complete Patch0.0.1 character | Newly accepted action / gameplay in this checkpoint |
| --- | --- | --- |
| Swordsman male |No —19-action set incomplete |None; Walk master gate remains unresolved |
| Swordsman female |No —19-action set incomplete |None |
| Mage male |No —18-action set incomplete |None |
| Mage female |No —18-action set incomplete |None |
| Archer male |No —20-action set incomplete |None |
| Archer female |No —20-action set incomplete |None |

Total remains **0/6 complete characters**. The ledger still requests114 logical
actions /96 paint jobs. The previously reported2/96 technical imports have not
been increased or recertified here. No new game test was run because no new
artwork passed admission. Packages, all-view variants, transitions and actual
six-character gameplay remain incomplete.

The available image interface exposes references and text instructions, not a
hard pose/mask constraint. Whole-sequence, larger sparse keys, explicit source
joint targets, a complete-frame local repair and direct sword-endpoint edits
have not produced a source-accurate approved master. A deterministic compositor
can protect outside pixels; it cannot correct wrong anatomy/weapon geometry
inside the proposed edit. Plugin discovery found no ControlNet/ComfyUI/Leonardo
integration; general editing apps are unconnected and their ability to satisfy
this exact production gate is unverified.

The unresolved prerequisite is a complete-master painting/retouch workflow that
actually preserves the source pose and passes the existing contact/temporal
gates. This is a capability/quality blockage, **not a request for more owner
permission**. Do not keep expanding rejected paintings, substitute idle clips,
or declare six characters finished from these source captures and tests.
