from pathlib import Path
p=Path('work/all-actions-v61/generation');s=(p/'build-S-candidate7.py').read_text();a=s.index("original=Image.open(");b=s.index(' a=np.array(im)')
s=s[:a]+'''raw=Image.open('/workspace/generated_images/exec-b5d48513-6015-4965-b938-9198c4cb72d9.png').convert('RGBA');assert raw.size==(1536,1024)
mapping=list(range(8));notes=[];small=[]
for i,slot in enumerate(mapping):
 x=i%4*384;y=i//4*512;im=raw.crop((x,y,x+384,y+512));kind='native_whole_pose';rect=[32,70,365,504]
''' + s[b:]
s=s.replace("out=g/'S-candidate7'","out=g/'W-candidate1'").replace("frames/idle/S/00.png","frames/idle/W/00.png").replace("v55/S-front4-motion-case.json","v55/W-side4-motion-case.json").replace('New whole-body S candidate','New whole-body W candidate')
# Author side contacts independently; only the near boot sole visible, hidden foot UNKNOWN.
s=s[:s.index('\ncontact=json.loads')]+'''\ncontact={'frames':[{k:r[k]for k in ('path','sha256')}for r in records],'surfaces':{'visible_overlap_boot':{'window':[150,465,310,515],'planted_frames':list(range(16)),'budget_px':{'x':6,'y':6}}}}
(out/'contact-case.json').write_text(json.dumps(contact,indent=2))
spec=importlib.util.spec_from_file_location('contact',root/'tools/sprite-contact-review.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);r=m.evaluate(contact,out);(out/'contact-review.json').write_text(json.dumps(r,indent=2));print('CONTACT',r['visible_surface_contact_pass'],r['summary'])
'''
# Profile actual authored path is discovered separately below.
paths=[Path('research/sprite-animation/pickup-views-v55/W-split-drape5-motion-case.json')]
s=s.replace('research/sprite-animation/pickup-views-v55/W-side4-motion-case.json',str(paths[0]))
(p/'build-W-candidate1.py').write_text(s)
