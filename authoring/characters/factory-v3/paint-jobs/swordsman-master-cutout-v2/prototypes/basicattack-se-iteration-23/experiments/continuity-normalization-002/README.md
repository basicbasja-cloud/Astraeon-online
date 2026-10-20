# Continuity normalization 002

## Result

**Registration pass; pose and character continuity still fail. Not approved for runtime.**

Re-normalized the 32 existing iteration-23 paintings against their matching Rokoko frames on a 1280×1280 canvas. The shared root is `(640,1056)`, equivalent to `(160,264)` in the 320px guide cell. The painted head-to-floor height is exactly 1.1× the matching guide measurement in every frame, and the canvas no longer forces a smaller scale on any frame.

This fixes the measurable size jump caused by frame 483 and 486 touching the old left margin and frame 498.5 touching the old lower margin. It does not repair the independently painted poses: the guide comparison still shows substantial pose mismatch in the lead-in and strike, plus changing cape silhouettes. The source image scale factors also remain wide (`0.505962–0.819327`) because the raw paintings have inconsistent dimensions. Treat this as a registration diagnostic, not a production master.

## Evidence

- [32-frame one-shot GIF](review/basicattack-se-one-shot.gif)
- [Normalized 32-frame contact sheet](review/basicattack-se-normalized-contact.png)
- [Rokoko guide comparison](review/basicattack-se-guide-comparison.png)
- [Normalization audit](review/normalization-audit.json)
- [Continuity audit](review/continuity-audit.json)

## Gate status

| Check | Result |
|---|---|
| Shared 1280px canvas and `(640,1056)` root | **PASS** |
| 32 source poses and source timing retained | **PASS** |
| Guide-relative head-to-floor ratio | **PASS**, 1.1× for all frames |
| Canvas scale limiting | **PASS**, zero frames limited |
| Painted pose follows each Rokoko pose | **FAIL** |
| Stable full-character silhouette and cape | **FAIL** |
| Separate semantic character layers | **PENDING** |
| Runtime or owner approval | **NOT APPROVED** |
