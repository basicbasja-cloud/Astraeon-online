# v41 — use approved pixels, action goals and visible surfaces together

## 1. Bind the approval before measuring

The user asks “ต่อเลย เอาภาพ gif ที่แอพพรูพแล้วเป็นตัวตรวจ”. The authoritative prior acceptance is frozen in [the v40 acceptance receipt](../rear-motion-v40/user-v39-acceptance.json). Decode the exact approved v39 GIFs, bind their hashes, retain their actual exposure durations and compare the corresponding logical frame. The resulting [reference inventory](approved-gif-reference.json) contains both GIFs and all sixteen decoded exposures. A first/last duplicate is still a real logical exposure with a real hold.

The new `approved-gif-compare.py` verifies the GIF hash, acceptance-receipt hash and coverage, current PNG hashes, exposure correspondence and exact encoded comparison clock. It produces side-by-side actual pixels and a sheet. Optional SHA-bound visible tracks stay in image pixels; their reversals are reported without per-axis gain fitting. Planted-surface tracks fail at the unchanged6pxbudget; missing points stay unknown. A separate current exact-image manual action review is mandatory. The code cannot authenticate a hidden shoulder or recognize anatomical hand ownership from a label alone.

Do not fit the approved front-view XY to the new rear-view XY. Compare phase, cadence, recovery and registration while also checking the current physical view. In particular, do not repeat v40's mistake of fitting independent peak amplitudes: normalized phase can look correct while the body never reaches the intended pose. New prop-contact amplitude also is not covered by the accepted unarmed GIF.

## 2. Make the interaction real in the source

The source defines world forward`(0,-1,0)`. Rear camera is physically at`(6,9,5.5)`, diagnostic side at`(9,0,5.5)`, both orthographic2.5on384×512. Anatomical right follows its bone even when its projected hand crosses the body's midline. In this rear-left view the **near free arm is LEFT** and the far picking arm is RIGHT.

Eight authored source keys have hinge degrees`[0,12,50,65,54,26,4,0]`. Hips move backward/down, knees flex and both source ankles/toes remain fixed. The head pitches down with the reach. The source uses original analytic two-bone IK; CC0PickUp informed timing only. It is not an unchanged retarget, trained system, mocap capture or reproduction of the GOAL networks.

The crystal has half-height`.075`and initial center`(0,-.85,.075)`, so its lower bound touches world ground. Its grab socket is at its top`(0,-.85,.15)`. The right palm, wrist and grip are **different points**: wrist is`.06`above palm and grip is`.05`below palm. Contact is key3/display4. Before contact the item stays fixed; afterward the item's top stays attached to the same right grip, and it is stored atkey7/display8. A previous source had a floating center/implicit palm assumption; keep its archived JSON/inputs rather than changing history.

`pickup-source-action.py`checks fourteen bounded source facts: order, lengths, fixed feet, real hip hinge/lowering, forward reach, grounded stationary object, right grip/socket contact, explicit palm/grip offset, carry attachment, free-hand separation, independent camera projection, actual image hashes and visible palm/item at contact. Primary source maximum bone-length error is about1.08e-7; maximum projection error is about.000119px. [Saved-bone replay](source-bone-replay.json) independently reopens actual animation and checks endpoints at the eight authored ticks; maxerrorabout4.36e-7. This is not force/mass balance, detailed finger fit, dense-between-key contact proof or a final skinned mesh.

The `.blend`contains animated bones plus a terminal mesh snapshot. Run the renderer to regenerate all eight actual mesh captures; changing Blender time alone does not replay those procedural mesh states. This limitation must travel with the artifact.

## 3. Use actual occlusion, then inspect the painting

Both source capture banks share all168point records/336projections and cameras exactly. The second adds visible thigh/shin/knee/boot ownership, without changing the primary frozen source. Blue is right; orange is left. These are full-scene renders, not isolated hidden limbs pasted in front of the cape. A separate visibility pass uses opaque blockers; at contact there are331visible right-palm pixels and368visible item pixels. Zero visible palm pixels at rest are an expected occlusion, not permission to invent observations.

Native1/2 still draw the near left arm picking up and a separate far fist at the hip. A label change would not repair this. Remove the wrong arm silhouettes in an **input-only** guide, overlay actual visible owner shapes, and establish one corrected deepest-key drawing. Then request the whole strip together again. The single goal edit is a repair/guide for an existing key, not independent generation of every animation frame. Its clipped cape/placement are not accepted final art.

Native3–6 qualitatively separate the high folded free hand and low picking glove more clearly. That does not establish a correctly weighted whole action. Native6 still fails real foot contours, and hidden proximal arm chains remain unobserved. Native7's stronger lower-body owner guide is a retained failure. More detailed prompt text is not a geometry constraint.

