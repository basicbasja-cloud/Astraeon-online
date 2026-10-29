# Pickup SW paint pilot — single shared calibration review

The rejected nine-frame painted sheet was reviewed using one uniform transform for the whole sequence. It was calculated from the first-frame dark-foreground bounds: scale `0.7587301587`, translation `[47.2206,45.3397]` in a 384px cell. It is a **diagnostic calibration**, not a production fit: foreground bounds include hair, costume and sword and do not identify bones or landmarks. No frame-specific scale or translation was applied.

[Guide and shared-transform GIF](comparison.gif) · [all bound measurements and source hashes](receipt.json). The first frame aligns in the vertical foreground bounds by construction. With exactly the same transform on frame 8, the draft foreground top is 65px above the guide top and its bottom is 49px above the guide bottom; frames 6 and 7 also have large discrepancies. Different costume and body proportions affect the bounds, but this size of change shows that a single simple registration does not make this nine-frame draft follow the guide. The pose, foot and body differences need direct master correction rather than admitting it through automatic fitting.

The GIF repeats nine poses at diagnostic timing; the unmodified draft has a white background and is not a cutout. There is no art, contact, loop, runtime or game approval. Inputs and original artwork remain unchanged. Two focused tests passed. Reproduce to a fresh destination:

```sh
python3 tools/character_factory_v3/review_fixed_calibration_pickup_pilot.py --output <fresh-output-directory>
python3 -m unittest discover -s tests/character_factory_v3 -p test_fixed_calibration_pickup_pilot.py -v
```
