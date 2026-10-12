"""Native Canvas exports -> review GIF/APNG; explicit semantic limits retained."""
import gzip,hashlib,importlib.util,json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'research/sprite-animation/ro-attack-paintover-v22'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 sp=importlib.util.spec_from_file_location('walk_build',Path(__file__).with_name('build-registered-walk.py'));m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);r=json.loads((OUT/'evidence/browser-report.json').read_text());data=json.loads((OUT/'evidence/attempt3-registration-and-grip.json').read_text());captures=[];comparison=[];scope=[]
 for c in r['capture']:
  name=f'{c["time_ms"]:04}.png';main=Image.open(OUT/'capture'/('main-'+name)).convert('RGBA');ref=Image.open(OUT/'capture'/('ref-'+name)).convert('RGBA');body=Image.open(OUT/'capture'/('body-'+name)).convert('RGBA');fx=Image.open(OUT/'fx'/name).convert('RGBA');a=np.array(fx)[:,:,3];assert bool((a>0).any())==c['fx_active'];captures.append(main);b=Image.new('RGBA',(1536,512),'#272727');b.alpha_composite(ref,(0,0));b.alpha_composite(body,(512,0));b.alpha_composite(main,(1024,0));comparison.append(b)
 assert not np.array(Image.open(OUT/'fx/0880.png'))[:,:,3].any(),'GIF would freeze an expired tail'
 m.clip(OUT/'RO-attack',captures,[20]*45,False);m.clip(OUT/'RO-frame-comparison',comparison,[20]*45,False);m.clip(OUT/'RO-attack-loop-demo',captures+[captures[-1]],[20]*45+[1200],True)
 # Independent image-space Y comparison, not a hidden-joint/accuracy score.
 for k in data['keys']:
  source=Image.open(OUT/'source/body-only'/f'{k["source_index"]:04}.png').convert('RGBA');art=Image.open(ROOT/data['frames'][[0,1,2,4,5,6][k['body_key']]]['path']).convert('RGBA');s=np.array(source)[:,:,3];a=np.array(art)[:,:,3];scope.append({'body_key':k['body_key'],'source_index':k['source_index'],'observed_source_head_top_y':int(np.where(s>128)[0].min())*4+50,'observed_art_head_top_y':int(np.where(a>128)[0].min()),'other_boot_delta_xy_px':k['held_out_other_boot_delta_xy']})
 baseline=scope[0]
 for row in scope:row['head_top_phase_delta_error_px']=(row['observed_art_head_top_y']-baseline['observed_art_head_top_y'])-(row['observed_source_head_top_y']-baseline['observed_source_head_top_y'])
 save(OUT/'evidence/independent-surface-comparison.json',{'rows':scope,'maximum_absolute_head_top_phase_error_px':max(abs(v['head_top_phase_delta_error_px']) for v in scope),'source_correspondence_status':'REVIEW_REQUIRED_WITH_VISIBLE_SURFACE_DISCREPANCIES','scope':'Topmost opaque foreground is visually identified as hair in these6source/draft images. Different hair shape and pose proportions affect the comparison. This is not a recovered head bone/root, naturalness or anatomical accuracy score. Calibrated screen-left boot is excluded from independent validation.','natural_motion_approved':False,'production_ready':False})
 formats=[]
 for path in sorted(OUT.glob('*.gif'))+sorted(OUT.glob('*.png')):
  with Image.open(path) as im:
   if getattr(im,'n_frames',1)==1:continue
   times=[]
   for i in range(im.n_frames):im.seek(i);times.append(im.info['duration'])
   expected=2100 if 'loop-demo' in path.name else 900;assert sum(times)==expected
   formats.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'decoded_presentation_frames':im.n_frames,'decoded_exposure_ms':times,'total_ms':sum(times),'loop_extension':im.info.get('loop'),'body_authored_pose_count':6,'captured_body_exposure_count':9})
 save(OUT/'evidence/decoded-format-clocks.json',formats);save(OUT/'evidence/FX-capture-check.json',{'samples':45,'body_keys':6,'captured_source_exposures':9,'body_duration_ms':900,'own_fx_emission_interval_ms':[500,880],'source_weapon_exposure_scope':'Captured full RO reference shows strike smear at source5–8; our own inferred FX clears20ms before body completion to make terminal raster playback safe.','final_encoded_sample_fx_empty':True,'one_shot':True,'demo_idle_hold_ms':1200,'sweep':'clockwise_overhead','actual_painted_finger_wrap_verified':False,'body_anatomy_approved':False})
 print('PACKAGED_RO',len(formats),'formats / final FX empty / max headtop phase discrepancy',max(abs(v['head_top_phase_delta_error_px']) for v in scope))
if __name__=='__main__':main()
