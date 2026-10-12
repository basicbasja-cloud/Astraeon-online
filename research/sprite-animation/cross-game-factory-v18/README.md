# Production research และ reference book v18

ผู้ใช้อนุมัติ [ต้นแบบเดินตัวตรงW v17](../ro-gait-v17/evidence/user-approved-upright-source.json) แล้ว และขอศึกษาเกมหลายแบบ เทียบshot/frameจริง ลงลึกถึงproduction/GitHub skills เพื่อสร้างfactoryของเรา รอบนี้ให้RO/RO3/ToSและภาพต้นแบบของเราเป็นเกณฑ์คุณภาพ;ตัวอย่างเล็กใช้เรียนระบบ ไม่ลดรายละเอียดงานเรา

[Reference reader ทีละเฟรม](reference-book.html) · [Production findings/ไกด์ใช้ซ้ำ](../../../skills/modular-eight-direction-sprites/references/cross-game-production.md) · [แผนpart/frameของต้นแบบที่อนุมัติ](factory-plan.json)

**ยังไม่เป็น factory ผลิตภาพสำเร็จ**:315 samplesใหม่,source/code auditsและjob plannerเป็นฐานทดลอง ภาพวาดv17ทั้งสองรอบยังไม่ผ่าน;ไม่มีaccepted painted part bankครบหรือnew generation backendที่ผ่านproduction

## Ref ใกล้คุณภาพงานเรา

