# Full-body attack repair study

2026-10-11. Trigger: the user rejected a 30 FPS painted attack for shaking, requested a lower RO-like rate and sword trail, then rejected a six-pose remake because the lower body stood still. The remake's planted-foot instruction was an incorrect overcorrection. This note supersedes the earlier higher-pose-rate recommendation for this attack.

## Sources actually inspected

- [Ragnarok Research Lab — animation timing](https://ragnarokresearchlab.github.io/rendering/animation-systems/) and [ACT anchors/layers](https://ragnarokresearchlab.github.io/file-formats/act/): explicit action timing, attachments, and the 24 ms experimental tick versus the historical 25 ms convention. No original-client timing experiment was reproduced here.
- [roBrowserLegacy ACT loader](https://github.com/MrAntares/roBrowserLegacy/blob/master/src/Loaders/Action.js) and [entity renderer](https://github.com/MrAntares/roBrowserLegacy/blob/master/src/Renderer/Entity/EntityRender.js): current downloaded code retains 25 ms conversion, camera-relative modulo-eight facing, separate body/head/equipment composition and explicit action-speed overrides. Comments about proprietary-client internals are claims by that implementation, not independent evidence.
- [ragassets renderer](https://github.com/adsonpleal/ragassets): a public APNG request for job 1, action 87, weapon 2 was decoded into nine frames with 100 ms delays. The image is a community render from its merged client asset tree; gender/class customization and exact original-client timing were not independently verified. First canvas-parameter requests failed with HTTP 500; default-canvas requests succeeded. Only successful images were visually studied. This study observes a lifted preparatory leg, body displacement/downward commitment, and the blade smear during the strike. No RO artwork is admitted into the new character.
- [Flare hero source](https://github.com/flareteam/flare-game/tree/af6eee6d339ac98011864bfe89da837fe7769c28/art_src/characters/hero) and [animation definition](https://github.com/flareteam/flare-game/blob/af6eee6d339ac98011864bfe89da837fe7769c28/art_src/animation_defs/characters/hero.txt): four 100 ms swing poses, eight view rows, aligned separate feet/legs/chest/hands/weapon layers. Source layers were composited for visual study, with a separate lower-body/torso comparison. This sparse example does not establish how much leg motion every new attack should have.
- [Clint Bellanger's explanation of the Flare assets](https://opengameart.org/content/isometric-hero-and-heroine): eight directions, replaceable layers, a Blender render workflow and shared 128² frame canvases. Study assets retain their own attribution/license; they are not the new character design.
- [Saint11 tutorials](https://github.com/saint11/Saint11Tutorials/tree/ce1393eb2c46441d917134a9fd52e15575ee10a7): AttackSheet.gif, Attack1x.gif and TopDownAttack.gif were downloaded and visually inspected. The top-down study demonstrates stacked body layers moving into the attack, the opposing arm/leg, one grounded foot and recovery overshoot. These are specific artist examples, not permission to mirror an asymmetric equipped character.
- [SLYNYRD eight-direction attacks](https://www.slynyrd.com/blog/2025/5/23/pixelblog-56-top-down-character-attack-animation): six poses, anatomical weapon-hand consistency, variable timing, strike smear and recovery. The sword example is 400 ms; merely adopting its pose count while freezing the body does not apply the lesson.
- [GDQuest attack effects](https://www.gdquest.com/library/juicy_attack/) and [Wesnoth weapon blur](https://wiki.wesnoth.org/How_to_create_motion_blurs): forward-swing-only effect timing, projected arcs and a collapsing residual. A separate static trail can be useful; its placement still requires visible blade-sweep inspection.
- [Animation Mentor body-mechanics breakdown](https://www.animationmentor.com/blog/animation-tips-tricks-what-makes-or-breaks-a-good-body-mechanics-shot/): anticipatory/action weight shifts and the relationship between body parts. Retrieved and studied; the AnimSchool weight article was HTTP-blocked, so it is not counted as inspected.
- [Bottoms, Greenhalgh & Sinclair, 2013](https://actabio.pwr.edu.pl/fcp/YGBUKOQtTKlQhbx08SlkTUARAUWRuHQwFDBoIVURNWHhbFVZpCFghUHcKVj0GQUw/302/public/publikacje/v15-4-2013/74.pdf), DOI 10.5277/abb130414: the full five-page fencing-lunge paper was downloaded and read. It studies fourteen club épée fencers and relates rear knee/hip and front hip kinematics to sword velocity. Its scope is a thrusting lunge; it explicitly leaves torso/arm contributions unresolved. It supports studying the legs, not prescribing exact slash angles or claiming a causal physical simulation. The kendo PubMed downloads were challenge pages and are not counted as paper reads.

## Revised procedure

1. Establish the attack's body action and active contacts, including any pivot or step, before polished character art.
2. Fix the ground root, camera and scale. Permit pelvis travel, spine/head motion and released-foot movement relative to that root.
3. Block load, coil, drive, cut, follow-through and recovery. Verify purposeful knee changes, hip travel/rotation and torso drive while hiding the weapon/effects.
4. Use the approved character design plus the original pose guide in a coherent whole-strip art pass. Previous rejected sheets are failure evidence, not animation bases.
5. Verify the drawings against the guide at native scale. Contact-marker alignment alone cannot validate anatomy, identity or acting.
6. Add a separate blade trail aligned with the projected sweep, phase-controlled by the same clock, clear during recovery/interruption.
7. Validate normal/slow playback, contact phases, loop and one-shot transitions. Distinguish export/browser tests from actual game integration.

## Original blocking proof

The new study uses eight authored keys over 800 ms, projected into eight views. It models a planted lead sole, a rear toe pivot with heel release, fixed limb lengths, moving pelvis, separate pelvis/chest rotations, counterbalancing empty arm and a rigid-length right-hand blade. It does not reuse game art.

Across 401 continuous samples, it reports zero planted toe/front-heel drift, no unreachable IK targets and numerical bone-length error below 3e-16 world units. Authored ranges are 0.32 world units of hip travel, 0.12 vertical hip motion, approximately 38° rear-knee and 29° lead-knee change, 28° pelvis rotation, 52° shoulder rotation, and 0.108 world units of rear-heel lift. The blade clears the ground. Those are diagnostic design choices, not RO measurements or proven physically correct dynamics.

These checks prevent the specific frozen-lower-body regression. The final painted sprite must independently demonstrate the movement and retain coherent identity. A successful rig or GIF decode does not mean the user has approved the artwork or that all eight painted directions and replacement parts exist.

Reproducible original study: [source and evidence](../../../../skills/modular-eight-direction-sprites/studies/full-body-attack/README.md). Source retrieval audits distinguish successful study inputs from failures. Public study images are excluded from the new-character deliverable package.

## Painted candidate v3

The new coherent art pass uses the original character design and joint guide. It visibly changes knee bend, hip position, torso rotation, counter-arm position and rear-leg extension. A blade overlapping the next figure was caught before extraction; a new whole-strip layout separated all eight figures. Body frames use the same 0.5 scale and a registered front-toe marker. They are not independently resized to their opaque bounds. The rear foot is permitted to move; it does not exactly follow the guide's planted rear-toe target.

The export has eight timeline entries, seven distinct body drawings, delays `[80,100,100,60,60,120,140,140]` ms and an 800 ms loop. Its final ready entry reuses the first RGBA image. Average timeline cadence is ten entries/second, with faster strike holds and slower recovery; this is a new design choice, not a universal RO rate. The separate sword trail is visible only in drive/cut/follow-through, with a weaker residual during follow-through.

GIF decoding verified frame count, durations and exact endpoint equality; source/export bounds checks passed. Actual Chromium playback completed normal one-shot, quarter-speed loop and interruption checks without page errors. Return-to-ready clears the trail and reproduces the same ready canvas. Browser screenshots and body-only strike were visually inspected. These checks verify this preview, not actual game integration or pleasing timing under all gameplay conditions.

Rejected by the user for apparent third-pose left-hand ownership, rejected effect and flattened parts. Only one painted facing exists. Head/clothing/weapon remain flattened together, so this is not the requested finished modular character. Fine painted-detail consistency, actual runtime contacts, all other directions, replaceable equipment coverage and gameplay transitions still need work. Neither the guide's exact contacts nor a subpixel marker-registration check proves the painted silhouette is free from jitter.

Candidate files: [attack-v3](README.md); deliverable ZIP: [character package](../../packages/silver-scarf-full-body-attack.zip). Previous 24-frame and six-frame candidates remain rejected.
