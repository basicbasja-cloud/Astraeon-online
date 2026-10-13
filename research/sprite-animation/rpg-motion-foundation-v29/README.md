# Fresh RPG motion foundation v29

เริ่มวิจัยใหม่ตามคำสั่ง: **ไม่ใช้ท่าฟันเก่าของเราเป็นต้นแบบ และเพิ่ม dash เป็น optional research ตามคำสั่งล่าสุด** ครอบคลุม humanoid ผู้เล่น/NPC; ท่า optional เป็นหัวข้อวิจัย ไม่ใช่ยืนยัน mechanic ใหม่เข้าเกม ใช้สาขาเดิมเท่านั้น

## สิ่งที่ได้จริง

| รายการ | จำนวน / สถานะ |
| --- | --- |
| Reference leads: เกม/sprite/video/rig/preset/mocap/เอกสาร/paper/skill | **92 แหล่ง** พร้อม URL/commit/retrieval status |
| Action specifications | **99 ท่า ใน11กลุ่ม**; มี phases/contact/event/จุดตรวจรายท่า |
| Acquired GLB animation records | **73**; ตัดrestpose2 เหลือ**71candidate motions** รวมdash6 |
| Actual new external rig evaluations | **639pose samples** พร้อมworld/local matrices, rest basis, native key times |
| Creator animated preview captures | **745native GIF exposures** /3คลิป พร้อมPTS/duration/order/pixel hashes |
| Fresh isometric sprite atlas study | **8action boards** /256unique grid cells (272action-cell uses) |
| Primary PDFs | **7ฉบับ**; อ่านส่วนวิธี/ข้อจำกัดที่เลือก ไม่อ้างreproduceทั้งpaper |
| Dataset audit | binding/clock/RGBA/structure/exclusions; **production=false** |
| ท่าเดินWที่เคยผ่าน | **13ไฟล์ unchanged** |
| Original new character motion / trained model / final modular factory | **ยังไม่มีการอนุมัติหรืออ้างว่าทำสำเร็จ** |

จำนวนแต่ละชนิดห้ามรวมเป็น “เฟรมถูกต้องทั้งหมด” ดู [corpus summary](corpus-summary.json), [audit](audit.json), [การตรวจW](protected-W.json) และ [regression tests](regression-tests.txt)

## อ่าน know-how และ dataset

- [KNOW-HOW: ผลิตและตรวจ sprite motion แบบละเอียด](KNOW-HOW.md)
- [99 motion recipes: เฟส/contact/event/QAแต่ละท่า](MOTION-RECIPES.md)
- [DATASET-CONTRACT: ที่มา/สิทธิ์/clock/annotation/splits/ข้อจำกัด](DATASET-CONTRACT.md)
- [REFERENCE-ANALYSIS: ข้อค้นพบจากไฟล์/โค้ด/ภาพจริง](REFERENCE-ANALYSIS.md)
- [PAPER-METHOD-NOTES: วิธีจากprimarypapersและการประยุกต์](PAPER-METHOD-NOTES.md)
- [SOURCES:92แหล่งและระดับหลักฐาน](SOURCES.md)
- [CLIP-BROWSER:71motion candidates/639poses](CLIP-BROWSER.md)
- [CAPTURE-BROWSER:745exposuresและทุกcontactsheet](CAPTURE-BROWSER.md)
- [PRODUCTION-PLAN: ลำดับทดลองหลายmotion/parts/ตัวละครใหม่](PRODUCTION-PLAN.md)
- [DASH-NOTES: source6คลิป/การเคลื่อนที่/contact/transitionที่ต้องตรวจ](DASH-NOTES.md)
- [Reusable SKILL.md](../../../skills/modular-eight-direction-sprites/SKILL.md)

## ภาพ/rigตัวอย่างที่เปิดดูได้เลย

| ตัวอย่าง | หลักฐาน |
| --- | --- |
| Run8ทิศของexternalisometric source | [board](sprite-boards/run.png) |
| Cast8ทิศของexternalisometric source | [board](sprite-boards/cast.png) |
| Swing /Shoot /Hit /Die | [swing](sprite-boards/swing.png), [shoot](sprite-boards/shoot.png), [hit](sprite-boards/hit.png), [die](sprite-boards/die.png) |
| Source chest interaction | [9real native-time samples](preset-boards/ual2-oga--Chest_Open.png) |
| Fresh source sword movement candidate | [9real native-time samples](preset-boards/ual2-oga--Sword_Regular_A.png); ไม่ใช่ท่าเก่าเรา/ไม่วัดbladecontact |
| Actual GIF preview exposures | [page1](captures/kaykit-preview-1/frames-review.png), [preview2](captures/kaykit-preview-2/frames-review.png), [preview3](captures/kaykit-preview-3/frames-review.png) |
| Creator GLBs/licenses | [UAL2](open-data/ual2-oga/UAL2_Standard.glb), [license](open-data/ual2-oga/License.txt), [legacyKayKit](open-data/kay-oga/KayKit_AnimatedCharacter_v1.2.glb), [license](open-data/kay-oga/License.txt) |

