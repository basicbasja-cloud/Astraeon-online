"""Fresh-body and native-hand diagnostics with complete visibility restoration."""
import bpy, math, json, bmesh
from mathutils import Vector
s=bpy.context.scene;assert s.name=='ASTRAEON_ANATOMY_SOURCE_05'
p='SM_Anatomy05_';root=bpy.data.objects['ROOT_AnatomySource05'];body=bpy.data.objects[p+'Body'];head=bpy.data.objects[p+'Head']
geometry=[o for o in s.objects if o.type in ('MESH','CURVE')]
hidden={o:o.hide_render for o in geometry};slots={o:[(a.link,a.material) for a in o.material_slots] for o in geometry}
camera=s.camera;old=(root.rotation_euler.z,s.render.resolution_x,s.render.resolution_y,s.render.filepath)
out='C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/anatomy-base-05/renders/'
holdout=bpy.data.materials.new('Anatomy05_DiagnosticHoldout');holdout.use_nodes=True
ns=holdout.node_tree.nodes;ns.clear();a=ns.new('ShaderNodeHoldout');b=ns.new('ShaderNodeOutputMaterial');holdout.node_tree.links.new(a.outputs[0],b.inputs[0])
clay=bpy.data.materials.new('Anatomy05_BodyClay');clay.use_nodes=True
bsdf=next(n for n in clay.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bsdf.inputs['Base Color'].default_value=(.30,.34,.40,1);bsdf.inputs['Roughness'].default_value=.8
diagnostic=camera.copy();diagnostic.data=camera.data.copy();diagnostic.name='CAM_Anatomy05_GripDiagnostic';s.collection.objects.link(diagnostic);diagnostic.data.ortho_scale=.42
receipt=json.loads(s['anatomySourceReceipt']);center=Vector(receipt['handTargets']['R']['center'])
weapon=[o for o in geometry if not hidden[o] and o.name.startswith((p+'Blade_',p+'Hilt_',p+'Identity_Weapon'))]
hands=[bpy.data.objects[p+'Cloth_Glove_R']]
armor=[o for o in geometry if o.name.startswith(p+'Polish_Bracer') and '_R' in o.name and not hidden[o]]
def restore():
    for o,ss in slots.items():
        o.hide_render=hidden[o]
        for a,(link,mat) in zip(o.material_slots,ss):a.link=link;a.material=mat
def render(name):s.render.filepath=out+name+'.png';bpy.ops.render.render(write_still=True)
try:
    s.render.resolution_x=320;s.render.resolution_y=320
    for direction,angle in [('S',0),('SW',-45),('W',-90),('NW',-135),('N',-180),('NE',-225),('E',-270),('SE',45)]:
        restore();root.rotation_euler.z=math.radians(angle);render(direction+'-current')
        for obj in geometry:
            if obj not in weapon:
                for slot in obj.material_slots:slot.link='OBJECT';slot.material=holdout
        render('weapon-visible-'+direction)
        restore()
        for obj in geometry:obj.hide_render=obj not in weapon
        render('weapon-isolated-'+direction)
        if direction in ['SE','W','NW','N']:
            restore()
            for obj in geometry:
                obj.hide_render=obj not in [body,head]
                if obj==body:
                    for slot in obj.material_slots:slot.link='OBJECT';slot.material=clay
            render('anatomy-only-'+direction)
            restore()
            for obj in geometry:
                if obj in hands:obj.hide_render=True
            render('glove-removed-'+direction)
            s.camera=diagnostic;diagnostic.location=root.matrix_world@center+diagnostic.rotation_euler.to_quaternion()@Vector((0,0,10))
            s.render.resolution_x=640;s.render.resolution_y=640;restore();render('grip-equipped-'+direction)
            for obj in geometry:obj.hide_render=obj not in weapon+hands+armor
            render('grip-isolated-'+direction)
            restore();s.camera=camera;s.render.resolution_x=320;s.render.resolution_y=320
    restore();root.rotation_euler.z=math.radians(45);s.render.resolution_x=1280;s.render.resolution_y=1280;render('SE-current-large')
finally:
    restore();s.camera=camera;root.rotation_euler.z,s.render.resolution_x,s.render.resolution_y,s.render.filepath=old
    bpy.data.objects.remove(diagnostic,do_unlink=True);bpy.data.materials.remove(holdout);bpy.data.materials.remove(clay)
bm=bmesh.new();bm.from_mesh(body.data)
receipt['topology']={'vertices':len(bm.verts),'faces':len(bm.faces),'triangles':sum(len(f.verts)==3 for f in bm.faces),'boundaryEdges':sum(e.is_boundary for e in bm.edges),'nonmanifoldEdges':sum(not e.is_manifold for e in bm.edges),'maxWeights':max(sum(g.weight>.00001 for g in v.groups) for v in body.data.vertices),'minWeightSum':min(sum(g.weight for g in v.groups) for v in body.data.vertices),'maxWeightSum':max(sum(g.weight for g in v.groups) for v in body.data.vertices)};bm.free()
receipt['camera']={'canvas':[320,320],'root':[160,264],'scale':camera.data.ortho_scale,'matrix':[list(row) for row in camera.matrix_world]}
receipt['actualGripAndClothedWristNeedVisualReview']=True
s['anatomySourceReceipt']=json.dumps(receipt)
print('NEW_ANATOMY_SOURCE_CHECKS '+s['anatomySourceReceipt'])
