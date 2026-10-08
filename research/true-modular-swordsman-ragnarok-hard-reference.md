# Hard reference study for ASTRAEON's modular Swordsman

Research used to guide production, not content. No Ragnarok pixels or sheets
are stored in the ASTRAEON asset tree.

## Pages inspected manually

| Resource | What was visible | Principle carried into ASTRAEON |
| --- | --- | --- |
| [Male Swordsman](https://www.spriters-resource.com/pc_computer/ragnarokonline/asset/141350/) | One flattened 801×992 PNG; eight facing families plus grouped attack, hit/fall and weapon poses. Page metadata says `Animations (0)`. | Keep body scale stable; make front, quarter, profile and back silhouettes easy to tell apart; hold a clear weapon-hand read through action poses. |
| [Female Swordsman](https://www.spriters-resource.com/pc_computer/ragnarokonline/asset/141255/) | One flattened 798×892 PNG with its own body proportions and grouped poses; `Animations (0)`. | Treat female anatomy as its own authored art; share direction names and registration semantics. |
| [Male Mage](https://www.spriters-resource.com/pc_computer/ragnarokonline/asset/141305/) | One flattened 787×894 PNG with front/side/back views and raised-arm/casting-like poses; `Animations (0)`. | A cast pose needs a distinct upper-body silhouette while the character's scale and view stay fixed. |
| [NPCs (Walking)](https://www.spriters-resource.com/pc_computer/ragnarokonline/asset/127670/) | One flattened 984×1034 PNG containing multiple short directional walk groups; `Animations (0)`. | Contact and passing poses stay recognizable at small size; front, profile and back views retain a stable ground line. |
| [NPCs (Male, Animated)](https://www.spriters-resource.com/pc_computer/ragnarokonline/asset/127669/) | One flattened 1005×2141 PNG mixing still poses with motion sequences; `Animations (0)`. | Keep motion groups organized and readable without adding frames that do not change the action. |
| [Male Novice](https://www.spriters-resource.com/pc_computer/ragnarokonline/asset/141313/) | Eight-direction character sheet reviewed for movement and small-size clarity. | A compact frame budget can communicate motion when contact/passing poses are distinct and directional timing stays consistent. |

## Hard-reference boundary

The inspected website pages provide **no component list, per-part images, named
action list, frame durations, or animation labels**. Each page displays one
flattened PNG and reports `Animations (0)`; that counter does not mean the sheet
contains no poses. It means the page exposes no indexed animation records. A
literal RO part count or action count cannot be read from these pages. I use the
requested ASTRAEON modular part contract and the repository's action schema
instead of inventing numbers for RO.

The site is still the hard standard for visual results: eight-direction
readability, consistent scale, weapon handedness, clean silhouette changes,
leg contact/passing clarity, frame economy, and attachment placement. We do
not trace RO sprites, copy exact costumes, reuse its pixels, or duplicate
one-to-one poses. ASTRAEON keeps its own silver/lavender hair, mustard cape,
bronze armor, ivory panels, teal details, painted rendering, and character
identity from the user-supplied base art.

## ASTRAEON production decisions

- Eleven editable authoring sources compile to seven runtime slots. Part
  boundaries follow the requested ASTRAEON production contract, because the
  flattened RO sheet does not expose parts.
- The existing Swordsman runtime contract defines 18 motion names. The current
  gameplay routes 16 to Swordsman states; `Sit` is supported but optional, and
  `Blink` belongs to Mage. Existing `wardrobe.js` still hard-requires all 18,
  so a class-aware load gate is needed before runtime integration.
- `Idle` uses 8 frames and `Walk` uses 16, matching the repository's current
  art contract. These counts are ASTRAEON decisions and are not claimed as RO
  frame counts.
- The gait is authored from one pose source with fixed femur/tibia lengths,
  alternating contact, loading, passing, push-off and swing. Pose quality and
  art quality remain separately reviewed.

Reference pages were viewed through the Cloud Browser and manually compared
with ASTRAEON contact sheets during authoring.
