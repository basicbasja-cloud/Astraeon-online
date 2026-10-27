"""Inventory all logical character actions without treating coverage as approval."""
import argparse,csv,json
from pathlib import Path


def build_inventory(config,ledger,base):
    rows=[]
    for character in config['characters']:
        class_id=character['class'];character_id=character['id']
        for name,action in config['classes'][class_id]['actions'].items():
            guide_id=ledger['action_guide_bindings'][class_id+'/'+name]
            matches=[j for j in ledger['paint_jobs'].values() if j['character']==character_id and name in j['actions']]
            if len(matches)!=1:raise ValueError('Action must resolve exactly one paint job: '+character_id+'/'+name)
            paint=matches[0]
            if paint['guide_job']!=guide_id or paint['frame_count']!=action['frames']:
                raise ValueError('Source/paint/action sequence mismatch: '+character_id+'/'+name)
            expected=action['frames']*len(action['authored_directions'])
            present=sum((base/'guides'/guide_id/view/f'{i:03d}.png').is_file() for view in action['authored_directions'] for i in range(action['frames']))
            receipt_path=base/'cutouts'/paint['id']/'import-receipt.json'
            receipt=json.loads(receipt_path.read_text()) if receipt_path.is_file() else {}
            imported=receipt.get('paint_job')==paint['id'] and receipt.get('all_frames_present') is True and receipt.get('recomposition_mismatches')==0
            rows.append({'character':character_id,'class':class_id,'action':name,'frames':action['frames'],
                         'directions':action['authored_directions'],'loop':action['loop'],
                         'guide_job':guide_id,'paint_job':paint['id'],'reuse_from':action.get('reuse_from'),
                         'expected_frame_views':expected,'source_pngs_present':present,
                         'import_receipt_coverage':imported,'art_approved':False,'gameplay_approved':False,
                         'next_gate':'MASTER_ANATOMY_AND_TEMPORAL_REVIEW' if imported else 'SOURCE_REVIEW_AND_MASTER_AUTHORING'})
    return {'status':'FACTUAL_COVERAGE_INVENTORY_NOT_ART_ACCEPTANCE','logical_actions':len(rows),
            'unique_paint_jobs':len({r['paint_job'] for r in rows}),
            'imported_unique_paint_jobs':len({r['paint_job'] for r in rows if r['import_receipt_coverage']}),
            'completed_characters':0,'rows':rows,
            'note':'PNG presence is not hash/pose approval. Import receipts are technical coverage only. Art/gameplay gates remain unapproved until explicit review evidence is integrated.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    root=Path(__file__).resolve().parents[2];base=root/'authoring/characters/factory-v3/patch-0.0.1'
    report=build_inventory(json.loads((base/'factory.json').read_text()),json.loads((base/'ledger.json').read_text()),base)
    if args.output.exists():raise ValueError('Choose a new inventory destination')
    args.output.mkdir(parents=True);(args.output/'inventory.json').write_text(json.dumps(report,indent=2)+'\n')
    with (args.output/'inventory.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(report['rows'][0]));writer.writeheader();writer.writerows(report['rows'])
    print(json.dumps({k:v for k,v in report.items() if k not in ['rows','note']}))

if __name__=='__main__':main()
