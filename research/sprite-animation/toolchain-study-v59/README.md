# ศึกษาและติดตั้ง Scenario / SPA / img2game2d

งานนี้ต่อจากv58ที่ผู้ใช้ปฏิเสธภาพตัวขาด: ใช้ตัวพร้อมชุดทั้งชิ้นต่อเฟรม หัวพร้อมผม อาวุธ และtrail ห้ามกลับไปประกอบแขนขาเป็นภาพสุดท้าย

| เครื่องมือ | ส่วนที่ใช้จริง | ขอบเขต |
|---|---|---|
| [Scenario Sprite Animation](https://github.com/scenario-labs/skills/tree/49dd26e47371163ae0020c7f5627d0993626bfc2/skills/scenario-sprite-animation) | ติดตั้งสกิลในโครงการ รัน grid-builder และตัวร่างคำขอหมัด4มุม/ยืน8มุม | ยังไม่ได้เชื่อมScenarioMCP/บัญชี ไม่ได้สร้างวิดีโอหรือใช้เครดิต ตัว cycle_sheets ที่ย้ายตำแหน่ง/กลับภาพ/แปลงพาเลตไม่ใช้กับเราตรงๆ |
| [SPA](https://github.com/aigengame/aseprite-automation/tree/ee2ea8f027bafdbed4f040c8288a1095b287e8b8) | ติดตั้งสกิลและCLI0.5.0ในPython3.13แยกจากระบบ | ต้องมีAsepriteแยกต่างหาก ทดสอบruntime API41 และไฟล์4เลเยอร์/16เฟรมพร้อมส่งออกจริงผ่านแล้ว ดูnative-roundtrip-review.json |
| [img2game2d](https://github.com/MrFaraidun/img2game2d/tree/aad3b73026eba631c47a3e674c98d048362cc6f0) | ติดตั้งสกิลพร้อมforge อ่านstate gate ตรวจintake/continuity และแพ็กภาพ | ไม่ใช้ procedural animator, layer decomposition, defringe หรือ normalization กับภาพของเราอัตโนมัติ |

สกิลต้นทางอยู่ `.agents/skills/` พร้อมcommitและlicense ไม่มีการแก้สกิลเก่าของโครงการ ใช้สกิลเชื่อมงาน `.agents/skills/astraeon-whole-body-workflow/SKILL.md` เพื่อรักษาข้อกำหนดของผู้ใช้

## สิ่งที่พบจากไฟล์จริง

img2game2d เดาสไตล์ท่าก้มนี้เป็น3d_renderedด้วยความมั่นใจ44% และเดามุมหน้าเป็นside ดูimg-style.json/img-views.json จึงมีmanual-analysis.jsonแก้ความหมายโดยไม่แก้ภาพ ผลheuristicไม่เป็นตัวตัดสินมุมหรือกายวิภาค

ตัวgenerate_spritesheetต้นทางใช้maskตัวเองตอนpasteRGBA ทำให้alphaเปลี่ยนจริงทุก16ช่อง เก็บผลก่อนแก้ไว้ในimg-upstream-atlas-negative.json แก้เพียงบรรทัดpasteในสกิลที่ติดตั้ง พร้อมLOCAL-PATCHES.json ตัวเชื่อมใช้เวลาแต่ละเฟรมจากต้นฉบับแทนค่าfps12ที่ต้นทางใส่มา

ผลแพ็กหลังแก้:16ช่องRGBAตรงทุกไบต์ เวลา90×15+550=1900ms ไม่มีการย้าย ย่อขยาย หรือดัดภาพแต่ละเฟรม ดูlossless-pack/pack-review.json และlocal-integration-review.json มี5กรณีลบตรวจข้อมูลเสีย/เพิ่มชิ้นเข่า/สเกลแคนวาส/แหล่งภาพเปลี่ยน/ตัวแบบsegmented

ตัวcontinuityของimg2game2dให้0.816และไม่ผ่าน สอดคล้องกับปัญหาท่าก้มเดิม ไม่ได้ปรับthresholdเพื่อให้ผ่าน ค่าIoUนี้ไม่ใช่การยืนยันข้อต่อหรือเกณฑ์เดียวตัดสินท่าทาง ชุดv58ยังไม่ผ่านmotion/contactและhead-swap

## คำสั่งใช้ซ้ำ

ติดตั้งCLIในโครงการใหม่ด้วย `python tools/setup-sprite-tools.py` ถ้าต้องสร้างAsepriteสำหรับใช้ในเครื่อง ให้ใช้ `--build-aseprite` ต้องมีuv, Python3.13, g++, git, pkg-config และdpkg-deb ซอร์สกับไบนารีอยู่เฉพาะwork/ ไม่แจกไบนารีAsepriteในbranch

จากรากโครงการ:

```sh
python tools/whole-body-toolchain.py pack --clip research/sprite-animation/whole-body-v58/pickup-S-four-slot.json --frames research/sprite-animation/whole-body-v58/frames/full --out work/my-pack
python tools/whole-body-toolchain.py editable --clip research/sprite-animation/whole-body-v58/pickup-S-four-slot.json --out work/my-editable --spa work/tool-runtime/spa-env/bin/spa --aseprite work/tool-runtime/aseprite-build/bin/aseprite
```

เลือกโฟลเดอร์ปลายทางใหม่เพื่อรักษาต้นฉบับ `pack` ตรวจpixel/clock ส่วน`editable`จัดไฟล์nativeด้วยSPA แล้วต้องตรวจไฟล์saved/exportจริงอีกครั้ง ตัวเชื่อมไม่อนุมัติภาพศิลป์ ไม่วาดท่าที่หาย และไม่ทำhead-swapให้ถูกโดยอัตโนมัติ

สถานะstateของimg2game2dยังเหลือmanual production analysis/spec/build/review ไม่ได้ใส่doneให้ทั้งpipelineเพื่อให้ดูครบ การแพ็กครั้งนี้เป็นdiagnosticของเฟรมที่มีอยู่ ไม่ใช่ส่งออกงานproduction

## ปัญหาติดตั้งที่แก้แล้ว

การcloneSPAแบบตื้นได้fixtureเป็นตัวชี้GitLFSขนาด129ไบต์ แทนไฟล์Asepriteจริง1404ไบต์ ทำให้probeไม่ยอมรับการอ่าน/สร้างเอกสาร ใช้wheelPyPIทางการ0.5.0ซึ่งมีข้อมูลครบแล้ว ตรวจโค้ดPython/Lua250ไฟล์ตรงกับcommitที่อ่านทั้งหมด ดูspa-wheel-provenance.json และspa-source-wheel-code-review.json ไม่ได้แก้probeให้ข้ามเงื่อนไข

PNGต้นทางไม่ได้ระบุโปรไฟล์สี แต่เอกสารnativeเริ่มเป็นsRGBและการเปิดผ่านบางoperationกลับไปใช้ค่าเริ่มต้น การกำหนดNoneครั้งเดียวจึงไม่พอ เก็บสองกรณีล้มเหลวไว้ในnative-profile-negative/และnative-profile-none-negative/ ตัวเชื่อมสุดท้ายทำสำเนาPNGสำหรับนำเข้าโดยใส่metadata sRGBและตรวจว่าทุกRGBAตรงต้นฉบับ ไม่มีการแปลงสีหรือเปลี่ยนภาพ ดูnative-editable/import-profile-assignment.json ส่วนPNGที่มีICCแบบอื่นจะปฏิเสธจนกว่าจะมีตัวเชื่อมโปรไฟล์ที่ตรวจแล้ว

ตัวbootstrapสำหรับbuildAsepriteใช้สูตรDebianLinuxของเครื่องนี้ ไม่ได้ทดสอบข้ามระบบ หากมีAsepriteอยู่แล้วให้ระบุpathของตัวเอง ไม่ต้องbuildซ้ำ ไบนารีอยู่เฉพาะwork/และไม่ได้แนบเผยแพร่ ส่วนไฟล์งาน.asepriteเป็นภาพต้นฉบับของโครงการ

หลังเผยแพร่เคสนี้ให้ใช้เป็นหลักฐานอ่านอย่างเดียว งานแก้ภาพรอบใหม่ไปwork/หรือเคสv60 ห้ามรันauthoringทับหลักฐานเดิม

## ไฟล์แก้ไขที่ตรวจแล้ว

[ดาวน์โหลดไฟล์Aseprite4เลเยอร์/16เฟรม](native-editable/pickup-four-slots.aseprite) · [ผลตรวจnativeและPNGส่งออก](native-roundtrip-review.json)

ชั้นtrail/weaponเว้นว่างสำหรับท่าก้มมือเปล่า ชั้นbodyเป็นภาพตัวเต็มต่อเฟรม ไม่มีการประกอบเข่าหรือแขนระหว่างเล่น ชั้นheadยังเป็นmaskทดลองจากv58 จึงยังไม่อนุมัติการเปลี่ยนหัว เป้าหมายของไฟล์นี้คือให้แก้ภาพและส่งออกซ้ำได้สะดวก ไม่ใช่ประกาศว่างานศิลป์ใหม่ผ่านแล้ว

ใช้`work/tool-runtime/spa-env/bin/python`แทน`python`ในคำสั่งตัวเชื่อมได้หากPythonหลักยังไม่มีPillow/numpy ตัวsetupติดตั้งdependenciesของตัวช่วยไว้ในvenvเดียวกัน
