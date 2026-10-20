# Rejected WeaponSlash pilot

`basicattack.svg` is the editable source for a direction-specific contact
effect. `basicattack.png` is its transparent 1280×1280 raster render for the
layered review tools. The user review rejected this stroke design: it crosses
the character and does not follow the sword.

- Sheet contract: eight 160px direction columns in `S, SW, W, NW, N, NE, E, SE`
  order and eight chronological frame rows.
- Only row 3 is populated, matching the contact pose in the old eight-frame
  BasicAttack pilot. The curves are not registered to the moving sword, so the
  preview overlaps the character incorrectly.
- Keep the SVG and PNG as rejected diagnostic artifacts. Do not import or use
  them in runtime. Replace them with a per-frame `WeaponLight` layer aligned to
  the blade in the new 16-frame attack guide.

The rejected preview is
`review/weapon-slash-pilot/layered-v3-basicattack-8-directions.gif`. It is
retained so the next effect design can be compared against it.
