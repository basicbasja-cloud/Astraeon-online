# Swordsman Hit: trimmed clip and Idle transition study

**Rejected as final guide; joint-space transition needs floor correction and motion review.** The native Hit clip resets at its last source frame: SW head movement from sample 10→11 is 3.63 runtime px, larger than the preceding sample (1.62 px). This flags a candidate reset, not a standalone judgment of visual quality or gameplay timing.

Two isolated object-frozen experiments trim the native clip to source range `[0,9]` and blend its last pose into `Idle_Sword` frame 0. The 16-frame version samples 12 source poses plus four explicit joint-space transition poses; the 20-frame version has the same 12 source poses plus eight transition poses. These are Blender-evaluated poses, not repeated sprite frames. The [20-frame eight-view guide](normal.gif) and [slow review](slow.gif) use illustrative timing and repeat the one-shot solely for review.

Across eight views, the largest projected head, right-hand, and blade-tip step during the 4-pose blend was 2.50, 4.02, and 11.97 runtime px respectively; the 8-pose blend was 1.28, 2.02, and 6.02. More samples change timing, and projected movement alone does not prove smoothness or human motion.

The 20-frame transition **does not pass floor review**. In SW Blender evaluation, the lowest foot/ball-weighted skin vertices reach −18.17 mm left and −23.39 mm right relative to tentative z=0 at frame 15. These selected vertices are not yet verified anatomical contact points; negative Z nevertheless warrants 3D correction and visual review. Grip, blade thickness, body intersections, actual Idle selection, timing and gameplay remain unverified. No 2D translation was used to hide these results.

[Jobs, 16/20 manifests and contact receipt](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-hit-trim-idle-20261029/). Reproduce into fresh paths:

```sh
blender -b -t 2 --python tools/character_factory_v3/render_swordsman_hit_frozen_study.py -- --job authoring/characters/factory-v3/patch-0.0.1/research/swordsman-hit-trim-idle-20261029/job-20.json --output /tmp/hit-trim20
python tools/character_factory_v3/review_swordsman_hit_trim_idle.py --source /tmp/hit-trim20 --output /tmp/hit-trim20-review
blender -b -t 2 --python tools/character_factory_v3/render_swordsman_hit_transition_contact_study.py -- --job authoring/characters/factory-v3/patch-0.0.1/research/swordsman-hit-trim-idle-20261029/job-20-contact-sw.json --output /tmp/hit-trim20-contact
python -m unittest discover -s tests/character_factory_v3 -p test_review_swordsman_hit_trim_idle.py -v
```

Two review-tool tests passed. No source artwork, canonical guide or runtime data was changed; this is not a finished action or character.
