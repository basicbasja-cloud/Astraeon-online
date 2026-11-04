# Swordsman production factory engine checkpoint

The retained-art factory now exposes the actual nineteen patch targets for each Swordsman body, rather than only its two historical illustrated actions. The queue is generated from `factory.json`, ledger and technical import receipts. Guide PNG counts, intake status and pending visual/gameplay gates are separate. A historical sixteen-frame SkillOverhead review is explicitly not counted as the thirty-two-frame SkillAction target. Missing states have no artwork substitution.

The queue generator verifies SHA-256 for all **896 protected original Swordsman files**. Both male and female target lists contain nineteen logical actions. Their Blender guides can be inspected by action, authored direction and frame. These are source mannequins, not final character artwork. Source providers and exact guide IDs remain visible.

The illustrated viewer adds previous-frame onion skin, which does not wrap the end of a one-shot to its beginning. Source-guide stepping has explicit buttons. A browser audit can run at `/proof/character-factory.html?integrity=1`; it reassembles **128 original frame/views** from the actual PNG cutouts and compares Canvas RGBA to the original masters. All 128 match with both core layers and hand occluder order. FX are deliberately excluded from master equality because they are separate effects. Equality does not qualify semantic boundaries, hidden surfaces, grip, anatomy, blade trajectory, art naturalness or gameplay.

[Detailed pixel results](128-frame-pixel-check.json) · [browser evidence](engine-evidence.json) · [capture](engine.png) · [replay actions](engine-params.json).

## Validation

- The source queue generated successfully and checked all 896 retained-file hashes.
- Catalog indexes 1,040 existing layer/master PNGs and validates their 512px dimensions.
- Craft Anything's explicit audit URL produced 128/128 exact browser recompositions, no console/page errors or HTTP failures. A queue interaction then selected both bodies, opened the Walk NW source and stepped to frame 1/15.
- Earlier trial walkthroughs did not actually start the pixel audit: offscreen clicks were reported successful by Craft Anything despite no result. Explicit result checks caught this. The integrity button is disabled until its catalog is ready; the audit URL makes this operation directly repeatable. A slider-key command was not focusable; source stepping now has dedicated buttons. These earlier trials are not counted as passing audits.

Rebuild with:

```sh
python tools/character_factory_v3/build_review_catalog.py
python tools/character_factory_v3/build_swordsman_production_queue.py
```

Serve the repository on localhost:8769 and run the saved Craft Anything parameters with the pinned 0.3.0 CLI. `?queue=1` opens the work queue/source inspector. The underlying source PNGs and original artwork remain unchanged. Main-game loading/admission is not altered here. Coverage remains 2/96 technical imports and 0/6 completed characters; no Swordsman is declared complete by this tool checkpoint.

A separate five-step browser run verified frame 2 with the previous-frame overlay enabled: [capture](onion.png), [evidence](onion-evidence.json), [actions](onion-params.json). This overlay is a review aid, not an altered exported master.
