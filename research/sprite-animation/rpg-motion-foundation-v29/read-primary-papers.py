#!/usr/bin/env python3
"""Fetch primary PDFs for local reading. Do not publish full paper contents."""
import concurrent.futures,hashlib,importlib.util,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('fetch',ROOT/'fetch-evidence.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
URLS={
 'reconform':'https://arxiv.org/pdf/2502.21207',
 'skelaware':'https://deepmotionediting.github.io/papers/skeleton-aware-camera-ready.pdf',
 'inbetween':'https://static-wordpress.ubisoft.com/montreal.ubisoft.com/wp-content/uploads/2020/07/09155337/RobustMotionInbetweening.pdf',
 'motionmatch':'https://theorangeduck.com/media/uploads/other_stuff/Learned_Motion_Matching.pdf',
 'deepmimic':'https://xbpeng.github.io/projects/DeepMimic/DeepMimic_2018.pdf',
 'anidoc':'https://arxiv.org/pdf/2412.14173',
}
def read(item):
 id,url=item;r={'source_id':id,'url':url,'inference_executed':False}
 try:
  response,data=mod.get(url,cap=40_000_000)
  if response.status_code!=200 or not data.startswith(b'%PDF'):raise ValueError('No PDF HTTP '+str(response.status_code))
  pdf=ROOT/'local-cache'/(id+'-paper.pdf');pdf.write_bytes(data);text=pdf.with_suffix('.txt')
  subprocess.run(['pdftotext','-layout',str(pdf),str(text)],check=True)
  r.update(status='pdf_text_available',pdf_sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),local_text=str(text.relative_to(ROOT)),reading_scope='targeted methods/limitations pending reviewer notes, not full-paper completion')
 except Exception as e:r.update(status='failed',error=str(e)[:300])
 return r
def main():
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:records=list(pool.map(read,URLS.items()))
 # PFNN was already retrieved in the general page pass.
 pdf=ROOT/'local-cache/pfnn.pdf'
 if pdf.exists():
  text=pdf.with_suffix('.txt');subprocess.run(['pdftotext','-layout',str(pdf),str(text)],check=True)
  records.append({'source_id':'pfnn','status':'pdf_text_available','url':'https://www.pure.ed.ac.uk/ws/files/35467734/phasefunction.pdf','pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'local_text':str(text.relative_to(ROOT)),'inference_executed':False,'reading_scope':'targeted methods/limitations pending reviewer notes, not full-paper completion'})
 (ROOT/'paper-retrieval.json').write_text(json.dumps({'papers':records},indent=2)+'\n');print([(r['source_id'],r['status']) for r in records])
if __name__=='__main__':main()
