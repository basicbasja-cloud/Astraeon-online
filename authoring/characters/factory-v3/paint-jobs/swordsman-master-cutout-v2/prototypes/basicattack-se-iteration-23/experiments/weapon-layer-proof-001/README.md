# Separate weapon layer proof

## Result

**Weapon cutout and transform proof only; not approved for runtime.**

Three body-only poses (source frames 498.5, 499, and 499.5) were normalized to the shared 1280px canvas. One high-detail standalone sword image is rotated to the Rokoko wrist-to-palm axis and layered under a small patch of the painted glove. The sword is kept as a separate transparent `Weapon` layer. A painted-fist annotation replaces the projected guide palm as the grip pivot because the generated artwork's fist does not land exactly on the projected guide hand.

The first guide-palm placement put the blade through the character's head. The painted-fist version connects the hilt to the glove, and its measured rendered blade axes match the guide axes for this three-frame pilot. The full character pose still misses the guide, especially around the strike, and the frame count is too small for smooth playback. There is no `WeaponLight` trail, no cape cutout, no other directions, and no runtime package.

## Evidence

- [Three-frame one-shot GIF](assembly-stable-canvas-001/review/weapon-layer-one-shot.gif)
- [Character, weapon, and composite contact sheet](assembly-stable-canvas-001/review/composite-contact.png)
- [Weapon layer contact sheet](assembly-stable-canvas-001/review/weapon-layer-contact.png)
- [Axis, grip, and frame audit](assembly-stable-canvas-001/review/weapon-layer-audit.json)
- [Hand grip annotations](painted-grips.json)

## Gate status

| Check | Result |
|---|---|
| Sword is independently editable | **PASS** |
| Painted fist visible over sword grip | **PASS for this pilot** |
| Sword direction follows the guide axis | **PASS for 3 sampled frames** |
| Full body pose follows the guide | **FAIL** |
| Full attack timing and continuity | **PENDING** |
| Separate frame-matched `WeaponLight` | **PENDING** |
| Runtime or owner approval | **NOT APPROVED** |
