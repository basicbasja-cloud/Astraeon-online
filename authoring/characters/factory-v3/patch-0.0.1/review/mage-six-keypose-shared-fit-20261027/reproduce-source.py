from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,'tools/character_factory_v3')
from fit_complete_master_contacts import fit_contacts,transform_master
from register_planted_foot_masters import observed_sole
base=Path('authoring/characters/factory-v3/patch-0.0.1');root=base/'review/mage-six-keypose-masters-20261027/Master';out=base/'review/mage-six-keypose-shared-fit-20261027';out.mkdir(exist_ok=True);(out/'Master').mkdir(exist_ok=True)
painted=[];guides=[];guideimages=[];records=[]
for j,i in enumerate([0,4,8,12,18,23]):
 image=Image.open(root/f'{j:03d}.png').convert('RGBA');guide=Image.open(base/f'guides/ebac492fbc20b608880c/SW/{i:03d}.png').convert('RGBA').crop((360,440,1160,1240)).resize((512,512),Image.Resampling.LANCZOS);canvas=Image.new('RGBA',(768,768));canvas.alpha_composite(guide,(128,128));guideimages.append(canvas)
 def points(im):
  candidates=observed_sole(im)[1]
  if len(candidates)!=2:raise ValueError('Ambiguous sole components')
  return sorted([c['point'] for c in candidates])
 painted.append(points(image));guides.append(points(canvas));records.append({'sample_index':j,'source_pose':i,'painted_contacts':painted[-1],'guide_contacts':guides[-1],'source_sha256':hashlib.sha256((root/f'{j:03d}.png').read_bytes()).hexdigest()})
scale,translations,residuals=fit_contacts(painted,guides);sheet=Image.new('RGB',(1536,1024),'#ddd');previews=[]
for j,row in enumerate(records):
 image=transform_master(Image.open(root/f'{j:03d}.png'),scale,translations[j]);image.save(out/'Master'/f'{j:03d}.png');row.update({'whole_frame_translation':translations[j].tolist(),'paired_fit_residual_px':residuals[j].tolist()});bg=Image.new('RGBA',image.size,'#ddd');bg.alpha_composite(image);draw=ImageDraw.Draw(bg)
 for x,y in guides[j]:draw.line((x-10,y,x+10,y),fill='red',width=2)
 previews.append(bg.convert('RGB'));sheet.paste(bg.resize((512,512),Image.Resampling.LANCZOS),((j%3)*512,(j//3)*512))
sheet.save(out/'registered-contact-review.jpg',quality=96);previews[0].save(out/'keypose-inspection.gif',save_all=True,append_images=previews[1:],duration=650,loop=0)
receipt={'status':'SHARED_SCALE_CONTACT_STUDY_NOT_ANATOMY_ACCEPTANCE','shared_scale':scale,'one_scale_per_frame':False,'frames':records,'max_fit_residual_px':float(residuals.max()),'anatomical_contact_points_manually_approved':False,'note':'Screen-ordered visible raster sole components, not manually approved anatomical landmarks. Resampling does not add detail or prove tracing. Both feet and full anatomy still need review.','runtime_admitted':False}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('scale',scale,'max residual',residuals.max())
