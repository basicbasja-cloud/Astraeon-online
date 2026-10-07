"""Run each existing test file and report individual TAP checks, not file counts."""
import subprocess,re,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'docs/review/wayfarer-capital-v76/node-final';out.mkdir(exist_ok=True)
files=['expanded_town','golden_pipeline','locomotion-transitions','motion','painted_locomotion','world_v3'];reports=[]
for name in files:
 f='tests/'+name+'.test.cjs';r=subprocess.run(['node','--test-reporter=tap',f],cwd=root,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(out/(name+'.test.log')).write_text(r.stdout)
 counts={k:int(re.search(r'^# '+k+r' (\d+)\s*$',r.stdout,re.M).group(1)) for k in ['tests','pass','fail']};record={'file':f,'exitCode':r.returncode,**counts};print(json.dumps(record),flush=True);reports.append(record);assert r.returncode==0 and counts['fail']==0 and counts['pass']==counts['tests']
with (root/'world/v3/wayfarer-spatial.json').open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
report={'sourceSHA256':sha,'files':reports,'totalTests':sum(r['tests'] for r in reports),'failures':0};assert report['totalTests']==96;(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS 96 individual Node checks',flush=True)
