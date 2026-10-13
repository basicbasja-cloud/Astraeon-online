"""Unknown-first real-art gait cases and an actual-source numerical failure control."""
import json,math,copy,importlib.util
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'research/sprite-animation/combat-gait-study-v23'
s=importlib.util.spec_from_file_location('mechanics',ROOT/'skills/modular-eight-direction-sprites/scripts/motion-mechanics.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':m.sha(p)}
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    feedback=OUT/'evidence/user-feedback.json';src=ROOT/'research/sprite-animation/eight-walk-factory-v20/source-phase12/source-index.json';d=json.loads(src.read_text())
    for i,view in enumerate(['S','SE','E','NE','N','NW','W','SW']):
        frames=[];theta=i*math.pi/4;forward=np.array([math.sin(theta),-math.cos(theta),0])
        records=[r for r in d['records'] if r['facing']==view]
        for k,r in enumerate(records):
            progress=float(np.dot(np.subtract(r['bones']['foot_r']['world'],r['bones']['foot_l']['world']),forward));expected='passing' if abs(progress)<.012 else 'r' if progress>0 else 'l'
            image=ROOT/'research/sprite-animation/registered-walk-attack-v21/walk'/view/'frames'/f'{k:02}.png'
            frames.append({'time_ms':k*75,'duration_ms':75,'image':bind(image),'source_image':bind(ROOT/r['paths']['dressed-owner']),
                'source_key16':r['source_key16'],'reference_lead':expected,'source_ankle_forward_difference_world':progress,
                'observed_lead':None,'feet':None,'root_xy':None,'contact_state_reviewed':False,
                'scope':'Reference lead from actual source ankles/world facing only, not an observed painted lead or certified support.'})
        case={'schema':'motion-mechanics-v1','action':'walk','loop':True,'bindings':[bind(src)],
            'feedback':{**bind(feedback),'selector':['walk',view]},'frames':frames}
        dump(OUT/f'evidence/gait-{view}-case.json',case);dump(OUT/f'evidence/gait-{view}-report.json',m.audit(case,ROOT))
    p=OUT/'evidence/flare-coupling-case.json';case=json.loads(p.read_text());dump(OUT/'evidence/flare-coupling-report.json',m.audit(case,ROOT))
    bad=copy.deepcopy(case);f=bad['frames'][16];hand=np.array(f['hand_matrix_world']);weapon=np.array(f['weapon_matrix_world']);local=np.linalg.solve(hand,weapon);a=math.radians(190);spin=np.eye(4);spin[:2,:2]=[[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]];f['weapon_matrix_world']=(hand@spin@local).tolist()
    bad['scope']='Synthetic counterfactual modification of one actual-source sample: weapon rotates190deg inside the unchanged hand frame. Not a captured/source animation.'
    dump(OUT/'evidence/weapon-spin-negative-case.json',bad);report=m.audit(bad,ROOT);assert 'Weapon moves inside the hand-local grip frame' in report['warnings'];dump(OUT/'evidence/weapon-spin-negative-report.json',report)
    raw=OUT/'raw/attack-body-only-rejected.png';im=None
    from PIL import Image
    im=Image.open(raw).convert('RGBA');size=im.width//2;bank=OUT/'attack-body-only-rejected';bank.mkdir(exist_ok=True);frames=[]
    for i in range(4):
        cell=im.crop((i%2*size,i//2*size,i%2*size+size,i//2*size+size));path=bank/f'{i:02}.png';cell.save(path)
        frames.append({'time_ms':i*100,'image':bind(path),'visible_points':None,'balance_review':'USER_REJECTED_FALLING'})
    case={'schema':'motion-mechanics-v1','action':'attack','attack_representation':'hand_sweep_tail','user_status':'USER_REJECTED_FALLING',
        'bindings':[bind(raw),bind(OUT/'evidence/pilot-rejections.json')],'frames':frames}
    dump(OUT/'evidence/body-only-rejected-case.json',case);dump(OUT/'evidence/body-only-rejected-report.json',m.audit(case,ROOT))
    print('MECHANICS_REAL_CASES',8,'walk views, actual source positive/negative and rejected body-only bank')
if __name__=='__main__':main()
