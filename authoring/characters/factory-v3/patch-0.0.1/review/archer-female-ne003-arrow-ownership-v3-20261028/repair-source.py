from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
import numpy as np
b=Path('authoring/characters/factory-v3/patch-0.0.1/review');src=b/'archer-female-ne003-native-bow-study-v2-20261028';master=b/'archer-coherent-recovery-masters-v2-20261026/female/NE/Master/003.png';out=b/'archer-female-ne003-arrow-ownership-v3-20261028';out.mkdir(exist_ok=False)
a=np.array(Image.open(master).convert('RGBA'));labels=np.array(Image.open(src/'labels.png'));before=labels.copy();ys,xs=np.where((labels[198:218,132:180]==1)&(a[198:218,132:180,3]>0));labels[ys+198,xs+132]=3;Image.fromarray(labels).save(out/'labels.png');parts={}
for value,role in [(1,'BodyCostume'),(2,'HeadHair'),(3,'Weapon')]:
 p=a.copy();p[labels!=value]=0;parts[role]=Image.fromarray(p);parts[role].save(out/(role+'.png'))
merged=Image.new('RGBA',(512,512))
for role in ['BodyCostume','HeadHair','Weapon']:merged.alpha_composite(parts[role])
result=np.array(merged);visible=a[:,:,3]>0;assert np.array_equal(a[visible],result[visible])and np.array_equal(a[:,:,3],result[:,:,3]);assert not np.any((before!=labels)&~((np.indices(labels.shape)[1]>=132)&(np.indices(labels.shape)[1]<180)&(np.indices(labels.shape)[0]>=198)&(np.indices(labels.shape)[0]<218)))
page=Image.new('RGBA',(900,360),'#ddd')
for col,(label,img) in enumerate([('previous Weapon',Image.open(src/'Weapon.png')),('repaired Weapon',parts['Weapon']),('BodyCostume',parts['BodyCostume'])]):
 page.alpha_composite(img.convert('RGBA').crop((110,110,310,310)).resize((300,300),Image.Resampling.NEAREST),(col*300,35));ImageDraw.Draw(page).text((col*300+4,4),label,fill='black')
page.convert('RGB').save(out/'arrow-ownership-review.jpg',quality=98);receipt={'status':'ONE_FRAME_NATIVE_ARROW_OWNERSHIP_REPAIR_NOT_COMPLETE_WEAPON','source_master_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'input_labels_sha256':hashlib.sha256((src/'labels.png').read_bytes()).hexdigest(),'moved_visible_source_pixels':len(xs),'edited_region':[132,198,180,218],'newly_painted_pixels':0,'visible_recomposition_mismatch_pixels':0,'remaining_bow_string_hand_occlusion_review':True,'runtime_admitted':False,'changed_pixels':[{'x':int(x+132),'y':int(y+198)}for y,x in zip(ys,xs)]};(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'repair-source.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:receipt[k]for k in ['moved_visible_source_pixels','visible_recomposition_mismatch_pixels','runtime_admitted']}))
