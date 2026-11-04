# Swordsman Walk SW · whole-master paintover

**Candidate, not a finished action or playable character.** Sixteen whole painted poses are captured in one sheet from the original Mesh2Motion Walk guide and the protected original character design. The new painting restores navy/ivory cloth, silver hair, gold scarf, bronze armor and closed brown gloves relative to the rejected gold-chest draft. No body parts are independently generated or assembled.

[Native-timing GIF](normal.gif) · [Slow GIF](slow.gif) · [Whole-master browser inspector](../../../../proof/swordsman-master-review.html)

All 16 poses receive one fixed fractional-grid transform into the 768 authoring canvas: source guide crop `[420,520,1116,1216]`, destination `[210,260]`, tile size348. Native generated tiles are313.5px because the tool returned a1254px square sheet. Enlarging the canvas does not add detail. The original source sheet is preserved.

Native Walk duration is1,666.6667ms, verified directly from the source GLB's animation input bounds. Every recorded guide source sample matches that timeline at the pinned renderer's24fps. Browser playback uses104.1667ms per sampled pose; GIF centisecond rounding is distributed over the cycle, avoiding systematic speedup. This is motion playback timing; a gameplay cycle-distance and movement-speed contract still needs approval.

The inspector predecodes all16 paintings and16 guides before enabling playback. It offers source overlay, previous-frame overlay, frame stepping, backgrounds and the actual240×240 runtime raster at root `[120,172]`. It is a diagnostic page, not the game map. It leaves runtime admission unchanged.

## Open gates

- Verified painted anatomical/sole landmarks and source-relative contact error; mannequin foot bones and bounding boxes cannot certify soles.
- Full loop/pose, body-fit, wrist/grip, style and edge review. Sparse key screenshots cannot establish all of these.
- Remaining seven Walk directions, same-frame semantic cutouts, genuine variants, gameplay stride and real game transitions.
- All other Swordsman actions remain in the19-action production queue. No new cutout intake or completed character is claimed.

## Reproduce the deterministic review

```sh
python tools/character_factory_v3/review_locked_grid_master.py \
  --sheet authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-sw-color-guide-20261104/generated-sheet.png \
  --guide authoring/characters/factory-v3/patch-0.0.1/guides/4e519e1eadc69aaf28a2/manifest.json \
  --output /tmp/fresh-swordsman-walk-master-review
```

Use a fresh output. The review can be regenerated from the preserved sheet; a generative model is not claimed to reproduce the sheet bit for bit. Color-control capture has a separate proof: all16 silhouettes are identical and maximum projected landmark error is zero relative to the unchanged native guide. It does not approve clothing geometry or paint.

## Checks actually run

[Verification](verification.json): all16 master hashes reproduce from the preserved sheet with the shared transform; all896 protected baseline hashes match. GIFs decode to16 distinct frames, normal cycle1,670ms and slow/guide cycle5,000ms. The slight normal-cycle difference is centisecond quantization.

[Craft Anything Chromium evidence](browser-evidence.json) and [capture](browser.png): all16 masters/guides loaded, actual frame2 reached via two steps, source and previous-frame overlays toggled. Six scripted steps completed, no recorded console/page errors or HTTP failures. This does not approve contact geometry or gameplay.

## Follow-up correction was rejected

Fixed heel/toe sets now follow the same rest-mesh vertex IDs through all16 poses. This avoids the changing lowest-vertex identity in earlier diagnostics. [Trace](fixed-source-features.json) records selection, skinning, source/camera hashes and every world/projected coordinate. The selected points must still be associated with visible painted boot features; they do not certify contact or a clothed character fit.

Three lower-body painting proposals were inspected. A pair still altered pose/costume; a single-region paint introduced proportions/appearance and boundary differences; a whole16-pose lower crop introduced row/crop offsets. **All are rejected** and kept under `patch-0.0.1/unused/swordsman-walk-lower-rejected-20261104`. Existing factory `normalize_fixed_viewport_batch.py` and `apply_local_paint_repair.py` produced the bounded single-frame candidate:8,190 changed pixels, zero changes outside the mask. That technical scope check did not make the art acceptable. The complete SW master candidate and runtime bindings were not replaced.

[Rejected comparison](rejected-boundary-comparison.png) · [Reasons and source hashes](lower-repair-rejections.json)

Do not repeat the same sparse/diffusion or whole-crop repaint inputs. Resolve the character-fit and visible painted feature correspondence against the protected original, then make coherent whole-master corrections. None of the follow-up proposals closes an acceptance gate or adds an action.

## Factory fixes after the rejected paint proposals

- Color controls incorrectly treated `head_leaf` faces as navy cloth. The wrapper now classifies both head groups against the actual head bone;208 upper-skull faces receive the silver reference color. This is a bald pose scaffold with color hints, not actual hair geometry. The new16-frame capture preserves every alpha silhouette and projected landmark exactly (zero mismatches/error). Both wrapper versions are pinned alongside their separate captures; the earlier paint inputs are not silently replaced.
- The existing `apply_local_paint_repair.py` CLI now rejects an output that replaces an input, rejects preexisting PNG/receipt files, loads one pinned input snapshot and checks that inputs remain unchanged before publication. Fresh outputs use exclusive creation. On copied fixtures, same-input/existing-output cases are rejected, all inputs remain identical and the fresh repair matches the prior algorithm's pixels. Publication of PNG+receipt remains two writes, not a fully atomic pair. [Checks](repair-preservation-checks.json).
- The earlier remote checkpoint's100 unchanged paths match Git blob hashes; two report files advanced locally afterward and are included in the follow-up checkpoint. The local staged patch remains intact.
