# Three-class production readiness — 26 October 2026

**Storage update:** the owner subsequently authorized cleanup. Evicting obsolete guide caches recovered 6.37 GB; the immediate capacity blocker described below is resolved. See [cleanup and preservation evidence](../cleanup-20261026/README.md). The six-character production status is still incomplete.

**INCOMPLETE.** Scope remains Swordsman, Mage and Archer, male and female, all patch 0.0.1 actions. General/movement views use eight actual cameras; attacks and casting use four actual diagonals. No missing animation is substituted.

This report reads actual factory import receipts and per-pose bindings. It does not count guide captures, draft sheets, compositor checks or illustrative GIFs as finished actions.

| Class | Sex | Actions with complete imported coverage | Runtime admitted |
|---|---|---:|---|
| Swordsman | male | 1/19 | No |
| Swordsman | female | 1/19 | No |
| Mage | male | 0/18 | No |
| Mage | female | 0/18 | No |
| Archer | male | 0/20 | No |
| Archer | female | 0/20 | No |

**2/96 imported paint jobs, 0 complete admitted characters.** Both imports cover Swordsman BasicAttack. Imported coverage alone still does not approve anatomy, wrists, smoothness, timing, costume swaps or gameplay.

## Reusable work preserved

- Swordsman: protected earlier art, male/female BasicAttack imports and the long native sword trail. Other required actions still need complete imported coverage and review.
- Mage: modular 32-pose casting study and 16-pose NE walking study, separate complete heads/hand/staff, male/female heads, and 10 editable walking sheets with 160 verified cells. These studies have not been imported as complete jobs and do not complete any character.
- Archer: source contact/arm fixes and four-view attack studies exist. The retained review identifies reappearing recovery arrows, per-frame painting drift, unseparated bow/gloves/quiver in body masks, and missing hidden-surface repairs. None is admitted as a complete character action.
- The recent eight-view Mage costume generation failed camera/background review and is explicitly rejected; it is not used in any delivered atlas.

## Concrete capacity blocker for completing the scope

Measured filesystem free space: **160.4 MiB** on a **31.45 GiB** filesystem.

The current native five-image walking pose averages **438.0 KiB**. Scaling that observed output to the **12,864** missing action-pose positions gives **5.37 GiB** for the pose images alone, before raw drawing sources, editable sheets, atlases, replay scratch and Git history. This is an illustrative capacity estimate, not a lower bound: aliases, cutout reuse, class differences and future packaging affect actual size. A single small study still fits; finishing and retaining the full requested factory does not fit the current workspace.

Prior cleanup already removed this pipeline's rejected disposable scratch and shared 627 groups of byte-identical immutable guides without dropping any path or changing hashes. Most remaining usage is retained source/capture evidence and Git history. No uploaded source, canonical guide, motion or original art is deleted to force a completion claim.

**Required infrastructure:** expand this workspace from 32 GB to at least 64 GB, or attach a persistent additional volume with at least 20 GiB free for native production artifacts. No new account or paid art provider is needed. Expansion is not available through this session's tools.

## Resume order after capacity is available

1. Keep the protected Swordsman cutouts/trail unchanged and finish its missing general/skill states from the approved source motions.
2. Finish the Mage native-view costume templates with correct front/back/side anatomy, then complete the required views and actions. Reject incorrect camera drawings before layer import.
3. Repaint the Archer's omitted far bow-holding arm from the native guide; bind the bow to that hand, preserve the release hand, and remove reappearing recovery arrows before producing modular parts.
4. For all three: import only complete source-aligned cutouts, verify hair/costume swaps, package each of six characters without fallbacks, and inspect actual gameplay on the requested map.

[Machine-readable action/direction matrix](readiness.json). Reproduce using:

```sh
python tools/character_factory_v3/report_patch001_readiness.py --output /tmp/patch001-readiness-new.json
```

The remaining art work is not complete and the capacity fix alone will not complete it.
