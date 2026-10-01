"""Re-author a registered eight-phase gait around stable painted costume views.

Run after exporting source metadata with the companion Node command below.
Leg geometry is authored into the atlas, never procedurally bobbed at runtime.
"""
import json, math, subprocess
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
source=subprocess.check_output(['node','-e',"global.window={};require('./directional-metadata.js');require('./hero-registration.js');console.log(JSON.stringify({meta:window.AstraeonDirectionalMetadata['warrior'],registration:window.AstraeonHeroRegistration['warrior']}))"],cwd=ROOT)
data=json.loads(source);meta=data['meta'];reg=data['registration']
original=Image.open(ROOT/'assets/warrior-directional-v1.webp').convert('RGBA')
S=3;cell=192;anchor=(96,174);atlas=Image.new('RGBA',(cell*8,cell*8))
records=[]
torso_atlas=Image.new('RGBA',(cell,cell*8))
# Eight stable idle costume views preserve the actual rear-left orientation.
source_rows=list(range(8))
phases=['left-contact','left-down','right-passing','right-swing','right-contact','right-down','left-passing','left-swing']
for row,srow in enumerate(source_rows):
 idx=srow*6;x,y,w,h=meta['frames'][idx];body=original.crop((x,y,x+w,y+h))
 pixels=body.load()
 for py in range(body.height):
  for px in range(body.width):
   r,g,b,a=pixels[px,py]
   if r>190 and g<80 and b<90 and r>g*2:pixels[px,py]=(r,g,b,0)
 outline=meta.get('outlines',[])
 if outline:
  mask=Image.new('L',body.size);ImageDraw.Draw(mask).polygon([tuple(p) for p in outline[idx]],fill=255)
  from PIL import ImageChops
  body.putalpha(ImageChops.multiply(body.getchannel('A'),mask))
 ax,ay=reg['anchors'][idx];factor=140/reg['heights'][srow]
 # A stable torso registration. Original generated legs are removed, not reused.
 cutoff=round(h*.72)
 # Remove only the original legs; preserve the full sword and cape silhouette.
 mask=body.getchannel('A');ImageDraw.Draw(mask).rectangle((round(ax)-25,cutoff,round(ax)+25,h),fill=0);body.putalpha(mask)
 body=body.resize((round(w*factor),round(h*factor)),Image.Resampling.LANCZOS)
 upper_x=round(anchor[0]-ax*factor);upper_y=round(anchor[1]-ay*factor)
 hip_y=upper_y+round(cutoff*factor)-10
 torso=Image.new('RGBA',(cell,cell));torso.alpha_composite(body,(upper_x,upper_y));torso_atlas.alpha_composite(torso,(0,row*cell))
 angle=math.pi/2-row*math.pi/4
 forward=(math.cos(angle),math.sin(angle))
 # The stance travels exactly the projected half-cycle distance at scale .5.
 sx,sy=math.cos(angle),math.sin(angle)
 det=48*22-(-32)*14
 wx,wy=(22*sx+32*sy)/det,(48*sy-14*sx)/det
 ground_pixels_per_unit=1/math.hypot(wx,wy)
 travel=.95*.25*ground_pixels_per_unit/.5
 lateral=(math.sin(angle),-math.cos(angle)*.38)
 for col in range(8):
  im=Image.new('RGBA',(cell*S,cell*S));d=ImageDraw.Draw(im)
  contacts=[];feet=[]
  # Linear stance travel cancels root displacement; swing returns the other foot.
  for leg in range(2):
   phase=(col/8+leg*.5)%1
   stance=phase<.5
   along=travel*(1-4*phase) if stance else -travel+2*travel*((phase-.5)/.5)
   lift=0 if stance else 11*math.sin((phase-.5)*2*math.pi)
   side=(-1 if leg==0 else 1)
   hip=(96+lateral[0]*side*8,hip_y+lateral[1]*side*8)
   foot=(96+lateral[0]*side*9+forward[0]*along,174+lateral[1]*side*9+forward[1]*along-lift)
   knee=((hip[0]+foot[0])*.5-forward[0]*lift*.5,(hip[1]+foot[1])*.5-2-lift*.25)
   feet.append((hip,knee,foot,leg,stance))
  for hip,knee,foot,leg,stance in sorted(feet,key=lambda t:t[2][1]):
   def seg(a,b,width,color):d.line([(round(a[0]*S),round(a[1]*S)),(round(b[0]*S),round(b[1]*S))],fill=color,width=round(width*S))
   seg(hip,knee,16,'#302b28');seg(hip,knee,12,'#62564a');seg((hip[0]-2,hip[1]),(knee[0]-2,knee[1]),2,'#b59d67')
   seg(knee,foot,14,'#282c2b');seg(knee,foot,11,'#444541');seg((knee[0]-2,knee[1]),(foot[0]-2,foot[1]-3),2,'#807454')
   # Articulated knee plate and a distinct toe/heel silhouette for each leg.
   kx,ky=knee;d.ellipse(((kx-6)*S,(ky-4)*S,(kx+6)*S,(ky+5)*S),fill='#756a50',outline='#b3a173',width=S)
   fx,fy=foot;toe=forward[0]*5
   d.polygon([((fx-5)*S,(fy-6)*S),((fx+4)*S,(fy-6)*S),((fx+6+toe)*S,(fy-1)*S),((fx+5+toe)*S,(fy+2)*S),((fx-5)*S,(fy+2)*S)],fill='#32332e')
   seg((fx-4,fy),(fx+4+toe,fy),2,'#a58d60')
   # Original greave texture is reprojected onto the authored shin segment.
   texture=original.crop((x+round(ax)-8,y+round(h*.79),x+round(ax)+8,y+round(h*.96)))
   texture=texture.resize((11*S,max(8,round(math.dist(knee,foot)*S))),Image.Resampling.LANCZOS)
   texture.putalpha(texture.getchannel('A').point(lambda a: min(a,210)))
   texture=texture.rotate(math.degrees(math.atan2(foot[0]-knee[0],foot[1]-knee[1])),resample=Image.Resampling.BICUBIC,expand=True)
   im.alpha_composite(texture,(round((knee[0]+foot[0])*.5*S-texture.width/2),round((knee[1]+foot[1])*.5*S-texture.height/2)))
   contacts.append({'hip':[round(v,2) for v in hip],'knee':[round(v,2) for v in knee],'foot':[round(v,2) for v in foot],'leg':'left' if leg==0 else 'right','x':round(fx,2),'y':round(fy+2,2),'stance':stance})
  im.alpha_composite(body.resize((body.width*S,body.height*S),Image.Resampling.LANCZOS),(upper_x*S,upper_y*S))
  im=im.resize((cell,cell),Image.Resampling.LANCZOS)
  bounds=im.getbbox();atlas.alpha_composite(im,(col*cell,row*cell))
  records.append({'phase':phases[col],'footAnchorX':96,'footAnchorY':174,'visibleBodyHeight':140,'bodyClipY':upper_y+round(cutoff*factor),'frameBounds':list(bounds),'contacts':sorted(contacts,key=lambda c: c['leg'])})
atlas.save(ROOT/'assets/warrior-walk-v2.webp',lossless=True)
torso_atlas.save(ROOT/'assets/warrior-torso-v1.webp',lossless=True)
frames=[[col*cell,row*cell,cell,cell] for row in range(8) for col in range(8)]
registration={'anchors':[[96,174]]*64,'heights':[140]*8,'frames':records}
js='/* Generated by tools/build-warrior-walk.py. Explicit temporal phase and foot contacts. */\n'
js+='window.AstraeonDirectionalMetadata["warrior-walk"]='+json.dumps({'cols':8,'rows':8,'frames':frames,'source':'warrior-walk-v2.webp'},separators=(',',':'))+';\n'
js+='window.AstraeonHeroRegistration["warrior-walk"]='+json.dumps(registration,separators=(',',':'))+';\n'
(ROOT/'warrior-gait.js').write_text(js)
atlas.resize((768,768)).save('/tmp/warrior-gait-review.png')
print('Authored 64 registered frames, eight phases, two tracked foot contacts per frame.')
