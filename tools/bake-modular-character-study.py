"""Ragnarok-style semantic layers from the current static source, via MCP.

Body/outfit and head/hair share the intact anatomical source. A stable head
polygon region separates their raster passes without cutting or changing its
deformation topology. These are equipped visible-only passes, not universal
swap-safe animation assets. No armatures/actions/runtime admission are created.
"""
import bpy,math,json

s=bpy.context.scene;assert s.name=='ASTRAEON_ASSET_FIT_04'
p='SM_AssetFit04_';root=bpy.data.objects['ROOT_AssetFit04'];body=bpy.data.objects[p+'Body']
geometry=[o for o in s.objects if o.type in ('MESH','CURVE')]
hidden={o:o.hide_render for o in geometry}
active=[o for o in geometry if not hidden[o]]
head_objects=[o for o in active if o.name in [p+'Eyes',p+'Brows'] or o.name.startswith((p+'FaceDetail_',p+'Hair_'))]
weapon=[o for o in active if o.name.startswith((p+'Blade_AxisGuide',p+'Hilt_Provisional',p+'Guard_Provisional',p+'Identity_Weapon'))]
cape=[o for o in active if o.name.startswith(p+'CapeRefit_')]
claimed=set(head_objects+weapon+cape+[body])
outfit=[o for o in active if o not in claimed]
groups={'BodyOutfit':[body]+outfit,'HeadHair':[body]+head_objects,'Weapon':weapon,'Cape':cape}
headindex=body.vertex_groups['Head'].index
weights={v.index:sum(g.weight for g in v.groups if g.group==headindex) for v in body.data.vertices}
headfaces={f.index for f in body.data.polygons if sum(weights[i] for i in f.vertices)/len(f.vertices)>=.5}
assert 0<len(headfaces)<len(body.data.polygons)
materials=list(body.data.materials);indices=[f.material_index for f in body.data.polygons]
assert len(materials)==1,'Expected the current single skin material'
slots={o:[(slot.link,slot.material) for slot in o.material_slots] for o in geometry}
settings=(s.render.resolution_x,s.render.resolution_y,s.render.filepath,root.rotation_euler.z)
holdouts={}
for culled in [False,True]:
    m=bpy.data.materials.new('Fit04_ModularHoldout_'+str(culled));m.use_nodes=True;m.use_backface_culling=culled
    ns=m.node_tree.nodes;ns.clear();a=ns.new('ShaderNodeHoldout');b=ns.new('ShaderNodeOutputMaterial');m.node_tree.links.new(a.outputs[0],b.inputs['Surface']);holdouts[culled]=m

def restore():
    for o,ss in slots.items():
        o.hide_render=hidden[o]
        for slot,(link,mat) in zip(o.material_slots,ss):slot.link=link;slot.material=mat
    body.data.materials.clear()
    for mat in materials:body.data.materials.append(mat)
    for f,index in zip(body.data.polygons,indices):f.material_index=index

def mask(obj):
    for slot in obj.material_slots:
        culled=bool(slot.material and slot.material.use_backface_culling)
        slot.link='OBJECT';slot.material=holdouts[culled]

out='C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/asset-fit-04/renders/'
try:
    s.render.resolution_x=320;s.render.resolution_y=320
    for d,a in [('S',0),('SW',-45),('W',-90),('NW',-135),('N',-180),('NE',-225),('E',-270),('SE',45)]:
        root.rotation_euler.z=math.radians(a)
        for module,objects in groups.items():
            restore()
            for obj in active:
                if obj not in objects:mask(obj)
            if module in ['BodyOutfit','HeadHair']:
                # One mesh and the same subdivision normals in both passes.
                body.data.materials.append(holdouts[False])
                for f in body.data.polygons:
                    wanted=(f.index in headfaces)==(module=='HeadHair')
                    f.material_index=0 if wanted else 1
            s.render.filepath=out+'modular-'+module+'-'+d+'.png';bpy.ops.render.render(write_still=True)
finally:
    restore()
    s.render.resolution_x,s.render.resolution_y,s.render.filepath,root.rotation_euler.z=settings
    for mat in holdouts.values():bpy.data.materials.remove(mat)
    bpy.context.view_layer.update()
receipt={'ownerApproved':False,'runtimeAdmitted':False,'coverage':[],
    'directions':['S','SW','W','NW','N','NE','E','SE'],'canvas':[320,320],'root':[160,264],
    'logicalParts':['BodyOutfit','HeadHair','Headgear','Weapon','Cape'],
    'bakedParts':list(groups),'headgear':{'state':'unequipped','asset':None,'rendered':False},
    'headRegion':{'method':'mean inherited Head weight >= 0.5 per source polygon','faces':len(headfaces),'sourceTopologyChanged':False},
    'objects':{n:[o.name for o in os] for n,os in groups.items()},
    'scope':'Visible-only layers of this static equipped combination; no arbitrary swapping or motion coverage',
    'cameraOrthoScale':s.camera.data.ortho_scale,'cameraMatrix':[list(row) for row in s.camera.matrix_world]}
s['modularStaticReceipt']=json.dumps(receipt)
print('MODULAR_STATIC_RECEIPT '+json.dumps(receipt))
