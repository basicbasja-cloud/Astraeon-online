# Shared standard for sprite creation and review

Draft v0.16, reviewed2026-10-12. User requirement: smoother movement and one reusable standard for our sprite work. This is an executable review baseline, not certification that arbitrary image generation is reliable. The currently exercised adapter is original humanoid W walking. [Actual errors, attempts and measurements](../../../research/sprite-animation/leg-ownership-v16/README.md).

## One character/action contract, several independent gates

Every character/action defines its own identity seed, rig family, camera, anatomical owners, source phases, exposures, loop/one-shot behavior, ground/root convention, replacement slots and uncertainty. Reuse the procedure; do not reuse another character's palette, landmarks, garment-based side labels or thresholds.

| Stage | Mandatory evidence | What it must never substitute for |
| --- | --- | --- |
| Source and pose plan | Actual rig/camera/bone parents and exact timestamps; fractional times retained | An artistically accepted source or correct paintover |
| Anatomy and occlusion | Paired pelvis→thigh→knee→ankle paths, near/far interruptions, image-bound rejection history | A moved cloth, colored guide, correct foot position or hidden-joint guess |
| Temporal continuity | Same visible surface, actual exposure times, character volume, every adjacent pair and applicable loop seam | Stable head alone or increased frame count |
| Contacts | Action-specific source surfaces/intervals; independently observed painted heel/toe or grip; traveled playback | Height candidate alone, support/weight or locked world contact |
| Parts | Complete hidden coverage, invariant owner/slot, common pose clock, real swaps | A flattened attractive sheet |
| Files/runtime | Decoded counts/delays/alpha, canvas/anchors, trim metadata and actual playback | Naturalness or anatomy approval |
| Acceptance | Exact reviewed new pixels, unresolved cases and bounded scope | A green CLI exit or inherited approval from an older image |

For attacks add wrist→palm→hilt ownership, blade path, stance/released-foot behavior and phase-controlled FX. For turning recalculate view depth; never mirror the asymmetric hero. For another rig family, export a fresh source contract. These action-specific adapters are requirements, not executed validations in this iteration.

## Executable shared review

`scripts/sprite-review-gate.py` preserves source fractional phases and camera-space hip side while binding actual artwork and user rejection receipts. A shown three-frame sequence is rejected as a group; this does not fabricate a separately observed hidden joint error in every member. Copying/relabeling the same rejected pixels cannot clear it. Different bytes start unreviewed, with no inherited positive acceptance. This is review-state enforcement, **not an automatic semantic classifier**.

`scripts/sprite-standard.py` recomputes anatomy/rejection, continuity and optional floor stages from SHA-bound original observation inputs. It refuses stages referring to different frame banks/order and mismatched loop modes. Floor/surface measurements cannot override known rejection. Unknown roots, owner chains, contacts and complete parts stay blockers. There is currently no positive complete-part/accepted-clip adapter in this new combined checker, so production remains blocked even if a metric improves.

```bash
# Diagnostic report; an ordinary successful exit means the report was computed.
PYTHONPATH=/tmp/astraeon-vision-deps python \
  skills/modular-eight-direction-sprites/scripts/sprite-standard.py \
  --contract research/sprite-animation/leg-ownership-v16/evidence/new-standard-contract.json \
  --out /tmp/sprite-report.json

# Promotion path MUST use this flag; unresolved/rejected work exits2.
PYTHONPATH=/tmp/astraeon-vision-deps python \
  skills/modular-eight-direction-sprites/scripts/sprite-standard.py \
  --contract research/sprite-animation/leg-ownership-v16/evidence/new-standard-contract.json \
  --out /tmp/sprite-report.json --require-production
```

The checker does not promote an asset or update the accepted seed. Preserve the last accepted art/research state until a new scoped review is complete. The earlier modular source pipeline remains a separate technical exercise with its own release blockers.

## Smoothness without masking anatomical errors

Establish correct phase spacing and contacts at source level before painting. Export the whole time plan; compare actual neighboring images with their corresponding source. Generate one coherent cycle from exact-phase ownership guides and a single appearance seed. A reference containing several poses may cause the generator to copy the wrong lead-leg pose: when repairing a specific phase, choose a same-phase accepted appearance reference and retain source geometry as priority. This is a useful hypothesis, not deterministic control.

