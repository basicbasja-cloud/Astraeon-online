# Mage adjacent two-pose sheet — rejected

This experiment requested frames 002 and 003 together, using their two exact SW guides and the same Mage reference. The same character design remains more consistent than in two independent generated frames, but the model changed the character's cell placement and apparent scale, and the posed staff and free arm do not reliably follow the two guides. The full-cell fixed overlay is a prompt/registration diagnostic, not an accepted production character-fit calibration; independent frame fitting was not used.

[Guide / paint / overlay](guide-comparison.jpg) · [two-frame diagnostic GIF](pair-diagnostic.gif) · [source hash receipt](receipt.json). Two frames cannot establish animation continuity or contact. The result is rejected and was not imported, cut into parts, or admitted to the game. Original sources and approved baseline are unchanged; 0/6 characters are complete.

Raw output, input prompt and diagnostic producer are stored under `authoring/characters/factory-v3/patch-0.0.1/painted-candidates/mage-adjacent-pair-sheet-20261028/`. The model and seed were not exposed. Reproduce the diagnostic from repository root with `python3 authoring/characters/factory-v3/patch-0.0.1/painted-candidates/mage-adjacent-pair-sheet-20261028/review.py`.

The full factory suite passed 375 tests in the current workspace, including the six recently added audit tests and Blender checks. This technical result does not approve the painting.
