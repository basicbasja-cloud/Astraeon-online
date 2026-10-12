# เดินตัวตรงและก้าวกระชับ v17

ผู้ใช้ปฏิเสธความสมูทของ v16 และถามว่า **ทำไมต้องย่อง แทนที่จะตัวตรงแบบ RO** รอบนี้แก้ท่าที่ source จริงก่อน แล้ววาดทับและตรวจซ้ำ ภาพเจนทั้งสองรอบยังไม่ผ่าน ไม่ย้ายคำอนุมัติขาจาก v12/v13 มาที่ภาพใหม่

[GIF ต้นแบบเดินตัวตรง16เฟรม](upright-source-800ms.gif) · [เทียบ RO / source / v16 / ภาพใหม่ทีละเฟรม](frame-review.html) · [ภาพวาดทดลอง8เฟรม—ยังไม่ผ่าน](candidate1/walk-source-cadence.gif) · [ไกด์ใช้กับตัวอื่น](../../../skills/modular-eight-direction-sprites/references/upright-compact-gait.md)

## เปลี่ยนอะไรที่ source

ท่าเอน preset เดิมไม่ใช่ข้อกำหนดของ sprite ใช้ neutral-rest spine/neck/Head แทน ลดก้าว ยกเท้าต่ำ และเขียนทางเดินเท้า/heel-toe roll/สะโพกใหม่ด้วย fixed-length IK ส่วนแขนใช้ template เดิมที่ลด amplitude ไม่ freeze body ทั้งตัว

- .8s /2ก้าว /stride.42 /stance60% /swing height.040 /pelvis bob±.004 world
-129bake keys;16actual export phases;257dense sole samplesจากไฟล์ที่เปิดใหม่
-จริง LEFTใกล้ /RIGHTไกล กล้องWเดิม ไม่มีmirror
-trial pelvis.584 unreachable:ปฏิเสธไม่saveไม่stretch;ปรับ.570และneutral thigh attachmentสำเร็จ
-`source-rig/`เป็นdraftกระชับแต่ยังเอน; **ต้นแบบที่ใช้จริงคือ `upright-source-rig/`**

[กระดูก/meshต้นแบบ8ช่วง](evidence/upright-eight-guides.png) · [editable rig](upright-source-rig/original-modular-walk.blend) · [motion](upright-source-rig/motion.json) · [actual source/floor receipt](source/source-ground.json)

## ตรวจซ้ำต้นแบบ ไม่อนุมัติภาพแทน

[Hash-bound source contract](evidence/source-contract.json) · [ผลคำนวณจริง](check/source-check.json)

| ตรวจ | ผล source จริง |
| --- | ---: |
|แนวpelvis→neck sagittal tilt|4.1215–4.1224°|
|minimum soleZ ที่257เวลา|.0009604world|
|ทั้งสองเท้ายกเกิน.015world|0candidate|
|fixed heelvertex drift ช่วงวางราบที่วัดได้|สูงสุด.00000355world|
|endpoint joint error รอบin-place|.000000688world|

ช่วงrightที่ขอบเริ่มคลิปมีจุดเดียว ตรวจ drift ไม่ได้ เก็บเป็นunevaluable ส่วนช่วง111samplesของแต่ละข้างวัดได้จริง ไม่เอาlowestvertexที่เปลี่ยนตำแหน่งมาทำcontactlock ไม่ยืนยันrolling contact/แรงรับน้ำหนัก/balance/ภาพเจน/ความเร็วเกม

[Metadata scope](evidence/source-metadata-scope.json) แยกhistorical template fieldsจากการauthorใหม่ `source_pose_edited:false` ในexportหมายถึงexportไม่แก้ไฟล์ที่เปิด มิได้หมายถึงsourceยังเป็นv9 เลือกactive action `original.compact.contact-walk` หากexportต่อ

## วาดทับแล้วตรวจ ผลยังไม่ผ่าน

[Provenance/prompts/hashes](provenance.json) เก็บ2jobs ใช้sourceของเราและappearanceของเราเท่านั้น ไม่ใส่ภาพRO/tutorialเข้าgenerator

| รอบ | ผล |
| --- | --- |
|1 [raw](evidence/attempt1-raw.png)|แถวบนตัวตรงขึ้น แถวล่างยังเอน บางphaseซ้ำ/ไม่ตามขาไกล source; packequalgridได้แต่placementยังผิด|
|2 [raw](evidence/attempt2-raw.png)|editทั้งชุดยังซ้ำท่าและไม่ได้ทำfar-rightleadingชัดเจน;equalgridpackปฏิเสธเฟรม1ชนขอบ ไม่มีclip/fitเพื่อให้ผ่าน|