## 4. Observe the exported surface, not just a declared anchor

The v40 connected-component observer correctly abstains when boots merge. Do not weaken it until it returns a preferred result. For this fixed rear view, the new `visible-floor-surfaces.py`instead observes two **reviewed visible contour windows**: near boot's outside toe-side extremum and far boot's outside heel-side extremum. Brown-material calibration and alpha128exclude low-alpha/invisible RGB; this threshold is an observer, never pixel cleanup. The windows and measured crosses are shown in the Canvas viewer. Clipping or insufficient material abstains.

These are **screen-labelled visible surfaces**, not anatomical ankles/toes. The far heel window cannot establish the hidden foot's owner, and source knee labels cannot establish which painted calf joins which thigh. A changed surface, foreign material, rotated foot, new camera or garment occlusion needs a new observation contract and review. Never transfer these windows blindly to another character.

For native6, native-equivalent display ranges are near`[12.18,.87]`, far`[22.62,3.48]`. Independently measuring the actual common-transform raster gives near`[12,1]`, far`[23,3]`. Both must pass6px; neither does. Native7's actual raster worsens to near`[17,5]`, far`[32,8]`. Do not round away failure or reduce display scale to make a metric pass. Display transform was fixed before selecting the candidate and is common to all eight keys.

Copying stationary boot patches into an **authoring input** improved vertical registration but did not stop the generated calf/knee from moving the heel sideways. The reproduction script rebuilds six actual input plates exactly in a temporary directory. Those patched pixels are never final exported art. All retained final review frames are genuine native crops plus the single common display transform, with no shoe clone, per-frame fit or final mesh warp.

The native raw-alpha checker is separate:1/3/7fail reviewed-empty patches;2/4/5/6pass those patches. Passing a few empty patches does not establish semantic matting, complete contour safety or no cell clipping. Native6's cape/frame boundary also needs review. A transparent output can still fail motion and anatomy.

## 5. An executable review instrument

[The offline Canvas viewer](approved-gif-review.html)plays three panels on the **same approved exposure index and clock**, supports frame scrubbing,20pxgrid, source-only bone overlay and actual painted-surface windows. It does not overlay known source joints onto the drawing and call them detected image joints. Click observations are bound to the exact current PNG hash; an occluded glove exports`xy:null`. Downloaded annotations are manual proposals for further verification, not automatic approval.

Browser testing uses synthetic clicks only to test coordinate conversion/export and explicitly clears them before screenshots. They must never become anatomical ground truth. Twenty-one actual browser checks exercise the clocks, all24displayed images, overlays, scrubbing, unknown export and failure status. Twenty-eight Python negative/control checks include shifted actual boot pixels, occluded/missing material, source grip/ground/attachment corruption, approval tampering and changed image bindings. These test the instruments; their success does not turn the rejected image bank into a passing motion.

## 6. What the factory still needs

Keep the current accepted front motion as the comparison baseline. Do not multiply directions or package the rejected rear bank as a production seed. The unresolved work is a source-faithful coherent painted body with correct lower-body registration, explicit hand/object contact and no clipped contour, followed by head/body separation and a real replacement test. Production slots stay **body with outfit + complete head style**; bones and possible internal authoring pieces are not mandatory player equipment pieces.

Seven whole-strip redraws and a single goal repair show that prompt-only repainting still cannot reliably enforce this geometry. The next experiment must control pose geometry before style completion and verify the full hip/knee/ankle chain, not merely issue a longer prompt or hide bad contacts with frozen shoe pixels. An authored rig/render-to-sprite route or a constrained body-only edit with closed neck/ankle receivers needs its own exact-image proof. It is a proposed next method, **not an executed/passing result here**.

All frozen v30–v40 evidence and protected W assets remain immutable. The old own attacks are excluded, MiniMax stays paused, and this is the same sole research branch under standing push authorization. No new user-art, all-view, concept-proportion, hidden-anatomy or full-factory approval is inferred.

## 7. Size amendment — latest user steering

The user adds: “ต้องให้ทันสอดรับกับ gif เก่าด้วยนะ แบบตีวใหญ่ตัวเล็กไม่เท่ากันไม่ได้นะครับ”. Measure the exact current approved master, not an older note's rounded figure or another iteration's neutral. Actual v39rest0alpha128bounds are`[118,82,331,480]`: **399pxheight**, not v37's different408pxobservation. Its full head-render layer spans113pxhigh/127pxwide; neck-to-sole authoring calibration is300px. The complete-head asset's old`.11`scale is tied to those exact texture bytes, not a universal numeric scale for new head textures.

The first native6neutral has478pxvisible height. The earlier`.87`review produces416px,17pxlarger than the approved399px, with floor6pxlower. Its terminal neutral is438pxor more and clipped. Keep [that failed comparison](before-size-qa.json).

