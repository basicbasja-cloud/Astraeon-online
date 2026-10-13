# Coordinated combat and readable gait

2026-10-13. The user rejects v22 attack and accepts only W walking from v21.
This supersedes surface-registration summaries as a visual acceptance signal.
The exact feedback and image hashes live in v23/evidence/user-feedback.json.

## Attack failure and source study

v22 painted six **body-only** RO keys, then rotated a single sword around a
manual palm coordinate. The first five exposures used −150°, then 40° and45°.
The drawn hand, wrist and forearm did not articulate with that prop. A correctly
located pivot, connected trail endpoint, clear terminal FX and good timestamps
do not make this a correct slash. Do not reuse this architecture for combat.

Four new complete-render requests study action47/87/95/103 with weapon2;
three additional weapon requests use1101/1201/1117 at action87. All successful
responses, hashes, dimensions and timings are retained. Visually, weapon2
shows no identifiable held blade during windup in these captures; action87
adds a large smear.1101/1201 likewise do not supply a visible complete blade
sequence.1117 visibly exposes blade pixels, including its down-right terminal
orientation, but hides most of the windup blade behind the body. These are
community renders, not recovered native client bones, an original-client
timing experiment or proof that a numeric weapon ID denotes our grip family.

The pinned [ragassets resolver](https://github.com/adsonpleal/ragassets/blob/4de4fa747431979d35c747d7edd549a872efd9e1/gateway/internal/render/resolve/resolver.go)
resolves weapon names and real view IDs, with a suffix fallback. Requested
weapon IDs are not interchangeable with a validated full motion reference.
Keep URL parameters **and actual visible pixels** in the receipt. Missing
blade/wrist points remain unknown; never fill them using a guessed rotation.

We reopened actual [Flare shortsword source](https://github.com/flareteam/flare-game/blob/af6eee6d339ac98011864bfe89da837fe7769c28/art_src/characters/hero/shortsword.blend)
with embedded script execution disabled. Its Shortsword object is parented to
MaleArm / Hand.Right. The full26-bone humanoid and actual weapon mesh are present.
The matching source descriptor declares swing position12, four100ms keys.
Frames13–16 are the one-based Blender correspondence to those zero-based
columns; this mapping is explicit, not an original-client capture.
We evaluate25actual source poses at1/8-frame intervals and render four keys
using its native unchanged camera. New neutral study materials do not alter
its motion or geometry. The source remains external research material.

| Native key | Wrist XY at512px | Projected blade angle | Hand-axis angle | Motion observation |
|---|---|---|---|---|
|13|209.82,210.41|−46.03°|−96.80°|Raised bent arm, blade up-right, rear leg lifted|
|14|183.63,241.76|−80.19°|−137.17°|Hand travels forward/down, shoulder/torso start committing|
|15|174.37,308.97|−174.51°|129.92°|Hand and blade extend down/forward, free arm counters back|
|16|201.11,336.31|107.79°|78.76°|Hand settles low, blade down-left, torso follows through|

Angles are screen-space with +Ydown, computed from actual projected weapon
vertex32 (tip), weapon-object origin and Hand.Right head/tail. The origin is a
geometric hilt reference, **not a measured palm surface**. The blade's motion
unwraps approximately −46→−80→−175→−252°, while the wrist moves about141px.
These are a W-like camera study, not RO-SE angles to paste into another view.
Across25samples, max element change in inverse(handWorld)×weaponWorld is
4.554e−7. This verifies fixed source attachment only. It does not approve our
painted grip, the source's acting, balance, floor contacts or production parts.

The [2026 Animation Mentor combat tutorial](https://www.animationmentor.com/blog/tutorial-animate-sword-fights-battle-sequences/)
was read for weapon weight, line of action, footwork, timing/spacing, contact
and wrist/elbow polish. The embedded video was not frame-captured this iteration.
Apply its planning principles before increasing frame count; do not borrow
the resistance timing of a cinematic stab for every gameplay slash.

[SLYNYRD's own eight-direction attack lesson](https://www.slynyrd.com/blog/2025/5/23/pixelblog-56-top-down-character-attack-animation)
separates anticipation, fast smear, follow-through and recovery, keeps the
same weapon hand and gives a six-key400ms sword example. Its timing is one
artist's example, not a universal RO clock. The new Flare paintover pilot has
four100ms attack keys and **no invented return-to-idle key**. Its stage ends
in follow-through; return/interrupt behavior must be authored separately.

## Reusable checks

`scripts/motion-mechanics.py` now checks actual hand-local weapon transforms,
image-bound observed palm/handle/tip/wrist/knuckle points, and projected
hand–blade orientation against a per-view source. Knuckles are not a wrist
bone head. A source bone matrix is not a painted hand observation. Art lacking
either must remain incomplete. Angular tolerances are declared diagnostics,
not accuracy percentages. Screen blade length and angle can vary through
foreshortening even when the 3D grip is rigid; no universal “blade follows
forearm angle exactly” rule is valid. The negative control rotates a weapon
inside an unchanged grip frame and is explicitly synthetic failure evidence.

## Walking failure and re-authoring contract

W is the protected appeal control. The other seven directions are rejected.
Hair registration does not measure stepping. Low body bounce plus small foot
motion can make an apparently stable bank slide. Review complete loops and
game-scale lower-body crops together with real source owner/depth passes.

Initial v20 generation used source phase4, while the rechecked comparison
bank uses phase12. This changes the half-cycle leg correspondence. Aligning
heads afterward cannot fix which anatomical leg performs a contact. A new E
pilot uses the **correct phase12 guide and uncovered owner passes from the
start**, retaining anatomical R as near and L as far. W pixels are untouched.
Do not retrospectively claim the rejected seven were drawn from that guide.

Required evidence for each view and phase:

- Both chains retain anatomical hip→thigh→knee→ankle→boot ownership. Cloth color
  and sorting feet by screen position do not establish ownership.
- Contact and swing alternate across both half-cycles. The advancing sole
  comes down into its own projected floor lane, then travels back relative to
  the root during stance; the opposite sole releases, clears and advances.
- The forward-contact keys on opposite half-cycles must show **different
  owners**. Passing poses may overlap; contour continuation, shadow/depth and
  the source owner/cutaway view must still resolve the transition.
- Front/back views need depth/occlusion evidence when projected forward travel
  is small. Near and far soles need not share a horizontal screen Yline.
- Actual runtime ground speed must match the stride. An in-place GIF alone
  cannot establish world foot-lock or no sliding in the game.

The checker compares observed lead with source phase, checks it against owned
sole geometry after subtracting source rest-lane offset, measures paired-foot
travel relative to an independent root and tests stance against each foot's
own floor lane. Merely changing R/L labels on stationary feet now fails.
Source-only positions, unknown painted owners, inferred contacts and binding
user rejection keep production blocked. Current seven failed image banks have
unknown-first templates rather than fabricated boot ownership measurements.

## Next production sequence

Validate one complete source attack and one corrected E walk at normal speed,
then annotate the new pixels and contact/swing transitions independently.
Keep source/painting/weapon clocks, shared scale and row-layout transforms
recorded. Add hand/wrist/weapon parts only after the integrated pose reads
correctly; regenerate hidden surfaces for replaceable parts instead of cutting
a flattened preview into masks. Expand to remaining walking views and diagonal
attack families only after these pilots pass visual review. A source attachment
check or a successful generation is not an accepted factory template.

## Feedback during this study: hand sweep and stance rejection

The user explicitly points out RO's hand-sweep plus sword-tail depiction,
without a continuously visible rigid sword. This agrees with the weapon2
capture's sparse blade/smear visibility. Support both depicted-weapon and
hand-tail modes. In hand-tail mode, require the correct attacking hand and
coordinated arm/body poses; do not require an on-screen tip/hilt measurement
that does not exist. Keep a hidden blade trajectory guide if useful, and author
the tail separately only during the forward strike. The new checker supports
this mode without turning absent blade pixels into invented observations.

After the four-key source test, the user rejects the body-only redraw:
“เหมือนจะล้มเลย”. Its rear leg stays suspended and torso keeps inclining over a
narrow one-foot base. Therefore **the Flare acting is not an accepted seed for
our ordinary attack**, even though its hand-local weapon attachment is valid.
Archive all three attack variants and do not add FX to hide this failure. The
new E redraw also repeats very similar half-cycle contact-looking poses and
keeps its arms forward; it is rejected by the agent before promotion. Exact
source guides and correct prompts did not guarantee the redraw's readability.

The user supplies a Witchcrafter isolated combo example. The matching-looking
[author's2021 combo post](https://imgur.com/gallery/quick-sword-combo-game-fhgjg7W)
was located, but the direct download returned429; its actual animated payload
was not acquired. Do not pretend a displayed still provides all source frames.
The author's [older2018 developer combo](https://forum.defold.com/t/witchcrafter-empire-legends/32285/12)
was acquired successfully from the public devlog:646×594,197GIFexposures,
6770ms with variable20–130ms durations. These are capture exposures, not197
distinct sprite drawings.36native decoded exposures9–44 and a12-pose comparison
board are retained; full source screenshots accompany the fixed-crop detail.

Observed older combo phases:

|Source exposure/time|Visible study observation|Limit|
|---|---|---|
|9/640ms|Broad forward smear carries first strike while torso remains compact|Beginning of this bounded selection already contains an active strike|
|12–18/760–950ms|Smear shrinks, raised arm/blade silhouette remains, torso begins settling|Grass obscures exact soles and effects hide wrist detail|
|21–30/1050–1370ms|Relatively upright recovery/ready silhouette persists|Repeated screenshot pixels may still include animated world particles|
|33/1470ms|Next strike uses a broad forward arc, lowered torso and stretched silhouette|This is a second combo move, not an extra inbetween for the first|
|36–39/1560–1670ms|Compact low follow-through changes to recovering posture|No actual skeletal rig or center-of-mass data recovered|
|42/1750ms|Character lifts back toward a readied posture|Crop can exclude tail; consult uncropped source|

The effect describes a fast committed strike; recovery and compact base
keep it readable. This is not evidence to keep one raised rear leg unchanged
through every key. Ground contacts in the screenshot are **unknown due to
grass**, not certified planted soles. The side-view reference informs gesture
and timing, not the depth/hip ownership in all eight oblique facings.

[Saint11's own quick-tip](https://www.patreon.com/saint11/posts/quick-tip-6877216)
explains how an exaggerated slash blur can imply a windup when a player needs
a responsive strike, with a longer return to sell the action. That motivates
hand-tail staging without a fully rendered blade in every exposure; it does
not excuse incorrect body balance. [GDQuest](https://www.gdquest.com/library/juicy_attack/)
likewise enables smear only on forward strike. Its freely rotating isolated
weapon example is **not our humanoid wrist/arm animation template**.

Next ordinary-slash blocking must start with a visibly stable two-foot stance,
clear hip/shoulder counterrotation, the anatomical right hand sweeping through
the target, modest torso commitment, then recovery. Rear heel/toe pivots or
steps are allowed when specifically demonstrated and reviewed; the entire rear
leg must not remain lifted by default. First validate a simple body-only pose
sequence against the chosen actual reference and a visible floor, then add
smear, hair/cape lag and interchangeable parts. Balance/acting review remains
independent of source attachment, registration and file checks.
