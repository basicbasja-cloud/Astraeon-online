# External references actually used

RO research fetched552 public community-renderer APNG responses and decoded2,504 exposures, including repeated drawings, from sword-m, sword-f, mage-f and thief-m. The ledger retains every URL, canvas, clock, content hash and decode count. It does not establish official-client gameplay clocks, universal monster/NPC behavior or redistribution rights for RO artwork. The delivered character frames contain original project art, not RO sprites.

- [roBrowserLegacy pinned runtime](https://github.com/MrAntares/roBrowserLegacy/tree/d0449c2a36eff0210555fa5d086f625c5fd1e006): action enum and camera-before-action direction lookup. Action12 is SKILL.
- [ragassets pinned community renderer](https://github.com/adsonpleal/ragassets/tree/4de4fa747431979d35c747d7edd549a872efd9e1): APNG asset rendering and explicit preview clocks.
- [Example swordman body pickup response](https://assets.latam-tools.com.br/image?job=1&gender=male&head=0&weapon=0&action=24&headdir=straight&enableShadow=false&canvas=240x260%2B120%2B225): community preview, not official timing. Full exact URLs/hashes are in `ro-capture-ledger.json`.
- [KayKit Character Animations](https://kaylousberg.itch.io/kaykit-character-animations): Kay Lousberg's CC0 reference source, `Rig_Medium_General.glb`/`Rig_Medium_CombatMelee.glb`, General `Idle_A`, `Melee_Unarmed_Idle`, `Melee_Unarmed_Attack_Punch_A`. Source GLB hashes, sampled data and license are retained in v57 and the reusable source kit.

Across the four sampled RO body families, idle/walk/sit have8 unique direction groups. Pickup/ready/attack1/hurt/dead/skill have4 paired groups S/SW, W/NW, N/NE, E/SE. Freeze and alternate weapon attacks were researched but are not part of this48-clip core. Freeze2 is a special-state exception. A Swordman full-head attack has a small N/NE difference despite identical body frames; body aliasing does not define a universal head policy.

Swordman male body exposure/distinct counts: idle3/1, walk8/8, sit3/1, pickup3/2, ready6/6, attack1 5/4, hurt3/2, dead1/1, skill6/6. The preview's100ms exposures are not claimed as the game's gameplay pacing. Our16-frame pickup,80-sample walk and original combat timings are authored choices. The CC0 punch steps forward; our basic attack explicitly adapts it to planted feet and an in-place body.

Original source-art authorship and generation: native host image jobs, exact prompts, ordered reference hashes and rejected originals are in v51/v52/v54/v55 generation ledgers. Native host billing is unknown. No external paid provider was called. Old project slash attacks were excluded from the new unarmed reference and authoring.
