# Swordsman Pickup SW — key-pose and head-drift studies

Three independently generated whole-body drafts now exist for guide frames 0, 8 and 16. [Guide / painted key poses](keyposes.png) uses one common 384px tile size and a shared `[0,17]` offset; [foreground bounds](keyposes-receipt.json) are only coarse diagnostics because they include hair, costume and weapon. The frame-0 free-hand repair and frame-8 cutout studies remain separately unapproved. **Three poses are not an animation** and no missing frame is repeated or synthesized.

The first frame-16 image placed its head visibly higher than the frame-8 candidate while the guide's head moved downward. Two separately prompted image edits were tried; the selected donor is composited into frame 16 only within a feathered head/neck/collar mask. Pixels outside the actual nonzero mask remain byte-identical to the original frame 16. [Before / donor / bounded repair](head-repair-comparison.png) · [key-pose toggle](head-study-toggle.gif). The toggle uses nonadjacent stills and is **not** a motion GIF.

## Head diagnostic and limitations

The existing CPU SAM2 tiny checkpoint generated multiple head mask suggestions for frame 8 and frame 16. Comparing mask-centroid displacement to the source head-joint displacement between these nonadjacent poses:

| SAM suggestion | Original frame 16 | Bounded repair |
|---|---:|---:|
| Candidate 0 | 3.12 runtime px | 0.90 runtime px |
| Candidate 2 | 3.05 runtime px | 1.20 runtime px |

[Full calculations and mask hashes](head-drift-receipt.json). Candidate 0 can include scarf; candidate 2 can omit facial/ear regions. The selected masks also differ in area (for candidate 2, 11,595 source pixels at frame 8 versus 9,291 at repaired frame 16). Their centroids are **not anatomical landmarks**, and these numbers neither establish correct head size nor meet a visual acceptance gate. The repair mask can include scarf/shoulder; inspect face, neckline, proportions, feet, weapon, alpha and all intermediate poses. No finished or playable action is implied.

The initial frame-16 image, donors and exact prompts are under patch `painted-candidates/swordsman-pickup-sw16-single-20261029/` and `painted-candidates/swordsman-pickup-sw16-head-repair-20261029/`. The bounded candidate and mask are in `review/swordsman-pickup-sw16-head-repair-bounded-20261029/`. Original and bounded SAM proposals are in `research/swordsman-pickup-sw16-head-sam-20261029/`. Generation model and seed were not exposed; SAM checkpoint is pinned to SHA-256 `7402e0d864fa82708a20fbd15bc84245c2f26dff0eb43a4b5b93452deb34be69`. The source guide, preserved Swordsman baseline, production ledger and runtime were not modified.

Thirteen focused `test_pickup_sw*` cases passed, including outside-mask pixel preservation and the diagnostic calculations. Reproduce using the preserved inputs and fresh destinations:

```sh
python3 tools/character_factory_v3/propose_pickup_sw16_head_repair.py --output <fresh-head-dir>
python3 tools/character_factory_v3/review_pickup_sw_keyposes.py --output <fresh-keypose-dir>
python3 tools/character_factory_v3/audit_pickup_sw_head_drift.py --output <fresh-audit-dir>
python3 -m unittest discover -s tests/character_factory_v3 -p 'test_pickup_sw*' -v
```

To recreate SAM masks use the existing SAM2 environment and `propose_pickup_sw16_sam_head.py --checkpoint <pinned-checkpoint> --source <image> --output <fresh-dir>`. No sequence-level master or cutout receipt is created by these tools.
