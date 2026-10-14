# Approved-GIF comparison and forward pickup — v41

ใช้ GIF v39 ที่ผู้ใช้แอพพรูพแล้วเป็นตัวตรวจจริง เก็บภาพและเวลาเดิมแบบไม่แก้ไข เพิ่ม viewer แบบ Canvas สามช่อง: **approved GIF / ภาพใหม่ / กระดูกต้นแบบ** พร้อมกริด เลื่อนทีละเฟรม ขอบรองเท้าที่วัดจริง และจดจุดจากภาพโดยผูกกับ SHA ของเฟรมนั้น

**สถานะภาพใหม่: ยังไม่ผ่าน ไม่ใช่ production final.** ผู้ใช้ย้ำว่าขนาดต้องสอดรับกับ GIF เก่า จึงเพิ่มการตรวจขนาดโดยตรง: ท่ายืนเดิม399px แต่ชุดใหม่ก่อนแก้416px ตอนนี้ล็อกสเกลทั้งชุดจากเฟรมยืนครั้งเดียวให้เฟรมแรก399px/พื้น480pxแล้ว แต่เฟรมกลับมายืนยังสูงอย่างน้อย420px และหัวในต้นทางถูกตัด จึงตกเกณฑ์อยู่ ห้ามย่อเฟรมนั้นแยกหรือยืดหัว/ตัวกลบปัญหา

การตรวจขอบรองเท้าจาก alpha จริงหลังล็อกขนาดยังพบเลื่อน10/25px เกิน6px ส่วนรายงานเก่าที่สเกล`.87`วัดวัสดุสีน้ำตาลได้12/23pxและเก็บไว้เป็นก่อนแก้ native7 ที่เพิ่ม guide ทั้งขาแย่ลง17/32px จึงไม่เลือกใช้ สัดส่วนหัวกับตัวและธนาคารพาร์ทยังไม่พิสูจน์ การทำให้ความสูงรวมเท่ากันเพียงเฟรมเดียวไม่ถือว่าผ่าน

- [เปิดเครื่องมือตรวจแบบออฟไลน์](approved-gif-review.html) — ดาวน์โหลดแล้วเปิดด้วย browser; GitHub แสดง source ของ HTML
- [GIF เทียบ approved กับภาพที่ล็อกขนาดแล้ว](size-locked-review/source/approved-vs-candidate.gif) · [clock แบบ game](size-locked-review/game/approved-vs-candidate.gif)
- [ขนาดเดิม/ก่อนแก้/หลังล็อก แบบ GIF](size-before-after-source.gif) · [ท่ายืนแรกและท่ายืนกลับมาตรวจขนาด](size-continuity-review.png) · [profile ขนาด399px](character-size-profile.json) · [size gate ที่ยังตก](size-locked-qa.json)
- [ภาพหน้าจอ viewer ที่ทดสอบจริง](approved-gif-browser.png) · [contact sheet](size-locked-review/source/approved-vs-candidate-sheet.png)
- [GIF กระดูกมุมหลังที่แก้การก้ม/เอื้อม/จับเป้าหมาย](rig-rear-source.gif) · [มุมข้างตรวจระยะเอื้อม](rig-side-source.gif) — เป็น source ไม่ใช่ final art
- [รายละเอียดความรู้และสิ่งที่ยังผิด](KNOW-HOW.md) · [บันทึก research](RESEARCH.md)
- [exact approved GIF bindings/decoded frames](approved-gif-reference.json) · [exact previous rejection](user-v40-rejection.json)
- [source action checks](source-action-qa.json) · [actual Blender-bone replay](source-bone-replay.json) · [full ownership source check](full-owner-source-action-qa.json)
- [current actual outline checks](size-locked-review/floor-qa.json) · [native6ก่อนล็อกขนาด](attempt6-review/floor-qa.json) · [native7 failed repair](attempt7-review/floor-qa.json) · [raw-matte failures](native-alpha-qa.json) · [raw cell clipping](native-boundary-qa.json)
- [eight retained native still outputs and exact inputs](generation-ledger.json) · [six exact input-guide reproductions](guide-reproduction.json)
- [28 action/reference regressions](test-receipt.json) · [13 size/outline regressions](size-test-receipt.json) · [26 real browser checks](browser-qa.json) · [integrity audit](audit-report.json)

## What changed

The old rear painting is rejected by the user: its hand did not reach forward and its body did not bend to collect. This iteration adds an **original target-conditioned source**, rather than pretending an unrelated preset already reaches the actual item. Analytic fixed-length limbs, explicit anatomical ownership, a grounded crystal, a separate right-hand grip socket, two physical cameras, actual per-key mesh captures and real animated Blender bones make the source inspectable. Fourteen source-only checks pass across eight authored keys, including65°peak hinge,0source foot displacement,0grip/socket error and336independent projections within.001px. No learned GOAL model, new Mixamo session, provider video or MiniMax is used.

The eight logical exposures use the **actual decoded approved GIF clocks**, not inferred mean FPS:

