# Iteration 8: early phase-registered SE sweep

**Status: review-only; motion and painted sword path rejected.** Direct 16-frame comparison finds the `Sword_Attack` guide thrust-like and the painted sword inconsistent with several guide poses. This iteration tests a separate trail layer only; it does not approve the source motion or character master.

The previous trial emitted its strongest trail at phase `0.63` (frame index 10), after the guide's overhead-to-forward sword motion. This pass starts at frame index 3 / phase `0.20`, reaches peak opacity at frame 6 / phase `0.39`, remains visible at the provisional maximum-extension frame index 8 / phase `0.50`, fades in frame 9, and clears before frame 10. The original plum-gray, lavender-silver, warm-ivory arc remains separate as `WeaponLight` and is 1.35× thicker than the initial sweep paint.

## Preview

- [SE one-shot GIF with the revised early trail](review/basicattack-se-weaponlight-one-shot.gif)
- [Guide and painted-trail side-by-side one-shot GIF](review/motion-guide-vs-painted-trail-one-shot.gif)
- [Trail-only 4×4 contact sheet](review/weaponlight-over-contact-4x4.png)
- [Transparent 16-frame trail strip](layers/WeaponLight/weaponlight-se-16.png)
- [Actual guide compared with the painted sword, all 16 SE frames](review/motion-guide-vs-painted-sword-4x4.png)
- [Frame-by-frame alignment verdict](review/motion-alignment-review.json)
- [Decoded GIF exposure timing from the research cadence auditor](review/animation-cadence-audit.json)

## Motion findings

- Pose-guide frames 3–4 move from a raised blade into a near-horizontal forward arc; the visible trail should start during that transition.
- Guide frame indices 4–8 keep the sword extended forward, then indices 9–10 rotate it toward recovery. The former phase `0.63` marker landed after this extension.
- The guide and painted sword diverge in frames 0–3 and 9–10; frames 4–8 also hold the painted blade nearly unchanged. The 3D guide reads as a thrust. Trail timing does not correct either mismatch.
- Research cadence audit decodes 16 frames and 2,530ms total playback, including the 600ms final recovery hold. The nonuniform exposure is intentional; the timing check does not establish natural motion or blade alignment.
- The 16-frame ImageGen full-sheet trial is rejected. Individually generated frames 3, 8–10 approximate selected blade directions, but frames 0–2 and 4 do not consistently follow their guide poses.

No runtime package, frame cutouts, eight-direction master, target-map preview, or owner approval exists for this trial.
