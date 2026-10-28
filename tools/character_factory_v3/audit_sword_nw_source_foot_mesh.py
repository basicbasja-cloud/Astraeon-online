"""Inspect native skinned foot mesh against preserved art in the locked camera.

Run in Blender. Mesh minima are geometry observations; painted sole landmarks
and animation acceptance still require explicit visual review.
"""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1'
GUIDE=BASE/'guides/c297971fcef09188ff60/manifest.json'
NATIVE=BASE/'research/native-rig-library-20261026/source/c297971fcef09188ff60.json'
BODY=BASE/'review/preserved-swordsman-canonical-cutouts-20261023/BasicAttack/NW/BodyCostume'
CANDIDATE=BASE/'review/swordsman-nw-registration-proposal-20261028/frame15/BodyCostume.png'
BINDING=BASE/'cutouts/f163f5e0b852f2767596/bindings.json'
STORE=BASE/'cutout-store/index.json'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(output):
    if output.exists():raise ValueError('Choose a fresh output')
    guide=json.loads(GUIDE.read_text());native=json.loads(NATIVE.read_text());job=guide['job'];frames=guide['views']['NW']['frames'];camera_data=guide['views']['NW']['camera']
    if native['source_manifest_sha256']!=sha(GUIDE):raise ValueError('Native library differs from capture')
    source=(ROOT/job['source_file']).resolve()
    if not source.is_relative_to(ROOT) or sha(source)!=job['source_sha256']:raise ValueError('Source rig changed')
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(source));scene=bpy.context.scene
    rig=max((o for o in bpy.data.objects if o.type=='ARMATURE'),key=lambda o:len(o.data.bones));mesh=next(o for o in bpy.data.objects if o.type=='MESH' and o.name=='Mannequin')
    for track in rig.animation_data.nla_tracks:track.mute=True
    action=bpy.data.actions.get('Sword_Attack_'+rig.name)
    if action is None:raise ValueError('Exact retained Sword_Attack action missing')
    rig.animation_data.action=action
    if hasattr(rig.animation_data,'action_slot') and action.slots:rig.animation_data.action_slot=action.slots[0]
    cd=bpy.data.cameras.new('FootAuditCamera');camera=bpy.data.objects.new(cd.name,cd);scene.collection.objects.link(camera);scene.camera=camera;cd.type='ORTHO';cd.ortho_scale=camera_data['ortho_scale'];camera.location=camera_data['location'];camera.rotation_euler=camera_data['rotation']
    scene.render.resolution_x=768;scene.render.resolution_y=768;scene.render.resolution_percentage=100
    groups={side:{mesh.vertex_groups[n].index for n in ('foot_'+side,'ball_'+side,'ball_leaf_'+side)} for side in ('l','r')}; initial=rig.matrix_world.copy();results={};max_error=0.;max_projection_error=0.
    def screen(v):
        q=world_to_camera_view(scene,camera,v);return [float(q.x*768),float((1-q.y)*768)]
    for i in (0,14,15):
        row=frames[i]; nf=native['frames'][i]
        if row['action']!='Sword_Attack' or nf['action']!=row['action'] or nf['source_frame']!=row['source_frame'] or row['source_frame']!=int(row['source_frame']):raise ValueError('Source frame mismatch')
        rig.matrix_world=initial.copy();scene.frame_set(int(row['source_frame']));rig.matrix_world.translation-=Vector(row['actor_root_delta']);bpy.context.view_layer.update()
        error=max((rig.matrix_world@rig.pose.bones[n].head-Vector(row['world_landmarks'][n])).length for n in ('head','pelvis','foot_l','foot_r'));max_error=max(max_error,error)
        if error>1e-5:raise ValueError('Replayed source differs from recorded geometry')
        for name in ('head','foot_l','foot_r'):
            actual=screen(rig.matrix_world@rig.pose.bones[name].head);expected=row['landmarks'][name]
            projection_error=math.hypot(actual[0]-expected[0]*.5,actual[1]-expected[1]*.5);max_projection_error=max(max_projection_error,projection_error)
            if projection_error>0.001:raise ValueError('Replayed camera projection differs from guide')
        deps=bpy.context.evaluated_depsgraph_get();evaluated=mesh.evaluated_get(deps);ev=evaluated.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
        try:
            sides={}
            for side in ('l','r'):
                vertices=[]
                for v in ev.vertices:
                    weight=sum(entry.weight for entry in v.groups if entry.group in groups[side])
                    if weight>=.5:
                        world=evaluated.matrix_world@v.co; vertices.append({'index':v.index,'world':[float(x) for x in world],'screen':screen(world),'weight':float(weight)})
                if not vertices:raise ValueError('No weighted foot surface')
                minimum=min(v['world'][2] for v in vertices);low=[v for v in vertices if v['world'][2]<=minimum+.01]
                sides[side]={'weighted_vertices':len(vertices),'lowest_world_z_m':minimum,'low_band_m':.01,'low_vertices':low}
            results[i]=sides
        finally:evaluated.to_mesh_clear()
    shifts={}
    for side in ('l','r'):
        prev={v['index']:v for v in results[14][side]['low_vertices']};after={v['index']:v for v in results[15][side]['low_vertices']};ids=sorted(prev.keys()&after.keys())
        differences=[[round((after[k]['screen'][j]-prev[k]['screen'][j])*240/768,6) for j in (0,1)] for k in ids]
        shifts[side]={'common_low_surface_vertices':len(ids),'screen_displacements_runtime_px':differences,'note':'Same source-mesh vertex indices in both lowest 1 cm bands; these are not painted-boot landmarks or proof of planted contact.'}
    bindings=json.loads(BINDING.read_text());store=json.loads(STORE.read_text());records={r['index']:r for r in bindings['frames'] if r['direction']=='NW'}
    items=[('00 original',0,BODY/'000.png'),('14 original',14,BODY/'014.png'),('15 original',15,BODY/'015.png'),('15 candidate',15,CANDIDATE)];crop=(300,480,445,590);page=Image.new('RGB',(1740,405),'#ddd');draw=ImageDraw.Draw(page);pins={}
    for col,(title,i,path) in enumerate(items):
        art=Image.open(path).convert('RGBA');record=records[i];a=store['assets'][record['assets']['BodyCostume']];oid=a['object'];srcpath=(ROOT/store['objects'][oid]['file']).resolve()
        if not srcpath.is_relative_to(ROOT):raise ValueError('Stored path outside repository')
        src=Image.open(srcpath).convert('RGBA')
        if hashlib.sha256(src.tobytes()).hexdigest()!=oid:raise ValueError('Imported pixels changed')
        if col<3 and src.tobytes()!=art.tobytes():raise ValueError('Preserved source differs from import')
        if col==3:
            shifted=Image.new('RGBA',src.size);shifted.alpha_composite(src,(-8,0))
            if shifted.tobytes()!=art.tobytes():raise ValueError('Candidate differs from recorded transform')
        tile=Image.new('RGBA',art.size,'#ddd');tile.alpha_composite(art);marker=ImageDraw.Draw(tile)
        for side,color in [('l','#00c3e8'),('r','#f44336')]:
            for v in results[i][side]['low_vertices']:
                x,y=v['screen'];marker.ellipse((x-1,y-1,x+1,y+1),fill=color)
        page.paste(tile.crop(crop).resize((435,330),Image.Resampling.NEAREST).convert('RGB'),(col*435,60));draw.text((col*435+5,8),title,fill='black');draw.text((col*435+5,26),'cyan=left mesh   red=right mesh',fill='black')
        pins[str(path.relative_to(ROOT))]=sha(path);pins[str(srcpath.relative_to(ROOT))]=sha(srcpath)
    output.mkdir(parents=True);page.save(output/'lowest-foot-surface.png')
    for p in (GUIDE,NATIVE,BINDING,STORE,source,Path(__file__).resolve()):pins[str(p.relative_to(ROOT))]=sha(p)
    receipt={'status':'NATIVE_WEIGHTED_FOOT_SURFACE_DIAGNOSTIC_NOT_ART_APPROVAL','blender':bpy.app.version_string,'source_mesh':mesh.name,'source_action':action.name,'skin_threshold':.5,'band_above_each_source_mesh_minimum_m':.01,'geometry_max_world_error_m':max_error,'projection_max_error_author_px':max_projection_error,'frames':results,'source_surface_frame14_to15':shifts,'source_sha256':pins,'limitations':['Weighted vertices and lowest surface band are source mesh evidence, not verified painted boot landmarks.','Being near source z=0 or in two low bands does not prove a foot is intentionally planted.','No painted contact or residual <=1 runtime pixel is certified.','Registration candidate is not imported or approved.'],'painted_contact_verified':False,'art_approved':False,'runtime_admitted':False}
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);r=build(args.output);print('FOOT_SURFACE_AUDIT',json.dumps({'status':r['status'],'geometry_max_world_error_m':r['geometry_max_world_error_m'],'common':{s:r['source_surface_frame14_to15'][s]['common_low_surface_vertices'] for s in ('l','r')}}),flush=True)