| Clock | Exposures in milliseconds | Total |
| --- | --- | --- |
| Approved source comparison | 190,180,190,180,190,180,190,600 | 1900ms |
| Approved game comparison | 100,100,100,100,100,100,100,600 | 1300ms |

The user did not choose one clock. The new floor-grasp target is a deeper/different interaction than v39's accepted unarmed reach-return. Different camera XY is not treated as equal, and prior acceptance does not transfer to new anatomy, target contact, direction or clothing.

## Reproduce

From the repository root:

```bash
python skills/modular-eight-direction-sprites/scripts/pickup-source-action.py --source research/sprite-animation/forward-pickup-v41/source/source.json --out /tmp/v41-source-action.json
python research/sprite-animation/forward-pickup-v41/reproduce-input-guides.py
python research/sprite-animation/forward-pickup-v41/test-action-and-reference.py
python research/sprite-animation/forward-pickup-v41/test-size.py
python research/sprite-animation/forward-pickup-v41/audit-evidence.py
```

The standalone comparison tool has a strict mode:

```bash
python skills/modular-eight-direction-sprites/scripts/approved-gif-compare.py --contract research/sprite-animation/forward-pickup-v41/attempt6-review/source-comparison-contract.json --out-dir /tmp/v41-comparison --require-checks
```

It must exit1 for the old unapproved painting. Matching the reference clock is insufficient. The latest matched-size comparison uses `size-locked-review/source-comparison-contract.json`; it must also exit1. `character-size-audit.py --contract .../size-locked-contract.json --out /tmp/size.json --require-size` must fail the clipped420pxheld-out return and unknown head/body family.

`build-review.py --attempt 6 --size-profile research/sprite-animation/forward-pickup-v41/character-size-profile.json` uses exactly one positive uniform scale`398/477≈.83438155`and translation`(31.79874214,61.97484277)`for the entire bank. Index0calibrates; index7is held out. The former`.87+(24.96,50)`review is kept as a negative size fixture. There is no per-key shoe clone, foot fitting, row registration, final art warp, anisotropic stretch or threshold cleanup. Guide-only patches/warps are retained inputs, never final sprite pixels. Native7 remains a failed alternate, not a newer accepted replacement.

Current artwork is a **flat research bank**, not a complete modular release. The production default remains coherent **body with outfit + complete head style**, with optional produced equipment; no switch to mandatory runtime limb pieces is implied. New head/body extraction, replacement coverage and all eight directions remain pending a passing painted motion. Exact accepted v39, prior frozen v30–v40 and thirteen protected W files remain unchanged. All work stays on the authorized research branch.


## Multi-part size amendment — 2026-10-14

The user clarified that character size includes all parts, not just total height. Matching399px is only a rest calibration. New `part-proportion-audit.py` requires18 observed dimensions: head width/height, shoulder breadth, torso length, chest/waist/pelvis widths, upper-arm/forearm lengths, arm thickness, hand width, thigh/shin lengths, leg/ankle widths, boot length/height and neck attachment. These names are requirements; a visible shoe/shaft segment is explicitly a surface proxy, never an inferred bone measurement.

Actual evidence is in [PART-SIZE-REVIEW.md](PART-SIZE-REVIEW.md), [annotated grid](part-proportion-review.png), [bound observations](part-proportion-contract.json) and [recomputed report](part-proportion-qa.json). The measurements were reviewed on actual pixels, with +/-2px per endpoint. This is an assisted measurement tool, not an automatic anatomy detector. Every missing, hidden, clipped or incompatible observation stays UNKNOWN and blocks a proportion pass.

Rear neutral0 to neutral7 uses the same view/nominal pose and one bank transform. The reviewed near shoe profile grows93.05px to113.11px, ratio1.2156: FAIL under the provisional8% same-view budget even allowing endpoint uncertainty. Reference front-view shaft35px versus rear49px is a **projected** ratio1.4, not proof of a40% anatomical error; view and foreshortening differ. Head horizontal slices are not maximum skull dimensions. Cape silhouettes cannot establish shoulder, chest, waist or pelvis width.

All ratios use the fixed399px family denominator, never a separately fitted frame height. Do not stretch limbs, fit each part, shrink return frames or reassign anatomical labels to hide growth. Cross-view validation needs a matching-view approved family reference or an independently validated projection adapter; this prototype rig has no such family-shape approval.

`character-size-audit.py` recomputes the bound part contract and refuses missing/stale/different-frame evidence. A hand-authored head/body PASS flag alone no longer clears size. Exact already-accepted masters serve only as an image-identity control. Viewer includes an18-item readout and actual endpoint overlay on approved/new images; unsupported frames/views do not inherit points.

Validation at this amendment:28source/GIF controls +13size controls +15part controls =56Python controls;31actual browser checks. A passing tool test means rejection/abstention works. New painted animation, part proportions, complete modular bank and production remain **REJECTED / UNKNOWN**, not approved.
