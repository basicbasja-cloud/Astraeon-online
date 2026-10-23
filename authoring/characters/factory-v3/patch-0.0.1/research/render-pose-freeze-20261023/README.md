# Adapted pose render correction — 2026-10-23

Earlier Swordsman illustrations remain the preserved visual baseline. This correction concerns source capture and does not replace those drawings.

Blender reevaluated active animation during rendering, dropping the manually adapted carry/sit pose. Viewport landmark checks alone did not catch the rendered error. The render-pre adapter freezes evaluated bone bases before drawing; the next sample still evaluates its original animation normally.

Evidence:

- Actual Blender regression: right-wrist alpha changes from 0 to 255 at pixel [220,233] with identical camera and intended world landmarks.
- 18 adapted guide jobs, 2,176 positions recaptured. All 49 current guide jobs have valid receipts.
- Maximum freeze world-matrix component error: 8.344650268554688e-7.
- PNG packaging preserves all alpha and visible RGB; only invisible RGB is cleared.
- Historical post-render wrist rotations were inconsistent with the adapted viewport. Old and new full pose metadata are **not** claimed identical.
- Mage BasicAttack already contains Enter/Shoot/Exit. An experiment adding another entry was rejected; it is not in the current ledger.
- Only four exact final-recovery mappings between CastRelease and BasicAttack were certified. Other samples differ and cannot be copied as exact source poses.

Current validation: 96 Python tests pass, including actual Blender captures. Earlier unchanged runtime checks: 146 Node checks pass. These certify technical behavior, not complete painted characters.

Painting remains draft. The SE full-strip study touches the shared viewport edge in several frames and is blocked. The older NE key study used a clipped source viewport and is rejected. The new NE `source-union-key-poses` plate uses all source poses to choose one fixed viewport, with four unclipped normalized keys; wrist/weapon alignment and temporal stability still require review. No per-frame silhouette fitting is used.

Patch completion remains incomplete: six characters and their full action sets have not been imported or verified as playable packages. Preserved Swordsman review packages are not counted as newly completed six-character production imports.
