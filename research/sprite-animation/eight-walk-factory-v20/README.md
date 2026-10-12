# Eight-direction walk and reusable motion QA — v20

ทำชุดทดลองเดิน **8ทิศ×8เฟรม =64masterframes** แล้วครับ มีภาพวาดทับใหม่7ทิศ และเก็บ W8เดิมตรงทุกพิกเซล รอบนี้9imagegen calls ให้72newdrawings:7first-facing sheets +2S/SWretry sheets. ภาพที่เลือกยังมีกรณีผิด/รอตรวจ จึง **ยังไม่ใช่ finalproduction หรืออนิเมชั่นที่ผ่านครบทุกทิศ**

Latest clarification: **“สมูทแปลว่าดูดีนะอนิเมชั่น แต่มันยังเด้งๆอยู่นิดหน่อยอันเก่าอะ”**. Record W's improved animation appeal **with residual bounce**, not jitter-free acceptance. [Bound clarification](evidence/user-bounce-clarification.json) preserves priorfeedback and exactW images.

## ดูภาพจริง

- [GIFรวม8ทิศ / uniform800ms control](eight-directions-uniform-800ms.gif) · [APNGรวม8ทิศ /600ms](eight-directions-600ms.png)
- [Motion reviewer](motion-review.html): download/open this standaloneHTML;8view playback, samephase direction switch, previous/next/scrub,600/800ms controls, RO source, actual original bones/dressed/cutaway guides, measured surface trajectory and verticalgraph. RasterCanvas, noSVG.
- Individual600ms GIFs: [S](candidates/S/walk-600ms.gif), [SE](candidates/SE/walk-600ms.gif), [E](candidates/E/walk-600ms.gif), [NE](candidates/NE/walk-600ms.gif), [N](candidates/N/walk-600ms.gif), [NW](candidates/NW/walk-600ms.gif), [W](candidates/W/walk-600ms.gif), [SW](candidates/SW/walk-600ms.gif).
- [All64art/source poses](evidence/paint-source-all-64.png) · [S/SE](evidence/review-pair-0.png) · [E/NE](evidence/review-pair-1.png) · [N/NW](evidence/review-pair-2.png) · [W/SW](evidence/review-pair-3.png)
- [Full measurements](evidence/summary.json) · [FrameCSV](evidence/temporal-measurements.csv) · [Reusable QA guide](../../../skills/modular-eight-direction-sprites/references/eight-direction-motion-qa.md) · [Next-motion research plan](NEXT-MOTION-RESEARCH.md)

## เครื่องมือตรวจพบอะไร

| Direction | Largest vertical step of measured hair-region | Verticalrange | Current status |
|---|---:|---:|---|
|S|2.87px|3.38px|REJECTED: visibleframe7 lead pattern repeatsframe3 instead of opposite referencephase |
|SE|32.08px|33.52px|Verticalwarnings; anatomy/contact review required |
|E|6.15px|6.45px|No current8pxverticalwarning; anatomy/contact still unknown |
|NE|33.41px|33.41px|Verticalwarnings; anatomy/contact review required |
|N|4.08px|5.54px|No current8pxverticalwarning; cape hides proximal evidence |
|NW|4.87px|5.64px|No current8pxverticalwarning; anatomy/contact still unknown |
|W original|16.21px|20.42px|Matches user's residualbounce observation; preserved for comparison |
|SW|21.12px|26.66px|Verticalwarnings; secondhalf phase/owners need review |

These are calibrated **surface-region measurements**, not logicalroot, naturalness scores, anatomicalaccuracy or a pass label. Budgets are provisional20pxhorizontal/8pxvertical/12pxrange on512master. The older20px total-step threshold missed W's16.2px predominantlyvertical jump. Original sourceHead at this view/phase has1.67pxmaxverticalstep/3.02pxrange; Headjoint and haircentroid are different features. Source native800ms and comparison600ms clocks remain separately labeled. No head pinning, per-frame centering, mirroring or silhouette-fitting was used to make numbers look better.

`sprite-motion-audit.py` also measures foreground opticalflow with forward/backward checks, uncertainty/occlusion masks and photometric residuals. It never writes warped pixels to masters. Low warp residual doesn't approve the pose: S can have a stablehead and computableflow but remainsREJECTED for its visiblelead pattern. Semantic leg identity requires paired proximal actual-pixel evidence; coloredcloth/forwardboot alone cannot identify the hiddenhip. Unknown root, paintedcontacts and completeparts block production.

