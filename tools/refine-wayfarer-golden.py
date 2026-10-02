"""Recorded second spatial/art review edit. Run on the saved Golden court.
Normal authoring continues from the resulting saved Blender scene.
"""
import bpy,json,math,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];kit=runpy.run_path(str(ROOT/'tools/blender-v3-kit.py'));mesh=kit['mesh'];scene=bpy.context.scene;terrain=bpy.data.collections['court-terrain']
def road(id,points,width,role='street'):
 for o in list(terrain.objects):
  if o.name.startswith(id+'-'):bpy.data.objects.remove(o,do_unlink=True)
 for j,(a,b) in enumerate(zip(points,points[1:])):
  dx,dy=b[0]-a[0],b[1]-a[1];n=math.hypot(dx,dy);nx,ny=-dy/n*width/2,dx/n*width/2
  vs=[(a[0]+nx,a[1]+ny,.005),(b[0]+nx,b[1]+ny,.005),(b[0]-nx,b[1]-ny,.005),(a[0]-nx,a[1]-ny,.005)]
  o=mesh(terrain,id+'-'+str(j),vs,[[0,1,2,3]],'paving','decorative',False);o['surface_role']='service' if role=='service' else 'residential';o['road_segment']=True;o['legacy_role']=role
road('inn-street',[[18.4,23],[17.4,26.0],[16.8,28.4],[14,28.4]],2.0)
road('artisan-street',[[26,23.5],[28.5,25.5],[31.2,30.5],[38.6,30.5]],1.8)
road('residential-access',[[26.1,26.5],[26.1,32.5]],1.0,'service')

root=bpy.data.objects['artisan-workshop-placement'];root.location=(35.5,28.5,0)
service=bpy.data.objects['artisan'];service.location=(-.2,1.9,0)
root=bpy.data.objects['market-shop-placement'];sprite=json.loads(root['data_json']);sx,sy=250/sprite['w'],375/sprite['h'];sprite.update(w=250,h=375);root['data_json']=json.dumps(sprite)
# Scale the authored physical ground plane with its revised painted registration.
for o in bpy.data.collections['market-shop'].objects:
 if o.type=='MESH':
  for v in o.data.vertices:
   px,py=v.co.x*48-v.co.y*32,v.co.x*14+v.co.y*22
   v.co.x=(22*px*sx+32*py*sy)/1504;v.co.y=(48*py*sy-14*px*sx)/1504
   v.co.z*=sy
s=json.loads(root['structure_json'])
for l in s['layers']:
 px,py=l['depth'][0]*48-l['depth'][1]*32,l['depth'][0]*14+l['depth'][1]*22
 l['depth']=[(22*px*sx+32*py*sy)/1504,(48*py*sy-14*px*sx)/1504]
root['structure_json']=json.dumps(s)


for c in bpy.data.collections:
 if c.get('family')=='vegetation':
  root=next(o for o in c.objects if o.get('kind')=='presentation');m=json.loads(root['structure_json']);m['layers']=[{'name':'trunk','region':[0,.66,1,1],'depth':[0,0]},{'name':'canopy','region':[0,0,1,.66],'depth':[.35,.45],'visibility':'selective-overhead'}];root['structure_json']=json.dumps(m)

routes={'guard-1':[[6.95,24.6],[6.95,19.1],[10.6,18.7],[10.6,24.6]],
        'customer-1':[[28.7,22.8],[31.0,24.0],[34.0,24.0],[34.5,22.8]]}
for id,points in routes.items():
 o=bpy.data.objects[id];root=o.parent;o['route_json']=json.dumps([[x-root.location.x,y-root.location.y,0] for x,y in points])

# Lightweight original masonry, authored as volumes with real collision. It
# defines the settlement edge, leaving the three registered gate mouths open.
boundary_paths=[[(5.0,23.5),(3,15),(7,7),(16,4.5),(19.2,4.5)],
                [(23.5,4.5),(28,4.5),(39.5,6),(40.3,22),(40.3,34.5),(28,36.7),(24,36.7)],
                [(19.3,37.2),(11,36.5),(8.2,28.7),(9.8,23.0)]]
index=0
for points in boundary_paths:
 for a,b in zip(points,points[1:]):
  id='town-wall-'+str(index);index+=1
  if id in bpy.data.collections:
   for o in list(bpy.data.collections[id].objects):bpy.data.objects.remove(o,do_unlink=True)
   bpy.data.collections.remove(bpy.data.collections[id])
  c=kit['family'](id,'fortification');dx,dy=b[0]-a[0],b[1]-a[1];n=math.hypot(dx,dy);nx,ny=-dy/n*.18,dx/n*.18
  poly=[(a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny),(b[0]-nx,b[1]-ny),(a[0]-nx,a[1]-ny)];vs=[(x,y,z) for z in [0,.95] for x,y in poly]
  mesh(c,id+'-masonry',vs,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],'stone','solid',True)

route=json.loads(scene['route_json'])
for stop in route:
 if stop['name']=='Blacksmith':stop['position']=[35.0,31.0]
 if stop['name']=='Inn':stop['position']=[14.3,28.6]
 if stop['name']=='Residential':stop['position']=[23.4,33.0]
 if stop['name']=='Shrine':stop['position']=[31,14.4]
scene['route_json']=json.dumps(route)
districts=json.loads(scene['districts_json'])
for d in districts:
 if d['name']=='Bronze Anvil':d['x']=35.5;d['y']=30
scene['districts_json']=json.dumps(districts)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-court.blend'));runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
