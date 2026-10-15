# Start here — ส่งต่องาน sprite factory

วันที่ส่งต่อ 2026-10-15 · งานปัจจุบัน v46 · ทุก path ในเอกสารที่อยู่ใน backticks นับจาก root repository เว้นแต่ระบุอื่น

## เป้าหมายและข้อจำกัดที่ผู้รับงานต้องรู้

สร้างตัวละคร RPG สไตล์ของเรา มี motion ที่ถูกต้องต่อเนื่อง ขาซ้าย/ขวาและมือจับอาวุธไม่สลับ แยก runtime เป็น body_outfit และ complete_head เพื่อเปลี่ยนหัว/ผม/อุปกรณ์ได้ ผู้ใช้ยอมรับเพียงบางตัวอย่าง ไม่ได้อนุมัติ factory ทั้งระบบ งานปัจจุบันเป็นท่าก้มเก็บของด้วยมือขวา ไม่ใช่ attack หรือ walk ใหม่

ใช้ branch เดียว `research/modular-sprites-full-body-2026-10-11` ของ `https://github.com/basicbasja-cloud/Astraeon-online.git` ห้ามย้ายไป main และห้ามนำ character asset ที่ถูกปฏิเสธจาก branch อื่นมาสอนงานเป็นตัวอย่างบวก มี standing authorization ให้ commit/push branch นี้ MiniMax พักไว้ ไม่ใช้ Tripo หรือ paid API/credits ภายนอก รอบ v46 ใช้ host-native image tool ตามคำขอวาดทับ เก็บจำนวน calls และไม่มีข้อมูล billing ยืนยัน ห้ามตีความว่า host tool มีราคาเป็นศูนย์

## อ่านและเปิดตามลำดับ

1. [สถานะที่เชื่อถือได้](01-STATUS-AND-DECISIONS.md) — สิ่งที่ user ยอมรับ เทียบกับสิ่งที่เครื่องมือผ่าน
2. เปิด `research/sprite-animation/paintover-handoff-v46/previews/eight-directions.gif` และ `review.html` เพื่อดูภาพวาดทับจริงเทียบ source
3. [แผนที่ไฟล์](02-FILE-MAP.md) และ [runbook](03-RUNBOOK.md) เพื่อทำต่อ
4. [ข้อกำหนดงานภาพ](04-ART-AND-ANIMATION-SPEC.md), [QA และ failure](05-QA-AND-FAILURES.md), [แหล่งความรู้](06-REFERENCE-CORPUS.md)
5. [รายการส่งต่อให้คนรับ](07-NEXT-OWNER-CHECKLIST.md) ระบุลำดับงานที่ยังค้าง

## Quick proof โดยไม่เปลี่ยนหลักฐาน

จาก root รัน `python research/sprite-animation/paintover-handoff-v46/verify-handoff.py` ตรวจ hash ของ historical manifests, accepted W, raw paintovers และ inventory รวมถึง local links ไม่เรียก provider ไม่ render ไม่แก้ภาพ ไม่ใช่การอนุมัติกายวิภาค

เอกสาร README เก่าของ research และหัวข้อ historical ใน skill อาจแสดงเลขเวอร์ชันเก่า ให้เอกสารชุดนี้เป็น entry ปัจจุบัน แต่ใช้ receipt ของแต่ละ case เป็นหลักฐานเฉพาะเรื่อง ห้ามอ้างข้อความสรุปแทนผลตรวจจริง
