from pathlib import Path
p=Path('work/all-actions-v61/generation/build-S-candidate5.py')
s=p.read_text().replace("out=g/'S-candidate5'","out=g/'S-candidate6'")
a=s.index("original=Image.open(");b=s.index(" a=np.array(im)")
s=s[:a]+'''original=Image.open(g/'S-down-layout2/raw.png').convert('RGBA')
mid=Image.open('/workspace/generated_images/exec-383f10af-ab1e-44b7-a649-4b501945d52b.png').convert('RGBA').resize((1152,512),Image.Resampling.LANCZOS).crop((384,0,768,512))
arm=Image.open('/workspace/generated_images/exec-fab35cbe-6041-4a09-a7ee-2fe36ae51f69.png').convert('RGBA');assert arm.width*512==arm.height*1152
arm=arm.resize((1152,512),Image.Resampling.LANCZOS).crop((384,0,768,512))
late=Image.open(g/'S-outward4-canonical.png').convert('RGBA')
mapping=[0,2,3,'mid','arm-mid',5,6,7];notes=[];small=[]
for i,slot in enumerate(mapping):
 if slot=='mid':im=mid.copy();kind='native_targeted_midpoint';rect=[104,32,330,480]
 elif slot=='arm-mid':im=arm.copy();kind='native_targeted_arm_midpoint';rect=[64,32,330,486]
 elif i>=5:im=late.crop(((i-4)*384,0,(i-3)*384,512));kind='native_targeted_clear_arm_pose';rect=[32,32,330,508]
 else:
  x=slot%4*384;y=slot//4*512;im=original.crop((x,y,x+384,y+512));kind='native_whole_pose';rect=[104,32,330,508]
''' + s[b:]
s=s.replace("full.save(out/'keys'/f'{i:02}.png');keys.append(full)","\n if i==0:full=Image.open(root/'research/sprite-animation/core-family-v56/frames/idle/S/00.png').convert('RGBA')\n full.save(out/'keys'/f'{i:02}.png');keys.append(full)")
s += '''
contact=json.loads((g/'S-candidate5/forefoot-case.json').read_text());contact['frames']=[{k:r[k] for k in ('path','sha256')}for r in records]
(out/'contact-case.json').write_text(json.dumps(contact,indent=2)+'\\n')
spec=importlib.util.spec_from_file_location('contact',root/'tools/sprite-contact-review.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=m.evaluate(contact,out);(out/'contact-review.json').write_text(json.dumps(r,indent=2)+'\\n');print('CONTACT',r['visible_surface_contact_pass'],r['summary'])
'''
Path('work/all-actions-v61/generation/build-S-candidate6-impl.py').write_text(s)
exec(compile(s,str(p), 'exec'))
