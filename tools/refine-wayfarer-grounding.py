"""Third review: route clearance, registered masks and district frontage."""
import bpy,json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];kit=runpy.run_path(str(ROOT/'tools/blender-v3-kit.py'));mesh=kit['mesh'];scene=bpy.context.scene;terrain=bpy.data.collections['court-terrain']
def road(id,points,width,role='street'):
 for o in list(terrain.objects):
  if o.name.startswith(id+'-'):bpy.data.objects.remove(o,do_unlink=True)
 for j,(a,b) in enumerate(zip(points,points[1:])):
  dx,dy=b[0]-a[0],b[1]-a[1];n=(dx*dx+dy*dy)**.5;nx,ny=-dy/n*width/2,dx/n*width/2
  vs=[(a[0]+nx,a[1]+ny,.005),(b[0]+nx,b[1]+ny,.005),(b[0]-nx,b[1]-ny,.005),(a[0]-nx,a[1]-ny,.005)]
  o=mesh(terrain,id+'-'+str(j),vs,[[0,1,2,3]],'paving','decorative',False);o['surface_role']='service' if role=='service' else 'residential';o['road_segment']=True;o['legacy_role']=role
road('inn-street',[[18.4,23],[16.8,26.1],[13.5,28.4]],1.9)
road('artisan-street',[[26,23.5],[28.5,25.5],[30.7,26.8],[30.7,31.1],[35.5,31.1],[38.6,31.1]],1.7)
road('domestic-lane',[[13.5,28.4],[13.5,32.5],[38.6,32.5]],1.8)
road('residential-access',[[25.35,26.5],[25.35,32.5]],.9,'service')
road('service-lane',[[36.8,22.5],[38.6,25],[38.6,32.5]],1.0,'service')
road('north-street',[[16.2,15.5],[14.8,11.5],[14.8,5.8],[21.05,5.8]],1.8)
road('north-passage',[[21.05,5.8],[21.05,-3]],.7)
road('south-connection',[[20.95,32.5],[21.45,34.0]],1.4)
road('south-passage',[[21.45,34],[21.45,40]],.7)
bpy.data.objects['north-house-placement'].location.x=28.0
for id in ['forest-transition','forest-transition-approach']:
 o=bpy.data.objects[id];o.location.x=21.05-o.parent.location.x
workyard=bpy.data.objects['forge-workyard']
for v,xy in zip(workyard.data.vertices,[(31.5,29.5),(39,29.5),(39,32.3),(31.5,32.3)]):v.co.x,v.co.y=xy
for id,points in {'guard-1':[[6.95,24.6],[6.95,19.1],[10.6,18.7],[10.6,19.9],[6.95,19.1]],'guard-2':[[4.2,25.3],[6.95,26.2],[7.5,24.7]]}.items():
 o=bpy.data.objects[id];root=o.parent;o['route_json']=json.dumps([[x-root.location.x,y-root.location.y,0] for x,y in points])
root=bpy.data.objects['market-shop-placement'];m=json.loads(root['structure_json']);body=bpy.data.objects['market-shop-body'];points=[list(v.co)[:2] for v in body.data.vertices[:4]];depths=[14*x+22*y for x,y in points];rear=points[depths.index(min(depths))];front=points[depths.index(max(depths))]
for index,l in enumerate(m['layers']):l['depth']=rear if index==0 else front
root['structure_json']=json.dumps(m)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-court.blend'));runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
