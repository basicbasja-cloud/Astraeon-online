# Rendered motion acquisition — 2026-10-09

The owner superseded the raw-ACT-only stop condition. The active proof uses rendered RO player motion; exact ACT delays and original layer/socket coordinates are not claimed.

Public ragassets output at https://assets.latam-tools.com.br/image was decoded as APNG for Stand, Walk, selected sword Attack and Ready in all eight direction indices. `tools/acquire_ro1_render_reference.py` reproduces the private research boards. `rendered-reference.json` commits URLs, hashes, frame counts and observed renderer delays without copyrighted frame pixels. The ignored board is `authoring/characters/private-ro-reference/RO_REFERENCE/`.

The pinned roBrowser WeaponAction mapping selects SWORD (weapon view2) → selector1 → ATTACK2/group10 → action80+direction for Swordman. Group40 renders unarmed punching,88 renders a thrust,96 is the inspected client skill group; alternatives were inspected before selection. Group80 gives raised preparation, committed overhead/diagonal sweep and recovery intent. Some adjacent attack directions reuse rendered artwork; ASTRAEON directions are independently painted, including a repaired NW strip, with no production mirroring. Anatomical handedness is retargeted to the approved ASTRAEON right hand.

Stand with straight head has one unique pose; repeated renderer slices are not breathing keys. Idle uses that standing landmark with ASTRAEON raster breathing refinements. Walk preserves8 source phases and adds8 transitions within600ms. Attack preserves9 rendered attack landmarks plus a Ready recovery boundary, adds6 transitions and retimes the presentation to450ms. Attack contact marker is170ms. This is a downstream presentation choice, never Combat authority or an assertion of original ACT timing.

Confidence: rendered phase evidence HIGH, painted anatomical retarget/attachment calibration MEDIUM, exact ACT delays UNKNOWN. Attachment transforms are measured/retargeted on painted ASTRAEON poses, not ACT-extracted coordinates. Source motion and painted approximation require owner review.

Painted assembly ordering is an ASTRAEON INTERPRETATION, not an extracted ACT
layer list. Rear loaded frames keep the cape over the back torso throughout;
the contact/follow-through profile moves the sword across the cape for a readable
arc. East uses a side/front profile so the cape cannot hide the face. These
direction/frame profiles are data, not character-specific engine branches.
Off-center leaning scalp measurements and overlapping recovery unit conversion
were repaired after actual composite review. Original generated recovery tails
were superseded by coherent chunks returning to inspected Ready at the waist.

---

Historical format-only research below records what was unknown before rendered acquisition; its raw-ACT-only stop condition is superseded.

# RO1 motion evidence — 2026-10-08

See [reference-manifest.json](reference-manifest.json) for source URLs, pinned
revisions, inspected-source hashes and SOURCE-DERIVED / ASTRAEON INTERPRETATION /
UNKNOWN labels. Fresh research read the format documents, parser implementations,
ActEditor direction/anchor controls, zrenderer composition and ragassets sampling.
No third-party source code or sprite pixels are incorporated into production.

ACT organizes variable-length frame sequences with ordered image layers and
transforms. SPR stores the referenced image cells separately. Attachment metadata
is not a semantic skeleton: inspecting anchor 0 cannot establish right-hand or
left-foot positions without pose annotation. Parent-minus-child anchor offsets
keep separately authored parts aligned. Head-facing slices in stand/sit must be
distinguished from animation time. Accessory frame counts can differ from body.

Eight-action grouping is independently visible in ActEditor and client/render
code. S, SW, W, NW, N, NE, E, SE is the documented conventional index mapping.
Idle block 0 and Walk block 1 are candidate mappings, pending verification against
the actual job data. Sword attack variant selection is unresolved; a generic
attack block is insufficient. Pinned zrenderer labels index96 as skill while the
newer ragassets README describes the upper blocks differently. Retain the
disagreement; do not manufacture a sword technique from either label.

Draw order is layered data, including component rules outside ACT. Inspected
shield ordering changes around indices2..5; head/body IMF priority and
garment job/action/frame rules can change it further. Those implementations do
not prove one universal ordering across client versions. ASTRAEON profiles must
be authored/reviewed against the selected reference and appearance.

Timing evidence differs. Older roBrowser scales stored intervals by25ms;
Research Lab's experimental analysis reports24ms. Preserve raw intervals in
extraction and require an explicit conversion profile. Gameplay walk speed and
attack duration also influence presentation in the inspected renderer. Never
infer Swordsman delays from a PNG grid or let presentation events drive damage.

No actual Swordsman ACT/SPR was available. Frame counts, durations, phase labels,
limb/contact intent, weapon arc, garment motion and anatomical anchors stay null
in the manifest. Format/renderer documentation cannot fill these fields.

## Reference intake

Place legally obtained references in ignored `authoring/characters/private-ro-reference/`
or pass an explicit private local path. Extract numeric ACT metadata locally;
inspect body/head/weapon/offhand/garment composition beside it. Record client
version, job/body variant, weapon selection, hashes and actual action IDs.
Annotate the observed keys with direction, contact intent, limb phase and action
phase, using ASTRAEON-created guides. Only derived metadata/guides may enter Git.
Do not publish RO bitmaps, use them as production textures, or require them at
runtime. Production remains gated until that key-pose evidence is present.

## Smoothing policy

Keep each observed key's identity, sequence, pose metadata, root, attachments,
draw profile and events. Insert frames only between adjacent observed keys,
including an explicitly recorded last→first pair for loops. Allocate time inside
the original interval so key timestamps and total duration stay fixed. Do not
double duration or automatically double every frame. Interpolate attachment
transforms using linear positions/scales and shortest-angle arcs; reviewed
painted in-betweens implement the pose, contact and cloth refinements. Numeric
anchor interpolation does not prove painted choreography or prevent foot skate.

RO phases → expanded ASTRAEON phases remains unpopulated until observed source
phases exist. Contact→loading→passing or ready→anticipation→contact→recovery are
possible annotation vocabulary, not claims about this Swordsman's source keys.
Dummy fixtures use synthetic IDs and provenance; they cannot satisfy Gate0.
