# Reusable image-joint and motion review know-how

## หลักฐานอะไรเป็น source of truth ได้

| Claim | พิสูจน์ด้วย | ข้อจำกัด |
| --- | --- | --- |
| ได้ไฟล์ใดจากแหล่งใด | URL/commit, SHA256, bytes, license receipt | ไม่พิสูจน์ว่าการแสดงเป็นธรรมชาติ |
| Source มีเวลา/ข้อต่อใด | serialized native times, evaluated rig hierarchy/world coordinates | bone center อาจอยู่ใต้ผิวหรือเสื้อผ้า |
| Capture มี exposure ใด | decoded index, PTS, duration, pixel hash | renderer clock อาจต่างจาก client attack speed |
| ภาพจริงมีจุดใด | image SHA + manually inspected visible joint/surface + uncertainty | ข้อสะโพกใต้ผ้าไม่ใช่ visible measurement |
| ภาพเดียวกันมี pixel correspondence | seeded flow + forward/back + texture/appearance checks | correspondence ไม่ใช่ semantic ownership |
| Drawing ถูก anatomy/acting | independent image review with source and visible chain | ยังไม่มี detector ที่พิสูจน์ครบทุกตัวละคร |
| Modular replacement พร้อม | complete isolated part bank + anchors + occlusion + swap tests | flattened sheet ไม่ผ่านเงื่อนไขนี้ |

## ขั้นตอนใช้กับตัวละครใหม่

1. เลือก motion source ใหม่จาก preset/capture ที่มีสิทธิ์และ provenance ตรง ห้ามใช้ท่าฟันเก่าที่ผู้ใช้ปฏิเสธ เปิด body-only และ weapon-only ก่อน effect เลือก neutral/anticipation/contact/recovery ตามภาพที่เห็น ไม่ใช้ชื่อคลิปเป็นหลักฐานว่าเกิด impact
2. เก็บ source native clock และ frame order ก่อน ห้ามบังคับทุกคลิปให้เป็น 8/16fps เปรียบเทียบแบบ native-time ก่อน ถ้าปรับเวลาเพื่อเกมให้มี clock แยก ไม่รายงานเป็นเวลาเดิม
3. ถ้าใช้ rig บันทึก rest matrices, hierarchy, exact anatomical names, camera/projection, scale, root policy, source hash และ native time ทุก sample Side ownership ใช้ชื่อกระดูกจาก source ไม่ใช้ screen-left/right
4. Rendering ต้องใช้ camera/canvas/anchor/scale เดียวตลอด family ห้าม fit แต่ละเฟรมตาม bbox หรือย้ายเท้าเฉพาะเฟรมให้ดูเรียบ ภาพ proof overlay ใช้ fixed shared crop ได้ แต่ต้องเก็บ transform เดียวและต้นฉบับ
5. วาดทับด้วยสไตล์เรา ภาพใหม่ทุกครั้งมี SHA ใหม่ annotation เก่าห้ามใช้ต่อโดยอัตโนมัติ Hair, head, body, cloth, arms, legs, equipment และ FX แยกสำหรับขั้น final; review overlay หรือ full character redraw ยังไม่ใช่ compatible parts
6. เปิด grid ที่ 8/16/32px แล้วเลือก anatomical joint ตรวจจาก pelvis→hip→knee→ankle→toe แบบทั้งเส้น จุดที่เห็นจริงเป็น `manual_visible`; จุดถูกผ้าปิด/ขาซ้อนให้ `unknown` ไม่เลื่อนสีไปขาที่ดูเหมือนตรง
7. ตรวจ frame ก่อน/หลังขาซ้อนจากภาพและ source ด้วยกัน การที่ด้านใกล้/ไกลมีสีหรือ pattern เสื้อเหมือนกันไม่พอ ต้องเห็น continuation ของ chain หรือมีหลักฐาน identity อิสระ หากยังแยกไม่ได้หยุดไว้ unknown และแก้การวาด depth/overlap
8. Seed keyframes ที่ผู้ตรวจยืนยันแล้ว พร้อม image hash, joint, x/y, uncertainty และ owner confirmation แยก source-projected seed ไว้เฉพาะ benchmark ห้ามแอบใช้ ground truth ทุกเฟรมแล้วอ้างเป็น image detection
9. รัน assisted bidirectional tracker เป็นข้อเสนอเท่านั้น ตรวจ low texture, appearance loss, forward/back disagreement, large step, alpha background, opposite-owner overlap และ labelled-keyframe endpoint agreement Lost/occluded point ห้ามต่อ chain แบบเดา
10. ถ้ามี source projection ที่ camera/canvas/phase ตรง ใช้ reference review โดยไม่ auto-fit ผลใกล้ opposite side เป็น possible mismatch; source overlap เป็น ambiguous; numeric fit ไม่ใช่ owner PASS การวาง pose source ถูกไม่ได้พิสูจน์ว่า redraw ถูก
11. ตรวจ continuity ของ root/neck/pelvis/sole/grip จาก visible image observations กับเครื่องมือ continuity/contact เดิม: velocity = Δpixel/Δtime, acceleration = Δvelocity/Δtime พร้อม cyclic seamเฉพาะ loop แยก intentional bob จาก unintended registration jump ไม่ใช้ bbox/top-of-hair แทน root
12. ตรวจ grounding โดยดู support chain, sole contact, heel/toe roll, perspective lane และ world root movement คู่กัน In-place stance foot เคลื่อนสวนการเดินได้; world-space contact ต้องอยู่คงที่ในช่วง support ห้ามใช้ foot Y เท่ากันทุกเฟรมเป็นนิยามการเดินราบ
13. ตรวจ wrist/grip/weapon plane ร่วมกัน Blade foreshortening/guard/hilt เปลี่ยนตามมุม ไม่ใช้ rotate ของดาบแบนมุมเดียวแทนทุก pose Tail ต้องตาม hand/weapon trajectory และ active-cut clock ไม่บดบัง body acting ที่ผิด
14. เล่น native-size/native-time, ช้า, frame-step และ body-only อีกรอบหลังแก้ ทุก report ต้องอ้าง image/seed/source hashes ปัจจุบัน Unknown, rejected art, unverified grip/contact/complete parts ทำให้ production ยัง blocked
15. เลือก low-frame-count family ที่ acting ชัดก่อน แล้วค่อยทดลองเพิ่ม in-between เฟรมใหม่ต้องผ่าน continuity/ownership/contacts ของตัวมันเอง จำนวนเฟรมมากไม่ใช่หลักฐานว่าสมูท

