# RPG sprite motion know-how — foundation v29

เอกสารนี้เป็นแนวทางผลิตที่เราสังเคราะห์ขึ้นจากหลักฐานรอบใหม่ ไม่ใช่คำรับรองว่าการเจนภาพจะถูกเสมอ และยังไม่มี motion ใหม่ของตัวละครเราได้รับอนุมัติ รอบนี้ไม่ใช้ท่าโจมตี/rig โจมตีเก่าของเราเป็น reference, conditioning, benchmark ที่ดี หรือ source key เลย เก็บของเก่าไว้เฉพาะประวัติการปฏิเสธ ท่าเดิน W ที่เคยผ่านยังคงเดิม

อ่านประกอบ [รายการ 99 action specifications](MOTION-RECIPES.md), [สัญญาข้อมูล](DATASET-CONTRACT.md), [วิเคราะห์หลักฐานจริง](REFERENCE-ANALYSIS.md), [ทะเบียนแหล่งข้อมูล](SOURCES.md) และ [แผนทดลอง](PRODUCTION-PLAN.md)

## 1. เริ่มที่สิ่งที่ผู้เล่นต้องอ่านออก

ท่าหนึ่งต้องตอบได้ว่า ตัวละครกำลังทำอะไร ทิศไหน ใช้อุปกรณ์อะไร ช่วงไหนที่เกิดผลในเกม และจะไป state ใดต่อ ถ้ารู้แค่ว่า “มี 8 รูป” ยังไม่มีคำตอบเหล่านี้

ตัวอย่างคำสั่งงานที่ใช้งานได้: “เดินปกติบนพื้นเรียบ ไป W ลำตัวตั้งแบบตัวละครเรา สับขาทั้งสองเห็นชัด ขาซ้ายและขาขวาผูกกับสะโพกเดิมตลอดวง ใช้ผ้า/ผมของเรา ยังไม่ทำ FX” ต่างจาก “ทำ 8 เฟรมให้สมูท” เพราะระบุ acting, support, ownership และสิ่งที่ต้องประเมิน

แยก **action family**, **weapon stance**, **facing**, **phase**, **appearance item** และ **world movement** ออกจากกัน ใช้ชื่อ stable เช่น walk.loop / sword.diagonal / cast.release / death.hold ไม่ใช้ชื่อ frame5 เป็นความหมายของท่า เพราะจำนวนเฟรมอาจเปลี่ยนภายหลัง

99 รายการในรอบนี้เป็น research superset ของ humanoid ผู้เล่น/NPC ไม่ใช่ยืนยันว่าทุกระบบเหล่านี้จะเข้าเกม ผู้ใช้อนุญาต dash เผื่อใช้แล้ว: วิจัยเป็น optional mechanic แยกจาก roll/slide/ก้าวธรรมดา สัตว์สี่ขา ปีก หางหลายข้อ ตัวไม่มีขาและบอสขนาดใหญ่ต้องมี adapter เพิ่ม ไม่ฝืนใช้ biped skeleton

## 2. ใช้ reference เป็นบทบาท ไม่ใช้ทุกแหล่งแทนทุกอย่าง

เลือกหลักฐานให้ตรงคำถาม:

| คำถาม | หลักฐานที่เหมาะ | สิ่งที่หลักฐานนั้นไม่ให้ |
| --- | --- | --- |
| ภาพระดับเกมอ่านท่าชัดไหม | sprite/gameplay ที่สเกลและ camera ใกล้เรา | ข้อต่อที่ซ่อนจริง |
| มือ/เท้าขยับอย่างไรตามเวลา | rig/mocap พร้อม timestamp | ภาพตัวละครเรา/ความถูกต้องของสีชุด |
| event เกิดเมื่อไร | animation descriptor + controller | แรงจริงจากภาพ |
| เปลี่ยนผม/อาวุธอย่างไร | slot/layer/item source + runtime | hidden content ที่ไม่มีใน flat PNG |
| การวาด sparse poses | tutorial ผู้วาด + exposed frames | anatomy acceptance ของ sheet ที่เราเจน |
| interpolation/retarget ใช้อะไรได้ | primary paper + implementation | ผลที่ยังไม่ได้ execute |

