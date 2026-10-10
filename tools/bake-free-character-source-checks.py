"""Eight-view static layer/removal proof from one editable source.

Visible-only layers describe this equipped pose, not arbitrary substitutions.
Whole hidden body surfaces remain in the source and are rendered separately.
"""
import bpy,math,json,bmesh

s=bpy.context.scene;assert s.name=='ASTRAEON_ASSET_FIT_04'
assert not any(o.type=='ARMATURE' for o in s.objects)
p='SM_AssetFit04_';root=bpy.data.objects['ROOT_AssetFit04']
out='C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/asset-fit-04/'
geometry=[o for o in s.objects if o.type in ('MESH','CURVE')]
groups={
 'BaseBody':[o for o in geometry if o.name in [p+'Body',p+'Eyes',p+'Brows'] or o.name.startswith(p+'FaceDetail_')],
 'Hair':[o for o in geometry if o.name.startswith(p+'Hair_')],
 'Weapon':[o for o in geometry if o.name.startswith((p+'Blade_AxisGuide',p+'Hilt_Provisional',p+'Guard_Provisional'))],
 'BackAccessory':[o for o in geometry if o.name.startswith(p+'CapeRefit_')],
}
claimed={o for objects in groups.values() for o in objects}
groups['Outfit']=[o for o in geometry if o not in claimed]
hidden={o:o.hide_render for o in geometry}
slots={o:[(slot.link,slot.material) for slot in o.material_slots] for o in geometry}
yaw=root.rotation_euler.z;settings=(s.render.resolution_x,s.render.resolution_y,s.render.filepath)
holdouts={}
for culled in [False,True]:
 m=bpy.data.materials.new('Fit04_StaticHoldout_'+str(culled));m.use_nodes=True;m.use_backface_culling=culled
 ns=m.node_tree.nodes;ns.clear();a=ns.new('ShaderNodeHoldout');b=ns.new('ShaderNodeOutputMaterial');m.node_tree.links.new(a.outputs[0],b.inputs['Surface']);holdouts[culled]=m
def restore():
 for o,ss in slots.items():
  o.hide_render=hidden[o]
  for slot,(link,mat) in zip(o.material_slots,ss):slot.link=link;slot.material=mat
def render(name):
 s.render.filepath=out+'renders/'+name+'.png';bpy.ops.render.render(write_still=True)
try:
 s.render.resolution_x=320;s.render.resolution_y=320
 for d,a in [('S',0),('SW',-45),('W',-90),('NW',-135),('N',-180),('NE',-225),('E',-270),('SE',45)]:
  root.rotation_euler.z=math.radians(a);restore();render(d+'-final-static')
  for name,objects in groups.items():
   restore()
   for obj in geometry:
    if obj not in objects:
     for slot in obj.material_slots:
      culled=bool(slot.material and slot.material.use_backface_culling)
      slot.link='OBJECT';slot.material=holdouts[culled]
   render('equipped-layer-'+name+'-'+d)
  if d in ['SE','W','NW','N']:
   for name in ['Outfit','Hair','Weapon','BackAccessory']:
    restore()
    for obj in groups[name]:obj.hide_render=True
    render(name.lower()+'-removed-'+d)
   restore()
   for obj in geometry:obj.hide_render=obj not in groups['BaseBody']
   render('full-body-only-'+d)
 restore();root.rotation_euler.z=math.radians(45)
 s.render.resolution_x=1280;s.render.resolution_y=1280;render('SE-final-static-large')
finally:
 restore();root.rotation_euler.z=yaw
 s.render.resolution_x,s.render.resolution_y,s.render.filepath=settings
 for m in holdouts.values():bpy.data.materials.remove(m)
 bpy.context.view_layer.update()
body=bpy.data.objects[p+'Body'];bm=bmesh.new();bm.from_mesh(body.data)
receipt={'scene':s.name,'ownerApproved':False,'runtimeAdmitted':False,'coverage':[],
 'armatures':0,'actionsInScene':0,'vertices':len(body.data.vertices),'faces':len(body.data.polygons),
 'quads':sum(len(f.vertices)==4 for f in body.data.polygons),'triangles':sum(len(f.vertices)==3 for f in body.data.polygons),
 'boundaryEdges':sum(e.is_boundary for e in bm.edges),'nonmanifoldEdges':sum(not e.is_manifold for e in bm.edges),
 'maxInheritedWeights':max(sum(g.weight>.00001 for g in v.groups) for v in body.data.vertices),
 'minInheritedWeightSum':min(sum(g.weight for g in v.groups) for v in body.data.vertices),
 'maxInheritedWeightSum':max(sum(g.weight for g in v.groups) for v in body.data.vertices),
 'modules':{n:[o.name for o in objects if not hidden[o]] for n,objects in groups.items()},
 'canvas':[320,320],'root':[160,264],'runtimeScale':.5,'runtimeRoot':[80,132],
 'cameraOrthoScale':s.camera.data.ortho_scale,'cameraMatrix':[list(row) for row in s.camera.matrix_world],
 'gripMethod':s.get('gripFrameMethod',''),'handTransformsAreStatic':True,
 'equippedLayerScope':'Visible pixels of this static equipped pose; not substitution-ready action coverage'}
bm.free();s['staticCheckReceipt']=json.dumps(receipt)
print('FIT04_STATIC_CHECK_RECEIPT '+json.dumps(receipt))
