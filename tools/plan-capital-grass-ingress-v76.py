"""Plan restrained planting against actual native floors and painted joints.

No procedural replacement lawn or new image is introduced. Street roots follow
the world UVs of the existing paving, within half a unit of a planted curb.
"""
import json, math, random, hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from shapely.geometry import Polygon, Point, MultiPoint, LineString
from shapely.ops import unary_union
from shapely.strtree import STRtree

R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v76/property-frontages'
raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();s=json.loads(raw)
p=json.loads((O.parent/'native-plan.json').read_text())
objects={a['id']:a for a in s['objects']}
assert 'capital-grass-ingress-v76' not in objects
cover=objects['capital-beta-frontage-groundcover']
green=unary_union([Polygon([a['vertices'][i][:2] for i in f]) for a in cover['parts'] for f in a['faces']])
private=unary_union([Polygon([a['vertices'][i][:2] for i in f]) for a in s['terrain']['surfaces']
    if a['material']=='houseApronPaving' and all(abs(v[2]-.04)<.0001 for v in a['vertices']) for f in a['faces']])
entries=[]
for lot in p['lots']:
    heading=lot['angle']+lot.get('frontageOffset',0);normal=(-math.sin(heading),math.cos(heading))
    for a in objects[lot['id']]['parts']:
        if not a['id'].endswith('-door-leaf'):continue
        center=[sum(v[i] for v in a['vertices'])/len(a['vertices']) for i in (0,1)]
        entries.append(LineString([center,[center[i]+normal[i]*4.2 for i in (0,1)]]).buffer(1.17,cap_style=2))
feet=[MultiPoint([v[:2] for v in a['vertices']]).convex_hull.buffer(.27)
      for o in s['objects'] for a in o['parts'] if a['role']=='solid' and min(v[2] for v in a['vertices'])<1]
anchors=([Point(a['position'][:2]).buffer(1.05) for o in s['objects'] for a in o.get('services',[])]+
    [Point(a['anchor'][:2]).buffer(1.05) for o in s['objects'] for a in o.get('portals',[])])
blocked=unary_union(entries+feet+anchors)
polys=[];floors=[]
for a in s['terrain']['surfaces']:
    if not a.get('walkable'):continue
    for f in a['faces']:
        for i in range(1,len(f)-1):
            vs=[a['vertices'][j] for j in (f[0],f[i],f[i+1])];poly=Polygon([v[:2] for v in vs])
            if poly.area<1e-9:continue
            polys.append(poly);floors.append((a['id'],a['material'],vs))
tree=STRtree(polys)
def support(q):
    hits=[]
    for i in tree.query(q,predicate='intersects'):
        name,mat,vs=floors[i];a,b,c=vs
        determinant=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        u=((b[1]-c[1])*(q.x-c[0])+(c[0]-b[0])*(q.y-c[1]))/determinant
        v=((c[1]-a[1])*(q.x-c[0])+(a[0]-c[0])*(q.y-c[1]))/determinant
        hits.append((u*a[2]+v*b[2]+(1-u-v)*c[2],name,mat))
    return max(hits) if hits else None
spec=s['materials']['publicTownStone']['texture'];im=Image.open(R/spec['file']).convert('RGB')
pixels=np.asarray(im);luma=np.mean(pixels,axis=2);size=spec['worldSize'];width,height=im.size
def seam(q):
    # Repeat wrapping and Texture.flipY match the ordinary WebGL material.
    u=(q.x/size)%1;v=(q.y/size)%1
    x=int(u*width)%width;y=int((1-v)*height)%height
    return float(luma[y,x])
r=random.Random(761603);roots=[];occupied=[]
def accept(q,kind):
    if blocked.intersects(q.buffer(.055)):return False
    hit=support(q)
    if not hit:return False
    z,floor,mat=hit
    if kind=='lawn' and (mat!='houseApronPaving' or not green.contains(q.buffer(.055))):return False
    if kind=='joint' and (mat!='publicTownStone' or seam(q)>103 or
        private.distance(q)<.24 or private.distance(q)>.49 or green.distance(q)>.8):return False
    if any((q.x-x)**2+(q.y-y)**2<.22**2 for x,y in occupied):return False
    occupied.append((q.x,q.y));roots.append({'position':[q.x,q.y,z+.012],'kind':kind,
        'floor':floor,'floorMaterial':mat,**({'paintedJointLuma':seam(q)} if kind=='joint' else {})})
    return True
