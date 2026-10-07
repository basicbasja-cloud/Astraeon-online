"""Native planted pockets and fuller, varied evergreen boughs.

Reuses the original full-resolution textures and alpha-aware lighting pipeline.
Tree trunks, collisions, curbs, actual floors, entrances and routes stay fixed.
"""
import bpy, json, math, runpy, random, hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]; O=R/'docs/review/wayfarer-capital-v76/property-frontages'
s=bpy.context.scene; assert s.get('capital_property_frontages') and not s.get('capital_natural_landscape')
exporter=runpy.run_path(str(R/'tools/export-world-v3.py')); before=exporter['export'](s)
plan=json.loads((O/'natural-lawns-plan.json').read_text())
assert hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()==plan['beforeSourceSHA256']
def invariant(data):
    return {'terrain':data['terrain'],'navigation':data['navigation'],'spawn':data['spawn'],'route':data['route'],
            'owners':[{k:o.get(k) for k in ('id','family','portals','services','lights','walkers','presentation')} for o in data['objects']],
            'solids':[(o['id'],a) for o in data['objects'] for a in o['parts'] if a['role']=='solid'],
            'doors':[(o['id'],a) for o in data['objects'] for a in o['parts'] if a['id'].endswith('-door-leaf')]}
guard=invariant(before)
def tris(data):return sum(len(f)-2 for o in data['objects'] for a in o['parts'] if a.get('visible',True) for f in a['faces'])
old_triangles=tris(before)
c=bpy.data.collections['capital-beta-frontage-groundcover']
for obj in list(c.objects):bpy.data.objects.remove(obj,do_unlink=True)
for a in plan['pieces']:
    d=bpy.data.meshes.new(a['id']);d.from_pydata(a['vertices'],[],a['faces']);d.materials.append(bpy.data.materials['grass']);d.uv_layers.new(name='WorldUV')
    scale=json.loads(d.materials[0]['texture_json'])['worldSize']
    for face in d.polygons:
        for li in face.loop_indices:
            v=d.vertices[d.loops[li].vertex_index].co;d.uv_layers.active.data[li].uv=(v.x/scale,v.y/scale)
    obj=bpy.data.objects.new(a['id'],d);c.objects.link(obj);obj['role']='decorative';obj['shadow']=False;obj['owned_block']=a['block']
trees=[]
sun_angle=math.atan2(-before['lighting']['sun']['cast'][1],-before['lighting']['sun']['cast'][0])
for c in sorted(bpy.data.collections,key=lambda c:c.name):
    if c.get('family')!='vegetation' or c.name=='capital-beta-frontage-groundcover':continue
    leaves=[o for o in c.objects if o.type=='MESH' and o.get('render_visible',True) and o.data.materials and o.data.materials[0].name in ('conifer70','conifer70Light','conifer70Shade')]
    assert len(leaves)==3,c.name
    stem=next(o for o in c.objects if o.type=='MESH' and o.get('role')=='solid')
    roots=[stem.matrix_world@v.co for v in stem.data.vertices];bounds=[o.matrix_world@v.co for o in leaves for v in o.data.vertices]
    cx=(min(v.x for v in roots)+max(v.x for v in roots))/2;cy=(min(v.y for v in roots)+max(v.y for v in roots))/2;base=min(v.z for v in roots)
    height=max(v.z for v in bounds)-base;radius=min(max(v.x for v in bounds)-min(v.x for v in bounds),max(v.y for v in bounds)-min(v.y for v in bounds))*.48
    index=int(c.name.rsplit('-',1)[1]) if c.name.startswith('capital-tree-') else 76+int(c.name.endswith('west'));rng=random.Random(76000+index)
    # Formal avenue pairs share a profile; lot trees vary their crown fullness.
    profile=(index//2)%3;exponent=(.78,.92,.66)[profile];phase=rng.uniform(0,math.tau)
    groups={m:([],[],[]) for m in ('conifer70','conifer70Light','conifer70Shade')}
    for tier in range(9):
        t=tier/8;rad=radius*(.06+.94*(1-t)**exponent);z=base+height*(.31+.69*t)
        for fan in range(10):
            angle=fan*math.tau/10+tier*.43+phase+rng.uniform(-.06,.06)
            rr=rad*rng.uniform(.90,1.0);drop=height*(.085-.045*t)
            # Illuminate by direction, not a repeated painted stripe per fan.
            sun_alignment=math.cos(angle-sun_angle)
            mat='conifer70Light' if sun_alignment>.42 and tier>1 else 'conifer70Shade' if sun_alignment<-.5 else 'conifer70'
            verts,faces,uvs=groups[mat];off=len(verts)
            for j in range(3):
                v=j/2;distance=rr*(.08+.92*v)
                for i in range(3):
                    u=i/2;a=angle+(u-.5)*(1.24-.16*v)+.08*math.sin(v*math.pi)
                    zz=z-drop*v**1.25+.08*rr*math.sin(math.pi*u)*math.sin(math.pi*v)
                    verts.append((cx+distance*math.cos(a),cy+distance*math.sin(a),min(base+height,zz)));uvs.append((u,1-v))
            for j in range(2):
                for i in range(2):k=off+j*3+i;faces.append([k,k+3,k+4,k+1])
    for obj in leaves:
        verts,faces,uvs=groups[obj.data.materials[0].name]
        inverse=obj.matrix_world.inverted();d=obj.data
        d.clear_geometry();d.from_pydata([inverse@Vector(v) for v in verts],[],faces);d.update()
        layer=d.uv_layers.active or d.uv_layers.new(name='BoughUV')
        for f in d.polygons:
            for li in f.loop_indices:layer.data[li].uv=uvs[d.loops[li].vertex_index]
        obj['conifer_v70']=True;obj['landscape_v76']=True
        old=d.color_attributes.get('BakedTownLight')
        if old:d.color_attributes.remove(old)
    trees.append({'id':c.name,'profile':profile,'height':height,'radius':radius,'boughs':90,'tiers':9,'parts':[o.name for o in leaves]})
assert len(trees)==78
tone=json.loads((O/'tone.json').read_text())
for name,color in {'conifer70':(.255,.385,.12),'conifer70Light':(.40,.54,.19),'conifer70Shade':(.145,.285,.075)}.items():
    mat=bpy.data.materials[name];assert name not in tone['materials']
    tone['materials'][name]={'before':list(mat.diffuse_color[:3]),'after':list(color)};mat.diffuse_color=(*color,1)
bpy.context.view_layer.update();after=exporter['export'](s);assert invariant(after)==guard
added=tris(after)-old_triangles;assert 0<added<27000,added
report={'beforeSourceSHA256':plan['beforeSourceSHA256'],'lawns':{k:v for k,v in plan.items() if k!='pieces'},'trees':trees,
        'addedTriangles':added,'triangleBudget':27000,'rootsAndCollidersPreserved':True,'floorsAndRoutesPreserved':True,
        'additionalTextures':0,'originalAlphaAndResolutionRetained':True,'visualAcceptance':'Pending source-matched gameplay review'}
(O/'landscape-authoring.json').write_text(json.dumps(report,indent=2)+'\n');(O/'tone.json').write_text(json.dumps(tone,indent=2)+'\n')
s['capital_natural_landscape']=1
bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
print('Native landscape:',len(plan['pieces']),'lawns;',len(trees),'fuller crowns;',added,'additional triangles',flush=True)
