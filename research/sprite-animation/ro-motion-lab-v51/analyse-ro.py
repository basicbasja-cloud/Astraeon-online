"""Compare real decoded directional sequences and retain the head-layer exception."""
from pathlib import Path
import json,collections,hashlib
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;d=json.loads((P/'ro-capture-ledger.json').read_text());groups=collections.defaultdict(list);views=['S','SW','W','NW','N','NE','E','SE'];labels=['idle','walk','sit','pickup','ready','attack1','hurt','freeze','dead','freeze2','attack2','attack3','skill']
for r in d['captures']:groups[(r['actor'],r['head'],r['weapon'],r['block'])].append(r)
analysis=[]
for (actor,head,weapon,block),rows in groups.items():
 by=collections.defaultdict(list)
 for r in rows:by[r.get('sequence_sha256','ERROR')].append(views[r['direction']])
 analysis.append({'actor':actor,'head':head,'weapon':weapon,'block':block,'label_from_pinned_roBrowser':labels[block],'request_count':len(rows),'all8_present':len({r['direction'] for r in rows if r['status']=='decoded' and r['all_frames_nonempty']})==8,'unique_sequence_count':len(by),'identical_direction_groups':list(by.values()),'native_preview_frame_counts':sorted({r.get('frames',0) for r in rows})})
assert all(r['all8_present'] for r in analysis)
policy=[]
for block in range(13):
 body=[r for r in analysis if r['block']==block and r['head']==0 and r['weapon']==0];counts={r['unique_sequence_count'] for r in body};assert len(counts)==1
 count=next(iter(counts));entry={'block':block,'action':labels[block],'observed_body_groups':count,'sampled_actors':[r['actor'] for r in body],'logical_directions':views,'head_policy':'Independent appearance/look layer; no body alias inferred from full-composite hashes','provenance':'Fresh four-actor head0 rasters + pinned roBrowser action lookup; not universal NPC/monster rule'}
 if count==8:entry.update(authoring_views=8,body_alias={v:v for v in views})
 elif count==4:entry.update(authoring_views=4,body_alias={v:views[i//2*2] for i,v in enumerate(views)})
 else:entry.update(authoring_views=None,body_alias=None,status='SPECIAL_STATE_REQUIRES_SEPARATE_REVIEW_NOT_AUTOMATIC_ONE_VIEW_CHARACTER')
 policy.append(entry)
# Same body paired N/NE, but a head-only difference in one attack frame.
def row(head,block,direction):return next(r for r in d['captures'] if r['actor']=='sword-m' and r['head']==head and r['weapon']==0 and r['block']==block and r['direction']==direction)
diff=[];a=Image.open(row(1,5,4)['cache']);b=Image.open(row(1,5,5)['cache'])
for i in range(a.n_frames):
 a.seek(i);b.seek(i);aa=np.asarray(a.convert('RGBA'));bb=np.asarray(b.convert('RGBA'));mask=np.any(aa!=bb,axis=2);y,x=np.where(mask)
 if x.size:diff.append({'index':i,'differing_pixels':int(mask.sum()),'bbox':[int(x.min()),int(y.min()),int(x.max()),int(y.max())]})
assert row(0,5,4)['sequence_sha256']==row(0,5,5)['sequence_sha256']
out=P/'ro-analysis';out.mkdir(exist_ok=True)
for block in range(13):
 board=Image.new('RGB',(1024,160),(40,43,48));dr=ImageDraw.Draw(board)
 for j in range(8):
  r=row(0,block,j);im=Image.open(r['cache']);im.seek(0);crop=im.convert('RGBA').crop((72,142,168,250));board.paste(crop,(j*128+16,32),crop);dr.text((j*128+3,4),f'{views[j]} {labels[block]}',(230,230,230));dr.text((j*128+3,143),r['sequence_sha256'][:9],(190,190,190))
 board.save(out/f'body-directions-{block:02}-{labels[block]}.png')
for block in [0,1,2,3,4,5,6,8,12]:
 n=row(1,block,0)['frames'];board=Image.new('RGB',(1024,n*130),(40,43,48));dr=ImageDraw.Draw(board)
 for j in range(8):
  r=row(1,block,j);im=Image.open(r['cache'])
  for i in range(n):im.seek(i);crop=im.convert('RGBA').crop((72,130,168,250));board.paste(crop,(j*128+16,i*130+12),crop);dr.text((j*128+2,i*130),f'{views[j]} /{i}',(230,230,230))
 board.save(out/f'full-poses-{block:02}-{labels[block]}.png')
receipt={'public_preview_requests':len(d['captures']),'decoded_exposures_including_duplicates':sum(r['frames'] for r in d['captures']),'groups':analysis,'direction_policy':policy,'head_attack_N_NE_exception':diff,'head0_body_pair_equal':True,'source_code':{'roBrowser_commit':'d0449c2a36eff0210555fa5d086f625c5fd1e006','action_map':'src/Renderer/Entity/EntityAction.js:161-173','screen_direction_lookup':'src/Renderer/Entity/EntityRender.js:766-772','world_item_vanish':'src/Engine/MapEngine/Item.js:64','pickup_animation':'src/Engine/MapEngine/Entity.js:893-904','ragassets_commit':'4de4fa747431979d35c747d7edd549a872efd9e1'},'original_art_cleared_for_production':False,'analytical_excerpts':'Gravity/Ragnarok artwork via cited public community renderer. Fixed crops/labels only for research; not original character assets.','source_gameplay_clock_verified':False}
(P/'ro-direction-analysis.json').write_text(json.dumps(receipt,indent=2)+'\n');(P/'direction-policy.json').write_text(json.dumps({'logical_direction_order':views,'actions':policy,'core_player_actions':['idle','walk','sit','pickup','ready','attack1','hurt','dead','skill'],'conditional_weapon_families':['attack2','attack3'],'non_core_special_states':['freeze','freeze2'],'scope':'Production plan for this original player family, based on sampled RO patterns, not proof all other classes/assets share them'},indent=2)+'\n');print('552requests /',receipt['decoded_exposures_including_duplicates'],'exposures /',len(analysis),'direction groups; head exception',diff)
