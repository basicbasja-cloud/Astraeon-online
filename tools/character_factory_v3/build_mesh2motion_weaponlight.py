#!/usr/bin/env python3
"""Build an original source-only slash trail from the same captured blade path."""
import argparse,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw


def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('guide',type=Path);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();m=json.loads((args.guide/'manifest.json').read_text());records=m['frames']
 def frame_path(i):return args.guide/records[i].get('image',f'frames/{i:03d}.png')
 size=Image.open(frame_path(0)).size[0];out=args.output;out.mkdir(parents=True,exist_ok=True);layers=out/'WeaponLight';layers.mkdir(exist_ok=True)
 tips=[np.array(r['sword_tip'],float) for r in records];grips=[np.array(r['sword_grip'],float) for r in records]
 speeds=[0]+[float(np.linalg.norm(a-b)) for a,b in zip(tips[1:],tips[:-1])]
 timing_points=[np.array(r.get('world_sword_tip',r['sword_tip']),float) for r in records]
 event_speeds=[0]+[float(np.linalg.norm(a-b)) for a,b in zip(timing_points[1:],timing_points[:-1])]
 peak=max(range(len(records)),key=lambda i:event_speeds[i]);threshold=max(event_speeds)*.2
 moving=[i for i in range(peak+1) if event_speeds[i]>=threshold];start=moving[0];stop=min(len(records)-1,peak+3);last=min(len(records)-1,stop+4)
 previews=[];effects=[];audits=[]
 def spline(points,time):
  k=min(len(points)-2,max(0,int(math.floor(time))));t=time-k;p0=points[max(0,k-1)];p1=points[k];p2=points[k+1];p3=points[min(len(points)-1,k+2)]
  return .5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)
 colors=np.array([(83,72,100),(163,153,192),(225,221,240),(255,246,224)],float)
 for i in range(len(records)):
  layer=Image.new('RGBA',(size*2,size*2),(0,0,0,0));draw=ImageDraw.Draw(layer)
  if start<=i<=last:
   fade=1.0 if i<=stop else (last+1-i)/(last+1-stop)
   newest=min(i,stop)
   # Smooth subintervals interpolate the SAME captured positions. Every integer
   # time still lands exactly on the source blade; no hand-drawn arc is added.
   begin=max(start-1,newest-3.5);samples=np.linspace(begin,newest,max(2,int((newest-begin)*16)+1))
   for older,j in zip(samples,samples[1:]):
    phase=(j-begin)/max(.001,newest-begin);age=newest-j
    g0,g1=spline(grips,older),spline(grips,j);t0,t1=spline(tips,older),spline(tips,j)
    ci=min(2,int(phase*3));ct=phase*3-ci;color=colors[ci]*(1-ct)+colors[ci+1]*ct
    for band in range(8):
     a=.3+.7*band/8;b=.3+.7*(band+1)/8;radial=(band+.5)/8
     alpha=int((.5+.5*phase)*225*fade*(.6+.4*math.sin(math.pi*radial)))
     p=[g0+(t0-g0)*a,g0+(t0-g0)*b,g1+(t1-g1)*b,g1+(t1-g1)*a]
     draw.polygon([(float(x)*2,float(y)*2) for x,y in p],fill=(*[int(v) for v in color],alpha))
   if i<=stop:
    draw.line([tuple(tips[i-1]*2),tuple(tips[i]*2)],fill=(255,249,235,int(235*fade)),width=4)
  effect=layer.resize((size,size),Image.Resampling.LANCZOS);effect.save(layers/f'{i:03d}.png');effects.append(effect)
  raw=Image.open(frame_path(i)).convert('RGBA');bg=Image.new('RGBA',raw.size,'#ececec');bg.alpha_composite(effect);bg.alpha_composite(raw)
  previews.append(bg.convert('RGB').resize((512,512),Image.Resampling.LANCZOS))
  a=np.asarray(effect.getchannel('A'))>8;ys,xs=np.nonzero(a)
  audits.append({'frame':i,'tip_step_px':round(speeds[i],3),'effect_alpha_pixels':int(a.sum()),'bbox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None,'touches_canvas_edge':bool(a[0,:].any() or a[-1,:].any() or a[:,0].any() or a[:,-1].any())})
 durations=m['gif_durations_ms'];previews[0].save(out/'source-blade-trail-one-shot.gif',save_all=True,append_images=previews[1:],duration=durations,disposal=2,optimize=False)
 ids=list(range(max(0,start-2),min(len(records),last+3)))
 sheet=Image.new('RGB',(320*4,320*math.ceil(len(ids)/4)),'#ececec');d=ImageDraw.Draw(sheet)
 for n,i in enumerate(ids):
  x,y=n%4*320,n//4*320;sheet.paste(previews[i].resize((320,320)),(x,y));d.text((x+5,y+5),f'{i} / src {records[i]["source_frame"]}',fill='black')
 sheet.save(out/'source-blade-trail-strike-contact.png')
 result={'status':'SOURCE_PROXY_EFFECT_GUIDE_NOT_PAINTED_WEAPON_APPROVAL','palette':'original muted plum-gray, lavender-silver, warm ivory','source_manifest':str(args.guide/'manifest.json'),'emission_timing_space':'source world' if 'world_sword_tip' in records[0] else 'projected source','spawn_frame':start,'max_tip_speed_frame':peak,'last_emission_frame':stop,'last_fade_frame':last,'layer':'independent transparent WeaponLight, all source frame coordinates unchanged','occlusion_preview':'effect drawn behind the source mannequin and blade; no face-covering overlay','method':'swept captured grip-to-tip segments with smooth subinterval interpolation, no copied Ragnarok effect art','frames':audits,'limitations':'Do not put this over a differently posed painted sword. Recheck or regenerate from the accepted painted weapon path.'};(out/'weaponlight-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['spawn_frame','max_tip_speed_frame','last_emission_frame','last_fade_frame']}))

if __name__=='__main__':main()
