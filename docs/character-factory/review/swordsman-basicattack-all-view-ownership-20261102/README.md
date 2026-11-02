# Preserved male Swordsman BasicAttack: all-view ownership review

**Not an approved action, cutout set, variant or gameplay result.** All 64 native
frames (16 each in SW/NW/NE/SE) were inspected in the linked boards. This closes
the inspection scope of this diagnostic, not the production gate. The immediate
priority remains one complete tall male Swordsman, then the other five characters.

Each row shows the unchanged complete master, BodyCostume + HeadHair + the
original WeaponHandOccluder with Weapon omitted, and Weapon alone. FX are omitted
deliberately so they cannot hide boundary errors. Every panel uses its complete
512px source canvas, without translation, fitting, scaling or deformation.

## Findings

The cutouts cannot support a clean equipment toggle throughout the action.
Blade edges, detached blade pieces and/or hilt remain outside Weapon. Some of
the clearest failures retain nearly the complete blade. The role called
WeaponHandOccluder is not certified to contain only hand pixels. Empty space
created by removing a weapon over clothing also requires authored hidden
surfaces; moving visible pixels alone cannot produce those surfaces.

These are visual observations, not inferred anatomy/contact measurements.
No number of failed pixels or accepted poses is inferred from these boards.

| View / source frames | Evidence and visible issues |
| --- | --- |
| SW 000–003 | [Board](SW-00-03.png): blade-edge fragments remain when Weapon is off; grip/hilt remain with the character. |
| SW 004–007 | [Board](SW-04-07.png): detached blade tips/edges remain; 006 has a long blade strip beside the head. |
| SW 008–011 | [Board](SW-08-11.png): 009–011 retain much of the blade; the isolated Weapon is incomplete. |
| SW 012–015 | [Board](SW-12-15.png): 012–014 retain blade-edge fragments; 013 has a conspicuous straight cut beside costume. The tiny 015 Weapon does not establish a clean hilt. |
| NW 000–003 | [Board](NW-00-03.png): blade fragments remain; 003 retains most of the diagonal blade across the body. |
| NW 004–007 | [Board](NW-04-07.png): 005 opens a diagonal gap by the head; 007 leaves a detached tip. Grip/guard are not consistently separated. |
| NW 008–011 | [Board](NW-08-11.png): 008 Weapon includes a scarf-colored island while the tip stays with the body; 009–011 retain blade fragments. |
| NW 012–015 | [Board](NW-12-15.png): detached blade edges remain through recovery; 015 retains almost the whole blade. |
| NE 000–003 | [Board](NE-00-03.png): blade tips/edges remain in 000–002; 003 retains essentially the blade silhouette. |
| NE 004–007 | [Board](NE-04-07.png): detached tip/edge fragments remain at all four poses; grip/hilt ownership is incomplete. |
| NE 008–011 | [Board](NE-08-11.png): 008–010 retain blade edges; 011 retains a long blade section beside/above the head. |
| NE 012–015 | [Board](NE-12-15.png): 012 retains a long blade edge; 014–015 retain detached edges. The very small 013 Weapon needs grip/hilt review against the source pose. |
| SE 000–003 | [Board](SE-00-03.png): detached edges remain; 001 Weapon includes a hair-colored/head-shaped piece and cannot be treated as a clean sword. |
| SE 004–007 | [Board](SE-04-07.png): 004 retains the upper blade; 005 retains nearly the whole blade while Weapon is a thin sliver; 007 retains a long edge. |
| SE 008–011 | [Board](SE-08-11.png): 008 and 010 retain blade sections; 009/011 still require grip/hilt and overlap cleanup. |
| SE 012–015 | [Board](SE-12-15.png): 012 has a tiny Weapon despite a visible guard/hilt; 013–015 retain detached blade-edge pixels. |

## Playback and verification

| View | Retained preview timing / dark | 3× slow / light |
| --- | --- | --- |
| SW | [One-shot GIF](SW-normal.gif) | [One-shot GIF](SW-slow-light.gif) |
| NW | [One-shot GIF](NW-normal.gif) | [One-shot GIF](NW-slow-light.gif) |
| NE | [One-shot GIF](NE-normal.gif) | [One-shot GIF](NE-slow-light.gif) |
| SE | [One-shot GIF](SE-normal.gif) | [One-shot GIF](SE-slow-light.gif) |

The GIF files have no loop extension. They retain the old per-frame preview
timing, including its 250ms terminal hold; they do **not** show a game idle
transition or validate source/event timing. Frame labels change, so no pose is
silently merged by GIF encoding.

All 64 BodyCostume + HeadHair + Weapon compositions match their masters on
visible RGBA pixels. Adding the original hand overlay changes zero pixels in all
64 equipped compositions. This does **not** mean the overlay is semantically
correct or that a different sword would work. The protected baseline manifest
was checked separately: **896/896 file hashes match**. No original artwork,
runtime binding or `render_canonical_part_guides.py` was changed.

[Receipt](receipt.json) records the script SHA-256, all 321 input hashes,
per-frame counts and timing. A fresh rebuild was compared byte-for-byte for all
25 generated files; all match. Existing-output refusal was checked without
changing the initial output. These checks validate reproducibility/preservation,
not art quality. No gameplay test was run at this checkpoint.

```sh
python tools/character_factory_v3/review_swordsman_attack_ownership_sequence.py \
  --output /tmp/swordsman-basicattack-ownership-fresh
```

The current workspace began clean on `work` at `3f8d41c`; it did not contain the
old staged renames/unstaged renderer edits described by the historical handoff.
The production branch was fetched and checked out at `0ea0efe`. No reset or
blanket staging was used. This is a partial clone/sparse checkout to fit the
managed workspace; absent sparse files are not deleted from Git.

## Next production work and honest coverage

Repair source-accurate complete masters where necessary, then annotate actual
same-frame blade, guard, pommel and hand boundaries across the sequence. Author
newly exposed costume/skin surfaces and the concealed weapon behind the hand.
Verify each proposed separation on light/dark backgrounds, then run real
alternate-weapon and combined-slot changes for all four views before runtime
admission. Do not copy the single-frame NW proposals over the sequence.

Swordsman male still has no newly accepted full Patch 0.0.1 action set. Swordsman
female, Mage male/female and Archer male/female also remain incomplete. The
ledger remains **114 logical action instances / 96 paint jobs**, with the last
reported **2 technical imports and 0/6 completed characters** unchanged. This
checkpoint adds no accepted action, variant, package or gameplay coverage.
