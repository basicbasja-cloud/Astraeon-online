# SW06 neighbor-guided head repair — rejected

The donor used both neighboring key poses and the original locked guide, then was feather-composited within the same bounded head/neck region. It changes no pixels outside that mask, but can change the scarf and shoulder within it. The reference output and full unmodified donor are preserved; they are not admitted to the game.

After the same provisional sole registration, SAM head-mask centroid versus guide movement gives 5.50/5.04 runtime px for 04→06 and 5.74/6.02 px for 06→08 (candidates 0/2), compared with 3.62/3.42 and 4.35/4.68 for the prior bounded trial. Masks may include costume or omit head features; the figures are diagnostics across nonadjacent frames, not visual or temporal acceptance criteria. Neither result establishes a stable head. More independent generations are not a reliable path to a coherent sequence by themselves.

Reproduce bounded composite: `python tools/character_factory_v3/propose_pickup_sw06_head_repair.py --donor authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-pickup-sw06-neighbor-repair-20261029/donor.png --output /tmp/pickup-neighbor-replay`.

All source artwork and the tall baseline are preserved. No accepted master, cutout or runtime package resulted.
