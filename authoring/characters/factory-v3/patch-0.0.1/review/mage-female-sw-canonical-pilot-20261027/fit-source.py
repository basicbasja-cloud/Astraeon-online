from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage
import numpy as np,json,sys,hashlib
sys.path.insert(0,'tools/character_factory_v3')
from calibrate_baseline_height import baseline_height_fit
from register_planted_foot_masters import observed_sole
from source_segment_timing import source_timing
b=Path('authoring/characters/factory-v3/patch-0.0.1');source=b/'review/mage-coherent-component-masters-20261026/female/SW/Master';ref=b/'review/preserved-swordsman-canonical-cutouts-20261023/BasicAttack/SW';out=b/'review/mage-female-sw-canonical-pilot-20261027';(out/'Master').mkdir(parents=True,exist_ok=True)
old=json.loads((b/'guides/c297971fcef09188ff60/manifest.json').read_text())['views']['SW']['frames'][0]['landmarks'];manifest=json.loads((b/'guides/ebac492fbc20b608880c/manifest.json').read_text());rows=manifest['views']['SW']['frames'];target=rows[0]['landmarks'];reference_head=np.array(Image.open(ref/'HeadHair/000.png'))[:,:,3]>200;reference_body=np.array(Image.open(ref/'BodyCostume/000.png'))[:,:,3]>200
im=Image.open(source/'000.png').convert('RGBA');a=np.array(im);rgb=a[:,:,:3].astype(float);yy,xx=np.indices(a.shape[:2]);scope=(xx>200)&(xx<280)&(yy>135)&(yy<215)&(a[:,:,3]>200);warm=(rgb[:,:,0]>rgb[:,:,1]*1.3)&(rgb[:,:,1]>rgb[:,:,2]*1.12)&scope;l,n=ndimage.label(warm);sizes=np.bincount(l.ravel());sizes[0]=0;hair=l==int(sizes.argmax());crown=float(np.nonzero(hair)[0].min());ground=float(np.nonzero(a[:,:,3]>200)[0].max());fit=baseline_height_fit(float(np.nonzero(reference_head)[0].min()),float(np.nonzero(reference_body)[0].max()),old['head'][1]*.5,np.mean([old[k][1]*.5 for k in ['foot_l','foot_r']]),target['head'][1]*.5,np.mean([target[k][1]*.5 for k in ['foot_l','foot_r']]),crown,ground);scale=fit['shared_scale'];ref_contacts=observed_sole(Image.open(ref/'BodyCostume/000.png'))[1];source_contacts=observed_sole(im)[1];tx=np.mean([c['point'][0] for c in ref_contacts])-scale*np.mean([c['point'][0] for c in source_contacts]);ty=fit['first_frame_y_translation'];fit.update({'shared_translation':[tx,ty],'reference':'preserved Swordsman BasicAttack SW pose0','candidate_crown_observation_y':crown,'candidate_ground_observation_y':ground,'per_frame_fitting':False,'pose_adjusted_crown_ground_baseline':True,'runtime_admitted':False})
records=[];previews=[];first=None;source_first=[target['foot_r'],target['foot_l']]
for i in range(24):
 path=source/f'{i:03d}.png';im=Image.open(path).convert('RGBA');im=im.transform((768,768),Image.Transform.AFFINE,(1/scale,0,-tx/scale,0,1/scale,-ty/scale),resample=Image.Resampling.BICUBIC);im.save(out/'Master'/f'{i:03d}.png');candidates=sorted(observed_sole(im)[1],key=lambda c:c['point'][0]);contacts=np.array([r['point'] for r in candidates]);
 if len(candidates)!=2:raise ValueError('Ambiguous two-foot measurement')
 if first is None:first=contacts.copy()
 expected=first+(np.array([rows[i]['landmarks']['foot_r'],rows[i]['landmarks']['foot_l']])-np.array(source_first))*.5;errors=np.linalg.norm(contacts-expected,axis=1)
 record={'index':i,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256((out/'Master'/f'{i:03d}.png').read_bytes()).hexdigest(),'observed_raster_sole_points':contacts.tolist(),'relative_guide_expected_points':expected.tolist(),'relative_contact_residual_authoring_px':errors.tolist(),'relative_contact_residual_runtime_px':(errors*.3125).tolist()};records.append(record)
 bg=Image.new('RGB',(384,404),'#ddd');crop=im.crop((192,256,576,640));bg.paste(crop,(0,20),crop);ImageDraw.Draw(bg).text((5,5),f'Mage female SW {i:02d} | shared fit | DRAFT',fill='black');previews.append(bg)
timing=source_timing(manifest,'SW')
for label,factor in [('source-time',1),('slow',3)]:previews[0].save(out/(label+'.gif'),save_all=True,append_images=previews[1:],duration=[d*factor for d in timing['gif_durations_ms']],loop=0,disposal=2)
contact=Image.new('RGB',(384*6,404*4))
for i,im in enumerate(previews):contact.paste(im,((i%6)*384,(i//6)*404))
contact.save(out/'all24-contact.jpg',quality=97)
result={'status':'CANONICAL_BASELINE_FIT_PILOT_REQUIRES_ART_AND_SEMANTIC_REVIEW','fit':fit,'frames':records,'source_timing':timing,'max_relative_raster_contact_runtime_px':max(max(r['relative_contact_residual_runtime_px']) for r in records),'all_raster_contact_observations_within_one_runtime_px':all(max(r['relative_contact_residual_runtime_px'])<=1 for r in records),'anatomical_contacts_manually_approved':False,'full_master_art_approved':False,'runtime_admitted':False,'note':'Single shared calibrated scale and translation across every frame. Contact observations track the same two screen-ordered visible boots against relative source-foot motion; semantic anatomy and full motion still require review.'};(out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print('fit',scale,[tx,ty],'max runtime residual',result['max_relative_raster_contact_runtime_px'])
