"""Uniform raw-container resize only; no character/frame/part fitting or shoe patches."""
from pathlib import Path
from PIL import Image
import json,hashlib,shutil,sys
P=Path(__file__).resolve().parent;attempt=int(sys.argv[1]) if len(sys.argv)>1 else 1;prefix='W-cleaned' if attempt==1 else 'W-cleaned-v'+str(attempt);out=P/'cleaned'/('W' if attempt==1 else 'W-v'+str(attempt));out.mkdir(parents=True,exist_ok=True);frames=[];normalization=[]
for i in range(16):shutil.copyfile(P/'articulated/W'/f'{i:02}.png',out/f'{i:02}.png')
for label,start in [('middle',4),('deep',8)]:
 f=P/'raw'/f'W-waist-{label}-cleanup{attempt}.png';im=Image.open(f).convert('RGBA');normalization.append({'source':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'raw_canvas':list(im.size),'normalized_container':[1024,1024],'same_whole_container_scale':1024/im.width,'scope':'Known2x2container normalization, not an image or foot match'});assert im.width==im.height;im=im.resize((1024,1024),Image.Resampling.LANCZOS)
 for j in range(4):im.crop((j%2*512,j//2*512,j%2*512+512,j//2*512+512)).save(out/f'{start+j:02}.png')
for i in range(16):
 f=out/f'{i:02}.png';frames.append({'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
d={'frames':frames,'durations_ms':[90]*15+[550],'container_normalization':normalization,'unchanged_rig_frames':[0,1,2,3,12,13,14,15],'native_cloth_cleanup_frames':list(range(4,12)),'production_pass':False};(P/(prefix+'-contract.json')).write_text(json.dumps(d,indent=2)+'\n');c=json.loads((P/'W-motion-profile.json').read_text());c['frames']=frames;(P/(prefix+'-motion-case.json')).write_text(json.dumps(c,indent=2)+'\n');contact={'frames':frames,'surfaces':{'visible_profile_sole':{'window':[190,480,285,505],'planted_frames':list(range(16)),'budget_px':{'x':2,'y':2},'distal_band_px':8,'min_component_area':40}},'alpha_threshold':128,'calibration_output_frames':[],'scope':'Visible sole only, not anatomical identity. Far shoe occluded in this profile; source isolated-foot traces remain separate.'};(P/(prefix+'-contact-case.json')).write_text(json.dumps(contact,indent=2)+'\n');board=Image.new('RGBA',(2048,2048),(40,43,48,255))
for i,f in enumerate(frames):board.alpha_composite(Image.open(P/f['path']),(i%4*512,i//4*512))
board.convert('RGB').save(P/(prefix+'-sixteen.png'))
