"""Audit source weights, sampled deformation, loop endpoints and fixed framing."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
import numpy as np
from mathutils import Matrix,Vector
base=Path(__file__).resolve().parents[1];s=bpy.context.scene
rig=bpy.data.objects[s['rigObject']];root=bpy.data.objects[s['rootObject']];root.rotation_euler.z=0
objects=[o for o in s.objects if o.get('spriteModule') and not o.hide_render]
issues=[];meshes=[]
for o in objects:
    bm=bmesh.new();bm.from_mesh(o.data)
    degenerate=sum(f.calc_area()<1e-10 for f in bm.faces)
    unweighted=0;bad_sums=0;invalid=0;maximum=0
    for v in o.data.vertices:
        groups=[g for g in v.groups if g.weight>1e-7];maximum=max(maximum,len(groups))
        if not groups:unweighted+=1
        if abs(sum(g.weight for g in groups)-1)>1e-5:bad_sums+=1
        invalid+=sum(o.vertex_groups[g.group].name not in rig.data.bones for g in groups)
    record={'name':o.name,'module':o['spriteModule'],'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),
            'boundaryEdges':sum(e.is_boundary for e in bm.edges),'nonmanifoldEdges':sum(not e.is_manifold for e in bm.edges),
            'unweightedVertices':unweighted,'unnormalizedVertices':bad_sums,'invalidBoneWeights':invalid,'maximumInfluences':maximum,
            'degenerateFaces':degenerate}
    bm.free();meshes.append(record)
    if unweighted or bad_sums or invalid or maximum>4:issues.append('Invalid skin weights: '+o.name)
    if o.get('spriteModule')=='Weapon' and degenerate:issues.append('Degenerate weapon surface: '+o.name)
clip_reports=[];camera=np.array(s.camera.matrix_world.inverted(),dtype=np.float64);span=s.camera.data.ortho_scale
for clip in json.loads(s['clips']):
    rig.animation_data.action=bpy.data.actions[clip['action']];samples=[]
    for frame in sorted(set([1,clip['frames']//2+1,clip['frames']])):
        s.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();points=[]
        lows={}
        for o in objects:
            evaluated=o.evaluated_get(dg);me=evaluated.to_mesh();local=np.empty(len(me.vertices)*3,dtype=np.float64);me.vertices.foreach_get('co',local)
            xyz=local.reshape(-1,3);xyz=np.c_[xyz,np.ones(len(xyz))]@np.array(o.matrix_world,dtype=np.float64).T
            points.append(xyz);lows[o['spriteModule']]=min(lows.get(o['spriteModule'],1e6),float(xyz[:,2].min()));evaluated.to_mesh_clear()
        xyz=np.concatenate(points);bounds=[]
        contact=json.loads(s['swordContact']);hand=rig.pose.bones[contact['bone']]
        grip=rig.matrix_world@(hand.matrix@hand.bone.matrix_local.inverted()@Vector(contact['centerModel']))
        grip_h=np.array([*grip,1.],dtype=np.float64)
        for direction,yaw in json.loads(s['directions']):
            turn=np.array(Matrix.Rotation(math.radians(yaw),4,'Z'),dtype=np.float64)
            cam=xyz@turn.T@camera.T;x=160+cam[:,0]*320/span;y=160-cam[:,1]*320/span
            projected_grip=camera@turn@grip_h
            bound={'direction':direction,'min':[float(x.min()),float(y.min())],'max':[float(x.max()),float(y.max())],
                   'gripPixel':[float(160+projected_grip[0]*320/span),float(160-projected_grip[1]*320/span)]};bounds.append(bound)
            if x.min()<1 or x.max()>319 or y.min()<1 or y.max()>319:issues.append(f'Clipped 3D projection {clip["name"]} {frame} {direction}')
        foot=[]
        for side in ['R','L']:
            weight=rig.pose.bones['Shin.'+side].constraints['GroundContactIK'].influence
            error=(rig.pose.bones['Shin.'+side].tail-rig.pose.bones['CTRL_Foot.'+side].head).length
            foot.append({'side':side,'ikInfluence':weight,'targetError':error})
            if weight>.999 and error>.002:issues.append(f'Unreachable planted foot {clip["name"]} {frame} {side}')
        scale_error=max(abs(v-1) for p in rig.pose.bones for v in p.scale)
        if scale_error>1e-6:issues.append('Pose scales a bone')
        samples.append({'frame':frame,'minimumZByModule':lows,'footIK':foot,'maximumBoneScaleError':scale_error,'projections':bounds})
    loop_error=0
    if clip['loop']:
        s.frame_set(1);first={p.name:p.matrix.copy() for p in rig.pose.bones};s.frame_set(clip['frames']+1)
        loop_error=max(abs(rig.pose.bones[n].matrix[i][j]-m[i][j]) for n,m in first.items() for i in range(4) for j in range(4))
        if loop_error>1e-4:issues.append('Loop endpoints differ: '+clip['name'])
    clip_reports.append({'name':clip['name'],'frames':clip['frames'],'loop':clip['loop'],'loopEndpointMatrixError':loop_error,'samples':samples})
report={'kind':'native_source_audit','nativeSHA256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
        'technicalVerdict':'PASS' if not issues else 'FAIL','visualVerdict':'REQUIRES_ART_REVIEW','ownerApproved':False,'runtimeAdmitted':False,
        'issues':sorted(set(issues)),'bones':len(rig.data.bones),'meshes':meshes,'clips':clip_reports,
        'sourceBoundaryNote':'Source nonmanifold joins are retained and reported. Closed manufactured accessories can be single-sided ornamental surfaces.'}
path=base/'authoring/characters/swordsman-production/fantasy-base-01/factory/source-audit.json';path.parent.mkdir(parents=True,exist_ok=True)
path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('FANTASY_AUDIT '+json.dumps({'technicalVerdict':report['technicalVerdict'],'issues':report['issues'],'actions':len(clip_reports)}),flush=True)
