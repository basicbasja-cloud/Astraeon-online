# Swordsman V3 development candidate in the game

**Historical evidence:** the small V3 development previews were retired and moved to `authoring/characters/factory-v3/unused` at the owner’s request. The old V3 preview URLs and capture commands no longer launch them. Use the original tall Swordsman as the visual baseline.

The existing player-renderer browser test now has an explicit `--allow-pending-v3` mode for `v3-painted-v2`. Its default strict mode still expects a real Run and SkillAction. The development mode records the candidate's actual pending behavior instead of hanging while waiting for an unavailable clip.

In Wayfarer Capital, Chromium checked Idle, movement in all eight directions, BasicAttack, equipment-state independence and a mobile viewport. It captured [one BasicAttack frame](basic-attack.png). When gameplay entered Run, the development renderer used Walk; [the fallback capture](run-walk-fallback.png) and [results](results.json) record this. SkillAction remains pending and was not captured. No page errors were reported. The still captures do not establish natural motion, trail timing, seamless transitions or art approval.

Reproduce by serving the repository locally and running:

```sh
python tests/swordsman_gameplay_browser.py --url http://127.0.0.1:8011 --body v3-painted-v2 --allow-pending-v3 --output /tmp/astraeon-v3-check
```

This explicitly selected development candidate is not any of the six missing patch001 runtime packages. Normal creation remains blocked by those missing packages. This check changes no runtime artwork or coverage: **0/6 newly complete characters and 2/96 technical imports**. The Mage [own-frame diagnostic GIF](../patch001-mage-own-frame-head-recovery-20261028/own-frame-normal.gif) remains unapproved.
