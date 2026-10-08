# Swordsman production — saved milestone, production continuing

The complete two-body, nine-animation character is **not ready for final visual approval**. All resulting art remains DEV_ONLY / NOT_APPROVED. Internal clip scores authorize continued production, not owner acceptance.

Base: `origin/codex/modular-sprite-pipeline-v0.1`, starting SHA `38228dd26ac8c5e8676a3a5904ad945742eadc42`. Production is isolated on `codex/swordsman-visual-production-v0.1`; protected branches are not merged or rewritten. Identity authority is the unchanged `authoring/characters/gait-rig-v50/approved-warrior-seed.png`. Its copied reference and measured identity lock live under the authoring production directory.

| Male milestone | Current best | Internal score |
|---|---|---|
| Coordinated eight-direction masters | directional-02 | 37/40 |
| Fixed-chain authoring walk proof | rig-walk/candidate-03 | 38/40 |
| Idle, eight directions × eight frames | Idle/candidate-03 | 93/100 |
| Walk, eight directions × sixteen frames | Walk/candidate-28 | 91/100 |
| Run, eight directions × twelve frames | Run/candidate-01 | 92/100 |
| BasicAttack, eight directions × sixteen frames | BasicAttack/candidate-06 | 91/100 |
| SkillAction, eight directions × fourteen frames | SkillAction/candidate-02 | 91/100 |
| Hit, eight directions × eight frames | Hit/candidate-02 | 92/100 |
| Death, Guard, Dash | Pending production | No score |
| Female Swordsman | Not started; male-first production | No score |

A continuous action-path regression subsequently withdrew BasicAttack04’s pass for an NE sword-angle singularity. Candidate05 was rejected for a long NW angular detour; candidate06 unwraps adjacent keys and passes its separate internal review.

The owner rejected earlier Walks. Rig candidate 02’s premature internal pass was withdrawn when measured thighs stayed ahead of the pelvis. Candidate 03 corrects rearward extension with fixed femur/tibia/foot lengths, knee poles, heel/sole/toe contact pivots, swing clearance and weight transfer. Painted candidate 28 fixes cloth joins, boot registration, foreshortened foot surfaces and the east far-arm guide. Ragnarok uploads are motion-readability benchmarks; their pixels, costume, proportions and exact timing are not runtime sources. The rejected generated arm study is retained with its diagnosis; accepted attack surfaces use existing same-direction costume paint.

## Presentation contract and runtime proof

Canvas: 320×320; root: (160,264); reference height: 176. Directions remain S, SW, W, NW, N, NE, E, SE without mirrored views. BaseBody, Hair, Outfit, Weapon, Headgear and BackAccessory are independent full-canvas layers sharing timelines and anatomical sockets. Default headgear/back parts are transparent. All runtime output is painted 2D PNG; articulated rigs are authoring-only.

`classId: Swordsman` supports extensible presentation `bodyVariant` values. Logical cosmetics resolve body-specific artwork. Only active cosmetics and requested clips preload; appearance switches atomically after readiness. Optional `keepAnimations` releases unneeded image references after transitions. The game development adapter retains Idle plus the most recent motion to avoid repeated decoding during stop/start; it does not guarantee immediate browser decoded-cache eviction. **Gameplay equipment never determines appearance.** No equipment-to-sprite mapping or gameplay/shop/backend redesign was introduced.

Select the male candidate in `sprite-preview.html`, or use the explicit actual game development flag `index.html?qa=1&swordsman=male`. Ordinary gameplay keeps the original player. Passed clips are available; pending entries are clearly tagged and disabled in the sprite preview. Development assets bypass ordinary asset caching; synchronized shell/cache version is 101.

Actual game captures under `in-game/` exercise Idle, all eight Walk directions, Run, BasicAttack, SkillAction and mobile scale. Saved test equipment changes to Legendary Fire Sword and Ancient Plate while cosmetic appearance remains unchanged. Browser captures prove software-rendered presentation, not mobile hardware performance.

Current runtime inventory: **34,769,235 bytes, 29 unique lossless atlases plus definition JSON**, including explicitly pending scaffold metadata. Source masters and strips remain separate from packed derivatives.

## Review evidence

- `canonical-reference.png`, `male-directional-source.png`, `male-modular-layers.jpg`.
- `authoring/characters/swordsman-production/rig-walk/candidate-03/`: editable Blender proof, shared cycle, eight-phase grid, normal/quarter previews, contact diagnostics, browser captures and internal gate report.
- `authoring/characters/swordsman-production/male/motion-candidates/`: current clip directories above contain lossless composites, six source strips, normal/quarter GIFs, gameplay-size captures, provenance and gate reports.
- `in-game/`: actual player renderer screenshots and executable-test results.
- `asset-inventory.json`: referenced files, sizes and SHA-256 hashes.
- `generation-provenance.json`: thirteen meaningful first-party jobs, decisions and source references; exact prompts and exclusions remain beside candidates.
- `validation-results.json`: scoped automated results; technical validity is separate from visual acceptance.

Remaining work: finish the remaining male clips in order, complete actual game action proof and normal-game/cache regressions, then produce the female variant using the established contract. The complete production score remains unset. Final visual approval belongs to the owner.
