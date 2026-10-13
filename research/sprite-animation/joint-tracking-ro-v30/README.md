# v30 — image joint review, Ragnarok coverage, current rig/presets

2026-10-13. ต่อจาก v29 โดยไม่ใช้ท่าฟันเก่าของเราเป็นต้นแบบ งานรอบนี้เป็นเครื่องมือและหลักฐานวิจัย ยังไม่มี animation ตัวละครใหม่ที่ผ่าน production

เปิด [grid viewer](joint-grid-review.html) ใน browser หลังดาวน์โหลดไฟล์ HTML: ภาพทั้งหมดฝังอยู่ในไฟล์ ไม่ต้องโหลด SVG หรือเชื่อมต่อบริการอื่น GitHub แสดง HTML เป็น source จึงต้องเปิดไฟล์ locally ใช้ [ภาพหน้าจอเครื่องมือ](grid-browser-review.png) ดูหน้าตาได้ทันที

- [Know-how และขอบเขต source of truth](KNOW-HOW.md)
- [RO inventory, action/direction/part findings](RAGNAROK.md)
- [Animation, rig, preset และ tracking research](METHODS-AND-PRESETS.md)
- [ผลวัด tracking พร้อม coverage](assisted-tracking-benchmark.json), [baseline ที่ยังผิด](tracking-benchmark.json)
- [RO เดินครบทุก exposure / 8 ทิศ](ro-grids/swordman-male-full-block01.png), [โจมตีครบทุก exposure / 8 requested ทิศ](ro-grids/swordman-male-full-block05.png)
- [Source bone grid 12 motions](preset-source-bone-grid.png), [173 serialized clip records](preset-clip-index.json)
- [ผลทดลอง DWPose จากภาพจริง](pose-model-image-review.png), [ค่าผิดพลาดเทียบ bone projection](pose-model-benchmark.json)

| สิ่งที่ทำจริง | ขอบเขต |
| --- | --- |
| RO 1,340 requests | 1,275 decoded, 65 HTTP failures; indexed 85 class families, 80 available / 5 unavailable |
| RO decoded exposures | 5,927decoded images/exposures:5,642timed +285untimed single images; fixed provider canvas, not official client timing |
| RO review books | 35 selected-exposure boards + 2 full-exposure boards; full raw raster banks excluded from Git |
| KayKit creator Free 1.1 | 14 CC0 GLB banks, 23 joints per bank; 173 records / 144 unique names / 1,397 evaluated poses |
| Clip classification | 153 motion-name candidates, 14 T-Pose records, 6 terminal/inactive pose-name records; no acting approval |
| Actual image tracking benchmark | 3 external clips × 16 renders on fixed 320×320 canvas; labelled-source keyframes 0/5/10/15 |
| Assisted proposals | p95 0.57–1.65px on retained subset, coverage 15–43%; all other points need review |
| DWPose experiment | ONNX/OpenCV CPU executed on 5 images; rendered benchmark errors too high, painted accuracy unknown |
| Tests | 15 Python regressions, 12 browser checks, 16 evidence-integrity checks; no anatomy/production acceptance |

Source-clock/bone/file truth exists. Hidden anatomical ownership in a drawing cannot be proved by a numerical fit or recoloring. This release explicitly refuses to call image tracking universally accurate. Keep source, pixel observations and artistic decisions separate.

Fresh external sword clips are allowed; old rejected own slash rigs/drawings remain excluded. Exact accepted v21 W 13 PNG/GIF files remain unchanged. Work and push only `research/modular-sprites-full-body-2026-10-11`.

Recheck: `PYTHONPATH=/tmp/astraeon-vision-deps python research/sprite-animation/joint-tracking-ro-v30/audit-v30.py` in this session. Install the optional [tested vision dependencies](../../../skills/modular-eight-direction-sprites/scripts/requirements-joint-review.txt) in a fresh environment for portable use. [Evidence manifest](evidence-manifest.json) binds published files; it excludes raw game archives, article caches and model weights.
