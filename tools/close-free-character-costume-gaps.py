"""Extend the same navy sleeve surface beneath each separate forearm plate."""
import bpy

s=bpy.context.scene;assert s.name=='ASTRAEON_ASSET_FIT_04'
body=bpy.data.objects['SM_AssetFit04_Body']
def region(face):
    weights={}
    for i in face.vertices:
        for g in body.data.vertices[i].groups:
            n=body.vertex_groups[g.group].name;weights[n]=weights.get(n,0)+g.weight
    return max(weights,key=weights.get)
for suffix,side in [('r','R'),('l','L')]:
    polys=[f for f in body.data.polygons if region(f) in ['clavicle_'+suffix,'upperarm_'+suffix,'lowerarm_'+suffix]]
    ids=sorted({i for f in polys for i in f.vertices});mapping={i:j for j,i in enumerate(ids)}
    old=bpy.data.objects['SM_AssetFit04_Refitted_Sleeve_'+side]
    mats=list(old.data.materials)
    data=bpy.data.meshes.new('Fit04_ContinuousSleeve_'+side)
    data.from_pydata([body.data.vertices[i].co+body.data.vertices[i].normal*.021 for i in ids],[],[tuple(mapping[i] for i in f.vertices) for f in polys]);data.update()
    for m in mats:data.materials.append(m)
    uv=data.uv_layers.new(name='PainterSurface');xmin=min(v.co.x for v in data.vertices);xspan=max(v.co.x for v in data.vertices)-xmin;zmin=min(v.co.z for v in data.vertices);zspan=max(v.co.z for v in data.vertices)-zmin
    for f in data.polygons:
        f.use_smooth=True
        for li in f.loop_indices:
            v=data.vertices[data.loops[li].vertex_index].co;uv.data[li].uv=((v.x-xmin)/max(.001,xspan),(v.z-zmin)/max(.001,zspan))
    old.data=data;old['sourceFit']='Continuous upper/lower sleeve underneath separate forearm armor'
    for modifier in old.modifiers:
        if modifier.type=='SHRINKWRAP':modifier.offset=.007
    for name in ['Fitted_Bracer_'+side,'Forged_BracerUpperRim_'+side,'Forged_BracerWristRim_'+side,'Bracer_Crest_'+side,'Bracer_FrontRidge_'+side]:
        obj=bpy.data.objects['SM_AssetFit04_'+name]
        wrap=obj.modifiers.get('PlateAnatomyClearance') or obj.modifiers.new('PlateAnatomyClearance','SHRINKWRAP')
        wrap.target=body;wrap.wrap_method='NEAREST_SURFACEPOINT';wrap.wrap_mode='OUTSIDE'
        wrap.offset=.024 if 'Crest' in name or 'Ridge' in name else .017
        obj.modifiers.move(len(obj.modifiers)-1,0)
print('CONTINUOUS_SOURCE_NATIVE_SLEEVES_FITTED')
