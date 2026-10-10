# Directional concept turnaround 01

**DEV_ONLY / TURNAROUND_REVIEW_FAILED.** The owner rejected W, NW and N for
incorrect sword direction and missing grip. See `OWNER_FEEDBACK.md`.
The parent concept is approved; the newly drawn directions are not.
Open `review.html` for canonical-order
direction cards, the approved concept comparison, and common-scale previews.

Selected sheet: `turnaround.png`. Initial `source.png` is retained: it repeated
SE and omitted SW. One correction supplied SW. The correction did not swap the
two profile cells as requested, so the manifest records their actual directions:

| Raw row | Column 1 | Column 2 | Column 3 | Column 4 |
|---|---|---|---|---|
| Top | S | SW | E | NW |
| Bottom | N | NE | W | SE |

The reviewer uses these cell coordinates to show **S, SW, W, NW, N, NE, E, SE**.
The NE sword tip extends two source pixels beyond its nominal cell into empty
space beside W. The display clipping regions include that tip and exclude its
tiny fragment from the W card, without moving either figure. The regions are
recorded in `provenance.json`. It crops only the browser display window.
Neither PNG is modified, mirrored,
repainted by code, or substituted for separate layer art.

## What is ready to judge

Eight distinct front, side and rear painted concepts derived from the approved
character. Compare hair/head size, face, shoulders, tunic, teal waist cloth,
gold cape, boots, camera elevation and sword shape across views. Rear cape
shape/trim and hidden costume surfaces are newly interpreted artwork requiring
owner review. The owner's feedback invalidates the earlier claim of plausible
sword placement: W, NW and N fail direction/grip. True skeletal handedness or
physical grip cannot be certified from a painted sheet alone.

## Limits

This is a **static directional concept review**, not final registered masters.
No exact 45-degree yaw, canonical anatomical root, matching foot planes or complete
occlusion correctness is claimed. The sheet also redraws the approved SE view;
the original concept file is unchanged and shown alongside for comparison.
Side-view sword visibility differs naturally, but the W grip is obscured and
requires checking when independent part art is made.

The artwork is a flattened composite in each cell. Independent BaseBody, Hair,
Outfit, Weapon and accessories remain unauthored. Motion coverage is zero.
Raw alpha has low-opacity residue; export cleanup and registration remain future
work. Pixel/hash checks certify file integrity only, not visual acceptance.

Common-scale game previews apply one scale to all eight fixed grid cells, with
one shared offset. There is no per-direction fitting or moving alpha-box anchor.
The 88/176 px target is nominal, and measured variation is shown. Preview placement
does not establish the physical foot root required by production.

## Owner decision

Accept the visual turnaround, or identify views/features requiring revision.
Specifically review the back cape and profile proportions against the approved
concept. This gate precedes independent source-part authoring and Walk/BasicAttack.

Prompts: `prompt.txt`, `correction-prompt.txt`. Sources and approval scope:
`provenance.json`, `../candidate-01/CONCEPT_APPROVAL.md`.
