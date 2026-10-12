"""Fixed-scale normalization and annotated blade/contact review of real art.

Actual empty-gutter panels recover overflow beyond nominal sheet cells. This
does not reconstruct or repaint anatomy. One grounded boot contour calibrates
capture registration; the other boot is held out and may fail independently.
"""
import hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'research/sprite-animation/registered-walk-attack-v21';SCALE=.88
TIMES=[0,100,220,300,360,440,560,700];DURATIONS=[100,120,80,60,80,120,140,100]
# Raw image observations: wrap center, blade base, blade tip. Not hidden bones.
BLADES=[[[167,369],[187,392],[297,519]],[[529,242],[539,212],[572,79]],[[918,159],[915,133],[877,20]],[[1350,263],[1390,270],[1519,274]],[[258,808],[284,830],[397,950]],[[644,834],[672,850],[789,953]],[[1026,827],[1052,845],[1159,943]],[[1313,840],[1350,865],[1453,983]]]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def contour(a,roi):
 x0,y0,x1,y1=roi;p=a[y0:y1,x0:x1];r,g,b,alpha=[p[:,:,i].astype(float) for i in range(4)];m=(alpha>192)&(r>g*1.05)&(b<r*.88)&(r>15)
 if m.sum()<100:raise ValueError('Boot palette/ROI inconclusive')
 yy,xx=np.where(m);bottom=int(yy.max());xs=xx[yy>=bottom-1];return [float(np.median(xs)+x0),float(bottom+y0)],int(m.sum())
def main():
 raw=OUT/'raw/SE-attack-attempt2.png';im=Image.open(raw).convert('RGBA');a=np.array(im);assert im.size==(1536,1024);bounds=[[i*384,0,(i+1)*384,552] for i in range(4)]+[[x0,552,x1,1024] for x0,x1 in zip([0,405,792,1167],[405,792,1167,1536])]
 for boundary in [405,792,1167]:assert a[552:,boundary,3].max()<=2,'Gutter crosses foreground'
 assert a[552,:,3].max()<=2
 records=[];frames=[];folder=OUT/'attack/SE/frames';folder.mkdir(parents=True,exist_ok=True);first_y=None
 for i,(x0,y0,x1,y1) in enumerate(bounds):
  origin=(i%4*384,i//4*512);right_roi=[origin[0]+70,470 if i<4 else 923,origin[0]+177,533 if i<4 else 1000];left_roi=[origin[0]+230,475 if i<4 else 925,origin[0]+340,533 if i<4 else 1000]
  rpoint,rcount=contour(a,right_roi);lpoint,lcount=contour(a,left_roi)
  if first_y is None:first_y=rpoint[1]
  tx=78;ty=455-SCALE*(rpoint[1]-origin[1]);masked=Image.new('RGBA',im.size);panel=im.crop((x0,y0,x1,y1));pa=np.array(panel);pa[pa[:,:,3]<=2]=0;masked.paste(Image.fromarray(pa),(x0,y0))
  frame=masked.transform((512,512),Image.Transform.AFFINE,(1/SCALE,0,origin[0]-tx/SCALE,0,1/SCALE,origin[1]-ty/SCALE),resample=Image.Resampling.BICUBIC)
  # Always inspect output occupancy; no silhouette/keyframe fitting.
  fa=np.array(frame);edge=max(fa[0,:,3].max(),fa[-1,:,3].max(),fa[:,0,3].max(),fa[:,-1,3].max());assert edge<=2,'Clipped master'
  p=folder/f'{i:02}.png';frame.save(p);frames.append(frame)
  xy=lambda v:[(v[0]-origin[0])*SCALE+tx,(v[1]-origin[1])*SCALE+ty]
  review=frame.copy();d=ImageDraw.Draw(review);blade=[xy(v) for v in BLADES[i]];d.line(blade,fill='#00e6ff',width=2)
  for v,col in [(xy(rpoint),'#2895ff'),(xy(lpoint),'#ff891b')]:d.ellipse((v[0]-4,v[1]-4,v[0]+4,v[1]+4),outline=col,width=2)
  rp=OUT/'attack/evidence/annotated'/f'{i:02}.png';rp.parent.mkdir(parents=True,exist_ok=True);review.save(rp)
  records.append({'key':i,'start_ms':TIMES[i],'duration_ms':DURATIONS[i],'image':str(p.relative_to(ROOT)),'sha256':sha(p),'crop_raw':bounds[i],'canonical_cell_origin':origin,'shared_scale':SCALE,'capture_translation_xy':[tx,ty],'right_boot_calibration':{'raw_roi':right_roi,'palette_contour_xy':rpoint,'pixels':rcount,'output_xy':xy(rpoint),'scope':'Visible screen-left boot bottom; calibration, excluded from independent contact validation.'},'left_boot_held_out':{'raw_roi':left_roi,'palette_contour_xy':lpoint,'pixels':lcount,'output_xy':xy(lpoint),'scope':'Independent visible other-boot surface, not a recovered hidden joint/world contact.'},'right_palm_xy':blade[0],'blade_base_xy':blade[1],'blade_tip_xy':blade[2],'weapon_owner_observed':'anatomical_right','hand_review':'Visible same right shoulder-bracer-palm chain throughout, handle between guard/pommel. Finger occlusion and exact source-to-painted joints remain unmeasured.'})
 original=records[0]['left_boot_held_out']['output_xy'][1];other=[r['left_boot_held_out']['output_xy'][1] for r in records];delta=[y-original for y in other];right=[r['right_boot_calibration']['output_xy'][1] for r in records]
 report={'schema':'painted-sword-attack-v21','facing':'SE','frames':records,'canvas':[512,512],'duration_ms':800,'loop':False,'raw':str(raw.relative_to(ROOT)),'raw_sha256':sha(raw),'gutter_alpha_noise_floor':2,'per_frame_scale':False,'calibration_mode':'Actual grounded screen-left boot surface, integer-free global affine translation plus one shared .88 scale','independent_other_boot_vertical_deviation_px':delta,'independent_other_boot_max_abs_deviation_px':max(abs(x) for x in delta),'independent_other_boot_range_px':max(other)-min(other),'calibrated_boot_range_px':max(right)-min(right),'world_contacts_verified':False,'painted_anatomy_approved':False,'complete_painted_parts':False,'production_ready':False,'source_acting_approved':False,'scope':'Surface registration/contact diagnostic with manual SHA-bound blade observations; no hidden-bone or physical support claim.'}
 save(OUT/'attack/evidence/painted-attack.json',report)
 sheet=Image.new('RGBA',(2048,1024));annotated=Image.new('RGBA',(2048,1024))
 for i,frame in enumerate(frames):sheet.alpha_composite(frame,(i%4*512,i//4*512));annotated.alpha_composite(Image.open(OUT/'attack/evidence/annotated'/f'{i:02}.png'),(i%4*512,i//4*512))
 sheet.save(OUT/'attack/SE/eight-frames.png');annotated.save(OUT/'attack/evidence/blade-contact-review.png')
 from importlib.util import spec_from_file_location,module_from_spec
 sp=spec_from_file_location('walk_build',Path(__file__).with_name('build-registered-walk.py'));m=module_from_spec(sp);sp.loader.exec_module(m);m.clip(OUT/'attack/SE/body-only',frames,DURATIONS,False)
 print('PAINTED_ATTACK',report['independent_other_boot_max_abs_deviation_px'],report['independent_other_boot_range_px'])
if __name__=='__main__':main()
