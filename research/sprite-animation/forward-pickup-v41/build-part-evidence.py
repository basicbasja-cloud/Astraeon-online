import json,hashlib,importlib.util
from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
s=importlib.util.spec_from_file_location('parts',ROOT/'skills/modular-eight-direction-sprites/scripts/part-proportion-audit.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def bind(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def line(points,definition,protocol):return dict(points=points,visibility='visible',reviewed_on_pixels=True,endpoint_uncertainty_px=2,definition=definition,protocol=protocol,covers_required_dimension=protocol!='hair_slice')
def frame(id,p,role,index,view):return dict(id=id,image=bind(p),role=role,index=index,view_id=view,pose_group='neutral' if index in [0,7] else 'pickup_pose_'+str(index),observations={k:dict(visibility='unknown',reason='Not yet observed on actual pixels; clothing/occlusion and foreshortening require review') for k in m.REQUIRED})
r=frame('approved0',P.parent/'recovery-key-v39/renders/review/full/00.png','approved',0,'v39_front_oblique')
r['observations'].update(head_width=line([[127,130],[240,130]],'Visible hair horizontal slice at y130, not maximum head width or skull width','hair_slice'),leg_thickness=line([[220,400],[255,400]],'Near visible boot shaft at mid-shin; not anatomical bone width','near_shaft_mid'),ankle_width=line([[228,430],[258,430]],'Near ankle gold band projected width','near_ankle_band'),boot_length=line([[211,466],[261,458]],'Near shoe toe-to-heel visible profile; front view foreshortened','near_toe_heel'),boot_height=line([[243,438],[243,477]],'Near shoe upper to sole visible vertical segment','near_shoe_height'),hand_width=line([[211,289],[231,302]],'Near glove visible diagonal width','near_glove_width'))
fs=[frame('candidate'+str(i),P/f'size-locked-review/{i:02}.png','candidate',i,'v41_rear_oblique') for i in range(8)]
fs[0]['observations'].update(head_width=line([[115,130],[227,130]],'Visible rear hair horizontal slice at y130, not maximum head width; skull hidden','hair_slice'),leg_thickness=line([[152,400],[201,400]],'Near visible boot shaft at mid-shin','near_shaft_mid'),ankle_width=line([[163,428],[205,423]],'Near ankle gold band projected width','near_ankle_band'),boot_length=line([[123,454],[216,457]],'Near shoe toe-to-heel visible profile','near_toe_heel'),boot_height=line([[192,438],[192,477]],'Near shoe upper to sole visible vertical segment','near_shoe_height'))
fs[7]['observations'].update(head_width=dict(visibility='clipped',reason='Native head contour reaches raw crop boundary; visible remainder cannot establish full head dimensions'),leg_thickness=line([[162,390],[214,390]],'Near visible boot shaft at mid-shin','near_shaft_mid'),ankle_width=line([[170,418],[222,418]],'Near ankle gold band projected width','near_ankle_band'),boot_length=line([[117,454],[230,459]],'Near shoe toe-to-heel visible profile','near_toe_heel'),boot_height=line([[200,434],[200,479]],'Near shoe upper to sole visible vertical segment','near_shoe_height'))
profile=json.loads((P/'character-size-profile.json').read_text())
c=dict(schema='visible-part-proportions-v1',approval_receipt=profile['approval_receipt'],approved_gif=profile['reference_gif'],fixed_family_height_px=399,same_view_relative_budget=.08,threshold_status='Provisional engineering review budget, not universal perceptual tolerance',frames=[r]+fs,comparisons=[dict(frames=['approved0',f['id']]) for f in fs]+[dict(frames=['candidate0','candidate7'])],annotation_method='Agent reviewed actual coordinate grids and enlarged boot crops; visible endpoints with +/-2px each, no inferred hidden hip/joints/anatomical left-right. Other metrics explicitly unknown.',user_size_scope='Head, shoulder/torso, arms/hands, legs/boots, attachment and ratios as well as total height. No per-part stretching or per-frame normalization.')
(P/'part-proportion-contract.json').write_text(json.dumps(c,indent=2)+'\n');q=m.run(c,ROOT);(P/'part-proportion-qa.json').write_text(json.dumps(q,indent=2)+'\n')
sc=json.loads((P/'size-locked-contract.json').read_text());sc['part_proportion_contract']=bind(P/'part-proportion-contract.json');(P/'size-locked-contract.json').write_text(json.dumps(sc,indent=2)+'\n')
# Reviewer evidence: original pixels with named surface endpoints, not changed art.
out=Image.new('RGB',(1152,570),(30,40,50));d=ImageDraw.Draw(out)
for k,f in enumerate([r,fs[0],fs[7]]):
 im=Image.open(ROOT/f['image']['path']).convert('RGBA');bg=Image.new('RGBA',im.size,(45,56,67,255));bg.alpha_composite(im);dr=ImageDraw.Draw(bg)
 for x in range(0,384,20):dr.line((x,0,x,512),fill=(100,130,145,100))
 for y in range(0,512,20):dr.line((0,y,384,y),fill=(100,130,145,100))
 for metric,o in q['measurements'][f['id']].items():
  if o['status']!='MEASURED':continue
  a,b=o['points'];dr.line([tuple(a),tuple(b)],fill=(72,255,189),width=2)
  for x,y in [a,b]:dr.ellipse((x-2,y-2,x+2,y+2),fill=(255,255,255))
  dr.text((a[0]+3,a[1]-12),metric.replace('leg_thickness','shaft')+':'+str(round(o['value_px'],1)),fill=(255,255,255))
 out.paste(bg.convert('RGB'),(k*384,30));d.text((k*384+8,8),f['id']+' / fixed family399px',fill='white')
d.text((8,545),'Different front/rear views: ratios are diagnostic, NOT a proportion pass. Rear neutral0 ->7 boot grows and FAILS.',fill=(255,190,130));out.save(P/'part-proportion-review.png')
rows=['# Actual visible part measurements','', 'All ratios use the same approved399px family height. These are visible surface measurements, not inferred joints or automatic semantic segmentation. Each endpoint has +/-2px uncertainty.','', '| Pair | Part | Ratio | Result |','| --- | --- | --- | --- |']
for row in q['comparisons']:
 if 'projected_ratio' in row:rows.append('| '+' -> '.join(row['frames'])+' | '+row['metric']+' | '+f"{row['projected_ratio']:.3f}"+' | '+row['status']+' |')
rows+=['','Front/rear comparisons remain UNKNOWN because the views differ. A projected larger boot is a warning, not an exact anatomical error percentage. The same-view neutral boot-length comparison independently FAILS. All unmeasured/occluded head, shoulder, torso, arm, hand and leg requirements continue to block a part-proportion pass.','', 'See part-proportion-contract.json for exact image SHA bindings, points and missing observations; part-proportion-qa.json recomputes the measurements.']
(P/'PART-SIZE-REVIEW.md').write_text('\n'.join(rows)+'\n')
print(q['checks']);print([x for x in q['comparisons'] if x['status']=='FAIL'])
