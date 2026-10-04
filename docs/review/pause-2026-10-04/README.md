# User-requested pause — 2026-10-04

Read `../../../CURRENT_HANDOFF.md` first. `summary.json` records saved source64, boot63/service-worker62 mismatch, stale63 ground bake, current hashes and scoped checks. Town and locomotion are unaccepted. No64 gameplay review was done.

Three PNGs and `views-source63.json` are actual source63 gameplay views, not64 proof. Logs preserve market/patrol/corner/ground/test work63 and flora/corner64. `previous-handoff-history.md` is superseded history, not current instructions.

## Restore raw animation captures

`archives/manifest.json` records13 independent ZIPs with SHA256, byte size and file count: four parts each for Warrior/Mage/Ranger60 and one transitions61. Each ZIP is valid on its own and contains a subset of paths. Extract **all parts into the same destination**, preserving directories. Do not concatenate ZIP files.

The extracted root contains `locomotion60-warrior/`, `locomotion60-mage/`, `locomotion60-ranger/` and `locomotion61-transitions/`. Copy `locomotion-dashboard.html` alongside those folders. Serve that root on loopback8012 and open `/locomotion-dashboard.html`. Relative paths expect the folders beside the HTML. Normal/quarter-speed GIFs, actual crops, raw videos, timelines and reports are retained. This is the rejected diagnostic viewer, not corrected character art.

`../locomotion-v61/` has lighter summaries and nine actual gameplay sheets. Held/rejected studies live under `authoring/characters/`; none are automatically production assets. Shutdown ends temporary servers. Recreate them after reboot if the user resumes.
