# Craft Anything applied to the retained-art character factory

The broken `sprite-preview.html` entry now opens `proof/character-factory.html`. This review page indexes existing original tall Swordsman cutouts directly instead of requesting nonexistent runtime definitions or restoring rejected packages from `unused`.

Available: BasicAttack and SkillOverhead with four actually authored diagonal views, source-review timing, frame scrubbing/stepping, quarter speed, one-shot replay and final-pose hold. BodyCostume, HeadHair, weapon, hand occluder and front/back trails retain their common 512px source canvas and recorded draw order. No per-frame fitting or mirroring is used. Layer toggles expose extraction/occlusion problems.

A separate historical SE skill prototype supports the existing gold/moon head, whole clothed body and weapon choices. These options are available only for that matching pose set, not mixed with the other actions. No new cosmetic art, hidden surfaces or anatomy approval is claimed. Existing trial edges and trail limits remain visible. The factory catalog validates dimensions and hashes all **912 existing source images**; no original image is changed or copied into a runtime package.

## RO source study

The Goro client was inspected at commit `33389d39e7a0e6ede2fd277b5b93afad02708b0e`. Current files moved from the older documented paths:

- [game/sprites/render.go](https://github.com/kivutar/goro/blob/33389d39e7a0e6ede2fd277b5b93afad02708b0e/game/sprites/render.go): `Humanoid` keeps separate head/weapon/weaponLight views; `composeHumanoidBillboard` selects layer order by body action/motion; `drawFallbackHumanoidLayers` binds overlays to common action/direction/body-motion state. Head-motion selection has its own policy, so this does not imply every RO head has exactly the same frame index as the body.
- [game/scene/sprite_render.go](https://github.com/kivutar/goro/blob/33389d39e7a0e6ede2fd277b5b93afad02708b0e/game/scene/sprite_render.go): direction normalization.

Craft Anything's `core-archive-show` recorded these two fetched source files with content hashes; [inventory evidence](ro-source-inventory.json). Semantic conclusions above come from reading the source, not an automated AI verdict. No Goro code or RO artwork is copied into the factory. Astraeon's existing source-specific draw order is retained rather than replacing it with a universal RO layer order.

## Browser validation with Craft Anything 0.3.0

- **15-step run:** entry redirect, two attack/skill views, frame stepping and compatible head/body/weapon swaps. [Screenshot](cosmetics.png), [network/console/DOM evidence](cosmetics.json), [parameters](cosmetics-params.json).
- **22-step run:** all four views of both baseline actions, then BasicAttack replay. Ends at frame **15 / 15** with final-pose status. [Screenshot](all-views.png), [evidence](all-views.json), [parameters](all-views-params.json).
- Both runs: no aborted steps, HTTP errors, console errors or page errors. Screenshots show rendered artwork, not just a successful UI click. These checks do not certify animation naturalness, trail geometry or semantic cutout boundaries.

To rebuild the catalog, run `python tools/character_factory_v3/build_review_catalog.py`. Serve the repository on loopback port 8769. Use the pinned Craft Anything installer documented in the earlier audit pilot, then execute each saved JSON through `--deep --allow-run --project <fresh temporary .cany folder> web-walkthrough-record @<params file>`. Stop the server afterward. Raw screenshot bytes are saved as PNG; base64 was removed from JSON to avoid duplication. Browser settings and tool versions are in evidence. The final loading-message adjustment was syntax-checked after the browser runs; it changes only pending-load presentation.

This is a development review factory, not complete playable characters: **2/96 technical imports, 0/6 completed characters** remains unchanged. Walk and remaining actions are not substituted with attack poses. Main-game wardrobe/loading is not repaired by redirecting this development entry page.
