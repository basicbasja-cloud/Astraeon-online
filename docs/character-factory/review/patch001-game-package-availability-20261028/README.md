# Patch 0.0.1 character packages in the real game

A read-only Chromium check loaded the normal game creation screen, selected Swordsman, Mage and Archer in turn, and observed that **Begin your journey is disabled for all three**. The six class/sex `sprite.json` paths referenced by the current patch registry returned HTTP 404. `git cat-file` also found that each path is absent from the current HEAD tree, so these six missing files are not solely a consequence of this sparse checkout. The creation UI attempted the default male package for each class; female package availability was checked by direct HTTP and Git-tree probes, not through gameplay.

[Mage creation screenshot](mage-creation.png) · [Swordsman](swordsman-creation.png) · [Archer](archer-creation.png) · [HTTP, tree and UI results](result.json)

This confirms the full patch cannot currently be played through the regular character creation flow. It does not prove anything about the quality of a sprite that has not been imported. No fallback art was substituted, and no runtime definitions changed. Completion remains **0/6 newly complete characters, 2/96 technical imports**.

Reproduce from the repository root using `python -m http.server 8011 --bind 127.0.0.1` in one terminal and `python docs/character-factory/review/patch001-game-package-availability-20261028/check.py --output /tmp/astraeon-package-probe` in another. The probe uses `/usr/bin/chromium`, Playwright and Git. The repository uses sparse checkout; the per-path tree check distinguishes unavailable working-tree files from paths that are missing in HEAD. The probe does not start gameplay, test animation, or certify visual quality.

## Separate development preview

The explicit `?swordsman=v3-painted-v2` development mode was also opened in Wayfarer Capital. The browser script captured the candidate while walking in all eight directions, including [SW in the actual scene](swordsman-development-sw-walk.png). This is a separate, unapproved Swordsman preview and does not make the six patch packages available. The existing gameplay script was interrupted after reaching its Run wait: this candidate marks Run as pending and its development renderer falls back to Walk, so the script's expectation of a current Run clip is unsuitable. Attack, skill and transitions were not validated by this interrupted run. No claim about seamless motion or grounding follows from the still images.
