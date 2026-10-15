# ท่าต่อจากก้ม: ยืนผ่อนคลาย และสะดุ้งเบา

ต่อหลัง v49 ตรวจพื้นเท้าของท่าก้ม16เฟรมผ่านแล้ว ใช้ภาพตัวละครต้นฉบับกับ **เมช 2D สำหรับการขยับเล็กในมุมหลัง N** สองท่า ไม่ได้เปลี่ยนท่าก้มเดิมเป็นเมช และไม่ใช้ภาพโจมตีเก่าของเราเป็นเรฟ

- [ตัวเล่นสองท่า: เลือกท่า/ทีละเฟรม/1×/0.25×](review.html)
- [หายใจ 16 samples](idle.relaxed-16.gif) · [ครบทุก sample](idle.relaxed-sixteen.png)
- [สะดุ้งเบา 16 samples](hit.light-16.gif) · [ครบทุก sample](hit.light-sixteen.png)
- [หลักฐานเรฟภายนอก](../pickup-contact-v49/references/README.md)
- [ผลตรวจเมช/ภาพ/ตัวเล่น](mesh-qa.json) · [ทดสอบใช้ซ้ำกับตัวละครอื่น](reuse-qa.json)

## เหตุผลและวิธีทำ

ภาพวาด8คีย์จาก imagegen สองครั้งอยู่ใน `raw/` พร้อมpromptและinput ledger ชุดแรกเท้าไหลในแถว แม้ระดับพื้นคงที่ ชุดสองยังเปลี่ยนตัวละคร/รูปทรงรองเท้า จึงไม่เลือกเป็นภาพท่าที่ผ่าน ไม่แก้ด้วยการย้ายเท้ารายเฟรมหรือแปะรองเท้าทับ

ท่าที่เลือกใช้ texture จาก neutralสุดท้ายของ v47 ชุดเดียวกับท่าก้ม การ export cropอยู่ใน `build-mesh-actions.py` และ SHAอยู่ใน `mesh-contract.json` ใช้ rest-space gridและน้ำหนักชุดเดียวสำหรับสองท่า ทุกsampleถูกเรนเดอร์จากทั้งtextureผ่านWebGL หัวช่วงบนเป็น rigid translation ช่วงลำตัว/ผ้าขยับต่อเนื่อง และช่วงรับน้ำหนักตั้งแต่y432คงที่ ไม่มีการวัดรองเท้าทุกเฟรมแล้วfitกลับ ไม่มีfoot patchหรือภาพท่อนขาที่คัดลอกมาปิดข้อผิดพลาดภายหลัง

คลิปภายนอกจริงคือ KayKit `Idle_A` และ `Hit_A`16เวลาที่จับไว้ใน v49 ใช้ curve head/chest/hips/wrists จาก projected bone displacement ไม่ใช่การคิดว่าภาพคีย์แม่ของเราเป็น external motion กำหนด gainคงที่4.0/1.6เพื่อปรับสเกลและการอ่านท่า ลบ foot projection translationของคลิปเพื่อทำปฏิกิริยาอยู่กับที่ ลด residualข้อมือ0.5 และเปลี่ยนเวลาเป็น1600/670ms รายละเอียดทุกค่าเปิดเผยในcontract เป็นการดัดแปลงท่า ไม่อ้างว่าretargetเทียบเท่า3Dต้นฉบับหรือhead pitchถูกต้องในมุมที่textureเดียวไม่มีข้อมูล

16samplesไม่ได้แปลว่าวาดใหม่16ภาพ: idleมี8rasterที่ต่างกันเพราะcurveสมมาตร ส่วนhitมี15rasterที่ต่างกันเพราะคีย์ต้น/ท้ายเหมือนกันตามการกลับพัก ชุดท่าก้มยังเป็น16ภาพที่เลือกไว้ตามv49 ทั้งสองแบบมีclock16entriesจริง ไม่มีการสร้างชื่อไฟล์เพื่ออ้างว่าภาพซ้ำเป็นภาพวาดใหม่

## ผลตรวจที่ทำจริง