RO, ToS และ Hades เป็นเป้าการอ่านภาพ/acting ที่มีคุณภาพ แต่ชื่อเกมหรือหน้า class ไม่ใช่ frame evidence คลัง free presets ให้โครงสร้าง motion; โมเดล low-poly ไม่ได้เป็นเกณฑ์คุณภาพงานภาพเรา แหล่งที่เรียบกว่าอย่าง LPC/Kenney ใช้ศึกษาการแยกพาร์ต/เฟส/การอ่าน silhouette ได้โดยไม่ลด art target

ก่อนเลือก reference หลัก ให้มีอย่างน้อยหนึ่งหลักฐานที่เห็น action ตั้งแต่ก่อนเริ่มจนจบ และอีกหลักฐานที่ตอบคำถามเฉพาะ เช่น sole support, palm grip หรือ state timing จำนวนแหล่งขั้นต่ำนี้เป็นกฎทำงานที่เสนอ ไม่ใช่ข้อเท็จจริงจาก paper และไม่ใช้จำนวน ref แทนคุณภาพ

## 3. อ่านลำดับเฟรมตามเฟสก่อนเลือกจำนวนภาพ

แบ่ง action เป็นเฟสเชิงความหมายก่อน แล้วจดเวลาจริงของแต่ละเฟสจากแหล่งที่มี clock ไม่สมมติว่ารูปที่วางติดกันมีระยะเวลาเท่ากัน

สำหรับ loop: neutral/load → contact/support → passing → opposite contact/support → seam สำหรับ one-shot: ready → anticipation → execution → follow-through → recovery → next state บางท่าไม่มีทุกเฟส หรือมี release/impact หลายครั้ง ต้องจดสิ่งที่เกิดจริง

แยก native key time ใน GLB, container PTS ในวิดีโอ/GIF, descriptor exposure ในเกม และ gameplay tick เป็นคนละชนิดข้อมูล รอบนี้ GLB 9 samples ต่อ clip เป็นการเลือกเวลาคีย์ต้นฉบับเพื่อทำ overview ไม่ใช่ 9 sprite keys ที่เหมาะที่สุด และไม่ใช่ exposure ของเกม

เลือก sparse keys ที่รักษาจุดเปลี่ยนสำคัญ เช่น maximum load, contact, release, fastest crossing, follow-through, planted recovery อย่าเพิ่มจำนวนเฟรมด้วยการคั่นทุกช่วงเท่ากันจน anticipation และ hit กลายเป็นการโบกช้าเท่ากันหมด ทดลอง exposure ที่เหมาะกับท่านั้นแล้วดู full speed ไม่ใช้ slow motion ตัดสิน “แรง” แทน playback จริง

Repeated drawings อาจเป็น hold ที่ตั้งใจ ต้องรักษาภาพซ้ำและระยะเวลาไว้อย่างชัดเจน ส่วน duplicated pose ที่เกิดจาก generator ไม่ทำตาม phase ต้องแยกเป็นข้อผิดพลาด จำนวนภาพ unique และจำนวน exposure เป็นคนละ count

## 4. ความต่อเนื่อง: แยก acting ออกจากการวางภาพ

นิยาม export camera, canvas, pixels-per-unit, world origin และ projected root ให้คงที่ทั้ง action bank ใช้ shared scale และ transform ที่มีเหตุผลจาก authoring sheet ห้ามปรับทุกเฟรมให้ bbox พอดีหรือวางหัวไว้ตำแหน่งเดียว แล้วบอกว่าการเด้งถูกแก้ เพราะนั่นอาจลบการย่อ/เหยียดที่ตั้งใจ

