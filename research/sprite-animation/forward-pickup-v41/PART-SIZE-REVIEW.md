# Actual visible part measurements

All ratios use the same approved399px family height. These are visible surface measurements, not inferred joints or automatic semantic segmentation. Each endpoint has +/-2px uncertainty.

| Pair | Part | Ratio | Result |
| --- | --- | --- | --- |
| approved0 -> candidate0 | head_width | 0.991 | UNKNOWN |
| approved0 -> candidate0 | leg_thickness | 1.400 | UNKNOWN |
| approved0 -> candidate0 | ankle_width | 1.410 | UNKNOWN |
| approved0 -> candidate0 | boot_length | 1.838 | UNKNOWN |
| approved0 -> candidate0 | boot_height | 1.000 | UNKNOWN |
| approved0 -> candidate7 | leg_thickness | 1.486 | UNKNOWN |
| approved0 -> candidate7 | ankle_width | 1.733 | UNKNOWN |
| approved0 -> candidate7 | boot_length | 2.234 | UNKNOWN |
| approved0 -> candidate7 | boot_height | 1.154 | UNKNOWN |
| candidate0 -> candidate7 | leg_thickness | 1.061 | PASS |
| candidate0 -> candidate7 | ankle_width | 1.229 | UNKNOWN |
| candidate0 -> candidate7 | boot_length | 1.216 | FAIL |
| candidate0 -> candidate7 | boot_height | 1.154 | UNKNOWN |

Front/rear comparisons remain UNKNOWN because the views differ. A projected larger boot is a warning, not an exact anatomical error percentage. The same-view neutral boot-length comparison independently FAILS. All unmeasured/occluded head, shoulder, torso, arm, hand and leg requirements continue to block a part-proportion pass.

See part-proportion-contract.json for exact image SHA bindings, points and missing observations; part-proportion-qa.json recomputes the measurements.
