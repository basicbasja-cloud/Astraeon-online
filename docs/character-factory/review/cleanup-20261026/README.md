# User-authorized unnecessary-file cleanup — 26 October 2026

The owner explicitly requested deletion of unnecessary files. Cleanup removed only superseded generated guide-frame cache and this turn's discarded draft exports. This resolves the immediate workspace capacity blocker; it does not finish the character art.

## Result

- 8,704 obsolete generated frame PNGs removed from 74 superseded guide jobs.
- Observed reclaimed space: **6.37 GB (5.93 GiB)**.
- After cleanup, approximately **6.1 GiB free**, up from about 150 MiB.
- All **48 active guide jobs / 5,568 expected images** remain present and nonempty.
- No tracked file, motion source, canonical rig, artist master, active sprite part or current atlas deleted.
- Capture manifests, source metadata and contact sheets for evicted jobs are retained. Historical frame PNGs are intentionally absent; replaying those obsolete captures may require recapture. The former guide deduplication report is a historical snapshot, not a claim that these later-evicted cache paths still exist.

## Selection and safeguards

Active ledger and paint-job guide IDs are protected, as are IDs referenced by retained research/import/cutout metadata and tracked consumers. Superseded planning-only files and cache inventories do not keep obsolete image caches active. Only untracked numeric PNGs directly inside actual camera folders of verified superseded guide jobs qualify. Nested paint references, symlinks, diagnostics and non-image files are excluded. Every candidate is hashed and the entire plan revalidated before any deletion; metadata hashes are checked afterward.

The first cleanup plan failed a path-depth guard before deleting anything; the corrected final plan explicitly excludes nested paint references. Failed unused plans and the rejected local rig draft exports were removed separately with their hashes retained.

## Evidence

- [Exact deleted-path and SHA-256 inventory](superseded-guide-plan-v3.json)
- [Measured deletion result](superseded-guide-result.json)
- [Active guide preservation](active-guide-preservation.json)
- [Discarded local draft hashes](discarded-local-drafts.json)
- [Updated six-character readiness/capacity](readiness-after-cleanup.json)

Production remains 2/96 imported jobs, zero complete newly admitted characters. The existing Mage walking GIFs and part sheets are unchanged. Work can resume within the recovered space, using current guide jobs rather than regenerating obsolete caches.