## Benchmark ที่แยกการวัดออกจากการอ้างความแม่น

Fixed camera 320×320, source UAL2 actual licensed external rig. 48 rendered images; source bone projection is reference, not independently observed skin-joint truth. Baseline uses source coordinates only at frame0. Assisted version explicitly seeds frames0/5/10/15, excludes those points from error statistics and scores 204 held-out target points per clip. No threshold tuned against held-out coordinates. p95 is recomputed with NumPy linear percentile interpolation; the JSON declares the method.

| Clip | Baseline coverage | Baseline p95 px | Assisted coverage | Assisted p95 px | Assisted retained >3px |
| --- | --- | --- | --- | --- | --- |
| Chest_Open | 61.6% | 11.63 | 29.4% | 0.57 | 0 |
| Sword_Regular_A | 17.3% | 13.77 | 14.7% | 0.68 | 0 |
| Walk_Carry_Loop | 62.0% | 6.15 | 42.6% | 1.65 | 0 |

The improved subset is more conservative: many valid-looking tracks become untrusted. **0 retained points over3px does not mean all joints are correct.** Coverage counts include hidden source bone targets that may have no measurable image point. Manual/source-labelled seed use must remain visible in any accuracy claim. The 3-clip results do not calibrate a confidence probability or prove generalization to painted characters.

DWPose actually ran on3 source images and2 protected painted W frames. Source-image median errors were6.99–9.18px, with definition/domain differences retained. The painted images have no independent joint GT; their accuracy is unknown. Raw model score is not an accuracy percentage. Use proposals to speed inspection only; current experiment is not admitted as an automatic production detector.

## CLI

Run from repository root with Python/Pillow/NumPy/OpenCV available (`PYTHONPATH=/tmp/astraeon-vision-deps` is this session's temporary dependency location, not a portable package path).

```bash
python skills/modular-eight-direction-sprites/scripts/joint-image-track.py \
  --case research/sprite-animation/joint-tracking-ro-v30/benchmark/Walk_Carry_Loop/assisted-case.json \
  --root . --out /tmp/joint-review --bidirectional
python skills/modular-eight-direction-sprites/scripts/build-joint-grid-review.py \
  --case research/sprite-animation/joint-tracking-ro-v30/benchmark/Walk_Carry_Loop/assisted-case.json \
  --tracks /tmp/joint-review/tracks.json --root . --out /tmp/joint-review.html
python skills/modular-eight-direction-sprites/scripts/joint-track-reference-review.py \
  --tracks /tmp/joint-review/tracks.json \
  --truth research/sprite-animation/joint-tracking-ro-v30/benchmark/Walk_Carry_Loop/truth.json \
  --out /tmp/source-review.json
```

Viewer changes mark the report stale. Export edits, rerun tracker, rebuild viewer, then inspect again. A fresh character case uses its own bound image paths/canvas/clock and manually inspected seeds; never copy benchmark source seeds to a different character. Reference review requires an explicitly bound projection adapter, not arbitrary RO pixels relabelled as bones.

## Next evidence gate

Build an independently double-reviewed visible-joint/occlusion set on fresh painted characters before estimating painted accuracy. Stratify profile E/W, limb crossings, headwear/capes, weapons and tiny native sprite sizes. Report errors, side-confusion rate, coverage, review time and abstentions per stratum; keep unseen characters held out. Test TAPIR or another point model against the same set rather than claiming stronger results from its paper. Then pilot idle/start-stop/turn/pickup/cast/hurt before new attack. Optional dash stays research only. No new artwork has been approved in this iteration.