- **Tree of Savior**: [Art Director MAGGI](https://treeofsavior.com/page/news/view.php?n=337) อธิบายquarter-view/readabilityและhand-drawn textures;[Swordsman official motions](https://treeofsavior.com/page/news/view.php?n=541) มีแหล่งGIFที่ศึกษาไว้ก่อนหน้า เปิดตรวจtrailer1920×1080ที่เก็บไว้เพิ่ม [30framesช่วงgroup idle](captures/tos-group-idle/frames-review.png) ไม่อ้างว่าเป็นstridecycleหรือได้hiddenskeleton
- **RO3**:ตรวจ [GungHo official announcement/PDF](https://www.gungho.co.jp/jp/news/ccjg5s00000000wh.html) และดูkeyvisualpage2จริง ใช้ดูfinish/costume ไม่แทนgameplaymotion ยังไม่ได้แคปRO3videoทีละเฟรมในรอบนี้
- **RO**:ใช้native8-poseWที่เก็บไว้กับprioraction-directionaudits;motionที่จะวาดทับต่อยังเป็นsource16เฟรมที่คุณอนุมัติ
- เพิ่มHades,Dead Cells,Project Terra/Alabaster Dawn,Vanillaware/Odin SphereและTalesWeaverเป็นproduction/qualityreferencesตามevidence scopeในไกด์ ไม่กล่าวว่าframe-studiedทุกเกมแล้ว

## Shot/frame ที่ตรวจจริง

| ชุด | จำนวน / เวลา | สิ่งที่เห็นและข้อจำกัด |
| --- | --- | --- |
|[CrossCode side-door](captures/crosscode-side-door/frames-review.png)|56 /1600ms|ช่วงยืน/เดินสั้นเข้าประตู ตามด้วยfade/roomchange ไม่เป็นloopหรือroottrajectoryเดียว|
|[CrossCode combat1](captures/crosscode-combat/frames-review.png),[2](captures/crosscode-combat/frames-review-02.png)|93 /3720ms|motion/FXหลายช่วง;ตัวละครถูกแสง/numbersบังมาก ไม่ให้hip/griptruth|
|[ToS group shot](captures/tos-group-idle/frames-review.png)|30 /1000ms|sourcePTS7.6–8.6s,fixedcrop550×450จาก1920×1080 ส่วนใหญ่held/idle-like ใช้รายละเอียด/volume|
|[Billboard front gait1](captures/billboard-front-gait/frames-review.png),[2](captures/billboard-front-gait/frames-review-02.png)|98 /10080ms|independentrigprototype มีgaitและinitialhold ไม่ใช่art targetหรือdirectionturnaroundที่ยืนยัน|
|[Billboard editor](captures/billboard-editor-keys/frames-review.png)|24 /1520ms|UI/key/partmechanicsช่วงสั้น;ไม่ได้ยืนยันfullstride/contact|
|[Valyria Wwalk](captures/valyria-walk-west/frames-review.png)|6 /780ms configured|actualatlas+Lua130msแต่ละexposure;ID13ซ้ำสองครั้ง ไม่ใช่gameplaycapture|
|[Valyria attack](captures/valyria-attack/frames-review.png)|8 /580ms finiteprefix +terminalhold|configured75/75/75/200/40/40/75 แล้วholduntilstatechange ไม่มีinventedduration/loop|

ทุกcaptureเก็บPTS/frameordinal/duration/SHAและfixedcrop ไม่มีper-framecenter/fit/mirror รวม301actualcontainer/video samples +14atlas/script reconstructed exposures =315 ใหม่ ไม่รวม22thumbnailreconหรือRO/ToSเก่าในยอดใหม่

ชื่อreconที่เดาไว้ก่อนถูกแก้หลังดูboardจริง:group-walk→group-idle,turn→front-gait,editor-walk→editor-keys ดูobserved-scope.jsonของแต่ละชุด ไม่เอาป้ายชื่อเก่ามาอ้างว่าเห็นmotionที่ไม่ได้เห็น

## ลงถึงsource/timeline/layers

**Flare**:อ่าน8itemdescriptorsที่commit`af6eee6`,eight-facinglayerlistและengineparser/setup/avatarจริง [descriptor coverage](evidence/flare-defined-coverage.json) ทุกactionที่ตรวจมีครบindex0–7 ไม่เดาว่าindex0คือทิศใด ตัวอย่างrun8poses/533ms,swing4/400ms offsetของpackedrectสำคัญกว่าการfitbounds ต่อทิศlayerorderต่างกัน;engineเตือนhero_layerslegacyและมีfallback จึงต้องpincontent+engineadapter ไม่copyformatเก่าไปอ้างว่าเป็นlatestlivepipeline

สามlargebodyatlasesคืนemptycontentจากconnector และblobreadไม่รองรับbinary จึงยังไม่ประกอบfullcharacterFlare มีhead/hands/weaponจริงเพื่อศึกษาพาร์ต แต่ไม่ส่งpartialbodyเป็นเกมcapture

**Valyria Tear**:ที่commit`1c882ef`แยกbody/steelweapon128displayแต่64nativeatlas [body/weapon/diagnostic overlay](evidence/valyria-body-weapon-board.png) overlayเป็นdiagnosticเท่านั้น ไม่อ้างrecoveredenginedraworder อ่านattackcontrollerพบslashthreshold`>410`,damage`>505`,stateleave`>730`;เวลาจริงขึ้นกับUpdateTime ไม่ใช้GIFdurationแทนgameplayeventclock ต้นฉบับlicensesอ่านจาก`LICENSES.txt`;READMElinkเก่าไม่มีfileจริง ไม่importassetsเข้าเกมเรา

**GitHub skills**:อ่านSKILL+implementationของ [sprite-gen](https://github.com/aldegad/sprite-gen/tree/611813b3f9d2069073cca8587e99647f8f184707),[AI-Sprite-Animation](https://github.com/JatCool/AI-Sprite-Animation/tree/3818664861613905a377eca26c4ea940c06a646d),[pixel-art skill](https://github.com/ervareza/agent-skill-pixel-art/tree/0de5e49a9ce9c1a326910b4efe3420c030ce3856) ไม่install/runprovider/Unityตามskillที่อ่าน เป็นresearchdata อ่านcodeพบcontactROIและlegbandsมีข้อจำกัด,near/farไม่ใช่ownerL/R,fillvacatedcellsไม่ให้hiddenpartsครบ,palette/gridQAไม่ตรวจanatomyหรือacting ไม่รับคำโฆษณาflawlessเป็นหลักฐาน

[Pinned snapshots/receipts](evidence/connector-receipts.json) · [page downloads](evidence/download-pages.json) · [source downloads](evidence/pinned-downloads.json) · [large tree archives](evidence/tree-archives.json) · [network block](evidence/blocked-actions.json)

ผ่าน142Python regression checks รวมactualfixture/negative testsเรื่องstalebindings,facing,hairvariants,repeatedIDs,terminalholds [ผลทดสอบ](evidence/regression-check.txt) ไม่เท่ากับผ่านanatomy/production

## เริ่มfactoryแบบผูกกับsourceจริง

[Actual source inventory](evidence/actual-source-inventory.json) เปิด`.blend`ที่approvedซ้ำ:170meshes,67bones,13sourceitemgroups,no unweightedvertices;activeactionต้องเป็น`original.compact.contact-walk` hair.silver/auburnเป็น2itemsของslotเดียว จึง12logicalcategories

`factory-plan.py`ตรวจapproval/source/frames/clock/inventoryhashes แล้วcompile16posekeys/208part-framejobsบนcanvas512จากactualgroundreceipt ไม่ใช้motion.camera256ที่เป็นmetadataเก่า ทุกjobยังNOT_AUTHORED,no new-artapproval แผนเก็บowner/sourceprojection/rootแต่ละphaseเพื่อให้backendวาดทับและตรวจได้ตรงกัน

```bash
blender -b --python-exit-code 2 --python skills/modular-eight-direction-sprites/studies/walk-test/inspect-factory-source.py -- \
 --approval research/sprite-animation/ro-gait-v17/evidence/user-approved-upright-source.json --out /tmp/factory-source-inventory.json
python skills/modular-eight-direction-sprites/scripts/factory-plan.py \
 --contract research/sprite-animation/cross-game-factory-v18/evidence/factory-contract.json --out /tmp/factory-plan.json
python skills/modular-eight-direction-sprites/scripts/reference-atlas.py \
 --contract research/sprite-animation/cross-game-factory-v18/evidence/valyria-attack-contract.json --output /tmp/valyria-attack-study
python skills/modular-eight-direction-sprites/studies/walk-test/build-reference-book.py --study research/sprite-animation/cross-game-factory-v18
PYTHONPATH=/tmp/astraeon-vision-deps python -m unittest discover -s skills/modular-eight-direction-sprites/scripts/tests -p 'test_*.py'
```

แผนยังขาดbackendที่รักษาgeometryกับภาพคุณภาพเรา,completepaintedparts/hiddencontent,wardrobeextremechecks,otherfacings/actionsและruntimecontact/eventadapter ต้องทดลองสิ่งเหล่านี้จริงก่อนเรียกว่าfactoryproduction ไม่ทำให้approvedsourceกลายเป็นapprovedpaintedpartsอัตโนมัติ

Reference readerให้step/nativePTS/zoomและเล่นboundedclipครั้งเดียว terminalholdไม่สร้างloop;CLIตรวจ315framehashesกับsyntaxแล้ว **browserbehaviorยังไม่ได้verify** เพราะChromiumlaunchล้มเหลวด้วยsocketpermissionในsandbox [status](evidence/browser-status.json) ไม่อ้าง10browserchecksในscriptที่รันไม่ถึงpage

Network-shellดาวน์โหลด2articlesถูกautomaticapprovalreviewหยุดเพราะusagelimit ไม่ได้รันและไม่retry ไม่มีการตัดสินว่าwebunsafe งานlocalและread-onlyconnectorsทำต่อได้ Currentresearchbranchเท่านั้น;ก่อนหน้าpushยังpendingdestinationconfirmation
