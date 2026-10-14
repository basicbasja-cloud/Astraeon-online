"""Integrity/authority audit. Passing integrity cannot approve rejected artwork."""
from pathlib import Path
import json,hashlib,importlib.util
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2];checks={};details={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def binding(b):
 p=ROOT/b['path'];return p.is_file() and sha(p)==b['sha256']
previous=[]
for path in sorted((ROOT/'research/sprite-animation').glob('*/evidence-manifest.json')):
 if path.parent.name in ['proportion-repair-v42','continuous-arm-v43']:continue
 manifest=json.loads(path.read_text());rows=manifest['files'];assert all(binding(row) for row in rows),path;previous.append(dict(path=str(path.relative_to(ROOT)),files=len(rows),unchanged=True))
checks['all_twelve_published_v30_v41_manifests_unchanged']=len(previous)==12;details['previous_manifests']=previous
w=json.loads((P.parent/'joint-tracking-ro-v30/protected-W.json').read_text());checks['all_protected_W_bytes_unchanged']=all(sha(ROOT/f['path'])==f['expected_sha256'] for f in w['files']);details['protected_W_file_count']=len(w['files'])
checks['exact_approved_v39_receipt_preserved']=sha(P.parent/'rear-motion-v40/user-v39-acceptance.json')=='18cfd24c16bb12ac58e2d92f93716b2bf3ae3c590129ebe1361dcd401571de86'
job_count=0
for case in [P.parent/'proportion-repair-v42',P]:
 ledger=json.loads((case/'generation-ledger.json').read_text())
 for job in ledger['jobs']:
  assert binding(job['prompt']) and all(binding(b) for b in job['direct_inputs']),job['name'];original=job['provider_original'];assert binding(original),job['name'];work=job.get('retained_work_copy',job.get('output'));assert binding(work);assert Image.open(ROOT/original['path']).convert('RGBA').tobytes()==Image.open(ROOT/work['path']).convert('RGBA').tobytes();job_count+=1
checks['twelve_actual_native_jobs_exact_inputs_provider_originals_and_pixels']=job_count==12
refs=json.loads((P/'paint/contact-reference-extraction.json').read_text());checks['static_appearance_reference_crops_bound']=sha(P/'paint/eight-contact-raw.png')==refs['raw_sha256'] and all(sha(P/v['file'])==v['sha256'] for v in refs['views'])
q=json.loads((P/'source-qa.json').read_text());skin=json.loads((P/'skin-qa.json').read_text());checks['nineteen_source_checks_pass_bounded_only']=len(q['checks'])==19 and q['source_metrics_pass'] and not q['production_pass'];checks['nine_actual_skin_checks_pass_bounded_only']=len(skin['checks'])==9 and skin['bounded_skin_study_pass'] and not skin['production_pass']
hinge=json.loads((P/'hinge-skin-qa.json').read_text());checks['eleven_corrected_hinge_skin_checks_pass_bounded_only']=len(hinge['checks'])==11 and hinge['bounded_hinge_skin_pass'] and not hinge['production_pass']
v=json.loads((P/'reference/video-frame-receipt.json').read_text());checks['all216actual_video_frames_and_unknown_terminal_clock']=v['decoded_frame_count']==216 and v['unknown_clock_frames']==[215] and all(sha(P/f['path'])==f['sha256'] and Image.open(P/f['path']).size==(352,240) for f in v['frames']);checks['video_clock_authority_preserved']=sum(f['clock_status']=='DIRECT_PTS' for f in v['frames'])==1 and sum(f['clock_status']=='DECODER_BEST_EFFORT' for f in v['frames'])==214 and v['frames'][-1]['container_pts_seconds'] is None and v['frames'][-1]['decoder_best_effort_seconds'] is None
motion=json.loads((P/'cmu-motion.json').read_text());checks['740actual120HzAMC_samples_and_source_bindings']=len(motion['frames'])==740 and motion['sample_rate_hz']==120 and all(sha(P/b['path'])==b['sha256'] for b in motion['inputs'])
checks['real_image_owner_counterexample_rejected']=not json.loads((P/'painted-owner-qa.json').read_text())['temporal_owner_review_pass'] and json.loads((P/'painted-owner-qa.json').read_text())['observed_owner_changes']==[[3,4]]
checks['regression_receipts_present']=len(json.loads((P/'arm-test-receipt.json').read_text())['checks'])==13 and len(json.loads((P/'painted-owner-tests.json').read_text())['checks'])==9
checks['twenty_actual_eightview_browser_controls']=len(json.loads((P/'browser-qa.json').read_text())['checks'])==20
checks['old_rig_user_rejection_retained']=json.loads((P.parent/'proportion-repair-v42/user-arm-rejection.json').read_text())['status']=='USER_REJECTED_CURRENT_ARM_RIG'
proposal=json.loads((P/'tripo-proposal.json').read_text());checks['optional_external_submission_still_not_executed']=proposal['status']=='PROPOSED_NOT_AUTHORIZED_NOT_EXECUTED' and proposal['cli']['executed'] is False and proposal['cli']['dry_run_executed'] is False;checks['proposed_front_payload_exact_and_back_excluded']=sha(P/proposal['input_image']['path'])==proposal['input_image']['sha256'] and 'model-back-REJECTED.png' in proposal['excluded_images']
out=dict(checks=checks,details=details,integrity_audit_pass=all(checks.values()),painted_motion_pass=False,production_pass=False,scope='Evidence integrity, source/test result scope and retained real failures. Not artwork approval. Optional external route pending; no execution/upload/job/billing.')
(P/'audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(checks));assert out['integrity_audit_pass']
