import bpy
from mathutils import Vector
for name in ['guild-hall','consortium-forecourt-arcades']:
 c=bpy.data.collections[name]
 print('COLLECTION',name,dict(c.items()))
 for o in c.objects:
  if o.type!='MESH' or not o.get('render_visible',True):continue
  if name=='guild-hall' and not any(k in o.name for k in ['nave','aisle-','tower-0','portal','front-pier','lantern','corner-drum']):continue
  if len(o.data.vertices)>50:continue
  vs=[o.matrix_world@v.co for v in o.data.vertices]
  print(o.name,[(round(min(v[i] for v in vs),2),round(max(v[i] for v in vs),2)) for i in range(3)],o.get('role'),o.data.materials[0].name)
for c in sorted([c for c in bpy.data.collections if c.name.startswith('frontage-')],key=lambda c:c.name):
 o=next(o for o in c.objects if o.name.endswith('-walls'));root=bpy.data.objects[c.name+'-placement']
 vs=[o.matrix_world@v.co for v in o.data.vertices]
 print('FRONTAGE',c.name,'root',tuple(round(v,2) for v in root.location),'scale',tuple(root.scale),'rotation',tuple(root.rotation_euler), 'bounds',[(round(min(v[i] for v in vs),2),round(max(v[i] for v in vs),2)) for i in range(3)])
