# Coherent-body motion: better contacts, failed lateral recovery — v38

The user asks to continue motion work after the concept-size comparison. This iteration keeps body-with-outfit plus a separate complete head, and repairs the existing unarmed crouch/reach/return pilot. It does not introduce an attack or change the unresolved concept proportion decision.

- [Before/after GIF at game comparison speed](before-after-game.gif), [source-clock comparison](before-after-source.gif).
- [Current candidate GIF](review-game.gif), [slower source-clock candidate](review-source.gif).
- [Actual eight-key sheet](motion-contact-sheet.png), [visible motion/contact diagnostics](motion-diagnostics.png), [neck detail](motion-neck-detail.png).
- [Interactive frame/clock reviewer](motion-preview.html), [combined decision](review-decision.json).
- [Bound neck/contact/phase report](motion-qa.json), [two-axis recovery report](spacing-qa.json), [browser checks](browser-qa.json), [integrity audit](audit-report.json).
- [Detailed know-how and reproduction](KNOW-HOW.md), [five actual generation jobs](generation-ledger.json), [explicit manual review](visual-review.json).

**Contacts improve, but the animation is not accepted.** The original limited neck/contact/vertical-phase checker now passes this candidate; the added two-axis checker catches a10.68pxleftward reversal from key6to7. It then moves20.58pxright to rest. A one-axis PASS would conceal that hitch. The reviewer, contact sheet, diagnostics and combined verdict retain the failure.

| Actual measured property | Previous v36 | Selected v38 |
| --- | --- | --- |
| Distinct body paintings / logical exposures | 6 / 8; early rest substitute | 7 / 8; genuine drawn intermediate |
| Far forefoot X, native at display scale | 6.703px, fails6px | 5.540px, passes6px |
| Far forefoot X, actual raster | 6px | 6px |
| Near forefoot X, native / raster | 5.865 / 6px | 4.749 / 5px |
| Near-sole raster Y range | 3px | 1px |
| Maximum neck endpoint residual | 2.61px | 1.20px |
| Held-out normalized vertical-phase error | .216 | .170 |
| Recovery drawing/vertical ordering | Fails: repeated rest | Passes |
| Lateral recovery | Early rest hid missing motion | **Fails:10.68pxleft reversal** |
| Combined motion / production | Not passed | **Not passed** |

This is not zero foot drift or error-free motion. All numbers cover reviewed visible forefoot/collar surfaces at this one view. Hidden hips/knees/finger identity and actual object contact are not automatically recovered. No new user-art, concept-proportion, all-view/action or production approval is inferred.

Five actual native still-image edit jobs are retained. **Only attempt2 enters the selected atlas.** The selection is raw art indices `[7,1,2,3,4,5,6,7]`: matching source rest0/7 reuse the same actual rest7; all six active drawings are distinct. There is no final-frame warping, per-frame scale/translation, copied shoe patch or early-rest replacement. All body frames use one common matrix and the head keeps v36scale`.11`.

Attempts1/4/5 contain changed packing/registration or poor recovery; attempt3 additionally contains a real translucent brown matte. Their local requests also changed unrequested visible regions. Packing hypotheses are retained as diagnostics and **not applied** to the selected assets. Diagnostic boot stencils/neutral-derived rig transforms are conditioning only, never selected artwork. Source/generation inputs and outputs are hash-bound; the prior concept attachment gap remains explicit.

Ten new real-error/negative-control tests, thirteen unchanged v36regressions and eighteen actual browser checks pass as tool evidence. The strict sequence gate still exits1 for the real lateral defect. All v30–v37frozen evidence and thirteen protected W files remain unchanged. MiniMax stays paused and old own attack motions are excluded. Work/push remains on the same sole research branch.
