# Factory V3 motion source evidence

Retrieved 2026-10-19. This record covers free sources acquired without an account or payment. The original archives and animation files stay in the local ignored `motions/inbox/` and `motions/raw/` folders; only source URLs, hashes, and license evidence are committed.

## Earlier candidates — now visually rejected

### Quaternius — LowPoly Animated Knight

- Source page: <https://opengameart.org/content/lowpoly-animated-knight>
- Download: `https://opengameart.org/sites/default/files/Knight%20Character%20by%20%40Quaternius.zip`
- The page identifies the author as Quaternius, lists CC0, describes idle/walk/run and other animations, and says weapons can be attached to `Palm.R`.
- The downloaded archive SHA-256 is `36aed14d0e27282bd006982e00206a852b1d8c00fc72f95c2437d9b4b5dccdb9`.
- The extracted animation source is `Knight Character by @Quaternius/Blends/KnightCharacter.blend`, SHA-256 `edc8036644626dbe20fbf2d2bd3b046688496962c0dacc516b3ea78f519a35e9`.
- Local evidence: `legal-evidence/opengameart-lowpoly-animated-knight.html`.
- The page requests no attribution; attribution is retained here as a courtesy. This source is not used to replace the canonical V3 character mesh.

### CMU Motion Capture Database conversion — Subject 16, clip 16_15

- Public mirror: <https://github.com/una-dinosauria/cmu-mocap>
- Clip URL: <https://raw.githubusercontent.com/una-dinosauria/cmu-mocap/master/data/16/16_15.bvh>
- The retained conversion README says the original database permits free use in research and commercial projects worldwide, and the conversion author imposes no additional restrictions. It requests this attribution when publishing: “The data used in this project was obtained from mocap.cs.cmu.edu. The database was created with funding from NSF EIA-0196217.”
- The same README discloses that converted BVH files have a guessed T-pose inserted at frame one and are 120 FPS. The retarget process skips that frame.
- Local evidence: `legal-evidence/cmu-mocap-conversion-READMEFIRST.txt` and `legal-evidence/cmu-mocap-index.txt`.
- The selected 16_15 BVH SHA-256 is `7459cd4be169477b4e2c629075a9cde9436e37a87cdf4e774574400f4ec942d8`.
- Usage status is recorded as `APPROVED_WITH_LIMITS` because the source asks for attribution. Retargeting and modification are permitted by the retained source statements.

## Selected replacement — Mesh2Motion Human Base Animations

- Official animation bundle: <https://github.com/Mesh2Motion/mesh2motion-app/blob/653a9698f5f315523072f1c3ff3496100401317b/static/animations/human-base-animations.glb>
- The official repository's `LICENSE-CC0.MD` says the models, Blender files, rigs, and animations are CC0 1.0 Universal and may be used commercially. The separate Mesh2Motion source-art repository also contains a CC0 license. Retained evidence and exact selected actions are in `legal-evidence/mesh2motion-cc0-license.md`.
- The pinned source commit is `653a9698f5f315523072f1c3ff3496100401317b`. The downloaded bundle SHA-256 is `406eb0a8dc4ab366e623b79b6e3005a4951392e1bda78ae39c1099d31147733c`.
- The bundle contains separate `Idle_Sword`, `Walk`, and `Sword_Attack` actions on a 66-bone human skeleton at 24 FPS. All three are mapped through `mesh2motion_human_glb` to new V3 actions. The raw GLB remains local and ignored by Git.
- The README notes some human clips originate from Quaternius. The selected bundle is licensed CC0 by the Mesh2Motion project; the old Quaternius source clips are not selected in this build.

## Rokoko — 13 Free Fight Animations

- Official resource page and stated game/commercial-use scope: <https://www.rokoko.com/resources/rokoko-mocap-13-free-fight-animations>.
- The selected `SwordFight_mixamo.fbx` is used only as a motion guide. Its exact archive and FBX hashes, source-page terms, missing receipt/license-file note, and AI-use limitation are documented in `legal-evidence/rokoko-13-free-fight.md`.
- The current review guide samples source frames 480–511 at 30 FPS, with additional true Blender half-frame evaluations for the 60 fps review. The original FBX remains local and ignored by Git. This pose-study retarget is not an approved canonical V3 rig action.

## Other reviewed but not selected

- The other Quaternius and Umplix motion files are listed in `candidates.json` with the visual or retarget reasons for rejection.
- MoCap Online was not used. This intake follows the user's direction to choose another free source; no account-only or paid material was acquired.

## Mixamo fallback evaluated

- Official FAQ: <https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html>
- Adobe states that Mixamo is free for users with an Adobe ID and that its characters and animations may be used royalty-free in commercial video games. The FAQ was reviewed on 2026-10-19; its page metadata says last updated 2021-09-14.
- Mixamo requires account sign-in to access downloads. No credentials were requested or stored, and no Mixamo FBX was received. This FAQ is source-level evidence only; it does not complete per-file provenance. Mesh2Motion now provides the selected free source, so Mixamo is not needed for this build.

## Scope

This evidence supports technical development and source permission review. It does not approve the character's visual quality, runtime admission, or owner sign-off. The selected motions remain `CANDIDATE` until the owner reviews the V3 output.
