# Corrected head/neck receiver and coherent-outfit motion validation — v36

The user identifies that v35's head does not meet the neck. The old declared pivot was not the painted collar opening, and the complete head texture brought its own black collar above the outfit's collar. Matching declared pivots did not prove a connected neck.

- [Actual before/after enlarged neck](neck-before-after-detail.png), [corrected neutral](neck-both.png).
- [Eight-key motion review GIF, source clock](review-source.gif), [faster game comparison](review-game.gif).
- [Interactive frame/clock/observed-edge review](motion-preview.html), [actual frame sheet](motion-contact-sheet.png), [all eight neck details](motion-neck-detail.png).
- [Original unselected eight-key GIF](raw8-source.gif), [failed repair sheet](motion-repair-raw.png).
- [Measured motion report](motion-qa.json), [browser tests](browser-qa.json), [playback decoding](playback-receipt.json), [integrity audit](audit-report.json).
- [Detailed reusable know-how and commands](KNOW-HOW.md), [generation ledger](generation-ledger.json), [manual exact-image review](visual-review.json).

The new head has a complete skin neck with no clothing. The body owns the collar; its original pixels draw in front of the inserted neck. This needs **three render passes but only two logical equipment slots**: coherent body-with-outfit and complete head/hair style. There is no individual limb resizing or requirement to equip each limb.

Motion uses the existing externally sourced CC0 KayKit `PickUp` timeline, an explicitly authored proportional guide, and genuinely new coherent body drawings. It is an unarmed crouch/reach/return; no actual prop interaction is claimed. Both feet are intended to remain planted. The review has eight logical exposures but **six distinct body drawings**, using an explicit early rest hold in place of an overshooting generated key. It is neither generated video nor an unchanged 3D retarget.

| Check | Result |
| --- | --- |
| Neutral painted neck receiver | Pass under the 2 px endpoint budget |
| Eight motion receiver endpoints / rendered bridge / collar occlusion | Pass; maximum endpoint residual 2.61 px under the declared 3 px motion budget |
| Common body transform / fixed head scale / source clock / exact raw crops | Pass |
| Raw generated recovery | Fails: 8.38 px above neutral |
| Explicit selected rest hold | Removes that overshoot; held-out normalized source-phase difference 0.216 under 0.25 |
| Selected far forefoot | **Fails:** 6.70 px native variation at display scale; 6 px after rasterization; budget stays 6 px |
| Selected near forefoot | 5.87 px native, 6 px rendered X; rendered Y range 3 px |
| Full motion / production | **Not passed**; foot shape/contact and sparse recovery still need work |

Thirteen actual-image/negative-control tests and fifteen real browser checks pass. These establish that the tools work for their stated scope; they do not convert the contact failure or hidden anatomy into approval. Reviewed collar points and forefoot bands are visible observations, not an automatic skeleton detector. New appearance, grip/hand anatomy, other hair styles/views and all-action production are unapproved.

All old v30–v35 frozen evidence and the exact thirteen protected W files remain unchanged. MiniMax remains paused; old own attack poses were not used. Four actual still-image generation jobs are retained. The first motion guide revision was overwritten before its bytes were frozen, its neutral composite was subsequently re-exported, and the head job's full original input manifest was not retained; these provenance gaps are explicit in the ledger rather than reconstructed as exact history.