Pixel/sourcephase issue history survives localflag relabeling. SHA/camera/sourcephase/image mismatch fails the contract. [S case/report](evidence/S-motion-report.json), [W case/report](evidence/W-motion-report.json), [issueledger](evidence/review-history.json). `--require-production` returns2 for these drafts.

## กระดูกจริงและphase correspondence

Reopened the separately approved original v17rig:67bones/170meshes. Physically rotated8views and sampled8poses, retaining sourceworld/XY joints and actual heel/toe geometry. [Corrected actualsource index](source-phase12/source-index.json) · [Source invariant check](evidence/source-invariant-check.json):64poses/128owner renders, unchangedsource files, fixed thigh/calf lengths. These original sourcechecks do not establish painted limb/contact correctness or approval of newviews.

Initial conditioning used16-key offset4. Frontal lead-foot inspection exposed a halfcycle mismatch with the RO bank. Retained that [initialsource export](source/source-index.json), then re-exported actual source withoffset12: `12,14,0,2,4,6,8,10`. Only cycle-startselection changed; no bones/poses/side labels were rewritten. This remains an approximate reviewed phase mapping, not recovered RO anatomy. Current selectedpaintings were firstattempts conditioned withoffset4 and are explicitly rechecked against the revisedreference; that does not retroactively change their generationprovenance.

S andSW got another whole-sheet edit withcorrectedguides. Sretry reverses the wrongcontact elsewhere;SWstill doesn't establish reliable oppositehalf ownership. Bothraw retries remain unapproved/rejected for this exercise in `raw/`, alongside prompts and actualfiles. We did not splice their prettiest frames into a supposedly correctedloop. Cross-view character size/placement still varies and needs originalroot/turnaround review; no individual image fitting hides it.

RO source is the existing64community-rendered poses, kept with originalframe hashes,canvas and75msexposures. It is not an officialclientrecording, exactnativeACT audit or recovered hiddenrig. Directions are explicit `S,SE,E,NE,N,NW,W,SW`; no rasterflip creates the asymmetricviews.

## Verification and reuse

[167Python regressions](evidence/regression-check.txt) include13new motionchecks: residualbounce below theoldbudget, loop/one-shot edges, wronglead despite stablehead, staleart/sourcephase, missingproximal evidence, exactissuehistory, contactunknowns and scopedflow. [16real Chromium checks](evidence/browser-report.json) verify8directions/256embeddedimage decoding,sharedphase,600/800ms boundaries,scrub,overlays,visibleblockers,play/pause andmobilelayout. [Desktop](evidence/viewer-desktop.png) · [Mobile](evidence/viewer-mobile.png). Browserused supportedinline localHTML with externalrequests blocked. This is standaloneQA, not gameintegration or measured runtimecadence.

W originals stay exact. Mastercanvas512, one raw384×512cell copied atpadding64,0; no per-frame scale/boundsfit. APNG600ms preserves8×75ms;GIF600ms hascentisecond80/70ms quantization. Uniform800ms controls use8×100ms. [Decoded clocks](evidence/decoded-format-clocks.json) preserve actualfilecounts/times. The combinedGIF800ms is a retimedreviewcontrol, not a newly selected userpreferredclock.

```bash
PYTHONPATH=/tmp/astraeon-vision-deps python \
 skills/modular-eight-direction-sprites/scripts/sprite-motion-audit.py \
 --case research/sprite-animation/eight-walk-factory-v20/evidence/W-motion-case.json \
 --out /tmp/W-motion-recheck.json --require-production

PYTHONPATH=/tmp/astraeon-vision-deps python \
 skills/modular-eight-direction-sprites/studies/walk-test/build-eight-walk.py
python skills/modular-eight-direction-sprites/studies/walk-test/build-motion-review.py
```

The currentadapter/sourcefamily is executedwalking. Different characters require their own rig/camera/partcontracts, calibratedsurfaceROI/budgets and freshactualimage review. Newmotions additionally require their event/contact/grip semantics, not copying walkthresholds. Flat64paintings do not supply complete replaceable hair/clothes/items; finalparts andmassproduction remain unresolved. See the concrete [researchstage plan](NEXT-MOTION-RESEARCH.md).

Only branch `research/modular-sprites-full-body-2026-10-11`.
