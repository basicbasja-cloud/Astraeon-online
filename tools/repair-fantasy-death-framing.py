"""Apply the reproducible Death settling fix and reuse proven unchanged clips.

Run once against the pre-fix native. Evaluated geometry, bone matrices and
camera are hashed before/after for every frame of every unchanged action.
Only those matching clips inherit caches; Death is rendered again.
"""
import bpy,hashlib,json,shutil,struct
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'authoring/characters/swordsman-production/fantasy-base-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pose_hashes():
    s=bpy.context.scene;rig=bpy.data.objects[s['rigObject']];root=bpy.data.objects[s['rootObject']]
    root.rotation_euler.z=0
    clips=json.loads(s['clips']);results={}
    objects=sorted([o for o in s.objects if o.type=='MESH' and (o.get('spriteModule') or o.get('swapModule')) and not o.hide_render],key=lambda o:o.name)
    for clip in clips:
        if clip['name']=='Death':continue
        h=hashlib.sha256();h.update(json.dumps(clip,sort_keys=True).encode())
        rig.animation_data.action=bpy.data.actions[clip['action']]
        for f in range(1,clip['frames']+1):
            s.frame_set(f);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
            for p in rig.pose.bones:
                for row in p.matrix:h.update(struct.pack('4f',*row))
            for o in objects:
                h.update(o.name.encode());evaluated=o.evaluated_get(dg);mesh=evaluated.to_mesh()
                for v in mesh.vertices:h.update(struct.pack('3f',*v.co))
                evaluated.to_mesh_clear()
            for row in s.camera.matrix_world:h.update(struct.pack('4f',*row))
            h.update(struct.pack('f',s.camera.data.ortho_scale))
        results[clip['name']]=h.hexdigest()
    return results
def patch_native(path):
    bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
    assert not s.get('deathFramingSettled'),'Already repaired'
    old=sha(path);before=pose_hashes()
    rig=bpy.data.objects[s['rigObject']];clip=next(c for c in json.loads(s['clips']) if c['name']=='Death')
    rig.animation_data.action=bpy.data.actions[clip['action']];p=rig.pose.bones['Hips']
    # Read all original keys first so editing interpolation cannot affect later samples.
    locations=[]
    for f in range(1,clip['frames']+1):s.frame_set(f);locations.append(p.location.copy())
    for f,location in enumerate(locations,1):
        s.frame_set(f);delta=Vector((0,-.05*(f-1)/(clip['frames']-1),0))
        p.location=location+p.bone.matrix_local.to_3x3().inverted()@delta
        p.keyframe_insert(data_path='location',frame=f,group=p.name)
    after=pose_hashes();assert before==after,'Unchanged clip geometry changed'
    s['deathFramingSettled']=True
    rig.animation_data.action=bpy.data.actions['F01_Idle'];s.frame_set(1)
    if 'swap' in path.name:s['baseNativeSHA256']=sha(ROOT/'.character-tools/checkpoints/fantasy-base-01-native.blend')
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    return old,sha(path),after
def migrate(kind,old,new,script,hashes,base_hash=None):
    oldkey=hashlib.sha256((old+sha(ROOT/'tools'/script)).encode()).hexdigest()[:16]
    newkey=hashlib.sha256((new+sha(ROOT/'tools'/script)).encode()).hexdigest()[:16]
    cache=ROOT/'.character-tools'/kind
    for name in hashes:
        source=cache/oldkey/name;target=cache/newkey/name
        assert source.is_dir();shutil.copytree(source,target,dirs_exist_ok=True)
        receipt=json.loads((target/'receipt.json').read_text())
        if kind=='sprite-bakes':receipt.update(nativeSHA256=new,cacheKey=newkey)
        else:receipt.update(bankSHA256=new,baseNativeSHA256=base_hash,cacheKey=newkey)
        receipt['reuseEvidence']={'previousNativeSHA256':old,'evaluatedPoseSHA256':hashes[name],'allClipFramesUnchanged':True}
        (target/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return newkey
native=ROOT/'.character-tools/checkpoints/fantasy-base-01-native.blend'
bank=ROOT/'.character-tools/checkpoints/fantasy-swap-bank.blend'
old,new,poses=patch_native(native)
key=migrate('sprite-bakes',old,new,'bake-character-sprites.py',poses)
oldbank,newbank,bankposes=patch_native(bank)
bankkey=migrate('swap-bakes',oldbank,newbank,'bake-fantasy-swap-bank.py',bankposes,new)
receipt=json.loads((OUT/'factory/swap-bank.json').read_text());receipt.update(baseNativeSHA256=new,bankSHA256=newbank)
(OUT/'factory/swap-bank.json').write_text(json.dumps(receipt,indent=2)+'\n')
(OUT/'factory/death-framing-repair.json').write_text(json.dumps({'oldNativeSHA256':old,'nativeSHA256':new,'oldBankSHA256':oldbank,'bankSHA256':newbank,'sourceSpaceDeathSettlement':[0,-.05,0],'unchangedClipGeometry':poses,'unchangedBankClipGeometry':bankposes,'cacheKey':key,'bankCacheKey':bankkey,'rerenderActions':['Death']},indent=2)+'\n')
print('DEATH_FRAMING_REPAIRED',flush=True)
