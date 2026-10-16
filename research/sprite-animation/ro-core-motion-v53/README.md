# Reusable motion source — active

New authoring only. The read-only v45 parent blend and all published old evidence remain unchanged.

`author-walk-source.py` authors an original compact walk on the saved original rig:800ms,0.32m stride,60% stance,0.06m swing lift and18° opposing arm swings. It stores65 samples and checks257 evaluated saved-rig times. Measured maximum stance sole-vertex world drift0.00014668m, floor error0.00007311m, leg-length error0.000000211m; the pose loop closes. These prove this bounded original source, never any painted image.

`render-walk-guides.py` renders8 poses through8 actual physical cameras in full and isolated leg-owner passes:128 captures. Orange is anatomicalLEFT, blueRIGHT. Isolated guides do not establish fullscene visible anatomy. An old animated pickup prop was caught in the initial walk source, despite setting its hide flag once. The failed source/captures remain under `negative-prop/`; the corrected author clears the prop action, keeps it hidden, and asserts absence at every render. Actual front owner rasters have zero unexpected interior colors, while the old sequence has1,781 unexpected pixels in total. `source/prop-absence-negative-control.json` records the control.

The first calibration mistakenly used a prior guide with a clipped prop. `negative-calibration/` preserves those display atlases. `render-neutral-calibration.py` now renders an actual clean neutral from the read-only parent; `register-walk-guides.py` verifies its unclipped body and derives one scale for every source view/phase. A guide is still an authored reference, not final art.

Three W native full-strip attempts are retained. Appearance-first ignores opposing arm action. Source-first improves arm timing but changes footwear and lower-body placement. A lower-body edit still does not reliably follow the owner guide. These images are not accepted as a completed walk or used as approved expansion seeds.

Next: author a reusable articulated2D sprite from static complete part art and an explicit neutral rest adapter. Control motion with source-derived bones, phase contacts and draw ordering; keep texture/shoe dimensions fixed in the rig. This is ordinary skeletal sprite animation from one rest asset, not frame-by-frame fitting or patching failed shoes. Internally articulated limbs can remain one selectable body+outfit group plus a complete head group. Hidden/disoccluded part art must be explicitly drawn/inpainted and reviewed; a cutout alone never proves hidden anatomy.

The overall48-clip core set remains active. Do not deliver another partial failed study as the final requested result.
