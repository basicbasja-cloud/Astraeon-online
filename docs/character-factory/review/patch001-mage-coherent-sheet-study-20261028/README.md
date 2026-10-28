# Mage four-pose sheet study — source alignment rejected

The earlier Swordsman workflow painted multiple coherent poses in one sheet. This study uses four actual Mage SW guide poses (002, 003, 006, 010) and the saved Mage identity as references for a single sheet. It is a small feasibility study and does not supply the intervening animation frames.

[Generated four-pose sheet](generated-sheet.png) · [guide, paint and overlay for each pose](guide-comparison.jpg) · [24-frame current diagnostic GIF](../patch001-mage-own-frame-head-recovery-20261028/own-frame-normal.gif)

The character design is more consistent across these four drawings than in the independently generated test. However, with one shared diagnostic scale and translation, the guide overlay shows mismatched staff and hand placement, including between 002 and 003. Leg/foot positions and intermediate motion have not passed. The generated sheet was therefore **rejected as a motion paintover**, and no masters, cutouts or runtime art were replaced. A shared visual fit is only an aid to inspection and is not validated registration.

Raw, exact prompt, source guide hashes and identity hash are under `painted-candidates/mage-consistent-four-pose-sheet-20261028`; the reproducible overlay and receipt are under the matching `review` directory. Run `python authoring/characters/factory-v3/patch-0.0.1/review/mage-consistent-four-pose-sheet-20261028/producer.py`. Image-generation model and seed are unavailable. Coverage remains **0/6 newly complete characters, 2/96 technical imports**.
