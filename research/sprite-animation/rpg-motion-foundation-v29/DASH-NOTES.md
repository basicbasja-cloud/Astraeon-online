# Optional dash research — latest user steering

ผู้ใช้เพิ่ม “เอา dash ด้วยก็ได้ เผื่อใช้” จึงรวม dash ในรอบv29แล้ว ข้อห้ามdashเดิมถูกแทนที่ การเพิ่มเป็นresearchไม่commitmechanicหรือiframes/stamina/cancel rulesเข้าเกม

## Actual source acquisition

- UAL2 Standard: Shield_Dash_RM และ Sword_Dash_RM —65joint humanoid source.
- Legacy KayKit1.2: DashFront, DashBack, DashLeft, DashRight —6joint sourceไม่มีโซ่ขา.
- รวม6dashclipsใน71motioncandidates;73serializedrecordsยังรวม2restposes.
- Blenderประเมิน9nativekeytimesต่อincludedclip:รวม639sourceposes.
- [source clips browser](CLIP-BROWSER.md), [inventory](clip-inventory.json), [user scope](dash-steering.json).

ชื่อRMเป็นlead ไม่ใช่การวัดroottravel/contactsที่อนุมัติแล้ว ภาพmontageที่มีdashไม่ยืนยันว่าเป็นmechanicแบบเดียวกับเกมเรา

ตรวจselected source samplesแล้ว: UAL2Shield_Dash_RM root endpointเดินทางประมาณ1.00sourceunitในแกน-y; Sword_Dash_RMประมาณ3.69 ส่วนKayKitBodyjointทั้ง4dashกลับendpointเดิมแม้เคลื่อนระหว่างทาง จึงไม่ใช่controllerroottravelauthorityเดียวกัน ดู [bound measurements](dash-travel-measurements.json) ค่าพวกนี้ไม่ใช่ระยะเกมเรา/velocityหรือdensecontacttruth

## ต้องกำหนดก่อน adapt

1. Body facing กับ travel vector: dashถอยได้โดยยังมองหน้า; dashด้านข้างต้องบอก anatomical/world side.
2. Root-motion versus in-place: sprite actor/controllerต้องใช้world displacement authorityเดียว ไม่ให้doublemovement.
3. Support mode: planted launch, steps, slide, declaredflight, landing; เลือกจากactualrefไม่เดาว่าdashทุกชนิดเท้าไม่ลอย.
4. Start/travel/end: load→push→travel→brake→plant/recover; dashloopจำเป็นเฉพาะเมื่อเกมextendtravelจริง.
5. Gameplay events: begin/end/controlreturn/cancel; invulnerability/collision/staminaเป็นdesigndecisionต่างหาก ไม่เกิดจากmotionpresetอัตโนมัติ.
6. Held item/cloak: hand/weapon ownerคงที่; tail/trailingclothตามvelocityphaseแต่ไม่บังcontactreview.

## Frame / runtime review

เก็บnativeclockและworld/roottransformsจริง วิเคราะห์pelvis/sole/palm/weaponตามเฟส ไม่ย้ายspriteoriginให้ดูนิ่งระหว่างdash และไม่เรียกintendedworldtravelว่าplacementerror

ทดสอบdashจากidle, walk และcombatready; สิ้นสุดต่อidle/walk/attack; interrupted/hit; ระยะสั้น/ยาวและgameplayspeedที่เลือก การstopต้องไม่teleportไปreadyหรือเหยียบกลางอากาศ ถ้ามีflightให้รับlanding contactอย่างมีเหตุผล

ขาซ้อนต้องตรวจจากsourceowner/depthและactualartใหม่เหมือนmotionอื่น; legacyKayKitใช้ตรวจเรื่องนี้ไม่ได้ ห้ามmirrorภาพตัวละครasymmetricเพื่อผลิตdashleft/right

Body-onlyและbody+propก่อนFX; จากนั้นตรวจกับcontrollermovementที่nativeplayback ถ้าระยะfoottravelไม่สัมพันธ์worldmovementให้แก้source/controller/phaseตามสาเหตุ ไม่แก้ด้วยเพิ่มFPS

ปัจจุบันมีexternalsourcecandidatesและspecificationเท่านั้น ยังไม่มีdashใหม่ของตัวละครเราได้รับอนุมัติหรือgameintegration
