# Guide-locked four-pose paint probe

## Result

**Identity consistency improved; exact pose fidelity remains partial. Review-only, not approved.**

Generated four full-body SE poses together from Blender guide frames 480, 493, 499, and 511, then edited the top-left guard pose to reduce its forward lean. A common generation pass keeps the hair, armor, tunic, boots, and palette more consistent than the independent 32-frame paintings. The adjacent-frame probe for 480–483 was rejected because it collapsed four slightly different guide poses into the same drawing.

The remaining four key poses are not yet an animation. Frame 480's arm/torso placement and frame 499's strike posture still miss guide landmarks. The weapon is intentionally absent, so there is no sword-axis or trail pass. Do not interpolate these four images into runtime frames or treat them as the complete action.

## Evidence

- [Normalized four-pose contact sheet](normalized/review/basicattack-se-normalized-contact.png)
- [Four-pose guide comparison](normalized/review/basicattack-se-guide-comparison.png)
- [Four-pose one-shot timing preview](normalized/review/basicattack-se-one-shot.gif)
- `source/painted-four-pose-sheet.png` is the edited sheet; `source/frames/` contains its frame cutouts.
- `source/guide-sheets/` records the exact guide panels and frame order.

## Gate status

| Check | Result |
|---|---|
| Shared character identity across one generation pass | **PARTIAL PASS** |
| Four distinct major action phases | **PASS** |
| Exact matching to each Rokoko body pose | **PARTIAL / FAIL** |
| Adjacent-frame motion | **FAIL**; 480–483 probe collapsed to one pose |
| Sword and hand alignment | **PENDING** |
| Cape as an editable layer | **PENDING** |
| Runtime or owner approval | **NOT APPROVED** |
