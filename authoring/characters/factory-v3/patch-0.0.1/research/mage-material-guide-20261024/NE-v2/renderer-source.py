"""Render a supplementary color-coded pose guide through the canonical renderer.

Only material ownership changes. Original mesh vertices, native motions, camera
and prop geometry remain untouched. Every result must retain the canonical
capture's alpha silhouette and projected source coordinates. This is guidance
for 2D painting, never final character artwork or a replacement factory capture.
"""
import argparse,ast,hashlib,json,sys
from pathlib import Path


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def instrument(source):
    tree=ast.parse(source);main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main')
    found=[i for i,n in enumerate(main.body)if isinstance(n,ast.For)and isinstance(n.iter,ast.Set)and {getattr(e,'id',None)for e in n.iter.elts}=={'rig','source_rig'}]
    if len(found)!=1:raise ValueError('Canonical import/material boundary differs')
    main.body.insert(found[0],ast.parse('_assign_material_profile(rig)').body[0]);tree.body=[n for n in tree.body if not(isinstance(n,ast.If)and isinstance(n.test,ast.Compare)and isinstance(n.test.left,ast.Name)and n.test.left.id=='__name__')];return ast.fix_missing_locations(tree)


def material_role(name,z):
    name=name.lower()
    if name.startswith(('head','neck')):return 'head'if name.startswith('head')else'skin'
    if name.startswith(('hand','thumb','index','middle','ring','pinky')):return 'skin'
    if name.startswith('lowerarm'):return 'cuff'
    if name.startswith(('foot','ball'))or(name.startswith('calf')and z<.40):return 'boots'
    if name.startswith(('pelvis','thigh','calf')):return 'pants'
    return 'coat'


def dominant_role(roles):
    priority=['head','skin','coat','cuff','pants','boots']
    if not roles or any(role not in priority for role in roles):raise ValueError('Invalid material roles')
    return max(priority,key=lambda role:(roles.count(role),-priority.index(role)))


def assign_materials(rig,assignments):
    import bpy
    palette={'skin':(.73,.49,.33,1),'hair':(.38,.12,.065,1),'coat':(.075,.11,.19,1),'cuff':(.88,.80,.63,1),'pants':(.13,.15,.14,1),'boots':(.31,.17,.08,1)}
    materials=[]
    for name,color in palette.items():
        mat=bpy.data.materials.new('GuideOnly_'+name);mat.diffuse_color=color;materials.append(mat)
    keys=list(palette)
    for obj in bpy.data.objects:
        if obj.type!='MESH' or obj.hide_render:continue
        if not any(m.type=='ARMATURE'and m.object==rig for m in obj.modifiers):continue
        before=hashlib.sha256(b''.join(bytes(str(tuple(v.co)),'ascii')for v in obj.data.vertices)).hexdigest();groups={g.index:g.name.lower()for g in obj.vertex_groups};roles=[]
        for vertex in obj.data.vertices:
            strongest=max(vertex.groups,key=lambda g:g.weight,default=None);name=groups.get(strongest.group,'')if strongest else'';z=(obj.matrix_world@vertex.co).z
            roles.append(material_role(name,z))
        obj.data.materials.clear()
        for mat in materials:obj.data.materials.append(mat)
        counts={k:0 for k in keys}
        for poly in obj.data.polygons:
            role=dominant_role([roles[i]for i in poly.vertices])
            if role=='head':role='skin'if(obj.matrix_world.to_3x3()@poly.normal).y<-.25 else'hair'
            poly.material_index=keys.index(role);counts[role]+=1
        after=hashlib.sha256(b''.join(bytes(str(tuple(v.co)),'ascii')for v in obj.data.vertices)).hexdigest()
        if before!=after:raise ValueError('Material guide changed rest mesh vertices')
        assignments.append({'object':obj.name,'rest_vertex_sha256':before,'vertices':len(roles),'faces_by_material':counts})
    if not assignments:raise ValueError('No weighted visible human guide mesh')