[ภาพทั้งหมดรอบ1](candidate1/frames-review.png) · [actual-pixel continuity](check/art-continuity.json)

ROIผมเลือกจากภาพใหม่จริง แยกจากjoints;เกณฑ์เตือน20pxไม่เพิ่มเพื่อให้ผ่าน **4→5=40.66px /8→1=32.20px** ภาพใหม่8เฟรมกับเก่า16เฟรมจึงไม่อ้างค่าต่อedgeเป็นการเปรียบเทียบเท่ากัน ยังไม่มีvisible root/proximal chain/contact observationsครบ ตัวcheckerไม่รู้เจ้าของขาอัตโนมัติ ผลsourceผ่านไม่ย้ายเป็นanatomy/acting PASS

ภาพทดลองใหม่มี8posesเพื่อลองphase economy แบบcaptureROที่มี8 ไม่ใช่downsampleจากภาพเก่า16 ต้นแบบยังมี16samples ทุกbankในviewerเล่น800msเท่ากันเป็นค่าเริ่มต้น;เปลี่ยนROnative600msให้ช้าลงในcontrolนี้อย่างเปิดเผย การmapRO `[2,3,4,5,6,7,0,1]`เป็นapproximate visual phase windows ไม่ใช่กระดูก/contactที่กู้คืน

[Decoded clock](check/cadence.json):ภาพใหม่GIF/APNG/WebPจริง8×100ms และsourceGIF16×50msทั้งหมด800ms uniform นี่ตรวจclockเท่านั้น ยังไม่สมูท/ถูกanatomyโดยอัตโนมัติ `walk-ro-cadence`เป็นชื่อlegacyในpacker ไม่ใช่หลักฐาน800msคือROnative

ผ่าน130Python regression checksกับ12browser behavior checks;ไม่ได้อนุมัติภาพ [Python](evidence/regression-check.txt) · [Browser](browser-check/browser-report.json) · [scriptที่รันจริง](evidence/browser-check.cjs)

## รีเสิร์ชและความรู้ใช้ซ้ำ

เปิดอ่านwritten tutorials ของAnimation Mentor เรื่องbasic human walkกับsneak walk;applyความต่างpostureและsource-first phase blocking ไม่ได้ดูembedded videos/ถ่ายcaptureใหม่ [scope](evidence/new-research.json) ตรวจnative8ROcaptureที่เก็บไว้เทียบกับsheetv16จริง ไม่ใช้assetตัวละครเดิมในgamebranches

บันทึกบทเรียน: upright postureเป็นauthoring choice;เพิ่มFPS/ทำGIFclockสม่ำเสมอไม่แก้motion;ต้องแยกsource-contact checkออกจากภาพใหม่ การเจนทั้งsheetยังไม่รักษาsourcegeometryครบ ปัจจุบันยังไม่มีaccepted painted modular parts หรือmass-production backend

## ทำซ้ำจากrepo root

```bash
# ต้องfresh output path;ต้นฉบับv9ไม่ถูกแก้
blender -b --python-exit-code 2 --python skills/modular-eight-direction-sprites/studies/walk-test/author-compact-walk.py -- \
  --blend research/sprite-animation/walk-test-v9/original-modular-walk.blend --output /tmp/upright-source-rebuild
blender -b --python-exit-code 2 --python skills/modular-eight-direction-sprites/studies/walk-test/export-ground-walk.py -- \
  --blend /tmp/upright-source-rebuild/original-modular-walk.blend --output /tmp/upright-export-rebuild --count 16 --dense-count 257 --view W
python skills/modular-eight-direction-sprites/scripts/compact-gait-check.py \
  --contract research/sprite-animation/ro-gait-v17/evidence/source-contract.json --out /tmp/upright-source-check.json
PYTHONPATH=/tmp/astraeon-vision-deps python skills/modular-eight-direction-sprites/scripts/walk-continuity.py \
  --observations research/sprite-animation/ro-gait-v17/evidence/continuity-case.json --out /tmp/upright-art-continuity.json
python skills/modular-eight-direction-sprites/studies/walk-test/build-upright-review.py \
  --study research/sprite-animation/ro-gait-v17 --candidate research/sprite-animation/ro-gait-v17/candidate1
python -m unittest discover -s skills/modular-eight-direction-sprites/scripts/tests -p 'test_*.py'
```

Source checker needs a newly hashed contract if usingrebuilt files;don't reuseoldhashes onnewoutputs. Rebuildsource actionmathematics is tested; imagegen outputs are retained stochastic attempts, not reproducible guaranteed pictures. Currentbranchonly;Gitpush remainsblocked by priorauto-review pendingexplicitdestinationconfirmation.
