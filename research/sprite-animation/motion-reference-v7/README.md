# Tree of Savior motion evidence — iteration 7

2026-10-11. **205 samples decoded and visually inspected**: 33 from a selected public Steam trailer interval, 45 from one official Fencer GIF, 127 from one official Murmillo GIF. These are external research pixels, never original character-package input. The user's own style remains the final art criterion; references may extend to any useful game/indie/GitHub source.

| Study | Source / samples | What is observable / what remains unknown |
|---|---|---|
| [Locomotion board](locomotion/frames-review.png) | `REFRESH! Tree of Savior`, trailer ID256661771; source PTS12.000–13.066667s; 33 samples / 1.100s full exposures | Moving scenery and actor/costume movement. Foreground pillars initially hide the actor, skirt hides leg joints; no recovered world contacts or hidden knee pose. |
| [Fencer Balestra board](fencer-balestra/frames-review.png) | [Official Rank8 article](https://treeofsavior.com/page/news/view.php?n=541), `image_9.gif`; 45 samples / 1.410s | Visible raised/changed sword/upper-body silhouette followed by a short attack obscured by effects/numbers. Not finger/hilt or exact lower-body evidence. |
| [Murmillo board1](murmillo/frames-review.png), [board2](murmillo/frames-review-02.png) | Same official article, `image_27.gif`; 127 samples / 5.160s | Early actor silhouette is clear; incoming monsters and large FX later occlude the body. Not a verified anatomical ownership/contact skeleton. |

Both Steam trailers were obtained from the author's [Steam store](https://store.steampowered.com/app/372000/Tree_of_Savior_English_Ver/) through public HLS streams in its appdetails response. One-second reconnaissance boards were inspected for shot selection; this is **not** a claim of a full-frame study of both trailers. The selected video sample and all selected GIF samples were then decoded without FPS resampling and inspected in complete review boards. Exact IDs/URLs/source hashes are in [provenance](provenance.json).

Each study records original frame ordinal, source PTS, exposure, decoded source dimensions, one fixed crop where used, frame hashes, and camera-motion declaration. Source→study coordinate conversion is recorded; no independent bbox alignment is performed. Initial Murmillo crop attempts exceeded its actual 500×250 canvas and failed without publishing output; the corrected crop is `(200,0,300,250)`. Locomotion uses `(880,330,300,360)` on the1920×1080 source. Fencer Balestra preserves its full500×281 canvas.

[All selected PNG frames + receipts/templates](all-selected-frames.zip) retain every decoded sample, including repeats. A few native samples are also visible directly in each directory. Templates are intentionally unannotated; there is **no detected or recovered skeleton** here. Unknown joints remain unknown. These sequences support motion/FX visibility decisions, but none establishes all of our anatomical production constraints.

Reproduce from local copies with `scripts/capture-reference.py` commands described in [the scripts guide](../../../skills/modular-eight-direction-sprites/scripts/README.md). For video selection: `--start-ms 12000 --end-ms 13100`, the fixed crop above, and `--camera-motion moving`. Windows select whole exposures by onset; no invented final hold or contact compensation.

For source-known bones instead, inspect the new [external rig study](../source-motion-v7/README.md). Original technical maps remain [rejected for naturalness](../conditioning-v7/README.md); adding more diagrams does not approve that acting.

Class attribution was checked against the article's inline image placement/captions: `image_9` belongs to Fencer Balestra Fente; `image_27` belongs to Murmillo's shield-skill preview. The original numeric filenames alone do not identify class/action.