def main():
    import numpy as np
    from PIL import Image
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from render_frozen_patch001_guides import run_capture
    args=sys.argv[sys.argv.index('--')+1:];p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-guide',type=Path,required=True);p.add_argument('--direction',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args(args)
    if a.output.exists():raise ValueError('Choose a fresh supplementary guide destination')
    source_manifest=a.source_guide/'manifest.json';original=json.loads(source_manifest.read_text());job=original['job'];canonical=Path(__file__).with_name('render_patch001_guides.py');frozen=Path(__file__).with_name('render_frozen_patch001_guides.py')
    if sha(canonical)!=job['renderer_sha256']:raise ValueError('Canonical source renderer differs')
    if a.direction not in original['views']:raise ValueError('Requested source view was not captured')
    supplemental={**job,'directions':[a.direction],'render_pose_freeze_revision':1,'render_pose_freeze_sha256':sha(frozen)};supplemental['id']=hashlib.sha256(json.dumps({'source':job['id'],'direction':a.direction,'material_implementation':sha(__file__)},sort_keys=True).encode()).hexdigest()[:20]
    implementation=sha(__file__);a.output.mkdir(parents=True);(a.output/'renderer-source.py').write_bytes(Path(__file__).read_bytes());job_path=a.output/'source-job.json';job_path.write_text(json.dumps(supplemental,indent=2)+'\n');assignments=[]
    scope={'__name__':'supplementary_material_guide','__file__':str(canonical),'_assign_material_profile':lambda rig:assign_materials(rig,assignments)};exec(compile(instrument(canonical.read_text()),str(canonical),'exec'),scope);scope['IMPLEMENTATION_DIGESTS'][Path(__file__).name]=sha(__file__)
    sys.argv=[sys.argv[0],'--','--job',str(job_path),'--output',str(a.output)];run_capture(scope['main']);captured=json.loads((a.output/'manifest.json').read_text());view=captured['views'][a.direction];source_view=original['views'][a.direction]
    if view['camera']!=source_view['camera']or len(view['frames'])!=len(source_view['frames']):raise ValueError('Supplementary camera or timeline differs')
    checks=[]
    for i,(left,right)in enumerate(zip(view['frames'],source_view['frames'])):
        if(left['action'],left['source_frame'])!=(right['action'],right['source_frame']):raise ValueError('Supplementary source controls differ')
        error=max(abs(x-y)for key in left['landmarks']for x,y in zip(left['landmarks'][key],right['landmarks'][key]))
        if error>1e-4:raise ValueError('Supplementary projected pose differs')
        image=a.output/a.direction/f'{i:03d}.png';source=a.source_guide/a.direction/f'{i:03d}.png';alpha=np.array(Image.open(image).getchannel('A'));expected=np.array(Image.open(source).getchannel('A'));changed=int(np.count_nonzero(alpha!=expected))
        if changed:raise ValueError('Supplementary silhouette differs: '+str(i)+' '+str(changed))
        checks.append({'index':i,'image_sha256':sha(image),'canonical_image_sha256':sha(source),'alpha_mismatch_pixels':changed,'maximum_projected_coordinate_error_px':error})
    if sha(__file__)!=implementation:raise ValueError('Material guide renderer changed during capture')
    receipt={'status':'SUPPLEMENTARY_MATERIAL_GUIDE_GEOMETRY_VERIFIED_NOT_FINAL_ART','canonical_guide_job':job['id'],'canonical_manifest_sha256':sha(source_manifest),'implementation_sha256':sha(__file__),'direction':a.direction,'mesh_material_assignments':assignments,'frames':checks,'source_geometry_modified':False,'canonical_files_modified':False,'runtime_admitted':False};(a.output/'material-guide-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'supplementary_frames':len(checks),'alpha_mismatch_pixels':0,'projected_pose_unchanged':True}),flush=True)


if __name__=='__main__':main()
