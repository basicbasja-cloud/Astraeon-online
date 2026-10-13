# Video-first character motion — draft0.28

The latest user explicitly rejects v27 bent-arm/lifeless slashing and requests
fresh generated VIDEO from the character appearance, then every native frame.
For this exercise, drop the old rig/joint coordinates/sparse sheet as motion
conditioning. Appearance identity remains the reference; old motion does not.

[v28 prepared inputs and brief](../../../research/sprite-animation/video-first-slash-v28/README.md)
are not a generated video. Runway supports image-to-video according to its
returned app description but is not installed/connected. No provider job, video
asset, model/cost quote or character-motion captures exist yet. Do not invent
those or silently substitute an old sprite GIF/rig render.

1. Prepare one clear neutral identity image and sufficient frame space for blade,
   body and footwork. Use own appearance/quality only; no old attack poses or rig.
2. Direct a performance: focus/intent, loading, decisive cut, extension, step/pivot,
   full-body follow-through, absorption and composure. Avoid imposing every bone
   coordinate or frozen stance on the generator. Keep a consistent sword hand,
   character identity and requested fixed full-body camera. Review without FX.
3. Discover the connected provider's actual model/schema and cost; preserve exact
   input hashes/prompt/job/asset receipt. No API credential is requested in chat.
   A prepared JSON brief is not a submitted provider invocation.
4. Keep the original downloaded video. Capture every presented frame at original
   PTS and duration, including visually identical holds. No FPS resampling,
   per-frame bbox fitting, recentering, limb warp or fabricated inbetweens.
5. Watch full-speed and slow playback before selecting sprite keys. Examine arm
   opening, wrist/grip/blade perspective, torso/hip/foot sequence, intent and
   contact continuity. Video models can still drift/morph/switch limbs. Reject
   failed acting/pixels, not just file/clock failures, and preserve the receipt.
6. Camera requested fixed is not verified fixed. AIvideo pixels are observed
   motion proposals, not actual hidden skeletal ground truth. Mark visible
   landmarks; occluded joints and anatomical ownership stay explicit unknowns.
7. Choose sparse keys only after the clip reads as a credible attack. Then study
   part compatibility/occlusion and source-clock alignment. Captured flat video
   frames do not automatically become complete interchangeable hair/equipment.

`capture-generated-video.py` reuses the real native decoder, rejects renamed GIFs
and unknown final timing, creates contact sheets and unknown-first landmark
inputs, and always leaves motion/anatomy/production unapproved. Decoding cannot
prove what conditioning was used; use the actual generation receipt for that.
Its solid-color/unequal-PTS fixtures test clocks and duplicate holds only. They
are not a sword animation or model-quality test. Exact v27rejected pixels are
added to the existing ledger so a relabeled case cannot erase the user's rejection.
