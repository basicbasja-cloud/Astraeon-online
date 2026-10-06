"""Build a detailed native capital house from an explicit reviewed preset."""
import bpy,json,math
from mathutils import Vector

def build_house(l,i,collection,root,kit,floor):
 c=collection(l['id'],l['family']);c['capital_district']=l['district'];c['building_preset_json']=json.dumps(l)
 r=root(c,(*l['center'],.04),l['angle']);k=kit(c,r);w,dep=l['width'],l['depth'];floor_z=3.5+(i%3)*.12;top=floor_z+2.65+(i%4)*.15
 o=k.box(l['id']+'-ground-core',(0,0,(floor_z+.20)/2),(w,dep,floor_z-.20),{'market':'merchantLimewash','workshop':'workshopLimewash','residential':'homeLimewash'}[l['family']]);o['role']='solid'
 k.box(l['id']+'-foundation',(0,0,.30),(w+.14,dep+.14,.60),'stone')
 if l['floors']==3:
  k.upper_face(l['id']+'-middle-front',w+.24,floor_z,top,[-w*.25,w*.25],'homeLimewash',(0,dep/2+.42),0)
  k.upper_face(l['id']+'-middle-back',w+.24,floor_z,top,[-w*.25,w*.25],'homeLimewash',(0,-dep/2-.12),math.pi)
  for side in (-1,1):k.upper_face(l['id']+'-middle-side-'+str(side),dep+.54,floor_z,top,[-dep*.24,dep*.24],'homeLimewash',(side*(w/2+.12),.15),-side*math.pi/2)
  floor_z,top=top,top+2.7
 k.build(-w/2,w/2,-dep/2,dep/2,l['family'],index=i,longrow=l['roof']=='long-ridge',top=top,floor=floor_z,door_h=2.8)
 o=k.box(l['id']+'-physical-core',(0,0,top/2),(w,dep,top),'homeLimewash',False);o['role']='solid';o['render_visible']=False
 for o in c.objects:
  if o.type=='MESH' and any(t in o.name for t in ('main-roof','dormer-') if 'roof' in t):o.data.materials[0]=bpy.data.materials[l['clay']]
 if l['balcony']:
  yy=dep/2+.75;zz=3.45;k.box(l['id']+'-balcony-floor',(0,yy,zz),(w*.60,.95,.16),'oak')
  for j in range(7):k.box(l['id']+'-baluster-'+str(j),(-w*.27+j*w*.09,yy+.40,zz+.50),(.085,.085,.94),'timber')
  k.box(l['id']+'-balcony-rail',(0,yy+.40,zz+.99),(w*.64,.16,.14),'oak')
  for xx in (-w*.25,w*.25):k.beam(l['id']+'-balcony-brace-'+str(xx),(xx,dep/2,zz-.8),(xx,yy+.30,zz-.12),.14)
 if l['wing'] and dep<7.2 and not l.get('pairedBlock') and not l.get('denseTownhouse'):
  yy=-dep/2-.40;ww=w*.43;hh=3.15;o=k.box(l['id']+'-rear-wing',(w*.22,yy,hh/2),(ww,1.4,hh),'homeLimewash');o['role']='solid'
  k.mesh(l['id']+'-wing-roof',[(w*.22-ww/2-.2,yy-.9,hh+.2),(w*.22+ww/2+.2,yy-.9,hh+.2),(w*.22+ww/2+.2,yy+.9,hh+.9),(w*.22-ww/2-.2,yy+.9,hh+.9)],[[0,1,2,3]],l['clay'])
 # Owned planting stays inside the frontage, even in dense paired plots.
 if l['garden']:
  gx=-w*.26;gy=dep/2+.28;k.box(l['id']+'-window-box',(gx,gy,.53),(w*.28,.46,.35),'stoneLight');k.box(l['id']+'-garden-soil',(gx,gy,.72),(w*.25,.34,.06),'soil',False)
  for j in range(5):
   xx=gx-w*.1+j*w*.05;k.box(l['id']+'-garden-leaf-'+str(j),(xx,gy,.81),(.21,.24,.15),'leaf',False)
   k.mesh(l['id']+'-garden-bloom-'+str(j),[(xx-.08,gy-.08,.91),(xx+.08,gy-.08,.93),(xx+.08,gy+.08,.91),(xx-.08,gy+.08,.93)],[[0,1,2,3]],'flowerRose' if i%2 else 'flowerIvory',False)
 if l['family']=='market':
  k.box(l['id']+'-display',(w*.22,dep/2+.61,.65),(1.8,.70,1.18),'oak')
  for j in range(5):k.box(l['id']+'-goods-'+str(j),(w*.22-.68+j*.34,dep/2+.61,1.33),(.27,.40,.23),['produceRose','produceOchre','produceGreen'][j%3],False)
 # Each raised doorway has source-owned stone tread contacts.
 doorx=-w*.23 if w<4.7 else -w*.22 if l['family']=='market' else 0
 for j in range(2):
  ya=dep/2+(2-j)*.22;yb=ya+.24;z=(j+1)*.22
  k.box(l['id']+'-entry-step-'+str(j),(doorx,(ya+yb)/2,z/2),(1.5,.24,z),'stoneLight')
  pts=[r.matrix_basis@Vector((x,y,z)) for x,y in [(doorx-.75,ya),(doorx+.75,ya),(doorx+.75,yb),(doorx-.75,yb)]]
  floor({'id':l['id']+'-entry-contact-'+str(j),'vertices':[list(v) for v in pts],'faces':[[0,1,2,3]],'material':'stoneLight','role':'forecourt','objectId':l['id']})
