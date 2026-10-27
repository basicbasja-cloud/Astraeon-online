"""Validate declared pose reuse against actual planned source jobs."""
import json
from pathlib import Path


def audit(config, ledger):
    records=[]
    for class_id, klass in config['classes'].items():
        for name, action in klass['actions'].items():
            target=action.get('reuse_from')
            if not target:
                continue
            if target not in klass['actions']:
                records.append({'class':class_id,'action':name,'target':target,'passed':False,'reason':'Missing target'})
                continue
            original=klass['actions'][target]
            source=ledger['guide_jobs'][ledger['action_guide_bindings'][class_id+'/'+name]]
            reused=ledger['guide_jobs'][ledger['action_guide_bindings'][class_id+'/'+target]]
            fields=['source_file','source_actions','frames']
            equal=all(source.get(k)==reused.get(k) for k in fields)
            # Direction subsets can select already authored views, never mirrors.
            same_job=source['id']==reused['id']
            covered=set(action['authored_directions']) <= set(reused['directions'])
            records.append({'class':class_id,'action':name,'target':target,
                            'passed':equal and same_job and covered and action['frames']==source['frames'] and original['frames']==reused['frames'],
                            'source_job':source['id'],'target_job':reused['id'],
                            'declared_frame_counts':[action['frames'],original['frames']]})
    return {'passed':all(r['passed'] for r in records),'bindings':records,
            'note':'Matching source jobs permit pose reuse only; painted RGBA, body fit and semantic masks still require separate acceptance.'}


if __name__=='__main__':
    root=Path(__file__).resolve().parents[2]
    base=root/'authoring/characters/factory-v3/patch-0.0.1'
    result=audit(json.loads((base/'factory.json').read_text()),json.loads((base/'ledger.json').read_text()))
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['passed'] else 1)
