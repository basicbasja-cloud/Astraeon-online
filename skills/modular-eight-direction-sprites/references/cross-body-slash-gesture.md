# Slash gesture, source checks and painted review

2026-10-13; current draftv0.25. The user rejects v24 without specifying the exact
defect in that message. Punch-like forward reach and repeated strike/follow are
our diagnosis, not a quote of the user's reason. Preserve the rejection binding.
WalkingW remains the only accepted walking bank. No current attack is accepted.

## Evidence used

- [SLYNYRD, Pixelblog56](https://www.slynyrd.com/blog/2025/5/23/pixelblog-56-top-down-character-attack-animation): the artist distinguishes across-body sword motion, brief smear, an effect-free follow-through and recovery. Its sword example has six authored exposures100/50/50/50/100/50ms,400ms. We downloaded the public tutorial GIF and decoded its actual first six exposures, rather than estimating timing from a video. The whole90-exposure container lasts22400ms and includes slower presentations: it is not90unique sword poses or a RO timing specification.
- [Saint11's source tutorials](https://github.com/saint11/Saint11Tutorials/tree/ce1393eb2c46441d917134a9fd52e15575ee10a7): `TopDownAttack1x.gif` has eleven container exposures, ten80ms and one120ms. Read the actual moving example and static phase diagrams separately. Tutorial exposure counts are not interchangeable with runtime body-key counts.
- [Academy of Historical Fencing, Six Cuts](https://swordfight.uk/the-six-cuts/): descending cuts follow a diagonal through the target and recover to guard; edge/grip alignment matters. This sabre system emphasizes wrist/finger mechanics. Our chibi source is an authored game gesture inspired by the cutting direction, not a faithful retarget of this demonstrator or a biomechanical simulation. We read the primary article and saw the cut diagram; we did not capture its embedded video frame by frame.
- [Pinned roBrowserLegacy WeaponAction](https://github.com/MrAntares/roBrowserLegacy/blob/a9d31a10880740f4a351fcfca402ea6567022926/src/DB/Jobs/WeaponAction.js): Swordman SWORD/SHORTSWORD choose1, NONE chooses0, spear chooses2. `EntityAction.js` indexes ATTACK1/2/3 and defines player blocks5/10/11. Thus prior Swordman action87 is10×8+SE7;47 is5×8+SE7. Do not guess another job's attack family from a numeric action alone.
- [Pinned EntityRender](https://github.com/MrAntares/roBrowserLegacy/blob/a9d31a10880740f4a351fcfca402ea6567022926/src/Renderer/Entity/EntityRender.js): weapon and weapon_trail are rendered separately; the source synchronizes sprite parts. This establishes separate render layers, not that every weapon SPR contains an arm/hand. We have not inspected a complete matching native armed-hand SPR in this iteration. A body-only capture cannot establish the whole armed result.

Receipts, hashes, native clocks, actual tutorial crops and the downloaded source
code are in [v25/source](../../../research/sprite-animation/cross-body-slash-v25/source/).
External tutorial pixels remain research-only; none enter our character package.

## Apply the findings before generation

1. Declare the slash family, right-hand ownership, facing/camera and exact body
   clock. Our SE cross-body study is8exposures/680ms; it is not a universal RO
   cadence. Author the pelvis/chest and both fixed-length arm chains together.
2. Use a compact shoulder windup, an intermediate cut, then a clearly different
   lower crossing finish. The elbow can bend in the intermediate pose and open
   into follow-through. Do not replace a sword sweep with a forward punch, or
   assume every real cutting technique needs the same arm bend.
3. Reopen the saved rig. Check actual source soles, fixed segment lengths,
   right palm mesh/hilt attachment and projected guide poses. A correct socket
   does not establish finger wrap, wrist edge alignment or pleasing acting.
4. Render a sword/grip conditioning guide, even when the final depiction omits
   the steel blade. Use a whole-sheet image edit with shared scale and the same
   source camera. Appearance references do not become approved motion seeds.
5. Inspect the new artwork independently. Annotate visible glove, cuff and armor
   contours against an enlarged coordinate review, with uncertainty. These are
   not observed internal shoulder/elbow/wrist joints. Do not copy source bone
   matrices into a painted-hand observation and call it verified.
6. Compare the cut→follow palm displacement and its direction with the source.
   For this declared source/camera only, the provisional minimum is16px after
   subtracting both4px annotation uncertainties. It catches v24's6.71px and
   v25attempt2's16.97px repeated-looking poses. Do not relax the threshold to
   pass those images. v25attempt3 gives86.98px; that does not prove anatomy.
7. Keep one calibrated boot out of validation. Check the other boot independently
   inXandY. A lowest-alpha surface point can change with foot shape; it is not a
   tracked heel vertex or physical stance proof. Keep warnings even ifYimproves.
8. Bind the tail to the same pose clock and the currently painted hand. Its
   leading face must reach the hand, its tip follows the declared virtual blade
   path, and it clears before recovery/cancellation. The virtual guide is authored,
   not recovered painted3D. Smear can indicate fast motion; it cannot correct
   failed body mechanics, a wrong hand or ambiguous grip/guard.

## Reusable checks and present limits

`scripts/slash-gesture.py` validates bound pixels, observed foreground support,
cut/follow separation, camera-specific crossing progress, source direction,
source facing-local wrist crossing, held-out boot variation and known rejection
history. It does not automatically detect a semantic left/right swap or evaluate
finger anatomy. The new registry covers v24 only; earlier rejections remain in
their existing receipts/constraints. A changed label cannot erase those registered
v24pixels. New bytes begin unreviewed.

The v25attempt3 gesture diagnostics improve, but held-out bootX16.32px/Y2.97px
exceed the provisional4px/2px diagnostics, and the generated grip/guard is still
ambiguous. Its report remains REJECTED_OR_INCOMPLETE, production_pass=false.
The painted actor is flat; only the procedural FX is separate. Source modular
geometry does not imply complete painted hair/clothing/equipment replacement.
Do not install this candidate as the factory's accepted seed.

Future characters must supply their own source rig/camera, physical limb owners,
style reference, clocks, grip family, contour observations and rejection history.
Calibrate budgets to those inputs and retain a known failed control. Reading this
guide does not permanently train a model or guarantee error-free generation.

The standalone audit returns diagnostic output even for incomplete art; use
`--require-production` to obtain exit2 when attempting promotion. The v25release
negative test exercises that refusal against the actual current candidate.
