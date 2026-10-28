from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,sys
sys.path.insert(0,'tools/character_factory_v3')
from register_planted_foot_masters import observed_sole
b=Path('authoring/characters/factory-v3/patch-0.0.1');p=b/'painted-candidates/mage-feet-own-frame-pilot-20261028/005';base=b/'review/mage-unflattened-head-staff-pilot-v5-20261028/Master/005.png';out=b/'review/mage-own-frame-feet005-pilot-20261028';out.mkdir(exist_ok=False);original=Image.open(base).convert('RGBA');raw=Image.open(p/'raw-shoes.png').convert('RGBA');mask=np.array(Image.open(p/'full-mask.png'))>0;source=np.array(original);crop=raw.convert('RGBa').resize((192,192),Image.Resampling.LANCZOS).convert('RGBA');records=[];page=Image.new('RGBA',(1360,460),'#ddd')
for col,dy in enumerate([None,0,-3,-5]):
 if dy is None:im=original;name='original'
 else:
  paint=Image.new('RGBA',(768,768));paint.alpha_composite(crop,(288,400+dy));im=Image.composite(paint,original,Image.fromarray(mask.astype('uint8')*255));name=f'y{dy:+d}';actual=np.array(im);changed=np.any(actual!=source,axis=2);assert not np.any(changed&~mask);im.save(out/(name+'.png'));records.append({'generated_patch_translation_author_px':[0,dy],'changed_pixels':int(changed.sum()),'outside_mask_pixels_changed':0,'protected_ankle_shin_pixels_changed':0,'native_visual_approved':False})
 _,soles=observed_sole(im,threshold=128,band=25);tile=Image.new('RGBA',(340,460),'#ddd');tile.alpha_composite(im.crop((300,450,470,565)).resize((340,230),Image.Resampling.NEAREST),(0,110));ImageDraw.Draw(tile).text((3,3),name+' / provisional',fill='black');page.alpha_composite(tile,(col*340,0));print(name,[x['point']for x in soles])
page.convert('RGB').save(out/'feet-comparison.jpg',quality=98);(out/'receipt.json').write_text(json.dumps({'status':'OWN_FRAME_BOUNDED_SHOE_REDRAW_OPTIONS_REQUIRE_ANATOMICAL_REVIEW','source_master_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256((p/'raw-shoes.png').read_bytes()).hexdigest(),'mask_sha256':hashlib.sha256((p/'full-mask.png').read_bytes()).hexdigest(),'options':records,'body_or_leg_copied_from_another_frame':False,'ankle_and_shin_fixed_outside_mask':True,'sole_bbox_is_not_accepted_foot_contact_measurement':True,'runtime_admitted':False},indent=2)+'\n');(out/'producer.py').write_bytes(Path(__file__).read_bytes())
