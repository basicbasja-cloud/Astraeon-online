"""Compare source motion shape by standard glTF joint rotations, not clip labels.

Phase-normalized similarity is a candidate-reuse diagnostic; native timing and
rest/mesh compatibility remain separate. No application implementation is used.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import numpy as np
from scipy.spatial.transform import Rotation,Slerp


class Glb:
    def __init__(self,path):
        self.path=path;data=path.read_bytes();self.sha=hashlib.sha256(data).hexdigest();pos=12;self.bin=None
        while pos<len(data):
            size,kind=struct.unpack_from('<II',data,pos);chunk=data[pos+8:pos+8+size];pos+=8+size
            if kind==0x4e4f534a:self.doc=json.loads(chunk)
            elif kind==0x004e4942:self.bin=chunk
        if self.bin is None:raise ValueError('Expected embedded GLB buffer')
        self.cache={};self.redundant_duplicates=[];self.parents={c:i for i,n in enumerate(self.doc['nodes'])for c in n.get('children',[])}
        skin=self.doc['skins'][0]
        self.bones={self.doc['nodes'][i]['name'].casefold():i for i in skin['joints']}
        if len(self.bones)!=len(skin['joints']):raise ValueError('Duplicate bone names')
    def accessor(self,index):
        if index in self.cache:return self.cache[index]
        item=self.doc['accessors'][index]
        if item.get('sparse'):raise ValueError('Sparse animation accessor unsupported')
        view=self.doc['bufferViews'][item['bufferView']]
        dtype={5126:'<f4',5123:'<u2',5125:'<u4'}[item['componentType']]
        width={'SCALAR':1,'VEC3':3,'VEC4':4,'MAT4':16}[item['type']]
        offset=view.get('byteOffset',0)+item.get('byteOffset',0);unit=np.dtype(dtype).itemsize
        result=np.ndarray((item['count'],width),dtype=dtype,buffer=self.bin,offset=offset,
                          strides=(view.get('byteStride',width*unit),unit)).astype(float)
        self.cache[index]=result
        return result
    def sample(self,clip,phases,names):
        count=len(phases);nodes=self.doc['nodes'];translations=[];quats=[];scales=[]
        for node in nodes:
            if 'matrix'in node:
                matrix=np.array(node['matrix']).reshape(4,4,order='F');scale=np.linalg.norm(matrix[:3,:3],axis=0)
                translations.append(matrix[:3,3]);quats.append(Rotation.from_matrix(matrix[:3,:3]/scale).as_quat());scales.append(scale)
            else:
                translations.append(node.get('translation',[0,0,0]));quats.append(node.get('rotation',[0,0,0,1]));scales.append(node.get('scale',[1,1,1]))
        tr=np.broadcast_to(np.array(translations),(count,len(nodes),3)).copy()
        qr=np.broadcast_to(np.array(quats),(count,len(nodes),4)).copy()
        sc=np.broadcast_to(np.array(scales),(count,len(nodes),3)).copy()
        if clip is not None:
            inputs=[self.accessor(s['input'])[:,0]for s in clip['samplers']];start=min(x[0]for x in inputs);end=max(x[-1]for x in inputs)
            times=start+(end-start)*phases
            seen={}
            for channel in clip['channels']:
                node=channel['target']['node'];path=channel['target']['path']
                if path not in ['translation','rotation','scale']:continue
                key=(node,path)
                sampler=clip['samplers'][channel['sampler']]
                if key in seen:
                    old=seen[key]
                    if not (np.array_equal(self.accessor(old['input']),self.accessor(sampler['input'])) and np.array_equal(self.accessor(old['output']),self.accessor(sampler['output'])) and old.get('interpolation','LINEAR')==sampler.get('interpolation','LINEAR')):
                        raise ValueError('Conflicting duplicate animation channel')
                    self.redundant_duplicates.append({'clip':clip['name'],'node':nodes[node].get('name'),'path':path})
                    continue
                seen[key]=sampler;x=self.accessor(sampler['input'])[:,0];y=self.accessor(sampler['output'])
                if np.any(np.diff(x)<=0):raise ValueError('Non-increasing sampler times')
                t=np.clip(times,x[0],x[-1]);mode=sampler.get('interpolation','LINEAR')
                if len(x)==1:values=np.repeat(y[:1],count,axis=0)
                elif mode=='STEP':values=y[np.maximum(0,np.searchsorted(x,t,side='right')-1)]
                elif mode=='LINEAR'and path=='rotation':values=Slerp(x,Rotation.from_quat(y))(t).as_quat()
                elif mode=='LINEAR':values=np.column_stack([np.interp(t,x,y[:,i])for i in range(y.shape[1])])
                elif mode=='CUBICSPLINE':
                    v=y.reshape(len(x),3,-1);j=np.clip(np.searchsorted(x,t,side='right')-1,0,len(x)-2);dt=x[j+1]-x[j];u=((t-x[j])/dt)[:,None]
                    values=(2*u**3-3*u**2+1)*v[j,1]+(u**3-2*u**2+u)*dt[:,None]*v[j,2]+(-2*u**3+3*u**2)*v[j+1,1]+(u**3-u**2)*dt[:,None]*v[j+1,0]
                    if path=='rotation':values/=np.linalg.norm(values,axis=1)[:,None]
                else:raise ValueError('Unsupported glTF interpolation '+mode)
                {'translation':tr,'rotation':qr,'scale':sc}[path][:,node,:]=values
        local=np.broadcast_to(np.eye(4),(count,len(nodes),4,4)).copy()
        local[:,:,:3,:3]=Rotation.from_quat(qr.reshape(-1,4)).as_matrix().reshape(count,len(nodes),3,3)*sc[:,:,None,:]
        local[:,:,:3,3]=tr;world={}
        def evaluate(i):
            if i not in world:world[i]=evaluate(self.parents[i])@local[:,i]if i in self.parents else local[:,i]
            return world[i]
        matrices=np.stack([evaluate(self.bones[name])for name in names],axis=1)
        rotation=matrices[:,:,:3,:3];rotation=rotation/np.linalg.norm(rotation,axis=-2)[...,None,:]
        return rotation


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--actionforge',type=Path,required=True);p.add_argument('--mesh2motion',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('Choose a fresh motion comparison')
    left,right=Glb(a.actionforge),Glb(a.mesh2motion)
    wanted=['pelvis','spine_01','spine_03','neck_01','head']
    for suffix in ['l','r']:
        wanted.extend(f'{part}_{suffix}'for part in ['clavicle','upperarm','lowerarm','hand','thigh','calf','foot','ball'])
    if any(n not in left.bones or n not in right.bones for n in wanted):raise ValueError('Missing shared core joints')
    phases=np.linspace(0,.97,33);source=[];target=[]
    def signatures(asset):
        rest=asset.sample(None,np.array([0.]),wanted)[0];records=[]
        for clip in asset.doc['animations']:
            rotations=asset.sample(clip,phases,wanted);delta=rotations@np.swapaxes(rest,-1,-2)
            q=Rotation.from_matrix(delta.reshape(-1,3,3)).as_quat().reshape(len(phases),len(wanted),4)
            records.append((clip['name'],q))
        return records
    source=signatures(left);target=signatures(right);stack=np.stack([q for _,q in target]);rows=[]
    for name,q in source:
        dots=np.clip(abs(np.sum(stack*q[None,...],axis=-1)),0,1);angles=np.degrees(2*np.arccos(dots));means=angles.mean(axis=(1,2));indices=np.argsort(means)[:3]
        rows.append({'actionforge_clip':name,'nearest_mesh2motion_by_phase_shape':[{'clip':target[i][0],'mean_core_joint_angle_difference_degrees':float(means[i]),'maximum_core_joint_angle_difference_degrees':float(angles[i].max())}for i in indices],
                     'source_equivalence_proven':False,'timing_equivalence_proven':False})
    result={'status':'PHASE_SHAPE_COMPARISON_NOT_SOURCE_EQUIVALENCE_OR_APPROVAL',
            'source_sha256':{'actionforge':left.sha,'mesh2motion':right.sha},'joints':wanted,
            'phases':phases.tolist(),'actionforge_clips':len(source),'mesh2motion_clips':len(target),
            'redundant_identical_duplicate_channels':{'actionforge':left.redundant_duplicates,'mesh2motion':right.redundant_duplicates},
            'comparisons':rows,'method':'World-rest orientation deltas on common core joints; standard glTF interpolation, native clips phase-normalized. Final reset endpoint excluded from shape signature.',
            'limitations':['Similarity is not proof of identical clips, correct contact, natural motion or matching timing.','No new source replaces preferred Mesh2Motion or the protected Swordsman art.']}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'actionforge':len(source),'mesh2motion':len(target),'best_score_examples':[(r['actionforge_clip'],r['nearest_mesh2motion_by_phase_shape'][0])for r in rows if r['actionforge_clip']in['walk_loop','sword_regular_b','spell_simple_shoot','idle_no_loop']]}))


if __name__=='__main__':main()
