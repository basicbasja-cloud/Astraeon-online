# Attack pose audit — 2026-10-10

The combined study remains unsuitable as the production master. This inspection
compares ready, contact, follow-through and recovery across the eight-direction
boards, plus the original South sheet and private RO1 South sequence. Observations
below are visual findings, not raw RO skeleton measurements.

| Direction | Observed problem | Required repair/check |
| --- | --- | --- |
| S | Boots shift up between the first and second source rows; recovery abruptly raises the sword | Preserve authored ground contact, add recovery transitions and validate return to ready |
| SW | Stance changes between ready and impact; silhouette remains close to front view | Check facing consistently through torso, face and feet; explicitly author any step |
| W | Chest/feet read three-quarter in several nominal profile frames | Establish a coherent profile camera before separating parts |
| NW | Impact sword tip appears beside the head, then at waist in follow-through while most arm is hidden | Verify the hidden right-arm trajectory and blade exit positions; do not infer correctness merely from occlusion |
| N | Ready and recovery lean differently; sword visibility changes around head/shoulder | Check stable back projection, right-hand ownership and far-side blade trajectory |
| NE | Recovery blade stays almost upright while ready blade points behind/down-left | Author the missing return arc; check feet and scale against neighboring directions |
| E | Ready shows more chest than impact; upright recovery differs substantially from ready | Stabilize facing and author the recovery-to-ready transition |
| SE | Foot placement differs between rows; recovery returns abruptly to overhead | Fix source stance and recovery while retaining right arm crossing from screen-left shoulder |

## Measured South stance

`tools/audit_character_stance.py` measures the bottom three opaque rows of each
boot inside manually selected source-cell regions. All six poses use the same
regions and the same sheet scale. No source pixels or registration are modified.
The measurement requires isolated boot regions; it cannot distinguish a boot from
another object in a badly selected region. The regions were inspected and narrowed
to the soles to exclude the down-left sword.

The diagnostic threshold is 2 runtime pixels for a proposed planted stance. This
is an ASTRAEON authoring check, not an asserted RO1 numerical standard. Intended
steps need explicitly authored contact intervals instead of this whole-sheet test.

| Source | Maximum drift from ready | Measurements above 2 px |
| --- | ---: | ---: |
| Existing South study | 16.364 px | 9 |
| New low-recovery experiment | 16.585 px | 9 |

Config: `authoring/characters/builds/swordsman-ro1-rebuild-v2/south-stance-audit.json`.
Measured results: `south-stance-audit.json` beside this document. These results
reject the new experiment as a stance repair. They do not prescribe shifting each
frame until the numbers pass; that would hide the source-art problem.

## New source-art experiment

`south-low-recovery-candidate.png` was generated with the built-in image tool using
the original South sheet and private RO1 South animation as references. Prompt:
retain character identity, six 512-square cells, South projection and right-hand
ownership; plant soles consistently; change the sixth pose to bent-elbow low
recovery after the downward follow-through. No warps or procedural body painting.

The sixth pose now has a lower sword and bent elbow, but the requested fixed stance
was not achieved. The new pose also needs subsequent frames returning to ready.
It is not an approved improvement to the entire loop and does not replace the
default study. The original source remains intact.

Comparison preview:
`character-pose-study.html?study=docs/review/character-ro1-rebuild-v2/low-recovery-study`.
Normal/half-speed APNG/GIF exports and source receipts are in `low-recovery-study/`.
The other seven directions are unchanged for comparison. Export boundary checks
pass; stance and visual checks fail. Do not equate those checks.

Next art work must establish a stable stance and a complete return arc before
promoting poses into the modular BodyWithOutfit/Head/WeaponPoseSet master. Keep the
existing 450 ms clock; assign genuinely authored intermediate poses to its existing
frames rather than hold six poses and call the recovery complete.
