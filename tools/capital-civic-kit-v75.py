"""Original civic architecture assembled from pierced facades and stone modules.

Native geometry only. Council, archive and exchange share construction details,
not complete silhouettes. The saved models contain real window reveals, arched
entrances, roofs, galleries, towers and dressed foundations.
"""
import bpy,math,runpy
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1]
FacadeKit=runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit']
def build_civic(spec,collection,root,floor):
 k=FacadeKit(collection,root);k.prefix='capital-v75-';name=spec['id'];w,d,h=spec['width'],spec['depth'],spec['height'];archive='archive' in name;exchange='exchange' in name
 wallmat='civicIvory';zbase=.65
 # Physical mass is separate from the pierced visible facades.
 core=k.box(name+'-physical-mass',(0,0,h/2),(w,d,h),wallmat,False);core['role']='solid';core['render_visible']=False
 k.box(name+'-foundation',(0,0,.28),(w+.45,d+.4,.56),'civicShadow')
 def facade(suffix,width,origin,angle):
  # Each storey has actual apertures with deep reveals and nine-light glazing.
  start=.60;floors=2 if exchange else 3;story=(h-.65)/floors
  for j in range(floors):
   centers=[(i-2)*width*.16 for i in range(5)]
   if suffix=='front' and j==0:
    # The center entrance is framed separately, leaving a true opening.
    before=set(collection.objects)
    for side in (-1,1):
     k.upper_face(name+suffix+'-ground-wing-'+str(side),width*.38,start,start+story,[-width*.12,0,width*.12],wallmat,(side*width*.31,0),0,wh=2.4,ww=1.18)
    rotation=Matrix.Rotation(angle,4,'Z')
    for o in set(collection.objects)-before:
     for v in o.data.vertices:v.co=rotation@v.co+Vector((*origin,0))
    # A dressed arch and inset paired doors occupy the open center bay.
   else:k.upper_face(name+suffix+'-floor-'+str(j),width,start,start+story,centers,wallmat,origin,angle,wh=min(2.4,story*.58),ww=1.48)
   start+=story
 facade('front',w,(0,d/2),0);facade('rear',w,(0,-d/2),math.pi)
 facade('west',d,(-w/2,0),math.pi/2);facade('east',d,(w/2,0),-math.pi/2)
 # Recolor shared construction pieces into the original civic stone palette.
 for o in collection.objects:
  if o.type!='MESH':continue
  m=o.data.materials[0].name
  if m=='timber':o.data.materials[0]=bpy.data.materials['civicShadow']
  elif m in ('oak','stoneLight'):o.data.materials[0]=bpy.data.materials['civicIvory']
  elif m=='frontageGlazing':o.data.materials[0]=bpy.data.materials['civicGlass']
 def arch(suffix,x,y,z,width,spring,rise):
  for i in range(12):
   aa,bb=i*math.pi/12,(i+1)*math.pi/12
   poly=[(x-math.cos(a)*r,z+spring+math.sin(a)*rr) for a,r,rr in [(aa,width/2,rise),(bb,width/2,rise),(bb,width/2+.25,rise+.25),(aa,width/2+.25,rise+.25)]]
   vs=[(xx,yy,zz) for yy in (y-.35,y+.35) for xx,zz in poly]
   k.mesh(name+suffix+'-voussoir-'+str(i),vs,[[0,1,2,3],[4,7,6,5],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]],'civicIvory')
  for side in (-1,1):k.box(name+suffix+'-jamb-'+str(side),(x+side*(width/2+.13),y,z+spring/2),(.26,.7,spring),'civicIvory')
 portalw=4.2 if exchange else 4.7;spring=3.6 if exchange else 3.4;rise=1.1
 arch('-portal',0,d/2+.22,.6,portalw,spring,rise)
 # Central bay's true arch aperture closes into stone spandrels.
 for side in (-1,1):
  xa,xb=portalw/2,w*.12
  k.box(name+'-portal-side-'+str(side),(side*(xa+xb)/2,d/2,2.55),(xb-xa,.24,5.1),'civicIvory')
 # Fill above the arch with curved underside; never cover the open doorway.
 ceiling=.6+(h-.65)/(2 if exchange else 3)
 for i in range(16):
  xa=-portalw/2+i*portalw/16;xb=xa+portalw/16
  za=.6+spring+rise*math.sqrt(max(0,1-(xa/(portalw/2))**2));zb=.6+spring+rise*math.sqrt(max(0,1-(xb/(portalw/2))**2))
  if max(za,zb)<ceiling:
   k.mesh(name+'-portal-spandrel-'+str(i),[(xa,d/2-.12,za),(xb,d/2-.12,zb),(xb,d/2-.12,ceiling),(xa,d/2-.12,ceiling),(xa,d/2+.12,za),(xb,d/2+.12,zb),(xb,d/2+.12,ceiling),(xa,d/2+.12,ceiling)],[[0,1,2,3],[4,7,6,5],[0,4,5,1]],'civicIvory')
 for side in (-1,1):
  k.box(name+'-door-leaf-'+str(side),(side*portalw/4,d/2-.36,2.28),(portalw/2-.08,.10,3.45),'civicDoor')
  for z in (1.10,3.32):k.box(name+'-door-brace-'+str((side,z)),(side*portalw/4,d/2-.29,z),(portalw/2-.20,.045,.10),'civicGold')
  k.box(name+'-door-pull-'+str(side),(side*.24,d/2-.21,2.35),(.075,.10,.40),'civicGold')
 # Corner pilasters, restrained gold courses and cornice relief.
 for xx in (-w/2,w/2):
  for yy in (-d/2,d/2):
   k.box(name+'-pilaster-'+str((xx,yy)),(xx,yy,h/2),(.56,.56,h),'civicShadow')
   for zz in (.45,h*.45,h-.3):k.box(name+'-capital-'+str((xx,yy,zz)),(xx,yy,zz),(.80,.80,.26),'civicIvory')
 for zz in (h*.33,h*.67,h):
  k.box(name+'-front-course-'+str(zz),(0,d/2+.20,zz),(w+.75,.50,.25),'civicIvory')
 k.box(name+'-gold-belt',(0,d/2+.47,h-.08),(w,.045,.085),'civicGold',False)
 # Three connected roof masses: central nave above quieter side wings.
 def roof(suffix,x,width,ya,yb,eave,peak):
  roofobj=k.mesh(name+suffix+'-roof',[(x-width/2,ya,eave),(x-width/2,yb,eave),(x,yb,peak),(x,ya,peak),(x+width/2,ya,eave),(x+width/2,yb,eave)],[[0,1,2,3],[4,3,2,5]],'civicSlate')
  roofobj['role']='overhead'
  slope=math.atan2(peak-eave,width/2)
  for face in roofobj.data.polygons:
   for li in face.loop_indices:
    v=roofobj.data.vertices[roofobj.data.loops[li].vertex_index].co
    roofobj.data.uv_layers.active.data[li].uv=(v.y/2.4,-abs(v.x-x)/math.cos(slope)/2.4)
  for yy in (ya,yb):k.mesh(name+suffix+'-gable-'+str(yy),[(x-width/2,yy,eave),(x+width/2,yy,eave),(x,yy,peak)],[[0,1,2]],'civicIvory')
  for side in (-1,1):
   k.beam(name+suffix+'-eave-'+str(side),(x+side*width/2,ya,eave),(x+side*width/2,yb,eave),.18,'civicShadow')
   k.beam(name+suffix+'-verge-'+str(side),(x+side*width/2,yb+.03,eave),(x,yb+.03,peak),.10,'civicGold')
  k.beam(name+suffix+'-ridge',(x,ya,peak+.05),(x,yb,peak+.05),.16,'civicGold')
 roof('-nave',0,w*.38,-d/2-.65,d/2+.75,h+.3,spec['roofPeak'])
 for side in (-1,1):roof('-wing-'+str(side),side*w*.345,w*.35,-d/2-.55,d/2+.60,h-.08,h+4.0)
 # Individual silhouette identities: archive's paired turrets and rose gallery;
 # council's crowned center and balcony; exchange's arcaded, canopy frontage.
 def tower(suffix,x,y,base,top):
  k.box(name+suffix+'-drum',(x,y,(base+top)/2),(2.5,2.5,top-base),'civicIvory')
  k.box(name+suffix+'-crown',(x,y,top),(2.85,2.85,.28),'civicGold')
  k.mesh(name+suffix+'-spire',[(x-1.8,y-1.8,top+.15),(x+1.8,y-1.8,top+.15),(x+1.8,y+1.8,top+.15),(x-1.8,y+1.8,top+.15),(x,y,top+4.0)],[[0,1,4],[1,2,4],[2,3,4],[3,0,4]],'civicSlate')
  k.box(name+suffix+'-finial',(x,y,top+4.38),(.11,.11,.65),'civicGold')
 if archive:
  for side in (-1,1):tower('-archive-turret-'+str(side),side*w*.37,d/2-.45,h-1.2,h+2.2)
  # Stone-framed luminous archive rosette, with radial mullions.
  cx,yy,cz=0,d/2+.48,h*.75
  vs=[(cx,yy,cz)]+[(2.0*math.cos(i*math.tau/24),yy,cz+2.0*math.sin(i*math.tau/24)) for i in range(24)]
  k.mesh(name+'-archive-rosette',vs,[[0,i+1,(i+1)%24+1] for i in range(24)],'civicGlassLight',False)
  for i in range(16):
   a,b=i*math.tau/16,(i+1)*math.tau/16
   k.beam(name+'-rose-rim-'+str(i),(2*math.cos(a),yy+.06,cz+2*math.sin(a)),(2*math.cos(b),yy+.06,cz+2*math.sin(b)),.16,'civicIvory')
   if i%2==0:k.beam(name+'-rose-ray-'+str(i),(0,yy+.08,cz),(1.9*math.cos(a),yy+.08,cz+1.9*math.sin(a)),.08,'civicGold')
 elif exchange:
  for j,x in enumerate((-10,-5.0,5.0,10)):
   arch('-exchange-arcade-'+str(j),x,d/2+1.0,.65,3.8,3.0,1.2)
   for band in range(6):
    xa=x-1.8+band*.6;k.mesh(name+f'-canopy-{j}-{band}',[(xa,d/2+.85,3.5),(xa+.6,d/2+.85,3.5),(xa+.6,d/2+2.4,3.05),(xa,d/2+2.4,3.05)],[[0,1,2,3]],'shopAwningSage' if band%2 else 'homeLimewash',False)
  tower('-exchange-bell',-w*.37,-d*.18,h-.5,h+2.0)
 else:
  # Broad octagonal lantern crowns the council; restrained gold ribs.
  rp=spec['roofPeak'];profile=[(rp-.15,2.0),(rp+.05,2.2),(rp+.95,2.2),(rp+2.35,1.75),(rp+3.45,.75),(rp+4.45,.10)]
  for j,((za,ra),(zb,rb)) in enumerate(zip(profile,profile[1:])):
   vs=[(r*math.cos(i*math.tau/8+math.pi/8),-2+r*math.sin(i*math.tau/8+math.pi/8),z) for z,r in [(za,ra),(zb,rb)] for i in range(8)]
   k.mesh(name+'-council-lantern-'+str(j),vs,[[i,(i+1)%8,(i+1)%8+8,i+8] for i in range(8)],'civicIvory' if j<2 else 'civicSlate')
   for i in range(8):k.beam(name+f'-lantern-rib-{j}-{i}',vs[i],vs[i+8],.05,'civicGold')
  k.box(name+'-balcony',(0,d/2+.95,5.6),(8.0,1.8,.22),'civicIvory')
  for j in range(13):k.box(name+'-baluster-'+str(j),(-3.75+j*.625,d/2+1.73,6.25),(.11,.11,1.1),'civicIvory')
  k.box(name+'-balcony-rail',(0,d/2+1.73,6.84),(8.1,.2,.16),'civicGold')
  for side in (-1,1):tower('-council-watch-'+str(side),side*w*.39,d/2-.6,h-1,h+(.9 if side<0 else 1.7))
 # Banners deliberately repeat civic colors without overwhelming the stone.
 for side in (-1,1):
  x=side*w*.22;k.box(name+'-banner-'+str(side),(x,d/2+.39,6.65),(1.00,.055,2.5),'clothBlue',False)
  k.beam(name+'-banner-arm-'+str(side),(x-.65,d/2+.47,8.0),(x+.65,d/2+.47,8.0),.07,'civicGold')
 # Physical three-tread public entrance contacts.
 x,y=spec['center']
 for j in range(3):
  ya=y+d/2+(3-j)*.42;yb=ya+.46;z=(j+1)*.20
  k.box(name+'-entry-riser-'+str(j),(0,ya+.23-y,z/2),(6.4,.46,z),'civicIvory')
  floor({'id':name+'-entry-tread-'+str(j),'vertices':[[x-3.2,ya,z],[x+3.2,ya,z],[x+3.2,yb,z],[x-3.2,yb,z]],'faces':[[0,1,2,3]],'material':'civicIvory','role':'forecourt','objectId':name})
 return k
