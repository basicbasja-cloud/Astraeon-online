# One-motion test: rig correctness and painted correctness are separate

Use one motion to test the whole path before multiplying directions/items. A new original character, actual baked animation and a painted playback are more useful evidence than another source list. For this test, unarmed walking isolates gait and avoids making an unsupported weapon-grip claim. It does not replace the required future attack/grip exercise.

The [v9 walk](../../../research/sprite-animation/walk-test-v9/README.md) uses existing audited CC0 source transforms, not source mannequin geometry or rejected project art. Source root travel is retained separately, uniform lower-limb scaling preserves gait width, and every target pose uses the original rest-axis basis. Reopen the saved action at actual timestamps rather than trusting an assignment log. Keep the engine movement clock compatible with the sprite clock.

## Test surfaces, not only bone origins

Foot meshes differ from an animation library's original skeleton. A valid ankle location does not imply a modeled boot stays above the floor. Evaluate actual deformed soles/footwear at source times. This test found initial minima around -0.0261 and repaired them by solving fixed-length hip–knee–ankle chains after measured per-foot lifts. Retain the source knee bend half-plane, foot orientation, pelvis movement and reachability checks. Do not stretch a leg to make a report pass.

The reopened sole minima are about 0.001 and no checked samples penetrate the declared floor tolerance. That only proves clearance at those 41 times. Define actual stance intervals and inspect restored world-space heel/toe trajectories before claiming contact-lock or natural weight transfer. Interpolated timestamps, sparsely held sprite exposure, clothing intersection, balance, native silhouettes and perceived gait remain independent review work.

## Paint against the motion, then test the painted pixels

Keep the source registration, camera, anatomical ownership, timing and guides. Generate the complete clip sheet together in the original visual identity. This reduces independent-frame drift but cannot lock poses. Inspect actual returned dimensions, alpha, grid, head/torso attachment, wrists, knees, soles, asymmetrical items and loop transitions. A camera-facing request cannot ensure matching projections or hidden anatomy.

The first v9 paintover enlarged and moved the figures. The second improved size but shifted all four lower-row cells up 13 pixels. One measured 499-pixel row pitch fixes that sheet-layout displacement during extraction. It applies the same correction to the entire row, leaves all individual drawings intact and retains raw evidence. It is not the source rig's coordinate contract, a per-pose silhouette fit or a fix for changing anatomy. Calibration yields zero hair-top range here because generated hair tops repeat; zero can indicate a frozen head rather than correct original bob.

Keep the painted candidate visibly separate from mesh checks. Neither a rigid-bone test nor floor clearance validates new generated glove/knee drawings. Review at native size and normal/quarter speed. Reject contours, clothing ownership and pose changes that violate the desired motion. Do not smooth away intentional source motion merely to improve a drift number.

## Preserve modularity through final art

This test has complete original body and clothing geometry plus two real hair variants. Its full isolated SE layers can be swapped with recorded depth. Exact native RGB reconstruction still fails; retain it as an approximate preview until the shading/depth/alpha policy is resolved.

The whole painted sprite is not interchangeable parts. Before mass production, accept a painted base, then author complete replacement hair/clothing/equipment against its exact pose keys and hidden coverage. A mask cut from a flattened painted sprite cannot supply missing scalp, limbs, garment backs or occluded replacement geometry. Complete the supported action/view/item matrix and validate actual runtime swaps before unlocking release.
