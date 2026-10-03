# Warrior run and visible-contact correction

Original ASTRAEON ImageGen sources are preserved here: the seven-direction run sheet and the separate W strip. The runtime result is `assets/warrior-run-v5.webp`. The prior walk/sprint full-body art remains in `painted-v4`; this continuation corrects their measured contacts and phase metadata.

Run `python tools/register-warrior-run-v44.py` from the checkout with Pillow, NumPy and SciPy. Registration isolates complete source bodies, applies one consistent scale, records brown boot soles and writes the complete atlas/manifest atomically. It does not repaint anatomy or attach procedural limbs. `warrior-run-contacts.jpg` is a registration inspection sheet.

Walk has continuous support and a 1.05-world-unit cycle; run has explicit passing/flight frames and a 1.8-unit cycle; sprint has a shorter support duty and a 2.3-unit cycle. Boot candidates use the lowest substantial brown component band to reject higher sword/cape tips. Per-frame flight metadata respects each direction's raised source poses rather than forcing a uniform planted schedule. Runtime support locks the painted sole in world space through a bounded whole-body translation; shadow position follows the displayed ground contact. Shared GPU textures preserve source frame detail without per-frame Canvas texture uploads.

Normal-input gameplay captures and rendered sole telemetry are necessary alongside registration tests. Contact checks do not automatically approve anatomy, costume consistency or animation appeal. Other class locomotion remains on its existing art path.

Reviewed exceptions: the W run's passing poses lift both boots; W/SW sprint tuck frames are airborne; SE sprint changes the visible support before the half-cycle. Landing after flight creates a new contact even when the atlas support tag repeats. Flight releases the old offset once over a frame interval, rather than restarting its fade on every airborne frame.
