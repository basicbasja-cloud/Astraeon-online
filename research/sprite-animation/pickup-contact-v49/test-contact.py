"""Regressions include the real old failure and another external character."""
from pathlib import Path
import importlib.util,json,copy,tempfile,hashlib
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('contact',P/'inputs/sprite-contact-review.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checks={};c=json.loads((P/'contact-case.json').read_text())
r=m.evaluate(c,P);assert r['visible_surface_contact_pass'];checks['current_sixteen_actual_browser_buffers_pass']=True
assert all(s['heldout_frame_count']==14 for s in r['summary'].values());checks['fourteen_validation_frames_not_used_to_fit_row_offsets']=True
assert not m.evaluate(json.loads((P/'before-contact-case.json').read_text()),P)['visible_surface_contact_pass'];checks['real_previous_failure_still_rejected']=True
q=copy.deepcopy(c);q['frames'][0]['sha256']='0'*64;assert not m.evaluate(q,P)['visible_surface_contact_pass'];checks['stale_image_rejected']=True
q=copy.deepcopy(c);q['frames'][0]['path']='missing.png';assert not m.evaluate(q,P)['visible_surface_contact_pass'];checks['missing_image_rejected']=True
for change in [lambda q:q.update(frames=[]),lambda q:q.update(surfaces={}),lambda q:q['surfaces'][next(iter(q['surfaces']))].update(planted_frames=[]),lambda q:q['surfaces'][next(iter(q['surfaces']))].update(planted_frames=[99])]:
 q=copy.deepcopy(c);change(q);assert not m.evaluate(q,P)['visible_surface_contact_pass']
checks['empty_vacuous_and_invalid_schedules_rejected']=True
blank=Image.new('RGBA',(100,100));assert m.observe(blank,[0,0,100,100])['status'].startswith('UNKNOWN')
two=blank.copy();d=ImageDraw.Draw(two);d.rectangle((10,40,25,65),fill='white');d.rectangle((50,40,65,65),fill='white');assert 'AMBIGUOUS' in m.observe(two,[0,0,100,100])['status']
assert m.observe(two,[10,30,40,80])['status']=='UNKNOWN_WINDOW_CUT';checks['missing_ambiguous_and_cut_surfaces_abstain']=True
with tempfile.TemporaryDirectory() as td:
 td=Path(td);frames=[]
 for i,y in enumerate([60,68]):
  im=Image.new('RGBA',(100,100));ImageDraw.Draw(im).rectangle((30,y-15,50,y),fill='white');f=td/f'{i}.png';im.save(f);frames.append({'path':f.name,'sha256':m.sha(f)})
 fixture={'frames':frames,'surfaces':{'support':{'window':[20,30,65,90],'planted_frames':[0,1],'budget_px':{'x':6,'y':6}}}}
 assert not m.evaluate(fixture,td)['visible_surface_contact_pass'];checks['eight_pixel_bounce_negative_rejected']=True
 fixture['surfaces']['support']['planted_frames']=[0];assert m.evaluate(fixture,td)['visible_surface_contact_pass'];checks['unplanted_frame_excluded_by_declared_schedule']=True
# Different model, pixel scale, palette and renderer: windows manually authored.
external={'schema':'visible-sprite-contact-v1','character':'External KayKit mannequin, CC0','frames':[], 'surfaces':{name:{'window':box,'planted_frames':list(range(16)),'budget_px':{'x':3,'y':3},'min_component_area':20,'distal_band_px':4} for name,box in [('screen_left',[75,285,124,355]),('screen_right',[125,285,174,355])]}}
for i in range(16):
 f=P/'references/kaykit-captures/Idle_A/N'/f'{i:02}.png';external['frames'].append({'path':str(f.relative_to(P)),'sha256':m.sha(f)})
r=m.evaluate(external,P);(P/'external-contact-case.json').write_text(json.dumps(external,indent=2)+'\n');(P/'external-contact-review.json').write_text(json.dumps(r,indent=2)+'\n');assert r['visible_surface_contact_pass'];checks['same_observer_reused_on_external_character_and_resolution']=True
# Source-to-buffer comparison permits only browser premultiplied alpha rounding.
data=json.loads((P/'layout-contract.json').read_text());audit=[]
for i,(bank,cell) in enumerate(data['mapping']):
 src=Image.open(P/data['images'][bank]).convert('RGBA');row=cell//4;crop=src.crop((cell%4*384,row*512,cell%4*384+384,row*512+512));x,y=data['origins'][bank+'_'+('bottom' if row else 'top')];expected=Image.new('RGBA',(384,512));expected.paste(crop,(x,y));a=np.asarray(expected).astype(int);b=np.asarray(Image.open(P/'renders/corrected'/f'{i:02}.png').convert('RGBA')).astype(int)
 assert np.array_equal(a[:,:,3],b[:,:,3]);opaque=a[:,:,3]==255;assert np.array_equal(a[opaque],b[opaque]);visible=a[:,:,3]>0
 assert (abs(a[:,:,:3]*a[:,:,3:]/255-b[:,:,:3]*b[:,:,3:]/255))[visible].max()<=1
 audit.append({'index':i,'alpha_exact':True,'opaque_rgba_exact':True,'opaque_pixel_count':int(opaque.sum()),'alpha128_pixel_count':int((a[:,:,3]>=128).sum()),'max_alpha128_straight_rgb_delta':int(abs(a[:,:,:3]-b[:,:,:3])[a[:,:,3]>=128].max()),'changed_translucent_pixels':int(np.any(a!=b,axis=2)[visible].sum()),'max_visible_rgb_delta':int(abs(a[:,:,:3]-b[:,:,:3])[visible].max()),'max_premultiplied_rgb_delta':float((abs(a[:,:,:3]*a[:,:,3:]/255-b[:,:,:3]*b[:,:,3:]/255))[visible].max())})
checks['source_alpha_and_opaque_art_unchanged_under_shared_origin']=True
(P/'pixel-audit.json').write_text(json.dumps({'frames':audit,'scope':'Unchanged raw sources. Browser alpha premultiplication can round translucent RGB; no opacity cleanup, foot patch or scale.'},indent=2)+'\n')
(P/'contact-qa.json').write_text(json.dumps({'pass':True,'checks':checks},indent=2)+'\n');print(json.dumps(checks))
