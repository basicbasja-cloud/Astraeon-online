"""Derive a mannequin head-envelope study without changing its motion or skeleton.

This is a design-fit guide experiment, never approved character art.
"""
import argparse,copy,hashlib,json,struct
from pathlib import Path
import numpy as np


def fit_head(points,weights,scale):
    if not 1<=scale<=1.5:raise ValueError('Head study scale must be in [1,1.5]')
    points=np.asarray(points);weights=np.asarray(weights)
    core=weights>.95
    if not core.any():raise ValueError('No unambiguous head envelope')
    center=(points[core].min(0)+points[core].max(0))/2
    influence=np.clip((weights-.05)/.90,0,1)
    result=points+(points-center)*(scale-1)*influence[:,None]
    return result.astype(points.dtype),center


def derive(source,scale):
    raw=source.read_bytes()
    if struct.unpack_from('<III',raw,0)[:2]!=(0x46546c67,2):raise ValueError('Expected GLB2')
    size,kind=struct.unpack_from('<II',raw,12)
    if kind!=0x4e4f534a:raise ValueError('JSON chunk required')
    document=json.loads(raw[20:20+size]);original=copy.deepcopy(document)
    bin_size,bin_kind=struct.unpack_from('<II',raw,20+size)
    if bin_kind!=0x004e4942:raise ValueError('Embedded BIN required')
    binary=bytearray(raw[28+size:28+size+bin_size]);before=bytes(binary)
    def view(index):
        accessor=document['accessors'][index];v=document['bufferViews'][accessor['bufferView']]
        if v.get('buffer',0)!=0 or v.get('byteStride') or accessor.get('sparse'):raise ValueError('Only contiguous embedded accessors supported')
        dtype={5126:'<f4',5121:'u1',5123:'<u2',5125:'<u4'}[accessor['componentType']];dim={'VEC3':3,'VEC4':4,'SCALAR':1}[accessor['type']]
        offset=v.get('byteOffset',0)+accessor.get('byteOffset',0);array=np.frombuffer(binary,dtype=dtype,count=accessor['count']*dim,offset=offset).reshape(accessor['count'],dim)
        return array,(offset,offset+array.nbytes)
    node=next(n for n in document['nodes'] if 'mesh'in n and 'skin'in n);skin=document['skins'][node['skin']]
    head_nodes={i for i,n in enumerate(document['nodes']) if n.get('name') in ['head','head_leaf']};head_joints=[i for i,n in enumerate(skin['joints']) if n in head_nodes]
    if len(head_joints)!=2:raise ValueError('Original human head and head_leaf required')
    primitive=document['meshes'][node['mesh']]['primitives'][0];attributes=primitive['attributes'];positions,pos_span=view(attributes['POSITION']);normals,normal_span=view(attributes['NORMAL']);joints,_=view(attributes['JOINTS_0']);weights,_=view(attributes['WEIGHTS_0']);indices,_=view(primitive['indices'])
    old=positions.copy();head_weights=(weights*np.isin(joints,head_joints)).sum(1);new,center=fit_head(old,head_weights,scale);positions[:]=new
    changed=np.any(new!=old,axis=1);triangles=indices.reshape(-1,3);touched=np.unique(triangles[np.any(changed[triangles],axis=1)])
    accum=np.zeros_like(new);face=np.cross(new[triangles[:,1]]-new[triangles[:,0]],new[triangles[:,2]]-new[triangles[:,0]])
    for column in range(3):np.add.at(accum,triangles[:,column],face)
    lengths=np.linalg.norm(accum,axis=1);valid=touched[lengths[touched]>1e-10];normals[valid]=accum[valid]/lengths[valid,None]
    document['accessors'][attributes['POSITION']]['min']=new.min(0).tolist();document['accessors'][attributes['POSITION']]['max']=new.max(0).tolist()
    allowed=np.zeros(len(binary),bool)
    for start,end in [pos_span,normal_span]:allowed[start:end]=True
    differences=np.frombuffer(before,'u1')!=np.frombuffer(binary,'u1')
    if differences[~allowed].any():raise ValueError('Non-geometry bytes changed')
    if document['animations']!=original['animations'] or document['nodes']!=original['nodes'] or document['skins']!=original['skins']:raise ValueError('Source motion/skeleton changed')
    foot=old[:,1]<.25
    if not np.array_equal(new[foot],old[foot]):raise ValueError('Foot vertices changed')
    payload=json.dumps(document,separators=(',',':')).encode();payload+=b' '*((-len(payload))%4);binary+=b'\0'*((-len(binary))%4)
    result=struct.pack('<III',0x46546c67,2,12+8+len(payload)+8+len(binary))+struct.pack('<II',len(payload),0x4e4f534a)+payload+struct.pack('<II',len(binary),0x004e4942)+bytes(binary)
    return result,{'status':'HEAD_ENVELOPE_GUIDE_STUDY_NOT_CHARACTER_ACCEPTANCE','head_envelope_scale':scale,'head_center_mesh_local':center.tolist(),'changed_position_vertices':int(changed.sum()),'total_vertices':len(new),'foot_vertices_checked':int(foot.sum()),'foot_positions_unchanged':True,'animation_and_skeleton_json_unchanged':True,'binary_changes_restricted_to_positions_and_normals':True,'source_sha256':hashlib.sha256(raw).hexdigest(),'output_sha256':hashlib.sha256(result).hexdigest(),'runtime_admitted':False}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--scale',type=float,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('Preserve previous fit study')
    result,receipt=derive(a.source,a.scale);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(result);a.output.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))

if __name__=='__main__':main()
