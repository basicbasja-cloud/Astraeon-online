"""Review an explicit action/view matrix. Missing or stale art never falls back silently."""
from pathlib import Path
import argparse, hashlib, json, math
from PIL import Image

DIRECTIONS = ['S','SW','W','NW','N','NE','E','SE']
CORE = {'idle':8,'walk':8,'sit':8,'pickup':4,'ready':4,'attack1':4,'hurt':4,'dead':4,'skill':4}

def resolve(action, world_direction, camera_direction):
    """Camera rotation is applied before the action's authored view aliases."""
    if type(world_direction) is not int or type(camera_direction) is not int:
        raise ValueError('directions must be integer indices')
    logical = DIRECTIONS[(world_direction + camera_direction) % 8]
    return action['aliases'][logical]

def evaluate(catalog, base):
    errors=[]; observed=[]
    def fail(message): errors.append(message)
    if catalog.get('directions') != DIRECTIONS: fail('direction order differs from policy')
    quantum=catalog.get('clock_quantum_ms');valid_quantum=quantum is None or (type(quantum) in [int,float] and math.isfinite(quantum) and quantum>0)
    if not valid_quantum:fail('invalid clock encoding quantum')
    actions=catalog.get('actions',{})
    for name,count in CORE.items():
        if name not in actions: fail(name+': missing action'); continue
        action=actions[name]; aliases=action.get('aliases',{}); clips=action.get('clips',{})
        expected={v: DIRECTIONS[(i//2)*2] if count==4 else v for i,v in enumerate(DIRECTIONS)}
        if aliases!=expected: fail(name+': unsafe or incomplete aliases')
        if set(clips)!=set(expected.values()): fail(name+': missing or extra authored views')
        for view,clip in clips.items():
            label=name+'/'+view; frames=clip.get('frames',[]); durations=clip.get('durations_ms',[])
            if clip.get('mirrored',False): fail(label+': asymmetric family cannot mirror')
            if not frames or len(frames)!=len(durations): fail(label+': missing frames or clock'); continue
            if any(type(t) not in [int,float] or not math.isfinite(t) or t<=0 or (valid_quantum and quantum is not None and abs(t/quantum-round(t/quantum))>1e-7) for t in durations): fail(label+': invalid or unencodable clock')
            if name=='pickup' and len(frames)!=16: fail(label+': pickup requires16 exposures')
            hashes=[]
            for n,frame in enumerate(frames):
                path=base/frame.get('path',''); expected_sha=frame.get('sha256'); prefix=label+'/'+str(n)
                if not path.is_file(): fail(prefix+': missing raster'); continue
                actual=hashlib.sha256(path.read_bytes()).hexdigest(); hashes.append(actual)
                if actual!=expected_sha: fail(prefix+': stale raster')
                with Image.open(path) as im:
                    if im.mode!='RGBA' or list(im.size)!=catalog.get('canvas'): fail(prefix+': wrong logical RGBA canvas')
                    if im.getchannel('A').getbbox() is None: fail(prefix+': empty character')
            review=clip.get('review',{})
            if review.get('frame_sha256')!=hashes: fail(label+': stale or absent visual review')
            if review.get('status')!='agent_visual_pass': fail(label+': visual review not passed')
            if not review.get('observations'): fail(label+': no concrete visual observations')
            checks=clip.get('checks',{})
            for required in ['registration','appearance','playback','pose_readability']:
                if checks.get(required) is not True: fail(label+': '+required+' not passed')
            if name=='pickup' and checks.get('whole_motion') is not True: fail(label+': whole motion not passed')
            observed.append({'action':name,'view':view,'exposures':len(frames),'distinct_rasters':len(set(hashes))})
    return {'pass':not errors,'errors':errors,'clips':observed,'required_authored_views':sum(CORE.values()),'scope':'Explicit original family core matrix, SHA-bound agent review and declared checks. Does not establish user approval, hidden anatomy, modular swaps or game integration.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('catalog',type=Path);p.add_argument('--output',type=Path);a=p.parse_args();r=evaluate(json.loads(a.catalog.read_text()),a.catalog.parent)
    result=json.dumps(r,indent=2)+'\n'
    if a.output:a.output.write_text(result)
    print(result);raise SystemExit(0 if r['pass'] else 1)