Never declare smoother overall from one improved seam. In our actual16-frame redraw, hair centroid seam improves14.5→7.3px while worst internal step worsens15.8→21.1px. Both8→9 and12→13 exceed the provisional20px surface budget. That drawing is not promoted. This metric is a palette-region proxy, not recovered Head motion or a leg-swap detector. Do not raise the threshold, fit each frame, freeze the head or slow playback to manufacture a pass.

Compare equal-duration clips to isolate drawing changes. Keep native source timing visible. Lower speed can reduce perceived jerk but does not repair geometry or step discontinuities. GIF10ms delay quantization needs cumulative boundary rounding; keep APNG/WebP and a precise browser clock for review. No universal Ragnarok FPS/frame-count rule follows from this experiment.

### Loops versus one-shot actions

`walk-continuity.py` now accepts `loop:false` and CLI `--non-looping` for bounded excerpts/one-shot actions. It measures onlyN−1forward edges, interior second differences and no last→first seam. Existing loop contracts defaulttrue and keep allNedges including the seam. Do not wrap a four-pose middle-of-walk repair back to its beginning and judge that jump as a full walk. `pack-motion-grid.py --non-looping` now exports one-play APNG/WebP and a GIF without a loop extension. Our first short-attempt previews were corrected to play once, with the mistakenly looping GIFs archived as failure evidence; the unchanged four masters are not a seamless cycle.

### Exact format cadence

The actual600ms/16 GIF decodes to30/40ms exposures while its nominal interval is37.5ms: exposure range/mean is26.7%. This is file-clock irregularity, not a measured percentage of perceived jerk. `animation-cadence.py` decodes real files and reports those values. Nonuniform artist-authored holds can be intentional and must not be treated automatically as defects.

`export-uniform-review.py` re-exposes the unchanged sixteen masters at50ms each on all three formats:800ms total, zero exposure variation. This is a20FPS review test and changes speed relative to the600ms control; it does not establish a universal sprite FPS. The600ms equal-duration drawing comparison and1333ms native-source view remain available. APNG/WebP alpha and visibleRGBA are verified against the same masters. Timing cannot repair the remaining owner/volume/contact defects or establish game-speed foot-lock.

## Fresh research and what is actually applied

[AniDoc's official CVPR2025 code/README](https://github.com/robbyant-research/AniDoc) separates an input sketch sequence from a character reference, with video-based generation rather than unrelated still images. Its documented default is14frames and the authors describe adjustments for other lengths; inference is reported to need about14GBVRAM. **Our inference, sixteen-frame adaptation and commercial checkpoint terms are not tested here.** We apply the architectural lesson to our standard: approve/control temporal geometry before color/identity refinement. A colored skeleton guide fed to still-image generation is not equivalent to executing AniDoc's sequence model.

[ToonCrafter's official project](https://ttwong12.github.io/papers/tooncrafter/tooncrafter.html) shows sketch-controlled interpolation, but also publishes semantic and appearance/disappearance failures. This supports inspecting occlusion and role identity after interpolation instead of trusting a smooth-looking video. No ToonCrafter inference, frame interpolation or third-party demonstration imagery is included in our character. Its site material has a separate noncommercial share-alike license, so we retain links and our own paraphrase rather than use their artwork as generation inputs.

[PhysAnimator CVPR2025 abstract](https://openaccess.thecvf.com/content/CVPR2025/html/Xie_PhysAnimator_Physics-Guided_Generative_Cartoon_Animation_CVPR_2025_paper.html) describes simulation-derived sketch guidance. Only the indexed abstract was available; direct page retrieval returned403. Do not call that a full-paper study or implemented physical simulator.

These findings motivate a future temporal line-art/part-based backend, while the current available image generator still has uncontrolled pose/layout drift. We have no executed external video backend or guaranteed error-free generation. Actual per-owner modular paint, full source-to-art correspondence, world contact and naturalness remain required before mass reproduction.
