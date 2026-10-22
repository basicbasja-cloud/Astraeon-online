import json,math,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,'tools/character_factory_v3');from build_fixed_grid_sequence_review import frames_from_sheet
b=Path('authoring/characters/factory-v3/patch-0.0.1');guide=b/'guides/2fed9f286cdd5c5ffbf4';m=json.load(open(guide/'manifest.json'));mesh=json.load(open(b/'research/archer-weighted-mesh-projections.json'));out=Path('/workspace/outputs/archer-nw-constraint-repair');out.mkdir(exist_ok=True)
old=[378,454,1158,1234];new=[288,364,1248,1324];cell=768;oldside=780;side=960;scale=cell/side;direction='NW';v=m['views'][direction];c=v['camera'];x,y,z=c['rotation'];Rx=np.array([[1,0,0],[0,math.cos(x),-math.sin(x)],[0,math.sin(x),math.cos(x)]]);Ry=np.array([[math.cos(y),0,math.sin(y)],[0,1,0],[-math.sin(y),0,math.cos(y)]]);Rz=np.array([[math.cos(z),-math.sin(z),0],[math.sin(z),math.cos(z),0],[0,0,1]]);rotation=Rz@Ry@Rx
project=lambda p:(rotation.T@(np.array(p)-c['location']))[:2]*[1536/c['ortho_scale'],-1536/c['ortho_scale']]+[768,768]
a=np.array(Image.open(b/'painted-candidates/archer-male-basicattack/NW/current-guide-rear-locked/head-cutouts/HeadHair/000.png'));ys,xs=np.nonzero(a[:,:,3]>32);head0=(np.array([xs.mean(),ys.mean()])-[189,227])*2
head_mesh0=np.array(mesh['frames'][0]['views'][direction]['HeadHair']['projected_vertex_centroid']);head_offset=head0+old[:2]-head_mesh0
foot_original={'r':np.array([155,281])*780/313.5+old[:2],'l':np.array([158,253])*780/313.5+old[:2]};foot_offsets={s:foot_original[s]-project(v['frames'][0]['contact_world']['target_toes'][s])for s in ['l','r']}
paints=[];guides=[];records=[]
for i in range(16):
 source=Image.open(guide/direction/f'{i:03d}.png').convert('RGBA').crop(new).resize((cell,cell),Image.Resampling.LANCZOS);bg=Image.new('RGBA',(cell,cell),'#ededed');bg.alpha_composite(source);draw=ImageDraw.Draw(bg)
 center=(np.array(v['frames'][i]['landmarks']['head'])+np.array([4,-28])*780/313.5-new[:2])*scale;rx,ry=62*scale,62*scale;draw.ellipse((center[0]-rx,center[1]-ry,center[0]+rx,center[1]+ry),outline='#cf318c',width=3);draw.line((center[0]-8,center[1],center[0]+8,center[1]),fill='#cf318c',width=2);draw.line((center[0],center[1]-8,center[0],center[1]+8),fill='#cf318c',width=2)
 feet={}
 for s,color in [('l','#19864d'),('r','#cc3b2c')]:
  point=(project(v['frames'][i]['contact_world']['target_toes'][s])+foot_offsets[s]-new[:2])*scale;feet[s]=point.tolist();px,py=point;draw.line((px-8,py,px+8,py),fill=color,width=3);draw.line((px,py-8,px,py+8),fill=color,width=3)
 original=Image.open(f'/workspace/outputs/archer-NW-canonical-paint-candidate/detail/{i:03d}.png').convert('RGBA');canvas=Image.new('RGBA',(cell,cell));extent=round(oldside*scale);canvas.alpha_composite(original.convert('RGBa').resize((extent,extent),Image.Resampling.LANCZOS).convert('RGBA'),(round((old[0]-new[0])*scale),round((old[1]-new[1])*scale)));paints.append(canvas);guides.append(bg);records.append({'index':i,'head_target':center.tolist(),'feet_targets':feet})
for name,frames,background in [('padded-master',paints,(0,0,0,0)),('annotated-guide',guides,'white')]:
 sheet=Image.new('RGBA',(cell*4,cell*4),background)
 for i,im in enumerate(frames):sheet.alpha_composite(im,((i%4)*cell,(i//4)*cell))
 sheet.save(out/(name+'.png'))
(out/'receipt.json').write_text(json.dumps({'guide_job':guide.name,'old_viewport':old,'new_uniform_viewport':new,'old_to_new_scale':oldside/side,'per_frame_body_fitting':False,'head_calibration':'One fixed illustrated head-envelope offset from the actual neck/head bone:4 native-cell pixels right,28 above. This corrects the original oversized upper-body placement; the same offset applies to every pose.','foot_calibration':'One constant per-foot shoe-envelope offset from pose0.','frames':records,'status':'CONSTRAINT_REFERENCE_NOT_FINAL_ART'},indent=2)+'\n')