ตรวจ trajectories ของ root/pelvis/head/soles/grips แยกกัน หัวขยับไม่ได้แปลว่าผิดเสมอ; pelvis ขึ้นจาก extension หรือก้มตอนลงพื้นอาจถูก ต้องหาว่าความเปลี่ยนแปลงมาจาก source acting, camera, world movement หรือ placement error ถ้าไม่มี root truth ให้รายงานเป็น visible-surface motion ไม่เรียก recovered root

เทียบทุก adjacent transition และ loop seam โดยใช้เวลาจริง:
- ระยะก้าวภาพอย่างเดียวไม่พอ ให้ดู displacement ต่อ exposure
- การเปลี่ยนทิศ velocity/acceleration ระหว่างเฟสต้องสอดคล้องเจตนา
- งดใช้เกณฑ์ “ความเร็วเท่ากันทุกช่วง” กับท่าโจมตี
- การยืนบนพื้นเดียวกันมี depth lanes ในภาพ orthographic เอียงได้ ไม่บังคับเท้าทุกข้างอยู่แถว pixel เดียวกัน
- ตรวจ seam ทั้งตำแหน่งและความเร็ว/เฟส ถ้า loop เป็น periodic; one-shot ไม่ต้องฝืนกลับไปเฟรมแรก

ดู 4 แบบ: native playback, slowed inspection, onion skin, trajectories แล้วกลับมาดู native อีกครั้ง ตัวเลขดีแต่ดูเหมือนสไลด์/ย่อง/ไร้แรงให้ยังไม่ผ่าน

## 5. ซ้าย–ขวาและการซ้อน

Anatomical L/R เป็นตัวตนจากตัวละคร ไม่ใช่ x น้อย/x มากบนจอ ไม่เปลี่ยน owner เมื่อก้าวนำหรือหันทิศ ผ้า teal, pouch หรือสี debug ช่วยจำ แต่ย้ายของเหล่านั้นไม่ใช่หลักฐานว่าขาต่อถูก

ใน rig ให้เก็บ side IDs, pelvis origin, hip–knee–ankle–toe chain, joint names และ rest transforms ใน sprite ให้ trace ทั้งคู่จาก proximal origin ที่มองเห็นได้ผ่าน thigh, knee และ calf/boot ถ้าสะโพกถูกปิด ให้บันทึก occlusion boundary/near-far order ที่เห็นจริง; จุดภายในยัง unknown ไม่ลาก chain สมมติแล้วเรียกว่าตรวจผ่าน

เฟรม crossing ต้องมี owner/cutaway guide จากแหล่ง 3D ที่เชื่อถือได้หากมี และ image review อิสระหลังวาด ตรวจว่าขาใกล้กล้องต่อ contour ผ่าน ขาไกลหายหลังขาใกล้ตาม depth ไม่ดูแค่ตำแหน่ง toe ตรง target

ถ้าภาพ 2D มีหลายคำอธิบายที่เป็นไปได้ ให้รายงาน ambiguous และแก้ staging ให้แยกง่ายขึ้น เช่น opening ที่เข่า, overlap boundary ที่ต้นขา, depth shading ที่สม่ำเสมอ ไม่เพิ่มความมั่นใจจากการทาสี owner เอง

Asymmetric costume และมือถืออาวุธห้าม mirror ไปอีกทิศ การหมุนตัว 3D หรือวาด facing ใหม่ต้องคง anatomical side

## 6. Contact เป็นช่วงเวลาและพื้นผิว

Contact มี owner, target, interval, point/surface และประเภท: planted sole, rolling toe, palm grip, seat, ladder rung, prop touch, body on floor จุด bone ankle ไม่ใช่พื้นรองเท้า จุด wrist ไม่ใช่ฝ่ามือ ด้ามอยู่ใกล้ wrist ไม่ใช่นิ้วจับด้ามถูก