def lines(geometry):
    if geometry.geom_type in ('LineString','LinearRing'):return [geometry]
    return [a for g in geometry.geoms for a in lines(g)]
lawn_candidates=[]
for line in lines(green.boundary):
    for j in range(int(line.length/.45)):
        q=line.interpolate((j+.5)*.45)
        for k in range(3):
            a=r.random()*math.tau;d=r.uniform(.08,.23)
            candidate=Point(q.x+math.cos(a)*d,q.y+math.sin(a)*d)
            if green.contains(candidate):lawn_candidates.append(candidate);break
r.shuffle(lawn_candidates)
for q in lawn_candidates:
    if sum(a['kind']=='lawn' for a in roots)>=800:break
    accept(q,'lawn')
joint_candidates=[]
for line in lines(private.boundary):
    for j in range(int(line.length/.55)):
        d=(j+.5)*.55;q=line.interpolate(d);near=line.interpolate(min(d+.04,line.length))
        dx,dy=near.x-q.x,near.y-q.y;n=math.hypot(dx,dy)
        if n<1e-8:continue
        for sign in (-1,1):
            outside=Point(q.x+sign*dy/n*.35,q.y-sign*dx/n*.35)
            if private.contains(outside) or green.distance(outside)>.8:continue
            # Search a small patch for a real painted joint, not an arbitrary
            # dark-green dot painted over the middle of a stone.
            choices=[Point(outside.x+x*.013,outside.y+y*.013) for x in range(-5,6) for y in range(-5,6)]
            choices.sort(key=lambda a:seam(a))
            joint_candidates.extend(choices[:4])
r.shuffle(joint_candidates)
for q in joint_candidates:
    if sum(a['kind']=='joint' for a in roots)>=400:break
    accept(q,'joint')
assert sum(a['kind']=='lawn' for a in roots)>=500
assert sum(a['kind']=='joint' for a in roots)>=100
parts={}
for index,root in enumerate(roots):
    x,y,z=root['position'];cell=(int(x//32),int(y//32))
    for blade in range(3):
        material='capitalGrassBladeLight' if (index+blade)%3 else 'capitalGrassBladeShade'
        name=f'capital-grass-{cell[0]}-{cell[1]}-{material}'
        a=parts.setdefault(name,{'id':name,'material':material,'vertices':[],'faces':[]})
        angle=r.random()*math.tau;dx,dy=.018*math.cos(angle),.018*math.sin(angle);off=len(a['vertices'])
        a['vertices'].extend([[x-dx,y-dy,z],[x+dx,y+dy,z],
            [x+r.uniform(-.035,.035),y+r.uniform(-.035,.035),z+r.uniform(.10,.22)]])
        a['faces'].append([off,off+1,off+2])
count=sum(len(a['faces']) for a in parts.values());assert count<4000
grass_spec=s['materials']['grass']['texture']
grass_pixels=np.asarray(Image.open(R/grass_spec['file']).convert('RGB'),dtype=float)/255
grass_linear=np.where(grass_pixels<=.04045,grass_pixels/12.92,((grass_pixels+.055)/1.055)**2.4)
receipt={'beforeSourceSHA256':hashlib.sha256(raw).hexdigest(),'owner':'capital-grass-ingress-v76',
    'roots':roots,'pieces':list(parts.values()),'triangles':count,'triangleBudget':4000,
    'counts':{kind:sum(a['kind']==kind for a in roots) for kind in ('lawn','joint')},
    'jointTexture':spec,'jointTextureSHA256':hashlib.sha256((R/spec['file']).read_bytes()).hexdigest(),
    'jointMaximumLuma':103,'maximumCurbDistance':.49,'maximumPlantingDistance':.8,
    'grassTextureMeanLinearRGB':grass_linear.mean(axis=(0,1)).tolist(),
    'grassTextureSHA256':hashlib.sha256((R/grass_spec['file']).read_bytes()).hexdigest(),
    'entranceClearWidth':2.34,'additionalTextures':0,'additionalObstacles':0}
(O/'grass-ingress-plan.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ('roots','pieces')},indent=2))