ฟอร์แมตอาวุธ/body/headจาก [Clint Bellanger’s creator archive](https://opengameart.org/content/isometric-hero-and-heroine) และ [Quaternius UAL2](https://opengameart.org/content/universal-animation-library-2) เป็นexternalstudy ไม่เปลี่ยนart styleเราและไม่เข้าshippingassetindex

ข้อพบสำคัญ: legacyKayKit1.2มีเพียง6skin jointsไม่มีโซ่ขา จึงตรวจขาซ้าย/ขาขวาจากrigนั้นไม่ได้ จำนวน161ในหน้าปัจจุบันเป็นคนละเวอร์ชันที่ยังไม่acquire ดู [bounded image review](image-review.json): boardที่ไม่ได้ตรวจทั้งชุดยังไม่ถือว่าตรวจผ่าน

PreviewGIFเป็นmontageหลายactor/titlechanges ไม่ใช่หนึ่งactionต่อเนื่อง10วินาที Sourcebonepositionsไม่ใช่contactsurfaces SourcePNGไม่มีnativeclockจึงไม่เดาFPS CurrentFlaredescriptorเป็นอีกversionแยกจากcreatorarchive

## Reproduce และตรวจซ้ำ

ต้องมีPython+Pillow, Blender4.3.2สำหรับsource evaluation และffmpeg/ffprobeสำหรับvideo capture ไม่มีpaid jobหรือdownloadedskillถูกexecute

จากrepo root:

```sh
python skills/modular-eight-direction-sprites/scripts/rpg-reference-audit.py --study research/sprite-animation/rpg-motion-foundation-v29 --out /tmp/rpg-corpus-audit.json
python -m unittest discover -s skills/modular-eight-direction-sprites/scripts/tests -p test_rpg_reference_audit.py -v
blender -b --python-exit-code 2 --factory-startup --python research/sprite-animation/rpg-motion-foundation-v29/sample-new-presets.py -- --study research/sprite-animation/rpg-motion-foundation-v29
python research/sprite-animation/rpg-motion-foundation-v29/render-preset-book.py
```

เปิดsourcehashes/clipinventory/samples/boardsก่อนนำไปใช้ ตัวsamplingเลือก9nativekeytimesต่อclipเพื่อoverview ไม่ใช่optimalproductionkeys ต้องsampleเพิ่มเติมจริงเมื่อเลือกmotionมาadapt

หน้าดูทีละเฟรม:จากfolderv29รัน `python -m http.server 8744 --bind 127.0.0.1` แล้วเปิด `http://127.0.0.1:8744/reference-reader.html` มีsourcePTS/exposure/ordinal/step/scrub/native1x/inspection0.25x ไม่มีSVG

ผลตรวจ: [12corpusnegative/structuretests](regression-tests.txt), [5actualdecoderregressions](decoder-regression-tests.txt), [12browserchecks](browser-review.json) ผ่านในขอบเขตที่ระบุ ไม่อนุมัติart/anatomy Browsercheckต้องมีPlaywright+Chromium;ตั้งPLAYWRIGHT_MODULE_PATH/CHROMIUM_EXECUTABLEเมื่อใช้เครื่องอื่น

สำหรับrefetchใหม่:fetch-evidence.py → acquire-open-samples.py → inspect-open-clips.py แล้วเก็บเป็นdatasetversionใหม่ อย่าoverwritepublishedreceiptแล้วเรียกversionเดิม Captureจริงใช้capture-reference.pyพร้อมsourceURLไปNEWfolder; losslessstorageตรวจRGBAทุกpixelก่อนแปลงWebP ไม่มีresample/warp/recenter

Localcacheเป็นfullsourcearticles/PDF/archives/rawPNGsและไม่push อ่าน/publishเฉพาะcitations/receipts/originalanalysis และlicensed selectedstudyassets คลังนี้ยังไม่training-readyหรือproduction-approved ไม่อ้างว่าดูทุกเกมหรือทำerror-freegenerationได้แล้ว
