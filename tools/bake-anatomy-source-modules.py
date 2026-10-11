"""Same-frame visible-only Ragnarok-style modules from the new anatomy study."""
import bpy,math,json
s=bpy.data.scenes['ASTRAEON_ANATOMY_SOURCE_05'];bpy.context.window.scene=s
p='SM_Anatomy05_';root=bpy.data.objects['ROOT_AnatomySource05']
geometry=[o for o in s.objects if o.type in ['MESH','CURVE']]
hidden={o:o.hide_render for o in geometry};active=[o for o in geometry if not hidden[o]]
head=[o for o in active if o.name==p+'Head' or o.name.startswith(p+'Hair_')]
weapon=[o for o in active if o.name.startswith((p+'Blade_',p+'Hilt_',p+'Identity_Weapon'))]
cape=[o for o in active if o.name.startswith(p+'DrapeCape')]
claimed=set(head+weapon+cape);body=[o for o in active if o not in claimed]
groups={'BodyOutfit':body,'HeadHair':head,'Weapon':weapon,'Cape':cape}
assert set(sum(groups.values(),[]))==set(active)
assert sum(len(v) for v in groups.values())==len(active)
slots={o:[(slot.link,slot.material) for slot in o.material_slots] for o in geometry}
settings=(s.render.resolution_x,s.render.resolution_y,s.render.filepath,root.rotation_euler.z)
holdouts={}
for culled in [False,True]:
    mat=bpy.data.materials.new('Anatomy05ModuleHoldout_'+str(culled));mat.use_nodes=True;mat.use_backface_culling=culled
    ns=mat.node_tree.nodes;ns.clear();a=ns.new('ShaderNodeHoldout');b=ns.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(a.outputs[0],b.inputs['Surface']);holdouts[culled]=mat
def restore():
    for obj,ss in slots.items():
        obj.hide_render=hidden[obj]
        for slot,(link,mat) in zip(obj.material_slots,ss):slot.link=link;slot.material=mat
directions=[('S',0),('SW',-45),('W',-90),('NW',-135),('N',-180),('NE',-225),('E',-270),('SE',45)]
try:
    s.render.resolution_x=320;s.render.resolution_y=320
    for d,yaw in directions:
        root.rotation_euler.z=math.radians(yaw)
        for name,objects in groups.items():
            restore()
            for obj in active:
                if obj in objects:continue
                for slot in obj.material_slots:
                    culled=bool(slot.material and slot.material.use_backface_culling);slot.link='OBJECT';slot.material=holdouts[culled]
            s.render.filepath='C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/anatomy-base-05/renders/modular-'+name+'-'+d+'.png'
            bpy.ops.render.render(write_still=True)
finally:
    restore();s.render.resolution_x,s.render.resolution_y,s.render.filepath,root.rotation_euler.z=settings
    for mat in holdouts.values():bpy.data.materials.remove(mat)
r={'directions':[d for d,yaw in directions],'bakedParts':list(groups),'logicalParts':['BodyOutfit','HeadHair','Headgear','Weapon','Cape'],'headgear':{'state':'unequipped','rendered':False},'canvas':[320,320],'root':[160,264],'objects':{name:[o.name for o in objects] for name,objects in groups.items()},'scope':'Visible-only static equipped combination; not arbitrary swap-safe frames or motion coverage','ownerApproved':False,'runtimeAdmitted':False,'coverage':[]}
s['modularStaticReceipt']=json.dumps(r)
print('NEW_ANATOMY_MODULES_BAKED')