[The new profile](character-size-profile.json)binds approved GIF/master/acceptance and the native rest0. Pixel-coordinate span scaling is`(480−82)/(501−24)=398/477`, followed by one bank translation. It yields first-neutral399pxandground480pxexactly. That is **calibration, not independent validation**. Every other pose gets precisely the same positive uniform transform. Do not independently shrink a return frame or force a crouching silhouette to standing height.

The held-out terminal neutral now measures **at least420px**,21pxtoo tall, and the raw head touches the source-cell boundary. It is a clipped lower bound, not a recovered true body height. [The size gate](size-locked-qa.json)fails; all raw frame contours are checked too. A cropped input cannot be repaired by giving the normalized export extra empty margins. Overall height matching also cannot prove head/body proportions: that separate exact-image family/layer review remains UNKNOWN and blocks a size pass. Do not resize head and body separately to manufacture ratios.

The three-panel viewer defaults to the new one-bank size profile, with an optional **before-size** view. Actual approved GIF frames stay untouched. The 3Dsource panel has its own disclosed once-only neutral display transform to399px/480floor; its physical world/camera data are unchanged and source-only bone overlay uses that same display matrix. This is pixel review registration, not proof of an identical in-game world root across cameras. Game admission still needs an explicit actor-root contract.

After this change, inspect the actual outline rather than assume a brown-material threshold measures its dark edge consistently after resampling. The new fixed, reviewed windows use alpha128and a100pxconnected-component **observation filter**: near`[85,460,225,490]`, far`[236,440,308,488]`. They avoid the ground prop, cape and neighboring extrema in this fixed non-crossing sequence. Actual raster drift is near`[10,1]`, far`[25,3]`; native-equivalent outline ranges are about`[10.0126,.8344]`and`[24.1971,3.3375]`. Both still fail6px. The old12/23brown-material result remains a distinct historical diagnostic, not a directly interchangeable measurement. Raw stray pixels/clipped contours are retained and fail their own checks; no pixels are removed by the observer.

Thirteen additional size/outline controls prove a positive exact-reference control, legitimate crouch height, the wrong416pxneutral, the399pxcalibration/420pxheld-out failure, per-key fitting/stretch/hash/review tampering and non-mutating foreground observation. There are now **41Python controls and26browser checks**. They still do not approve the new art. This size profile belongs to this character/reference; other body families need their own approved neutral and view-aware head/body proof.


## Multi-part size amendment — 2026-10-14

The user clarified that character size includes all parts, not just total height. Matching399px is only a rest calibration. New `part-proportion-audit.py` requires18 observed dimensions: head width/height, shoulder breadth, torso length, chest/waist/pelvis widths, upper-arm/forearm lengths, arm thickness, hand width, thigh/shin lengths, leg/ankle widths, boot length/height and neck attachment. These names are requirements; a visible shoe/shaft segment is explicitly a surface proxy, never an inferred bone measurement.

Actual evidence is in [PART-SIZE-REVIEW.md](PART-SIZE-REVIEW.md), [annotated grid](part-proportion-review.png), [bound observations](part-proportion-contract.json) and [recomputed report](part-proportion-qa.json). The measurements were reviewed on actual pixels, with +/-2px per endpoint. This is an assisted measurement tool, not an automatic anatomy detector. Every missing, hidden, clipped or incompatible observation stays UNKNOWN and blocks a proportion pass.

Rear neutral0 to neutral7 uses the same view/nominal pose and one bank transform. The reviewed near shoe profile grows93.05px to113.11px, ratio1.2156: FAIL under the provisional8% same-view budget even allowing endpoint uncertainty. Reference front-view shaft35px versus rear49px is a **projected** ratio1.4, not proof of a40% anatomical error; view and foreshortening differ. Head horizontal slices are not maximum skull dimensions. Cape silhouettes cannot establish shoulder, chest, waist or pelvis width.

All ratios use the fixed399px family denominator, never a separately fitted frame height. Do not stretch limbs, fit each part, shrink return frames or reassign anatomical labels to hide growth. Cross-view validation needs a matching-view approved family reference or an independently validated projection adapter; this prototype rig has no such family-shape approval.

`character-size-audit.py` recomputes the bound part contract and refuses missing/stale/different-frame evidence. A hand-authored head/body PASS flag alone no longer clears size. Exact already-accepted masters serve only as an image-identity control. Viewer includes an18-item readout and actual endpoint overlay on approved/new images; unsupported frames/views do not inherit points.

Validation at this amendment:28source/GIF controls +13size controls +15part controls =56Python controls;31actual browser checks. A passing tool test means rejection/abstention works. New painted animation, part proportions, complete modular bank and production remain **REJECTED / UNKNOWN**, not approved.