- ทั้ง32browser buffers: pixelช่วงy448ลงไปเหมือนrestที่เรนเดอร์ด้วยbackendเดียวกันทุกพิกเซล; ตัวตรวจพื้นผิวรองเท้าอิสระให้ช่วงแกว่ง0px ไม่ใช้ผลvertexแทนการตรวจภาพ
- ตรวจ241เวลาต่อคลิป: triangleไม่พลิกด้าน; area ratioต่ำสุด0.911ในidle และ0.747ในhit; vertexช่วงรับน้ำหนักคลาด0px หัวเป็นrigid translationภายในความคลาดfloating-point ไม่อ้างว่าทุกส่วนของclothไม่มีการยืดขณะขยับ
- ตรวจทุกเฟรมในตัวเล่น เล่นจริง1×/0.25× loopและpause ไม่มีpage error ใช้clockร่วมเดียวกับv49
- เปลี่ยนเป็นtextureตัวละครKayKit256×384 และ rest adapterใหม่ โดยไม่แก้renderer/observer:16bufferช่วงเท้าคงที่และผ่านตัวตรวจ3px มีรายงาน `reuse-external-*` การใช้ซ้ำยังต้องระบุrest bandsและcontact windowsของตัวละครใหม่ ไม่ใช่automatic anatomy detector
- ตัวอย่างเมชที่จงใจพับมีarea ratio -6.8125 จึงถูกจับได้ ไม่ถือว่ารันผ่านเพียงเพราะrenderได้
- จับข้อผิดพลาดGIFจริง:670msที่ส่งduration41/42msถูกencoderตัดเป็น640ms เก็บไฟล์ผิดไว้ใน `negative-controls/` แล้วปรับขอบเวลาclockร่วมเป็นหน่วย10ms รวม670ms และตรวจdecodeGIFเทียบclock ตัวเล่น/PNGใช้ข้อมูลclockเดียวกัน ไม่เปลี่ยนเวลาเฉพาะไฟล์GIF

ผลเหล่านี้ให้การตรวจแบบจำกัดสำหรับ **สองท่าขยับเล็ก มุมN และตัวละครนี้** ภาพยังไม่มีการเปลี่ยนperspectiveด้านที่มองไม่เห็น ไม่ใช่ท่ารับแรงหนัก ก้าวถอยหลัง นั่ง หมุนตัว หรือการโจมตีเต็มแรง การตรวจว่าเมชไม่พับไม่ใช่หลักฐานทุกกล้ามเนื้อ/ข้อต่อถูกต้อง หัวกับbodyยังไม่ใช่slotที่เปลี่ยนtextureได้อิสระ; ทั้งfactory/8มุม/เกมจริงยังไม่ผ่าน

ท่านั่ง-ลุกมีexternal capturesพร้อมแล้วในv49 แต่ไม่บังคับใช้เมชเล็กชุดนี้พับเป็นท่านั่ง เพราะจะต้องมีภาพsilhouette/occlusionใหม่และตารางเปลี่ยนจุดรับน้ำหนัก

## ใช้ซ้ำและตรวจซ้ำ

เครื่องมือที่รากrepo:

| เครื่องมือ | ข้อมูลที่เปลี่ยนสำหรับตัวละคร/ท่าใหม่ |
|---|---|
| `tools/sprite-mesh-player.js` | texture, canvas/grid, rest bands, influence centers/radii/support; ไม่fitรายเฟรม |
| `tools/sprite-contact-review.py` | SHA-bound frame list, alpha threshold, visible windows, planted frame scheduleและbudgetที่ประกาศก่อนตรวจ |
| `tools/sprite-clip-clock.cjs` | durations, loop, events; การเปลี่ยนappearanceไม่ควรสร้างclockใหม่ |

```sh
python3 research/sprite-animation/grounded-actions-v50/export-and-check.py
python3 research/sprite-animation/grounded-actions-v50/test-mesh-reuse.py
python3 research/sprite-animation/grounded-actions-v50/verify.py
```

ต้องมี Chromium/Playwright/Pillow/NumPy/SciPy; browserต้องใช้local socketได้ ตัวอย่างเป็นstandalone research player ไม่มีการแก้เกม ส่งdamage/inventory หรือเรียกAPIภายนอก หลังเผยแพร่ให้ตรวจด้วยverifyแบบอ่านอย่างเดียว และทำการแก้/สร้างภาพใหม่ในcaseถัดไป
