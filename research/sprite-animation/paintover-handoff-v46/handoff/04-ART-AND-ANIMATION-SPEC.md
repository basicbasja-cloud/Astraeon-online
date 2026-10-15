# Reusable art and animation specification

## Character identity and shape authority

Silver/lavender tousled hair, youthful anime face, mustard scarf/cape with ivory rune, bronze shoulder/bracer armor, navy and ivory tunic, brown belt/gloves/boots, olive trousers and a teal asymmetric cloth tab on anatomical LEFT. Match accepted v39 original art, with the user's original concept as visual intent. The original historical uploaded concept bytes are unavailable locally; do not fabricate an exact hash, new image measurements or a precise concept-derived head ratio.

Accepted v39 neutral alpha>=128 foreground bounds are [118,82,331,480] inclusive: 399 px high, 214 px wide on a 384×512 cell. That is a protocol-specific family reference, not a mandate that every facing's silhouette width is 214. The full head-layer reference is 113 px high/127 px wide and includes neck. Do not compare that with a crown-to-jaw crop or reuse the old .11 head-texture scale on unrelated head images. Size checks must cover head, neck attachment, torso, upper/lower arms, hand, thighs, shins, feet, shoulder/hip widths and ratios, not height alone.

A character family may have one disclosed common scale/translation calibrated from the neutral pose. Do not independently fit frames, views, limbs or crouch heights. Fit-to-bounds destroys motion amplitude and conceals bounce/size drift. v46 intentionally applies no such fitting; report actual mismatches. Preserve narrow neck/collar attachment and actual head tilt rather than floating a separately centered face.

## Coordinates and ownership

Rig world RIGHT = negative X; LEFT = positive X; forward=(0,-1,0). Our view order is S,SE,E,NE,N,NW,W,SW. Right/left means character anatomy, never screen position. Source owner renders blue RIGHT, orange LEFT; these are independent guide pixels, not permission to recolor a swapped drawing. Projected near/far limbs change across cameras; track the chain through pelvis/shoulder and depth.

At E/W limb overlap, visible upper thigh/hip attachment, occlusion edge, cast/contact shading and trouser-to-boot continuity must tell the truth. A teal tab moving from one leg to the other does not prove leg ownership. Hidden pelvis/joints must be marked UNKNOWN until exposed in another relevant observation or redrawn, not guessed from colored masks. Check actual painted layers and contacts separately from correct rig source.

## Pickup contract used now

Eight source keys: upright; begin crouch; deep reach; lowest contact; lift; rise holding in RIGHT; nearly upright holding; returned upright with item stored/absent. Anatomical LEFT is free and relaxed. Both boots remain planted. Gem is optional equipment/event content, not a third runtime body part. Eight exposures are [190,180,190,180,190,180,190,600] ms =1900 ms. Playback loops for review, but pickup is a one-shot game action with explicit start/contact/attach/store/end events. Do not score a cyclic motion loop unless the action is intentionally looped.

Check feet against the floor, knees, hip trajectory, body balance, elbow plane, wrist and grip separately. Small source residuals must be disclosed, not described as exact zero. Same camera/clock/neutral family across views. A lower head during a true crouch is expected; unmotivated whole-character translation is not.

## Modularity and future motions

Runtime anatomy grouping is body_outfit + complete_head, with optional hair/equipment slots when deliberately supported. Internal 3D arm/leg meshes and owner masks are authoring aids. They do not require the user to equip upper arms independently. Separation requires occluded painted surfaces, shared anchors, draw-order rules and swap demonstrations at every relevant pose. A complete head includes back hair/face/ears/neck coverage as designed; never leave a hole under hair.

For sword attacks, study a new source; old own attacks are excluded. Require anticipation, grounded weight transfer, torso/shoulder lead, coherent elbow→wrist→grip, diagonal blade-plane perspective and recovery. A single flat blade rotated in screen space is insufficient. Separate body/weapon/FX clocks; during very fast swing, an authored hand sweep + sword trail can replace visible rigid blade frames where readable. Repaint weapon foreshortening/orientation per key, never approve an independent spinning prop. Source geometry describes trajectory; painted contact and acting remain separate checks.

8 vs16 frames is an exposure/design decision, not a quality score. Added interpolation can introduce leg swaps, foot slide and duplicated poses. Start with readable key poses, contact events and clock; validate adjacent velocities, silhouettes and support phases before adding in-betweens. Dense source replay does not mean equally dense finished drawings.
