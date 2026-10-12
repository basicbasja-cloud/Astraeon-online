"""Direct RO body paintover bank:6body drawings,9captured exposures,shared scale.

Registration follows an observed boot surface in the captured raster, not an
invented bone/root. Intentional lift/lean remains. Other boot is held out.
"""
import argparse,hashlib,importlib.util,json,shutil
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'research/sprite-animation/ro-attack-paintover-v22';SOURCE=OUT/'source';KEYS=[0,1,2,4,5,6];MAP=[0,1,2,2,3,4,5,5,5];PALMS=[[165,132],[186,132],[178,132],[215,155],[253,175],[273,186]]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def module(name):
 p=ROOT/'skills/modular-eight-direction-sprites/scripts'/(name+'.py');s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sole(im,roi):
 a=np.array(im.convert('RGBA'));x0,y0,x1,y1=roi;p=a[y0:y1,x0:x1,3];yy,xx=np.where(p>128)
 if len(yy)<30:raise ValueError('Surface ROI inconclusive')
 bottom=yy.max()
 if bottom>=p.shape[0]-1:raise ValueError('ROI clips the observed sole bottom; enlarge reviewed ROI')
 return [float(np.median(xx[yy>=bottom-1])+x0),float(bottom+y0)]
def main():
 p=argparse.ArgumentParser();p.add_argument('--attempt',type=int,default=1,choices=[1,2,3]);args=p.parse_args();prefix='' if args.attempt==1 else f'attempt{args.attempt}-';bank=OUT/'body' if args.attempt==1 else OUT/'body'/f'attempt{args.attempt}'
 palms=PALMS if args.attempt==1 else [[167,140],[172,140],[169,140],[197,145],[243,160],[269,168]] if args.attempt==2 else [[163,140],[169,140],[169,140],[193,145],[241,160],[267,168]]
 # Reviewed per-key windows. A generic other-boot window previously captured
 # the supporting boot's toe in lifted poses; retain that invalid report.
 art_rois=[([145,415,255,495],[278,400,410,500]),([160,415,286,495],[317,315,435,435]),([160,415,286,495],[310,315,435,435]),([110,375,245,480],[285,375,425,500]),([120,375,250,480],[325,375,490,500]),([128,375,260,485],[330,375,490,500])]
 import os;os.chdir(ROOT);raw=OUT/'raw'/f'RO-body-attempt{args.attempt}.png';sheet=Image.open(raw).convert('RGBA');assert sheet.size==(1536,1024);cap=json.loads((SOURCE/'body-only/capture.json').read_text());source_frames=[];cells=[];measure=[]
 for j,k in enumerate(KEYS):
  source=Image.open(SOURCE/'body-only'/cap['frames'][k]['file']).convert('RGBA');source_frames.append(source);cell=sheet.crop((j%3*512,j//3*512,j%3*512+512,j//3*512+512));cells.append(cell)
  sr=sole(source,[5,60,35,95]);sl=sole(source,[35,50,65,95]);ar=sole(cell,art_rois[j][0]);al=sole(cell,art_rois[j][1]);measure.append({'source_left_screen_boot_xy':sr,'source_right_screen_boot_xy':sl,'art_left_screen_boot_xy':ar,'art_right_screen_boot_xy':al,'art_boot_rois':art_rois[j]})
 # One gauge at the first key. No independent figure scaling/pose fitting.
 def top(im):a=np.array(im)[:,:,3];return int(np.where(a>128)[0].min())
 scale=4*(measure[0]['source_left_screen_boot_xy'][1]-top(source_frames[0]))/(measure[0]['art_left_screen_boot_xy'][1]-top(cells[0]));assert .6<scale<1
 folder=bank/'keys';folder.mkdir(parents=True,exist_ok=True);body_keys=[];records=[]
 for j,(cell,points) in enumerate(zip(cells,measure)):
  target=[points['source_left_screen_boot_xy'][0]*4+126,points['source_left_screen_boot_xy'][1]*4+50];tx=target[0]-points['art_left_screen_boot_xy'][0]*scale;ty=target[1]-points['art_left_screen_boot_xy'][1]*scale
  a=np.array(cell);a[a[:,:,3]<=1]=0;cell=Image.fromarray(a);im=cell.transform((512,512),Image.Transform.AFFINE,(1/scale,0,-tx/scale,0,1/scale,-ty/scale),resample=Image.Resampling.BICUBIC);a=np.array(im);assert max(a[0,:,3].max(),a[-1,:,3].max(),a[:,0,3].max(),a[:,-1,3].max())<=1
  path=folder/f'{j:02}.png';im.save(path);body_keys.append({'key':j,'source_index':KEYS[j],'source_sha256':cap['frames'][KEYS[j]]['sha256'],'path':str(path.relative_to(ROOT)),'sha256':sha(path)})
  xy=lambda p:[p[0]*scale+tx,p[1]*scale+ty];observed=xy(points['art_right_screen_boot_xy']);expected=[points['source_right_screen_boot_xy'][0]*4+126,points['source_right_screen_boot_xy'][1]*4+50]
  records.append({'body_key':j,'source_index':KEYS[j],'shared_scale':scale,'capture_translation_xy':[tx,ty],**points,'calibration_surface_xy':target,'held_out_other_boot_xy':observed,'held_out_reference_other_boot_xy':expected,'held_out_other_boot_delta_xy':[observed[i]-expected[i] for i in range(2)],'right_grip_visible_palm_xy':xy(palms[j]),'grip_observation_uncertainty_px':4,'scope':'Observed source/draft boot surfaces; screen-side tracking is not recovered anatomical hip identity/world support. Palm is manual actual-pixel observation, not a bone.'})
 case={'schema':'captured-body-hold-case-v1','capture':{'path':str((SOURCE/'body-only/capture.json').relative_to(ROOT)),'sha256':sha(SOURCE/'body-only/capture.json')},'canvas':[512,512],'body_keys':body_keys,'exposure_to_body_key':MAP,'loop':False,'recovered_hidden_skeleton':False,'world_contacts_verified':False};save(OUT/'evidence'/(prefix+'body-hold-case.json'),case);save(OUT/'evidence'/(prefix+'body-hold-report.json'),module('reference-holds').audit(case,ROOT))
 expanded=bank/'exposures';expanded.mkdir(exist_ok=True);fs=[]
 for i,k in enumerate(MAP):
  dst=expanded/f'{i:02}.png';shutil.copyfile(ROOT/body_keys[k]['path'],dst);fs.append({'path':str(dst.relative_to(ROOT)),'sha256':sha(dst),'index':i,'time_ms':i*100,'duration_ms':100,'role':'authored_key','source_index':i,'body_key':k,'right_grip_visible_palm_xy':records[k]['right_grip_visible_palm_xy']})
 spec={'capture':case['capture'],'source_kind':'community_rendered_game','observed_frames':[{'path':str((SOURCE/'body-only'/f['file']).relative_to(ROOT)),**{k:f[k] for k in ['sha256','index','time_ms','duration_ms']}} for f in cap['frames']],'recovered_hidden_skeleton':False,'recovered_world_contact':False,'observations':[],'experiment':{'mode':'key_paintover','keys':fs,'sequence':fs,'cycle_ms':900,'canvas':[512,512],'clock_scope':'captured_container_clock'}};save(OUT/'evidence'/(prefix+'reference-truth-case.json'),spec);save(OUT/'evidence'/(prefix+'reference-truth-report.json'),module('reference-truth').audit(spec,ROOT))
 save(OUT/'evidence'/(prefix+'registration-and-grip.json'),{'raw':str(raw.relative_to(ROOT)),'raw_sha256':sha(raw),'global_scale':scale,'per_frame_scale':False,'source_surface_scale':4,'source_surface_offset_xy':[126,50],'calibration':'First-key height gauge, then observed screen-left boot trajectory; excluded from independent contact validation','keys':records,'frames':fs,'physical_contacts_verified':False,'anatomy_approved':False,'painted_parts_complete':False,'source_pose_correspondence':'DIRECT_OBSERVED_RO_BODY_PAINTOVER_NOT_EXACT_BONE_FIT'})
 sp=importlib.util.spec_from_file_location('walk_build',Path(__file__).with_name('build-registered-walk.py'));m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);images=[Image.open(ROOT/f['path']).convert('RGBA') for f in fs];m.clip(OUT/('RO-body-'+prefix+'paintover'),images,[100]*9,False)
 board=Image.new('RGBA',(3072,1024),'#272727');d=ImageDraw.Draw(board)
 for j,(src,k) in enumerate(zip(source_frames,body_keys)):
  body=Image.new('RGBA',(512,512));body.alpha_composite(src.resize((260,380),Image.Resampling.NEAREST),(126,50));board.alpha_composite(body,(j*512,0));board.alpha_composite(Image.open(ROOT/k['path']).convert('RGBA'),(j*512,512));d.text((j*512+8,8),f'RO source{KEYS[j]+1}',fill='white');d.text((j*512+8,520),f'Original paintover key{j+1}',fill='white')
 board.save(OUT/'evidence'/('RO-body-'+prefix+'frame-comparison.png'));print('RO_PAINTOVER_BODY',scale,'6keys/9exposures; independent other-boot deltas',[r['held_out_other_boot_delta_xy'] for r in records])
if __name__=='__main__':main()
