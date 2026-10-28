# Sprint binding checkpoint

The shared modular sprite adapter mapped gameplay state `sprint` to the `Run` clip even though the patch defines `Sprint` separately. The wardrobe's explicit mapping already chose `Sprint`; the defect affected callers relying on the shared adapter's default state map.

`STATE_CLIPS.sprint` now selects `Sprint`. If a definition lacks the clip, drawing reports `Missing runtime clip Sprint` instead of silently drawing Run. A regression checks both that missing-clip case and the actual sampled clip when Sprint is present. Synthetic test frames are used solely to verify selection; no new character art is claimed.

`node --test tests/modular_sprites.test.cjs tests/patch001_characters.test.cjs` passed 49 tests. This does not establish smoothness or gameplay acceptance. Patch coverage remains 0/6 complete characters; the Mage source-frame drift and Archer cutout/hand review remain open.
