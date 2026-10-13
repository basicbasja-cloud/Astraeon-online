#!/usr/bin/env python3
"""Build human-readable source/action/asset indexes from bounded evidence."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def load(name):return json.loads((ROOT/name).read_text())
sources=load('sources.json');receipts={r['id']:r for r in load('retrieval.json')['receipts']}
details=load('pinned-details.json')['files'];download_ids={r['source_id'] for r in load('downloads.json')['downloads'] if r['status']=='downloaded'}
for s in sources['sources']:
 r=receipts[s['id']];s['retrieval_status']=r['status'];s['retrieval_receipt']='retrieval.json#'+s['id']
 s['evidence_level']='page_retrieved' if r['status']=='page_retrieved' else r['status']
 if any(d['source_id']==s['id'] and d['http_status']==200 for d in details):s['evidence_level']='pinned_files_retrieved'
 if s['id'] in download_ids:s['evidence_level']='sample_acquired'
 if s['id']=='ual2-oga':s['evidence_level']='actual_source_evaluated_partial_visual_review'
 if s['id']=='kay-oga':s['evidence_level']='actual_source_evaluated_native_preview_captured_partial_review'
 if s['id']=='oga-hero':s['evidence_level']='actual_atlas_boarded_partial_visual_review'
 if r.get('commit'):s['observed_commit']=r['commit']
(ROOT/'sources.json').write_text(json.dumps(sources,indent=2)+'\n')
# Bounded excerpts, no complete third-party articles distributed.
retrieval=load('retrieval.json')
for r in retrieval['receipts']:
 if r.get('excerpt'):r['excerpt']=' '.join(r['excerpt'].split()[:60])
 if r.get('inspection_hints'):r['inspection_hints']=[x[:160] for x in r['inspection_hints'][:2]]
(ROOT/'retrieval.json').write_text(json.dumps(retrieval,indent=2)+'\n')
lines=['# Source index —'+str(len(sources['sources']))+' leads, explicit evidence level','', 'ข้อมูลแต่ละแถวบอกสิ่งที่ได้จริง ไม่ได้ยืนยันว่าอ่าน/ดูทุกเฟรมครบ หรือมีสิทธิ์นำทุกไฟล์ไป train/ship ดู DATASET-CONTRACT และ retrieval receipts ประกอบ','', '| ID / source | Type | Evidence | Use / rights hint |','| --- | --- | --- | --- |']
for s in sources['sources']:
 lines.append(f"| {s['id']} / [{s['title']}]({s['url']}) | {s['kind']} | {s['evidence_level']} | {s['application']} / {s['rights_hint']} |")
(ROOT/'SOURCES.md').write_text('\n'.join(lines)+'\n')
motions=load('motions.json')['motions'];families=list(dict.fromkeys(m['family'] for m in motions))
prefix={
 'idle':'ตรวจเท้ารับน้ำหนักเดิม, head/torso breathing แยกจาก origin, loop/return และ asymmetry; เริ่มด้วย native game-scale view ไม่มี FX',
 'locomotion':'จด support intervals ทั้งสองเท้าและworld movement mode; trace pelvis–thigh–knee–boot ตรง crossing ทุกเฟส; start/stop/turn ต้องตรง loop phase',
 'equipment':'สร้าง hand/prop/sheath attachment state ตามเวลา; ตรวจของซ้อน/ของหาย มือซ้ายขวาและ item extreme; controller event ผูก bank ใหม่จริง',
 'combat':'หา complete performance ใหม่; ดู load→execution→follow→recovery, support/base/hips/chest/arm/grip; สร้าง per-pose weapon perspective ก่อน tail',
 'ranged':'ติดตามสองมือและ prop/string; แยก prepare/draw/hold/release/reload; release projectile ครั้งเดียวจาก socket ณ event',
 'magic':'แยก start/loop/release/cancel/finish; body-only ผ่านก่อน FX; cast speed/tick/cancel/target หลายค่าใช้ clock authoritative เดียว',
 'reaction':'ประกาศทิศแรง/root displacement ที่ตั้งใจ; floor/seat/body support ต่างจากwalk; finite clip/terminalhold/recovery และ interruption ให้ครบ',
 'interaction':'target object/socket/seat มีตำแหน่งโลก; palm reach/grasp/release กับ commit ร่วมกัน; แยก garment/hiddenbody เมื่อย่อหรือนั่ง',
 'emote':'กำหนด personality/intent; owner ข้างเดิม, readable silhouette ที่สเกลเกม, loop/return; ท่ากระโดดต้องประกาศ intentional flight',
 'traversal':'conditional mechanic เท่านั้น; bound world support/flight/water/ladder/mount surfaces และ controller trajectory ก่อน redraw',
 'dash':'optional research ตามคำสั่งล่าสุด ไม่commitmechanicเข้าเกม; แยกbody facingกับtravel vectorและin-place/root motion; ตรวจstart/travel/brake/landing/cancel/return state ไม่อนุมานiframesจากภาพ'
}
lines=['# Motion recipes —99 research action specifications','', 'Phase/contact/event ในเอกสารนี้เป็น specification ที่เสนอ ไม่ใช่ labels ที่ตรวจครบจาก ref แล้ว จำนวนภาพ/exposure/facing ยังต้องทดลองตามท่า; conditional ไม่ใช่การเพิ่ม mechanic เข้าเกม เพิ่มdashเป็นoptionalresearchตามคำสั่งล่าสุด','', 'ใช้ร่วมกับ KNOW-HOW / DATASET-CONTRACT / REFERENCE-ANALYSIS ไม่ใช้ท่าโจมตีเก่าของเราเป็น source','']
for family in families:
 group=[m for m in motions if m['family']==family]
 lines+=['## '+family+' —'+str(len(group))+' specifications','',prefix[family],'']
 for m in group:
  lines += ['### '+m['id']+' — '+m['name_th'],'',
   '- ขอบเขต: '+m['scope']+'; ทิศที่เสนอ: '+m['proposed_direction_policy'],
   '- เฟส: '+' → '.join(m['phase_beats']),
   '- Contact ที่ต้องได้หลักฐาน: '+m['required_contact_semantics'],
   '- Event candidates: '+', '.join(m['event_candidates']),
   '- จุดตรวจเฉพาะ: '+m['specific_review'],
   '- Reference leads: '+', '.join(m['reference_leads'])+' (ค้นใน SOURCES; ยังไม่เท่ากับ verified matching clip)',
   '- วิธีทดลอง: ตรวจ reference phase/contact → blocking ใหม่ → source/actual-art review → parts/swaps → runtime transition/event → exact-byte acceptance','']
(ROOT/'MOTION-RECIPES.md').write_text('\n'.join(lines)+'\n')
boards=load('preset-board-manifest.json')['boards'];lines=['# Actual acquired source clip browser','', '71candidate clips including6dash /639evaluated overview poses. No production keys, contacts, acting or character-art acceptance inferred. Blue=source right bone names; orange=left. One common world projection/range per rig bank; diagrams are deliberately not centered/fitted per pose. Legacy Kay has no leg chains.','', '| Source clip | Overview | Samples |','| --- | --- | --- |']
for b in boards:lines.append(f"| {b['source_id']} / {b['clip']} | [board]({b['file']}) | {b['samples']} |")
(ROOT/'CLIP-BROWSER.md').write_text('\n'.join(lines)+'\n')
inventory=load('clip-inventory.json');capture_records=[]
for folder in sorted((ROOT/'captures').glob('kaykit-preview-*')):
 c=json.loads((folder/'capture.json').read_text());capture_records.append({'id':folder.name,'frames':len(c['frames']),'duration_ms':c['duration_ms'],'receipt':str((folder/'capture.json').relative_to(ROOT)),'boards':c['review_boards']})
(ROOT/'corpus-summary.json').write_text(json.dumps({'source_leads':len(sources['sources']),'motion_specifications':len(motions),'motion_families':len(families),'acquired_motion_counts':inventory['counts'],'evaluated_source_poses':sum(b['samples'] for b in boards),'native_capture_frames':sum(c['frames'] for c in capture_records),'captures':capture_records,'art_approved':False,'production_approved':False,'training_ready':False,'old_attack_used':False},indent=2)+'\n')
print(json.dumps({'sources':len(sources['sources']),'motion_recipes':len(motions),'clip_boards':len(boards)}))