ตรวจตาม phase: heel-strike อาจเปลี่ยนเป็น sole support แล้ว toe-off ได้ อย่าล็อกทั้งพื้นรองเท้าตลอดจนเคลื่อนไหวแข็ง คนเดินต้องเปลี่ยน support จึงไม่บังคับทั้งสองเท้านิ่งทุกเฟรม พร้อมกันอย่าปล่อยเท้ารับน้ำหนักทะลุหรือไหลไปกับภาพ

Root motion และ in-place ต้องประกาศชัด:
- root-motion ref: เก็บ world/root travel และตรวจ sole world contact
- in-place game: actor sprite อาจมี foot backward travel; ต้องประกอบกับ controller movement ก่อนตัดสิน foot sliding
- moving-camera video: ไม่มี world contact truth ถ้าไม่มี calibration; fixed crop ไม่ได้ทำให้ camera fixed
- floor plane ใน3D ต้อง project ด้วย camera เดียวกับ source
- sprite floor check ใช้ sole pixels ที่เห็นจริงแยกจาก bone/source prediction

## 7. แขน มือ อาวุธ และแรงที่อ่านได้

พิจารณา shoulder–elbow–wrist–palm–grip–blade พร้อม trunk/pelvis และ support ใช้ source rig ใหม่หรือ performance reference ใหม่ตาม motion ที่ต้องการ ไม่แก้ท่าเดิมวนด้วย socket coordinate

ข้อมือมี flexion/deviation และ forearm roll; มุม rotation รวมของ bone ไม่ใช่ flexion ของข้อมือและไม่ใช่หลักฐานว่าไม่มีการบิดมือ ตรวจ palm direction, finger wrap, guard clearance, blade axis และสองมือถ้ามี

อาวุธสามมิติเข้าหา/ออกจาก camera มี foreshortening, guard ellipse และ blade plane เปลี่ยน วาด/export แต่ละ pose perspective ให้ตรง motion อย่าใช้ flat sword ใบเดียวหมุนใน screen plane แทน bank เมื่อ pose เปลี่ยนมุมจริง วัตถุ rigid มีความยาวโลกคงที่ แต่ความยาว projected pixel ไม่จำเป็นคงที่

สำหรับ slash ช่วงเร็ว สามารถใช้ smear/tail เป็น weapon depiction ได้ แต่ให้ body action, hand sweep และจุด contact/release อ่านออกก่อน ปลายทาง effect ต้องตรงวิถีอาวุธ ตัวอย่าง smear ไม่บังคับให้แสดง rigid bladeทุก exposure; tail ไม่อนุมัติท่าที่มือแกว่งไร้แรง

ตัดสิน damage feel จาก contrast ของ load/execution/follow, direction/intent, range, shoulder–hip coordination และ recovery ไม่คำนวณ force จากระยะ pixel หรือเรียก pelvis shift ว่า center-of-mass ที่วัดได้ เกมอาจใช้ stylized exaggeration ให้ดูมีแรงโดยไม่เหมือนการฟันจริงทุกองศา แต่ต้องมี trajectory/grip/balance ที่อ่านได้

## 8. Motion modules ที่ต้องแยก

รายละเอียดทุก action อยู่ใน MOTION-RECIPES ส่วนหลักการที่ห้ามเหมารวม:

- idle ไม่ใช่ walk ที่ลดความเร็ว; look gesture ไม่ใช่เปลี่ยน facing ทั้ง body
- start/stop/turn มี support transition ของตัวเอง ใช้ phase-aware state transition ไม่สุ่ม jumpเข้า loop
- sword/axe/spear/bow/staff ไม่ใช่เปลี่ยนภาพอาวุธบนแขนเส้นเดียว น้ำหนัก ระยะ และจำนวนมือเปลี่ยน
- bow แยก nock/draw/hold/release/recover; projectile ออกจากตำแหน่งลูกธนู ณ release จริง
- cast แยก start/loop/release/cancel; channel tick ไม่ใช่หนึ่ง hit ทุก sprite frame
- block/parry/hit มี intent ต่างกัน; same effect flash ใช้แทน body response ไม่ได้
- knockdown/death เป็น finite transition + terminal pose; death hold ไม่ต้องย้อน loop
- sit down/up ต้องมี seat support; ground sit และ chair sit ไม่ interchangeable โดยไม่ปรับ contact
- pickup/use/drink มี hand–prop–target relation; prop disappearตรง commit ไม่ใช่ต้น windup
- emote ต้องคง costume/hand owner ระหว่าง gesture; ต้องตรวจ return seam ต่างจาก loop dance
- conditional traversal ต้องเปิดเมื่อ controllerมี mechanicนั้น; dash เป็น optional research ตามคำสั่งล่าสุด

## 9. Modular factory: source ครบจึงเปลี่ยนได้จริง

Dashได้รับอนุญาตให้วิจัยเผื่อใช้ตามคำสั่งล่าสุดแล้ว อ่าน [dash practice](DASH-NOTES.md): แยกbodyfacing/travelvector, start/travel/end, in-place/root-motion, support/flight/landingและevent/cancel ไม่commitmechanicเข้าเกมอัตโนมัติ

กำหนด logical slots และ item coverage matrix ก่อนสร้าง sheet เช่น base/face/hair-front/hair-back/torso/near-arm/far-arm/near-leg/far-leg/cloak-front/cloak-back/right-hand item/left-hand item โดย owner เป็น anatomical side แม้ export compositingจะแบ่งnear/farตามview

Logical slot ไม่จำเป็นเท่ากับ draw layer อาวุธหรือผ้าผืนเดียวอาจต้องแตกหน้า/หลังมือหรือขาในบางเฟส เก็บ draw order ต่อ facing/phase, masks และ item-specific attachment transform ไม่บังคับ global z orderเดียว

พาร์ต complete หมายถึงมีเนื้อภาพที่ต้องใช้เมื่อสลับ/ถอด/เปลี่ยนความยาว ไม่ใช่ตัดเฉพาะส่วนที่มองเห็นจาก flattened sprite Hidden scalp under hair, shoulder under cloak, palm behind grip, back of tabard และ body behind large shield ต้องมี source ที่ใช้งานได้

รวม variants ทดสอบก่อนทำ mass production: ผมสั้น/ยาว, ผ้าคลุมมี/ไม่มี, ดาบสั้น/ยาว, โล่เล็ก/ใหญ่, ไม่มีหมวก/หมวกสูง ชุดสุดขั้วต้องยังผ่าน anatomy/contact/canvas/clipping ไม่สรุปจากไอเทมตัวอย่างเดียว

Animation coverage ผูก item × body family × action × facing × phase ถ้าไม่มี clipให้ระบุ unsupported หรือ explicit compatible fallback ห้ามโหลด unknown frameแล้วอ้างว่า reuse สำเร็จ LPC และ Larianช่วยเห็นว่าการมีslot name/fallbackไม่ใช่มีภาพเหมาะกับทุก item

## 10. Redraw / generation ที่ให้ข้อมูลพอและไม่ซ่อนข้อผิดพลาด

ทำ neutral identity/costume sheet ของเราแยกจาก motion ref รอบวิจัยนี้ยังไม่สร้าง artworkใหม่ ไม่หยิบ actor sourceเก่าที่ไม่ผ่านกลับมาเป็น motion seed

เริ่ม one action/one view/body-only หรือ body+prop ที่ต้องดู gripได้ จาก reference phasesที่ตรวจแล้ว ค่อยเพิ่ม facing/parts ถ้าใช้งาน3D source ให้camera+projected pose+silhouette+depth+owner guidesอธิบายคนละเรื่อง ไม่ทำ debug color เป็นภาพที่อนุมัติแล้ว

Prompt briefประกอบด้วย identity, pose progression, actual phase times/proposed exposures, ground/support, anatomical owner, grip/weapon perspective, immutablecamera/canvas, constraints, nextstate และ visual acceptance checklist ไม่มีสูตรข้อความที่รับประกัน zero error

