# Motion recipes —99 research action specifications

Phase/contact/event ในเอกสารนี้เป็น specification ที่เสนอ ไม่ใช่ labels ที่ตรวจครบจาก ref แล้ว จำนวนภาพ/exposure/facing ยังต้องทดลองตามท่า; conditional ไม่ใช่การเพิ่ม mechanic เข้าเกม เพิ่มdashเป็นoptionalresearchตามคำสั่งล่าสุด

ใช้ร่วมกับ KNOW-HOW / DATASET-CONTRACT / REFERENCE-ANALYSIS ไม่ใช้ท่าโจมตีเก่าของเราเป็น source

## idle —4 specifications

ตรวจเท้ารับน้ำหนักเดิม, head/torso breathing แยกจาก origin, loop/return และ asymmetry; เริ่มด้วย native game-scale view ไม่มี FX

### idle.relaxed — ยืนปกติ

- ขอบเขต: core; ทิศที่เสนอ: 8-proposed
- เฟส: settle → breath → settle
- Contact ที่ต้องได้หลักฐาน: both soles
- Event candidates: none
- จุดตรวจเฉพาะ: อย่าเพิ่มเด้งจากการจัดภาพ; หายใจที่ทรวงอกไม่ขยับ origin
- Reference leads: ual2-oga, kay-itch, lpc, ro-act (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### idle.combat — ยืนพร้อมสู้

- ขอบเขต: core; ทิศที่เสนอ: 8-proposed
- เฟส: ready → small weight shift → ready
- Contact ที่ต้องได้หลักฐาน: soles;weapon grip
- Event candidates: none
- จุดตรวจเฉพาะ: คุม guard กับระยะศอก; ห้ามอาวุธหลุดจากมือ
- Reference leads: ual2-oga, kay-itch, lpc, ro-act (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### idle.look — มองซ้ายขวา

- ขอบเขต: core; ทิศที่เสนอ: 8-proposed
- เฟส: neutral → look → return
- Contact ที่ต้องได้หลักฐาน: soles
- Event candidates: none
- จุดตรวจเฉพาะ: หัวกับตาแยกจาก facing ตัว; ไม่เปลี่ยนข้างอุปกรณ์
- Reference leads: ual2-oga, kay-itch, lpc, ro-act (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### idle.fidget — ท่าพักเล็กน้อย

- ขอบเขต: core; ทิศที่เสนอ: 8-proposed
- เฟส: neutral → gesture → return
- Contact ที่ต้องได้หลักฐาน: soles
- Event candidates: none
- จุดตรวจเฉพาะ: ใช้ variant เป็นครั้งคราวไม่ต่อ loop กระตุก
- Reference leads: ual2-oga, kay-itch, lpc, ro-act (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

## locomotion —7 specifications

จด support intervals ทั้งสองเท้าและworld movement mode; trace pelvis–thigh–knee–boot ตรง crossing ทุกเฟส; start/stop/turn ต้องตรง loop phase

### walk.loop — เดินบนพื้นเรียบ

- ขอบเขต: core; ทิศที่เสนอ: 8-proposed
- เฟส: L-contact → L-support → R-contact → R-support
- Contact ที่ต้องได้หลักฐาน: alternating soles
- Event candidates: footstep
- จุดตรวจเฉพาะ: ต้องเห็นการสับขา; pelvis สูงขึ้นลงตามท่าไม่ตาม bbox
- Reference leads: ual2-oga, kay-itch, flare-content, ro-act (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### walk.start — เริ่มเดิน

- ขอบเขต: core; ทิศที่เสนอ: 8-proposed
- เฟส: idle → weight shift → first contact → walk
- Contact ที่ต้องได้หลักฐาน: support sole
- Event candidates: footstep
- จุดตรวจเฉพาะ: ออกจากขารับน้ำหนักจริงไม่เริ่มวงจรสุ่มเฟส
- Reference leads: ual2-oga, kay-itch, flare-content, ro-act (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### walk.stop — หยุดเดิน

- ขอบเขต: core; ทิศที่เสนอ: 8-proposed
- เฟส: stride → decelerate → settle
- Contact ที่ต้องได้หลักฐาน: incoming sole;both soles
- Event candidates: footstep
- จุดตรวจเฉพาะ: คงจุดสัมผัสสุดท้ายและเปลี่ยนความเร็วโลกพร้อมกัน
- Reference leads: ual2-oga, kay-itch, flare-content, ro-act (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### turn.in_place — หันอยู่กับที่

- ขอบเขต: core; ทิศที่เสนอ: 8-proposed
- เฟส: plant → pivot → replant
- Contact ที่ต้องได้หลักฐาน: support sole or toe
- Event candidates: none
- จุดตรวจเฉพาะ: ห้าม mirror; yaw กับเท้าต้องสอดคล้อง ไม่เปลี่ยนผ้าสะโพก
- Reference leads: ual2-oga, kay-itch, flare-content, ro-act (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### turn.walking — เลี้ยวระหว่างเดิน

- ขอบเขต: core; ทิศที่เสนอ: 8-proposed
- เฟส: stride → curve → new facing
- Contact ที่ต้องได้หลักฐาน: alternating soles
- Event candidates: footstep
- จุดตรวจเฉพาะ: เลือกทิศใหม่ด้วยกฎมุม/เฟสไม่ตัดสู่ขาฝั่งเดียวซ้ำ
- Reference leads: ual2-oga, kay-itch, flare-content, ro-act (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### locomotion.backstep — ถอยหนึ่งก้าว

- ขอบเขต: core; ทิศที่เสนอ: 8-proposed
- เฟส: load → back contact → settle
- Contact ที่ต้องได้หลักฐาน: alternating soles
- Event candidates: footstep
- จุดตรวจเฉพาะ: เป็นก้าวธรรมดา ไม่เป็น dash แฝง
- Reference leads: ual2-oga, kay-itch, flare-content, ro-act (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### locomotion.strafe — ก้าวด้านข้าง

- ขอบเขต: core; ทิศที่เสนอ: 8-proposed
- เฟส: shift → side step → recover
- Contact ที่ต้องได้หลักฐาน: support sole
- Event candidates: footstep
- จุดตรวจเฉพาะ: ตัวเลือกของ combat controller; ไม่บิดเท้าสวนแนวเข่า
- Reference leads: ual2-oga, kay-itch, flare-content, ro-act (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

## equipment —5 specifications

สร้าง hand/prop/sheath attachment state ตามเวลา; ตรวจของซ้อน/ของหาย มือซ้ายขวาและ item extreme; controller event ผูก bank ใหม่จริง

### weapon.draw — ชักอาวุธ

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 8-proposed
- เฟส: reach → grasp → draw → ready
- Contact ที่ต้องได้หลักฐาน: soles;palm;scabbard
- Event candidates: equip_attach
- จุดตรวจเฉพาะ: ย้ายจาก sheath socket สู่ palm ณ event เดียว; ไม่ซ้อนดาบสองเล่ม
- Reference leads: kay-itch, larian, mixamo (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### weapon.sheath — เก็บอาวุธ

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 8-proposed
- เฟส: align → insert → release → relaxed
- Contact ที่ต้องได้หลักฐาน: soles;palm;scabbard
- Event candidates: equip_detach
- จุดตรวจเฉพาะ: แนวปลายดาบกับฝักต้องตรง; ไม่หมุนภาพดาบแบนแก้
- Reference leads: kay-itch, larian, mixamo (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### weapon.swap — เปลี่ยนอาวุธ

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 8-proposed
- เฟส: put away → equip → settle
- Contact ที่ต้องได้หลักฐาน: soles;grip
- Event candidates: item_switch
- จุดตรวจเฉพาะ: กำหนดว่าจะ hide/show เมื่อไร; สถานะเกมต้องตรงภาพ
- Reference leads: kay-itch, larian, mixamo (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### shield.raise — ยกโล่

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 8-proposed
- เฟส: ready → raise → brace
- Contact ที่ต้องได้หลักฐาน: soles;forearm strap
- Event candidates: guard_on
- จุดตรวจเฉพาะ: arm owner ชัดและโล่ไม่ข้ามฝั่ง
- Reference leads: kay-itch, larian, mixamo (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### shield.lower — ลดโล่

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 8-proposed
- เฟส: guard → lower → ready
- Contact ที่ต้องได้หลักฐาน: soles;forearm strap
- Event candidates: guard_off
- จุดตรวจเฉพาะ: กลับ state ได้โดยไม่วาร์ป shoulder
- Reference leads: kay-itch, larian, mixamo (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

## combat —16 specifications

หา complete performance ใหม่; ดู load→execution→follow→recovery, support/base/hips/chest/arm/grip; สร้าง per-pose weapon perspective ก่อน tail

### sword.diagonal — ฟันดาบเฉียง

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: ready → load → accelerate → cross → follow → recover
- Contact ที่ต้องได้หลักฐาน: soles;one-hand grip
- Event candidates: hit_open, hit_close, recover_end
- จุดตรวจเฉพาะ: ใหม่ทั้งหมด; ดูมือท่อนแขนดาบบ่าอกเชิงกรานร่วมกัน; ไม่ใช้ท่าโจมตีเก่า
- Reference leads: ual2-oga, kay-itch, flare-content, saint11, slyn-castlevania (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### sword.horizontal — ฟันแนวราบ

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: load → hip turn → cross → follow → recover
- Contact ที่ต้องได้หลักฐาน: soles;grip
- Event candidates: hit_open, hit_close
- จุดตรวจเฉพาะ: ถ่ายแรงด้วยการหมุน ไม่เหวี่ยงข้อมืออย่างเดียว
- Reference leads: ual2-oga, kay-itch, flare-content, saint11, slyn-castlevania (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### sword.overhead — ฟันจากบนลงล่าง

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: load up → drop cut → absorb → recover
- Contact ที่ต้องได้หลักฐาน: soles;grip
- Event candidates: hit_open, hit_close
- จุดตรวจเฉพาะ: วิถีปลายดาบกับ blade plane เปลี่ยนตาม perspective
- Reference leads: ual2-oga, kay-itch, flare-content, saint11, slyn-castlevania (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### sword.thrust — แทงดาบ

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: guard → load → extend → withdraw
- Contact ที่ต้องได้หลักฐาน: soles;grip
- Event candidates: hit_open, hit_close
- จุดตรวจเฉพาะ: คงปลายดาบตามแนวแทง ไม่ส่ายเป็นวง
- Reference leads: ual2-oga, kay-itch, flare-content, saint11, slyn-castlevania (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### sword.heavy — ฟันหนัก

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: deep load → commit → follow → slow recover
- Contact ที่ต้องได้หลักฐาน: soles;grip
- Event candidates: hit_open, hit_close, recover_end
- จุดตรวจเฉพาะ: anticipation และ recovery แตกต่างจากเบา; ไม่เร่งทุกเฟสเท่ากัน
- Reference leads: ual2-oga, kay-itch, flare-content, saint11, slyn-castlevania (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### sword.combo_link — เชื่อมคอมโบ

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: follow1 → redirect → load2 → cut2
- Contact ที่ต้องได้หลักฐาน: soles;grip
- Event candidates: combo_window, hit_open, hit_close
- จุดตรวจเฉพาะ: ปลายท่าแรกเชื่อมต้นท่าที่สองจริง ไม่วาร์ปกลับ ready
- Reference leads: ual2-oga, kay-itch, flare-content, saint11, slyn-castlevania (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### dual.attack — โจมตีสองอาวุธ

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: load → cutA → cutB → recover
- Contact ที่ต้องได้หลักฐาน: soles;two grips
- Event candidates: hit_A, hit_B
- จุดตรวจเฉพาะ: owner แยกและใบดาบไม่ทะลุมืออีกข้าง
- Reference leads: ual2-oga, kay-itch, flare-content, saint11, slyn-castlevania (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### greatsword.attack — ดาบสองมือ

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: two-hand load → body cut → follow
- Contact ที่ต้องได้หลักฐาน: soles;two grips
- Event candidates: hit_open, hit_close
- จุดตรวจเฉพาะ: ตรวจสอง palm บนด้ามเดียว และระยะห่างมือ
- Reference leads: ual2-oga, kay-itch, flare-content, saint11, slyn-castlevania (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### axe.attack — ขวาน

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: load → head swing → impact → recover
- Contact ที่ต้องได้หลักฐาน: soles;grip
- Event candidates: hit_open, hit_close
- จุดตรวจเฉพาะ: หัวอาวุธมีมวล/รัศมีต่างจากดาบ; ไม่เปลี่ยนแค่ภาพไอเทม
- Reference leads: ual2-oga, kay-itch, flare-content, saint11, slyn-castlevania (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### mace.attack — กระบอง

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: load → strike → rebound → recover
- Contact ที่ต้องได้หลักฐาน: soles;grip
- Event candidates: hit_open, hit_close
- จุดตรวจเฉพาะ: impact/rebound อ่านชัด; ไม่ยืม follow ของดาบโดยไม่ตรวจ
- Reference leads: ual2-oga, kay-itch, flare-content, saint11, slyn-castlevania (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### spear.thrust — แทงหอก

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: brace → extend → reach → withdraw
- Contact ที่ต้องได้หลักฐาน: soles;two grips
- Event candidates: hit_open, hit_close
- จุดตรวจเฉพาะ: มือหลังดัน มือหน้าประคอง; shaft ไม่หลุดสองมือ
- Reference leads: ual2-oga, kay-itch, flare-content, saint11, slyn-castlevania (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### spear.sweep — กวาดหอก

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: load → turn → sweep → recover
- Contact ที่ต้องได้หลักฐาน: soles;two grips
- Event candidates: hit_open, hit_close
- จุดตรวจเฉพาะ: คำนวณ sweep radius กับ ground clearance
- Reference leads: ual2-oga, kay-itch, flare-content, saint11, slyn-castlevania (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### dagger.stab — แทงมีด

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: close guard → short drive → withdraw
- Contact ที่ต้องได้หลักฐาน: soles;grip
- Event candidates: hit_open, hit_close
- จุดตรวจเฉพาะ: ท่าสั้นกระชับไม่เท่าฟันดาบยาว
- Reference leads: ual2-oga, kay-itch, flare-content, saint11, slyn-castlevania (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### unarmed.punch — ต่อย

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: guard → load → drive → retract
- Contact ที่ต้องได้หลักฐาน: soles;fist
- Event candidates: hit_open, hit_close
- จุดตรวจเฉพาะ: chain สะโพกถึงหมัดและอีกมือ guard; ไม่ hyperextend
- Reference leads: ual2-oga, kay-itch, flare-content, saint11, slyn-castlevania (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### unarmed.kick — เตะ

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: shift support → chamber → extend → retract → plant
- Contact ที่ต้องได้หลักฐาน: one support sole
- Event candidates: hit_open, hit_close
- จุดตรวจเฉพาะ: เข่ากับสะโพกแกนชัด; ไม่ปล่อย support ลอย
- Reference leads: ual2-oga, kay-itch, flare-content, saint11, slyn-castlevania (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### shield.bash — กระแทกโล่

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: brace → drive → recover
- Contact ที่ต้องได้หลักฐาน: soles;shield strap
- Event candidates: hit_open, hit_close
- จุดตรวจเฉพาะ: โล่และ forearm เดินทางเดียวกันไม่เป็น prop ลอย
- Reference leads: ual2-oga, kay-itch, flare-content, saint11, slyn-castlevania (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

## ranged —8 specifications

ติดตามสองมือและ prop/string; แยก prepare/draw/hold/release/reload; release projectile ครั้งเดียวจาก socket ณ event

### bow.prepare — เตรียมธนู/ลูก

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: ready → nock → aim
- Contact ที่ต้องได้หลักฐาน: soles;bow grip;arrow
- Event candidates: arrow_visible
- จุดตรวจเฉพาะ: owner มือคัน/สายคงที่; นิ้วและลูกธนูต้องอ่านได้
- Reference leads: kay-itch, tos-ranger, lpc, flare-content (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### bow.draw — ง้างธนู

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: nock → draw → full draw
- Contact ที่ต้องได้หลักฐาน: soles;bow;string
- Event candidates: draw_complete
- จุดตรวจเฉพาะ: มือคันธนูออกห่างมือดึงสาย; string endpoints ไม่ทะลุแขน
- Reference leads: kay-itch, tos-ranger, lpc, flare-content (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### bow.aim_hold — ค้างเล็งธนู

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: full draw → micro settle
- Contact ที่ต้องได้หลักฐาน: soles;bow;string
- Event candidates: none
- จุดตรวจเฉพาะ: hold ไม่กลับสู่วงจร draw และไม่เด้ง
- Reference leads: kay-itch, tos-ranger, lpc, flare-content (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### bow.release — ปล่อยธนู

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: full draw → release → follow → ready
- Contact ที่ต้องได้หลักฐาน: soles;bow grip
- Event candidates: projectile_release
- จุดตรวจเฉพาะ: projectile กับปล่อยสายตรง clock; ห้ามออกตั้งแต่ windup
- Reference leads: kay-itch, tos-ranger, lpc, flare-content (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### crossbow.fire — ยิงหน้าไม้

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: aim → release → recoil → recover
- Contact ที่ต้องได้หลักฐาน: soles;grip
- Event candidates: projectile_release
- จุดตรวจเฉพาะ: รูปท่า/กลไกต่างจาก bow
- Reference leads: kay-itch, tos-ranger, lpc, flare-content (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### crossbow.reload — บรรจุหน้าไม้

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: lower → load → lock → aim
- Contact ที่ต้องได้หลักฐาน: soles;grip;bolt
- Event candidates: ammo_loaded
- จุดตรวจเฉพาะ: state ammo เปลี่ยนครั้งเดียวตรงจังหวะล็อก
- Reference leads: kay-itch, tos-ranger, lpc, flare-content (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### throw.item — ขว้างไอเทม

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: hold → load → throw → follow
- Contact ที่ต้องได้หลักฐาน: soles;prop grip
- Event candidates: prop_release
- จุดตรวจเฉพาะ: ปล่อย prop ตอนพ้น palm ไม่ใช่ตลอด flight
- Reference leads: kay-itch, tos-ranger, lpc, flare-content (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### wand.projectile — ยิงจากไม้คทา

- ขอบเขต: weapon-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: aim → channel → release → recover
- Contact ที่ต้องได้หลักฐาน: soles;wand grip
- Event candidates: projectile_release
- จุดตรวจเฉพาะ: ปลายคทาหรือมือเป็น emission socket ที่ระบุ
- Reference leads: kay-itch, tos-ranger, lpc, flare-content (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

## magic —9 specifications

แยก start/loop/release/cancel/finish; body-only ผ่านก่อน FX; cast speed/tick/cancel/target หลายค่าใช้ clock authoritative เดียว

### cast.start — เริ่มร่าย

- ขอบเขต: class-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: ready → raise → gather
- Contact ที่ต้องได้หลักฐาน: soles;optional staff grip
- Event candidates: cast_begin
- จุดตรวจเฉพาะ: pose ร่ายมี gesture ต่างจาก idle; อย่าซ่อนด้วย FX
- Reference leads: kay-itch, tos-element, tos-cleric, larian, lpc (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### cast.loop — ค้างร่าย

- ขอบเขต: class-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: gather → channel → gather
- Contact ที่ต้องได้หลักฐาน: soles;optional grip
- Event candidates: none
- จุดตรวจเฉพาะ: loop seam ปิด; cloth ไม่ reset ทุกวง
- Reference leads: kay-itch, tos-element, tos-cleric, larian, lpc (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### cast.release — ปล่อยเวท

- ขอบเขต: class-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: channel → release → follow → recover
- Contact ที่ต้องได้หลักฐาน: soles;optional grip
- Event candidates: cast_release
- จุดตรวจเฉพาะ: body peak กับ gameplay event และ FX ใช้นาฬิกาเดียวกัน
- Reference leads: kay-itch, tos-element, tos-cleric, larian, lpc (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### cast.interrupt — ร่ายถูกขัด

- ขอบเขต: class-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: channel → break → recoil → ready
- Contact ที่ต้องได้หลักฐาน: soles;optional grip
- Event candidates: cast_cancel
- จุดตรวจเฉพาะ: cancel ต้องหยุด FX/release; ไม่ยิงเวทซ้ำ
- Reference leads: kay-itch, tos-element, tos-cleric, larian, lpc (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### cast.channel — เวทต่อเนื่อง

- ขอบเขต: class-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: start → sustain → finish
- Contact ที่ต้องได้หลักฐาน: soles;optional grip
- Event candidates: channel_tick, channel_end
- จุดตรวจเฉพาะ: กำหนด tick rate แยกจากจำนวนภาพที่วาด
- Reference leads: kay-itch, tos-element, tos-cleric, larian, lpc (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### staff.cast — ร่ายถือไม้เท้า

- ขอบเขต: class-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: brace → raise → gesture → release
- Contact ที่ต้องได้หลักฐาน: soles;staff grip
- Event candidates: cast_release
- จุดตรวจเฉพาะ: คทาเคลื่อนตามมือและ projection แต่ละ pose
- Reference leads: kay-itch, tos-element, tos-cleric, larian, lpc (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### spell.heal — รักษา/สนับสนุน

- ขอบเขต: class-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: focus → offer → release → recover
- Contact ที่ต้องได้หลักฐาน: soles
- Event candidates: cast_release
- จุดตรวจเฉพาะ: แยก timing body/support aura เพื่อ reuse หลายสีเวท
- Reference leads: kay-itch, tos-element, tos-cleric, larian, lpc (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### spell.summon — อัญเชิญ

- ขอบเขต: class-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: prepare → invoke → release → settle
- Contact ที่ต้องได้หลักฐาน: soles
- Event candidates: summon_spawn
- จุดตรวจเฉพาะ: spawn event เดียวและสอดคล้อง network state
- Reference leads: kay-itch, tos-element, tos-cleric, larian, lpc (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### spell.teleport — วาร์ป

- ขอบเขต: class-dependent; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: prepare → vanish → appear → settle
- Contact ที่ต้องได้หลักฐาน: soles before/after
- Event candidates: vanish, relocate, appear
- จุดตรวจเฉพาะ: ไม่ใช่ dash; core ยังขึ้นกับระบบเกม
- Reference leads: kay-itch, tos-element, tos-cleric, larian, lpc (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

## reaction —13 specifications

ประกาศทิศแรง/root displacement ที่ตั้งใจ; floor/seat/body support ต่างจากwalk; finite clip/terminalhold/recovery และ interruption ให้ครบ

### hit.light — โดนตีเบา

- ขอบเขต: core; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: impact → recoil → recover
- Contact ที่ต้องได้หลักฐาน: support soles
- Event candidates: hurt
- จุดตรวจเฉพาะ: รักษา owner และอาวุธ; pose ต้องสื่อทิศแรงกระแทก
- Reference leads: kay-itch, flare-content, wesnoth, larian (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### hit.heavy — โดนตีหนัก

- ขอบเขต: core; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: impact → stagger → plant → recover
- Contact ที่ต้องได้หลักฐาน: changing soles
- Event candidates: hurt
- จุดตรวจเฉพาะ: root displacement เป็น motion ที่ตั้งใจ ไม่ใช่ placement jump
- Reference leads: kay-itch, flare-content, wesnoth, larian (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### hit.block — รับด้วยโล่

- ขอบเขต: core; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: brace → impact → absorb → ready
- Contact ที่ต้องได้หลักฐาน: soles;shield strap
- Event candidates: block_impact
- จุดตรวจเฉพาะ: shield hit socket กับการดูดซับแขนตรงกัน
- Reference leads: kay-itch, flare-content, wesnoth, larian (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### hit.parry — ปัดอาวุธ

- ขอบเขต: core; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: prepare → redirect → recover
- Contact ที่ต้องได้หลักฐาน: soles;grip
- Event candidates: parry_window
- จุดตรวจเฉพาะ: ตัวเลือกเกม; เปลี่ยนวิถีด้วย blade/forearm ไม่แค่ FX
- Reference leads: kay-itch, flare-content, wesnoth, larian (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### status.stun — มึนงง

- ขอบเขต: core; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: stagger → sway → recover
- Contact ที่ต้องได้หลักฐาน: soles
- Event candidates: status_on, status_off
- จุดตรวจเฉพาะ: สื่อเสียสมดุลแต่ไม่หลุด ground โดยไม่ได้ตั้งใจ
- Reference leads: kay-itch, flare-content, wesnoth, larian (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### status.freeze — แข็งค้าง

- ขอบเขต: core; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: current pose → hold → resume
- Contact ที่ต้องได้หลักฐาน: current supports
- Event candidates: status_on, status_off
- จุดตรวจเฉพาะ: snapshot ท่าปัจจุบัน ไม่จำเป็นมี sheet ใหม่
- Reference leads: kay-itch, flare-content, wesnoth, larian (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### status.fear — กลัว/หดตัว

- ขอบเขต: core; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: recoil → cower → recover
- Contact ที่ต้องได้หลักฐาน: soles
- Event candidates: status_on, status_off
- จุดตรวจเฉพาะ: บุคลิกและภาษากาย; ไม่เหมารวมทุก status เป็น idle สั่น
- Reference leads: kay-itch, flare-content, wesnoth, larian (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### fall.knockdown — ถูกล้ม

- ขอบเขต: core; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: impact → fall → ground contact
- Contact ที่ต้องได้หลักฐาน: soles then body surface
- Event candidates: ground_hit
- จุดตรวจเฉพาะ: ตรวจ body-ground surface และ garment; ไม่ใช้ bone head เป็น floor
- Reference leads: kay-itch, flare-content, wesnoth, larian (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### ground.down — นอนล้ม

- ขอบเขต: core; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: ground settle → hold
- Contact ที่ต้องได้หลักฐาน: body surface
- Event candidates: none
- จุดตรวจเฉพาะ: terminal hold ไม่ loop กลับตอนล้ม
- Reference leads: kay-itch, flare-content, wesnoth, larian (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### ground.getup — ลุกจากพื้น

- ขอบเขต: core; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: brace hands → rise → plant → stand
- Contact ที่ต้องได้หลักฐาน: palms;knees;soles
- Event candidates: recover_end
- จุดตรวจเฉพาะ: มือกดพื้นและ pelvis สูงตาม chain จริง
- Reference leads: kay-itch, flare-content, wesnoth, larian (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### death.fall — ตาย/ล้ม

- ขอบเขต: core; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: hit → collapse → settle
- Contact ที่ต้องได้หลักฐาน: changing soles/body
- Event candidates: death_begin, ground_hit
- จุดตรวจเฉพาะ: finite one-shot ไม่ต่อ idle ทันที
- Reference leads: kay-itch, flare-content, wesnoth, larian (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### death.hold — ศพค้าง

- ขอบเขต: core; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: settled corpse → hold
- Contact ที่ต้องได้หลักฐาน: body surface
- Event candidates: none
- จุดตรวจเฉพาะ: ไม่ถือ last-frame duration เท่ากับอายุ state
- Reference leads: kay-itch, flare-content, wesnoth, larian (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### revive — ชุบชีวิต

- ขอบเขต: core; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: ground → wake → brace → rise → ready
- Contact ที่ต้องได้หลักฐาน: body;palms;soles
- Event candidates: revive_commit
- จุดตรวจเฉพาะ: event health/state ไม่ผูกกับ GIF loop อัตโนมัติ
- Reference leads: kay-itch, flare-content, wesnoth, larian (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

## interaction —15 specifications

target object/socket/seat มีตำแหน่งโลก; palm reach/grasp/release กับ commit ร่วมกัน; แยก garment/hiddenbody เมื่อย่อหรือนั่ง

### sit.down — นั่งลง

- ขอบเขต: core-candidate; ทิศที่เสนอ: 8-proposed
- เฟส: stand → bend → lower → seat
- Contact ที่ต้องได้หลักฐาน: soles then pelvis/seat
- Event candidates: sit_enter
- จุดตรวจเฉพาะ: แยก ground sit กับ chair sit และความสูงที่นั่ง
- Reference leads: kay-itch, ual2-oga, larian, tmw-data (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### sit.idle — นั่งพัก

- ขอบเขต: core-candidate; ทิศที่เสนอ: 8-proposed
- เฟส: seated → breath → seated
- Contact ที่ต้องได้หลักฐาน: pelvis/seat;soles
- Event candidates: none
- จุดตรวจเฉพาะ: hair/head look และ cloak hidden content ต้องครบ
- Reference leads: kay-itch, ual2-oga, larian, tmw-data (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### sit.up — ลุกจากนั่ง

- ขอบเขต: core-candidate; ทิศที่เสนอ: 8-proposed
- เฟส: lean → push → plant → stand
- Contact ที่ต้องได้หลักฐาน: seat then soles
- Event candidates: sit_exit
- จุดตรวจเฉพาะ: รักษา support transfer ไม่เด้ง root
- Reference leads: kay-itch, ual2-oga, larian, tmw-data (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### pickup.ground — เก็บของบนพื้น

- ขอบเขต: core-candidate; ทิศที่เสนอ: 8-proposed
- เฟส: look → bend → reach → grasp → rise
- Contact ที่ต้องได้หลักฐาน: soles;palm/prop
- Event candidates: loot_commit
- จุดตรวจเฉพาะ: มือถึง prop ณ grasp; ไม่แค่ย่อโดยมือไม่ถึง
- Reference leads: kay-itch, ual2-oga, larian, tmw-data (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### use.potion — ดื่มยา

- ขอบเขต: core-candidate; ทิศที่เสนอ: 8-proposed
- เฟส: reach → hold → drink → lower
- Contact ที่ต้องได้หลักฐาน: soles;palm/prop;mouth
- Event candidates: consume_item
- จุดตรวจเฉพาะ: prop orientation กับปาก; consume เพียงครั้งเดียว
- Reference leads: kay-itch, ual2-oga, larian, tmw-data (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### use.food — กินอาหาร

- ขอบเขต: core-candidate; ทิศที่เสนอ: 8-proposed
- เฟส: hold → bite → chew → finish
- Contact ที่ต้องได้หลักฐาน: soles;palm/prop;mouth
- Event candidates: consume_item
- จุดตรวจเฉพาะ: ตัวเลือก; จำแนก prop และ face state
- Reference leads: kay-itch, ual2-oga, larian, tmw-data (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### interact.reach — กด/เปิด/สัมผัส

- ขอบเขต: core-candidate; ทิศที่เสนอ: 8-proposed
- เฟส: approach → reach → touch → return
- Contact ที่ต้องได้หลักฐาน: soles;palm/target
- Event candidates: interact_commit
- จุดตรวจเฉพาะ: target world socket ไม่อนุมานจาก sprite crop
- Reference leads: kay-itch, ual2-oga, larian, tmw-data (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### interact.chest — เปิดหีบ

- ขอบเขต: core-candidate; ทิศที่เสนอ: 8-proposed
- เฟส: reach → grasp → lift → return
- Contact ที่ต้องได้หลักฐาน: soles;chest handle
- Event candidates: chest_open
- จุดตรวจเฉพาะ: character กับ prop animation synchronized
- Reference leads: kay-itch, ual2-oga, larian, tmw-data (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### interact.talk — คุย/gesture

- ขอบเขต: core-candidate; ทิศที่เสนอ: 8-proposed
- เฟส: listen → gesture → settle
- Contact ที่ต้องได้หลักฐาน: soles
- Event candidates: dialogue_beat
- จุดตรวจเฉพาะ: head/hand gesture ไม่ทำ root เด้งหรือสลับมือ
- Reference leads: kay-itch, ual2-oga, larian, tmw-data (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### work.mine — ขุดแร่

- ขอบเขต: core-candidate; ทิศที่เสนอ: 8-proposed
- เฟส: load → swing → impact → recover
- Contact ที่ต้องได้หลักฐาน: soles;two grips
- Event candidates: resource_hit
- จุดตรวจเฉพาะ: optional; เครื่องมือหนักมี plane และ impact จุดแร่
- Reference leads: kay-itch, ual2-oga, larian, tmw-data (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### work.chop — ตัดไม้

- ขอบเขต: core-candidate; ทิศที่เสนอ: 8-proposed
- เฟส: load → cut → impact → recover
- Contact ที่ต้องได้หลักฐาน: soles;grip
- Event candidates: resource_hit
- จุดตรวจเฉพาะ: optional; ไม่แทนด้วย sword clip จนตรวจ contact
- Reference leads: kay-itch, ual2-oga, larian, tmw-data (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### work.fish — ตกปลา

- ขอบเขต: core-candidate; ทิศที่เสนอ: 8-proposed
- เฟส: cast → wait → pull → retrieve
- Contact ที่ต้องได้หลักฐาน: soles;rod grip
- Event candidates: line_release, catch_commit
- จุดตรวจเฉพาะ: optional; ใช้ clip หลาย state ไม่รวมทุกอย่างเป็น loop
- Reference leads: kay-itch, ual2-oga, larian, tmw-data (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### work.craft — คราฟต์/ตีเหล็ก

- ขอบเขต: core-candidate; ทิศที่เสนอ: 8-proposed
- เฟส: prepare → work → inspect → finish
- Contact ที่ต้องได้หลักฐาน: soles;tool/table
- Event candidates: craft_tick, craft_finish
- จุดตรวจเฉพาะ: optional; table height and palm tools
- Reference leads: kay-itch, ual2-oga, larian, tmw-data (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### carry.idle — ถือของ

- ขอบเขต: core-candidate; ทิศที่เสนอ: 8-proposed
- เฟส: hold → settle
- Contact ที่ต้องได้หลักฐาน: soles;two palms/prop
- Event candidates: none
- จุดตรวจเฉพาะ: optional; object center anchored grip ไม่ลอย
- Reference leads: kay-itch, ual2-oga, larian, tmw-data (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### carry.walk — เดินถือของ

- ขอบเขต: core-candidate; ทิศที่เสนอ: 8-proposed
- เฟส: contact → support → opposite contact → support
- Contact ที่ต้องได้หลักฐาน: alternating soles;palms/prop
- Event candidates: footstep
- จุดตรวจเฉพาะ: optional; arm swing ถูกลดจากถือของไม่หาย phase ขา
- Reference leads: kay-itch, ual2-oga, larian, tmw-data (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

## emote —7 specifications

กำหนด personality/intent; owner ข้างเดิม, readable silhouette ที่สเกลเกม, loop/return; ท่ากระโดดต้องประกาศ intentional flight

### emote.wave — โบกมือ

- ขอบเขต: optional; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: raise → wave → lower
- Contact ที่ต้องได้หลักฐาน: soles
- Event candidates: none
- จุดตรวจเฉพาะ: owner มือโบกและอุปกรณ์คงที่; clear silhouette
- Reference leads: kay-itch, ual2-oga, cmu, saint11 (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### emote.cheer — ดีใจ

- ขอบเขต: optional; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: prepare → celebrate → settle
- Contact ที่ต้องได้หลักฐาน: soles or declared jump
- Event candidates: none
- จุดตรวจเฉพาะ: การกระโดดต้องตั้งใจ; ไม่โยกด้วย image registration
- Reference leads: kay-itch, ual2-oga, cmu, saint11 (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### emote.bow — คำนับ

- ขอบเขต: optional; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: stand → bow → return
- Contact ที่ต้องได้หลักฐาน: soles
- Event candidates: none
- จุดตรวจเฉพาะ: hinge hips/spine readable; head proportion คงที่
- Reference leads: kay-itch, ual2-oga, cmu, saint11 (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### emote.point — ชี้

- ขอบเขต: optional; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: ready → point → hold → return
- Contact ที่ต้องได้หลักฐาน: soles
- Event candidates: none
- จุดตรวจเฉพาะ: มือชี้ anatomical ข้างเดิม ไม่ตามด้านหน้าจอ
- Reference leads: kay-itch, ual2-oga, cmu, saint11 (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### emote.sad — เศร้า

- ขอบเขต: optional; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: neutral → slump → settle
- Contact ที่ต้องได้หลักฐาน: soles
- Event candidates: none
- จุดตรวจเฉพาะ: บุคลิกด้วย shoulder/head gesture ไม่ย่อสเกลทั้งตัว
- Reference leads: kay-itch, ual2-oga, cmu, saint11 (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### emote.angry — โกรธ

- ขอบเขต: optional; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: tense → gesture → settle
- Contact ที่ต้องได้หลักฐาน: soles
- Event candidates: none
- จุดตรวจเฉพาะ: มืออาวุธและ offhand ระบุ; สีหน้าแยก slot ถ้าต้องใช้
- Reference leads: kay-itch, ual2-oga, cmu, saint11 (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### emote.dance — เต้น

- ขอบเขต: optional; ทิศที่เสนอ: 4-diagonal-pilot;8-if-needed
- เฟส: step phrase → opposite phrase → loop
- Contact ที่ต้องได้หลักฐาน: changing soles
- Event candidates: beat
- จุดตรวจเฉพาะ: optional; beat/timing seam and support explicit
- Reference leads: kay-itch, ual2-oga, cmu, saint11 (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

## traversal —9 specifications

conditional mechanic เท่านั้น; bound world support/flight/water/ladder/mount surfaces และ controller trajectory ก่อน redraw

### run.loop — วิ่งถ้าเกมมี

- ขอบเขต: conditional-not-committed; ทิศที่เสนอ: 8-proposed
- เฟส: contact → flight → opposite contact → flight
- Contact ที่ต้องได้หลักฐาน: alternating soles;flight
- Event candidates: footstep
- จุดตรวจเฉพาะ: optional; ไม่ใช่ dash; ไม่ยืนยันว่าระบบเกมเราใช้
- Reference leads: kay-itch, ual2-oga, epic-gasp, cmu (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### jump.takeoff — เริ่มกระโดด

- ขอบเขต: conditional-not-committed; ทิศที่เสนอ: 8-proposed
- เฟส: load → push → leave
- Contact ที่ต้องได้หลักฐาน: soles to flight
- Event candidates: leave_ground
- จุดตรวจเฉพาะ: optional; ประเมินจริงเทียบ gameplay velocity
- Reference leads: kay-itch, ual2-oga, epic-gasp, cmu (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### jump.air — กลางอากาศ

- ขอบเขต: conditional-not-committed; ทิศที่เสนอ: 8-proposed
- เฟส: rise → apex → fall
- Contact ที่ต้องได้หลักฐาน: none
- Event candidates: apex
- จุดตรวจเฉพาะ: optional; ไม่ใช้หลัก contact walk ตัดสิน
- Reference leads: kay-itch, ual2-oga, epic-gasp, cmu (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### jump.land — ลงพื้น

- ขอบเขต: conditional-not-committed; ทิศที่เสนอ: 8-proposed
- เฟส: contact → absorb → recover
- Contact ที่ต้องได้หลักฐาน: soles
- Event candidates: land
- จุดตรวจเฉพาะ: optional; ground event กับ lowest surface
- Reference leads: kay-itch, ual2-oga, epic-gasp, cmu (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### climb.ladder — ปีนบันได

- ขอบเขต: conditional-not-committed; ทิศที่เสนอ: 8-proposed
- เฟส: reach → pull → opposite reach → pull
- Contact ที่ต้องได้หลักฐาน: palms;rungs;feet
- Event candidates: rung_contact
- จุดตรวจเฉพาะ: optional; 4contactสัมพันธ์ world ladder
- Reference leads: kay-itch, ual2-oga, epic-gasp, cmu (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### swim.loop — ว่ายน้ำ

- ขอบเขต: conditional-not-committed; ทิศที่เสนอ: 8-proposed
- เฟส: pull → kick → recover
- Contact ที่ต้องได้หลักฐาน: water support
- Event candidates: stroke
- จุดตรวจเฉพาะ: optional; posture/cape wet semantics
- Reference leads: kay-itch, ual2-oga, epic-gasp, cmu (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### mount.enter — ขึ้นพาหนะ

- ขอบเขต: conditional-not-committed; ทิศที่เสนอ: 8-proposed
- เฟส: approach → grasp → step → sit
- Contact ที่ต้องได้หลักฐาน: palms;stirrup;saddle
- Event candidates: mount_attach
- จุดตรวจเฉพาะ: optional; สอง actor contacts ต้องสัมพันธ์
- Reference leads: kay-itch, ual2-oga, epic-gasp, cmu (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### mount.ride — ขี่พาหนะ

- ขอบเขต: conditional-not-committed; ทิศที่เสนอ: 8-proposed
- เฟส: seat follow → balance → loop
- Contact ที่ต้องได้หลักฐาน: saddle;stirrups
- Event candidates: none
- จุดตรวจเฉพาะ: optional; rider phase matches mount not independent idle
- Reference leads: kay-itch, ual2-oga, epic-gasp, cmu (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### mount.exit — ลงพาหนะ

- ขอบเขต: conditional-not-committed; ทิศที่เสนอ: 8-proposed
- เฟส: release → step → ground → stand
- Contact ที่ต้องได้หลักฐาน: saddle to soles
- Event candidates: mount_detach
- จุดตรวจเฉพาะ: optional; attach state ตรง contact
- Reference leads: kay-itch, ual2-oga, epic-gasp, cmu (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

## dash —6 specifications

optional research ตามคำสั่งล่าสุด ไม่commitmechanicเข้าเกม; แยกbody facingกับtravel vectorและin-place/root motion; ตรวจstart/travel/brake/landing/cancel/return state ไม่อนุมานiframesจากภาพ

### dash.start — เริ่มdash

- ขอบเขต: optional; ทิศที่เสนอ: 8-proposed;body-facing-and-travel-direction-independent
- เฟส: ready → load → push → travel_enter
- Contact ที่ต้องได้หลักฐาน: support sole then declared flight
- Event candidates: dash_begin, leave_support
- จุดตรวจเฉพาะ: แยกanticipationกับworld impulse; pelvis/support/releaseต้องสัมพันธ์
- Reference leads: ual2-oga, kay-oga, epic-gasp, mixamo (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### dash.loop — ช่วงเคลื่อนdash

- ขอบเขต: optional; ทิศที่เสนอ: 8-proposed;body-facing-and-travel-direction-independent
- เฟส: travel → controlled posture → travel
- Contact ที่ต้องได้หลักฐาน: declared glide/flight/steps
- Event candidates: dash_tick
- จุดตรวจเฉพาะ: ระบุin-placeหรือroot-motionและsupportmode; ห้ามใช้contactwalkตัดสินflight
- Reference leads: ual2-oga, kay-oga, epic-gasp, mixamo (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### dash.end — จบdash

- ขอบเขต: optional; ทิศที่เสนอ: 8-proposed;body-facing-and-travel-direction-independent
- เฟส: travel_exit → brake → plant → recover
- Contact ที่ต้องได้หลักฐาน: incoming sole or declared roll contact
- Event candidates: dash_end, recover_end
- จุดตรวจเฉพาะ: หยุดrootกับเท้ารับน้ำหนักพร้อมกัน; recoveryต่อwalk/idle/attackไม่วาร์ป
- Reference leads: ual2-oga, kay-oga, epic-gasp, mixamo (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### dash.forward — พุ่งหน้า

- ขอบเขต: optional; ทิศที่เสนอ: 8-proposed;body-facing-and-travel-direction-independent
- เฟส: load → drive_forward → brake → settle
- Contact ที่ต้องได้หลักฐาน: support transition
- Event candidates: dash_begin, dash_end
- จุดตรวจเฉพาะ: world displacementต้องไปfacingที่ประกาศ ไม่หมุนภาพแทนการเคลื่อน
- Reference leads: ual2-oga, kay-oga, epic-gasp, mixamo (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### dash.backward — พุ่งถอย

- ขอบเขต: optional; ทิศที่เสนอ: 8-proposed;body-facing-and-travel-direction-independent
- เฟส: load → drive_back → plant → settle
- Contact ที่ต้องได้หลักฐาน: support transition
- Event candidates: dash_begin, dash_end
- จุดตรวจเฉพาะ: body facingกับtravel directionแยก; ไม่mirrorสลับอุปกรณ์
- Reference leads: ual2-oga, kay-oga, epic-gasp, mixamo (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance

### dash.side — พุ่งด้านข้าง

- ขอบเขต: optional; ทิศที่เสนอ: 8-proposed;body-facing-and-travel-direction-independent
- เฟส: load → side_drive → plant → recover
- Contact ที่ต้องได้หลักฐาน: support transition
- Event candidates: dash_begin, dash_end
- จุดตรวจเฉพาะ: ซ้าย/ขวาตามตัวละครหรือworldต้องประกาศ; ไม่ถือเป็นภาพmirrorอัตโนมัติ
- Reference leads: ual2-oga, kay-oga, epic-gasp, mixamo (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)
- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance
