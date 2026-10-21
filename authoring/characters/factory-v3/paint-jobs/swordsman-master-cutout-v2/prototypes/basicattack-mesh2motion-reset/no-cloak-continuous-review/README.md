# No-cloak continuous animation review

Owner clarified that “continue” means an animated GIF, not a continuation prompt.

- `no-cloak-attack-one-shot.gif`: 16 actual painted poses at the sampled source cadence, followed by a recovery hold.
- `no-cloak-attack-slow.gif`: same poses, 3x slower, for hand/blade/body inspection.
- `guide-vs-paint-slow.gif`: source mannequin and painted animation side by side.
- `paint-contact.png`: chronological contact sheet.

All GIFs contain 16 frames and intentionally omit the loop extension: the native neutral recovery differs from the initial raised guard. They do not force an artificial last-to-first motion. No duplicates, painted-image crossfades, motion interpolation, whole-body warping or independent figure bbox scaling are used.

## Production and extraction

Generated all 16 poses in one sheet, using the canonical SE guide and the no-cloak guard identity study. This seed remains unapproved production art. A second image edit removed red matte artifacts onto white; both original output sheets and exact prompts are retained. `assembly-audit.json` records their hashes, matte extraction, frame timing and layout.

The generated sheet did not respect equal row heights: a naive 4x4 crop split boots and blades across rows. The final extraction selects the 16 complete connected figures at their native pixel scale, uses common horizontal slot offsets, and applies four explicitly documented common row translations with raw baselines `[336,665,953,1229]` to output baseline 432. This corrects sheet packing for review; it is not proof of source-root registration. No figure touches the final 512px canvas edge.

## Review limits

This is an owner-review animation draft, not final art or a runtime replacement. Sixteen painted poses sample the sixty-frame source; source-matched landmarks, silhouette/size continuity, wrist anatomy and sword length/orientation remain unapproved. Frames are full-character composites, not interchangeable outfit layers. No sword trail is added before the painted blade path passes review.