ตัวอย่าง performance briefสำหรับ cast: “same neutral adventurer, settled feet; gather hands, hold concentration, release toward target, ease back to ready; full body fixed camera; same staff hand and costume; no particles for first review.” Promptไม่ได้ทำให้ actual clipมีcontact labels ต้องตรวจ output

Whole-strip generationช่วยลดindependentframe identity drift แต่grid/silhouette/anatomyอาจยังผิด ถ้าจำเป็นต้องregen keyเดี่ยว ให้ใช้correctedkeybankรวมและตรวจadjacentทั้งสองด้าน+loopseamอีกครั้ง ไม่เปลี่ยนเฉพาะไฟล์แล้วใช้annotationเก่า

เลือกช่วง motion จากวิดีโอจริงที่genได้เท่านั้น เก็บ provider receipt/PTS/camera review เครื่องมือimage-onlyยังสร้างวิดีโอไม่ได้ ส่วน researchรอบนี้ทำได้โดยไม่ต้องมีvideo provider: ดาวน์โหลดreferenceจริง, อ่านsource, sampleexternalrig, builddataset/notes

## 11. QA มีหลายชั้นและผลผ่านจำกัดขอบเขต

1. provenance: bytes/source URL/commit/license/clockตรงและไม่ใช่ท่าเก่าที่ถูกห้าม
2. motion meaning: phases/intent/eventและtransitionเหมาะกับmechanic
3. source kinematics: joint chains/restbasis/contact surfaces/prop trajectory
4. actual artwork: owner/occlusion/grip/perspective/silhouetteและรายละเอียดชุด
5. temporal: exposure/frameorder/worldregistration/seams/nobounceandnoslide
6. modular: completeparts/hiddencontent/swaps/extremeitems/zorder
7. runtime: nativeplayback/worldmovement/cancelspeed/events/networkstate
8. artistic judgment: ดูดีแบบของเราและapprovedโดยผู้ใช้ในขอบเขตที่ระบุ

ผลhash/format/decoderผ่านไม่ข้ามข้อ2–8 Numeric trajectoryผ่านไม่อนุมัติ acting Color debugตรงไม่อนุมัติ owner ค่าความคลาดต่ำของoccludedjointไม่ทำให้jointเป็นobserved

มีknownnegative controls: swappedL/R, duplicatedpassingposes, oneframe shiftedY, fixedbodyspinningweapon, eventหนึ่งครั้งกลายเป็นสองครั้ง, itemremovedwithhole, one-shotforcedloop, mirrorasymmetriccostume ต้องตรวจว่าระบบblockกรณีเหล่านี้ได้จริงในadapterนั้น

## 12. ทำซ้ำกับตัวละครอื่น

Freeze approved character appearance +camera/body proportion contract แล้วเลือก new reference familyที่รองรับmechanicเดียวกัน Map restbasesและsidesให้ตรง,ปรับcontactsด้วยtargetsurfaces ไม่ยืดแขน/ขาเงียบๆเพื่อให้ปลายถึง เปลี่ยนcostumeแล้วตรวจocclusionและhiddenpartsใหม่

Reuseความหมายเฟส/schema/scripts/QAprocedure/referenceindexได้ ส่วนbudgets/pixelpalette/SIFTregions/restpose/socketlength/garmentdepthต้องcalibrateใหม่ให้ตัวละครใหม่ ห้ามนำคะแนนaccuracyตัวเก่าหรือapprovalภาพเก่ามาใช้กับnewpixels

บันทึกแต่ละ run: request, sourceSHA, tool versions, chosenphases, actualoutputbytes, annotationreviewer, failures, repairs, postrepairrecheck, acceptance scope และ runtime test evidence เมื่อท่าเดียวผ่านจึงขยายเป็น8ทิศ/หลายไอเทม/หลายตัวละคร ไม่ตีความการมีknow-howเป็นfactoryที่พิสูจน์แล้ว
