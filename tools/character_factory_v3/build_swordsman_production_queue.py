"""Publish actual Swordsman work targets and source coverage, never art approval."""
import hashlib,json
from pathlib import Path
from build_action_inventory import build_inventory
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build():
 config=json.loads((BASE/'factory.json').read_text());ledger=json.loads((BASE/'ledger.json').read_text());inventory=build_inventory(config,ledger,BASE)
 baseline_path=ROOT/'docs/character-factory/review/restore-tall-swordsman-baseline-20261026/baseline-proof.json';baseline=json.loads(baseline_path.read_text())
 for path,digest in baseline['baseline_files'].items():
  if sha(ROOT/path)!=digest:raise ValueError('Protected original changed: '+path)
 rows=[]
 for row in inventory['rows']:
  if row['class']!='Swordsman':continue
  job=ledger['paint_jobs'][row['paint_job']];character=next(c for c in config['characters'] if c['id']==row['character']);action=config['classes']['Swordsman']['actions'][row['action']]
  receipt_path=BASE/'cutouts'/job['id']/'import-receipt.json'
  rows.append({**row,'body_variant':character['body_variant'],'source_actions':action['source_actions'],'source_provider':action['source_provider'],'guide_root':'../'+(BASE/'guides'/row['guide_job']).relative_to(ROOT).as_posix(),'receipt_sha256':sha(receipt_path) if receipt_path.is_file() else None,'fit_id':job['fit_id'],'historical_review':{'BasicAttack':{'id':'BasicAttack','frames':16},'SkillAction':{'id':'SkillOverhead','frames':16}}.get(row['action'])})
 for sex in ('male','female'):
  selected=[r for r in rows if r['body_variant']==sex]
  if len(selected)!=19:raise ValueError('Swordsman target changed; update reviewer deliberately')
 report={'status':'SOURCE_AND_RECEIPT_COVERAGE_NOT_ART_APPROVAL','baseline_files_verified':len(baseline['baseline_files']),'baseline_proof_sha256':sha(baseline_path),'config_sha256':sha(BASE/'factory.json'),'ledger_sha256':sha(BASE/'ledger.json'),'rows':rows,'limits':['Source PNG presence is not source-pose or fitted-body approval.','Technical imports are not complete actions.','Historical sixteen-frame skill art does not cover the thirty-two-frame target.','No approved action or playable character is inferred from this queue.']}
 path=ROOT/'proof/swordsman-production-queue.json';path.write_text(json.dumps(report,indent=2)+'\n');print('38 logical action targets; protected baseline files verified:',report['baseline_files_verified'])
if __name__=='__main__':build()
