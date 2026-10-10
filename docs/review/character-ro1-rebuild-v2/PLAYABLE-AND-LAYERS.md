# Playable controller and modular art fit — 2026-10-10

This checkpoint adds reusable playable input and an original layered South attack
fit. It is not the finished Swordsman, nor a declaration of perfect assets.

## Playable input

`character-playable-controller.js` drives Idle, Walk and BasicAttack from input.
Eight directions move at the same speed. Attack retains its initial facing and
position until its MotionTemplate duration completes; remaining elapsed time goes
to movement/idle. Appearance changes retain frame, action and both clocks. This
module is presentation-only and does not implement damage or change Combat.

`character-playable.html?motion=PATH&appearance=PATH` accepts any compatible complete
pack. Keyboard and pointer movement, attack and semantic-slot selectors are included.
Missing Walk/Attack fails explicitly; owner-rejected packs are rejected. The page
does not invent a walking animation for the neutral study or alter saved games.

Five controller tests and real browser input/swap checks use the synthetic
`assembly-debug`/`debug-blue` fixture. The screenshot named
`playable-controller-fixture.png` is synthetic engine evidence, NOT playable
Swordsman proof. Input, eight directions, attack completion, appearance-clock
preservation, focus loss and responsive layout were exercised.

## Original modular art

New source files under `authoring/characters/builds/swordsman-ro1-rebuild-v2/`:

- `south-body-attack-candidate.png`: separated body attempt, rejected for partly
  opaque exterior despite its RGBA format. Retained to document the failure.
- `south-body-attack-cutout.png`: clean-background reconstruction with head and
  weapon removed; includes body-owned gloves. The background-removal generation
  changed scale/placement. It is NOT a pixel-preserving extraction.
- `south-weapon-pose-candidate.png`: six independently drawn sword poses with
  handles reconstructed and no body/hands, not a single rotated sword sprite.
- `south-layer-fit.json`: explicit neck, hand, weapon grip, phase ordering, scales,
  source rectangles and draft finger foreground masks. Head+Hair uses the fresh
  complete head resource already generated for the neutral study.

Built-in image generation was used. Body prompt: reconstruct dressed torso/arms/
hands/legs/boots from the original South study, remove complete head/hair and all
weapon pixels, preserve identity/poses/grid, leave an attachable neck. A cleanup
pass removed pommels and hilt fragments wrongly left in gloves. A background
removal pass produced the selected cutout but changed geometry/registration.
Weapon prompt: six original silver/gold swords matching phase angles with complete
handles, remove all character pixels, transparent exterior. Reference inputs were
the original art study and private RO1 South body-motion capture for topology and
anatomy. No RO pixels are included in these exported resources.

Open:
`character-layer-fit.html?config=authoring/characters/builds/swordsman-ro1-rebuild-v2/south-layer-fit.json`.
Body, Head+Hair and weapon can be hidden independently while the clock remains
unchanged. Phase draw order is authored; the anticipation blade goes behind the
head. Finger overlap is repainted from the body resource, not from weapon art.

`tools/export_character_layer_fit.py` captures the actual browser renderer in five
modes: composite, body, head, weapon and body+weapon. It exports exact-clock normal
and half-speed APNGs and six-pose boards under `south-layer-fit/` beside this file.

## Remaining failures

This is still South-only partial authoring data. Source feet move, the return arc
is incomplete, and the regenerated body's glossy shading/proportions diverge from
the earlier compact painted reference. The head pose is held across the phases;
it still needs appropriate attack tilt/compression. Draft grip and finger masks
require pixel-level visual review. No master approval has been recorded.

Do not expand these defects into seven more directions or label the fixture page
as the user's playable Swordsman. Resolve this modular pose quality first, then
author the remaining directions and complete Idle/Walk before integrating the
fresh production pack into the game. Keep the reusable tools and contracts.
