from pathlib import Path
from PIL import Image
import json,hashlib,shutil
root=Path.cwd();g=root/'work/all-actions-v61/generation';specs=json.loads((g/'job-ids.json').read_text());seed='research/sprite-animation/core-family-v56/frames/idle/S/00.png';G='work/all-actions-v61/generation/';R='/workspace/generated_images/exec-'
refs=[
 [seed,'work/all-actions-v61/pickup-S-source-guide16.png'],
 [G+'S-down-layout.png',G+'S-down-poses.png'],
 [G+'S-up-layout.png',G+'S-up-poses.png',G+'S-down-layout2/raw.png'],
 [G+'S-down-layout2/raw.png'],[G+'S-mid-key-guide.png'],[G+'S-hand-target-guide.png'],[G+'S-outward4-guide.png'],[G+'S-arm-mid-guide.png'],[G+'S-leg-lock-guide.png'],[G+'S-leg-lock-guide.png'],[G+'W-pickup-layout.png',G+'W-pickup-poses-guide.png'],[G+'E-pickup-layout.png',G+'E-pickup-poses-guide.png'],[G+'W-foot-lock-guide.png'],[G+'S-ready-layout.png',G+'S-ready-poses-guide.png'],[G+'W-ready-layout.png',G+'W-ready-poses-guide.png'],[G+'S-ready-layout.png',R+'4f2c3a39-fb76-459d-a994-c3c332c45d0f.png'],[G+'N-ready-layout.png',G+'N-ready-poses-guide.png'],[G+'E-ready-layout.png',G+'E-ready-poses-guide.png'],[G+'W-walk-layout.png',G+'W-walk-poses-guide.png'],[G+'W-walk-arm-clean-guide.png'],[G+'W-walk-layout.png',G+'W-walk-RO-large-guide.png'],[G+'W-walk-RO-arm-targets.png'],[G+'W-walk-mid-left.png',G+'W-walk-mid-right.png']]
statuses=[
 'REJECTED:4x4 cell crossing and cut footwear',
 'SELECTED S original cells0,2,3 only; otherposes neednative repairs',
 'REJECTED:recovery tooquick thenearlyneutral',
 'SUPERSEDED:closeddeepglove useful; midpointwrongcrown; notfinal',
 'SELECTED S middle cell only as key3',
 'REJECTED:hand intersectssole reviewwindow',
 'REJECTED:footdrift; key4 handtrajectory shootsout/up',
 'SUPERSEDED:armmidpoint coherent but feetdrift',
 'REJECTED:removed panelgrid and autozoomed/recomposed figures',
 'SELECTED S all4 cells as keys4..7; crown and bothsolebudgetsPASS',
 'REJECTED W:footXdrift; repairposeguideonly',
 'SELECTED E cells1..7 withwholeoriginalneutral lock; motion/contactPASS',
 'SELECTED W cells1..7 withwholeoriginalneutral lock; motion/contactPASS',
 'REJECTED Sready:firstvarianttoo tall/lowfloor; repairednative',
 'CANDIDATE Wready:8drawings,24exposures; contactsPASS; head/native/visual pending',
 'CANDIDATE Sready repaired:contactsPASS; head/native/visual pending',
 'CANDIDATE Nready:contactsPASS; head/native/visual pending',
 'CANDIDATE Eready:contactsPASS; head/native/visual pending',
 'REJECTED Wwalk:leg/arm phases inconsistent',
 'REJECTED/SUPERSEDED:localarms improved butwholegait stillphaseambiguous',
 'CANDIDATE Wwalk_RO:directROposeguide; armphasebad; retain0/2 asnativeevenposecandidates',
 'CANDIDATE Wwalk_ARMS:retain1/3/4/5/6/7 asnativeevenposecandidates; nofullmotionpass',
 'REJECTED:bankinbetweens not reliablehalfwayposes, somewrongphase; donotcountas16approveddrawings']
assert len(specs)==len(refs)==len(statuses)==23

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[];(g/'raw').mkdir(exist_ok=True)
for i,((key,uid),ref,status)in enumerate(zip(specs,refs,statuses),1):
 raw=Path(R+uid+'.png');dest=g/'raw'/f'job{i:02}.png';shutil.copyfile(raw,dest);rr=[]
 for n,path in enumerate(ref,1):
  f=Path(path);f=f if f.is_absolute()else root/f;assert f.is_file(),f;rr.append({'position':n,'path':str(f),'sha256':sha(f),'dimensions':list(Image.open(f).size)})
 prompt=g/'prompts'/f'job{i:02}.txt';rows.append({'job':i,'tool':'builtin image_gen.imagegen','prompt':str(prompt.relative_to(g)),'prompt_sha256':sha(prompt),'output':str(dest.relative_to(g)),'output_sha256':sha(dest),'original_output_path':str(raw),'dimensions':list(Image.open(raw).size),'transparent_background':True,'ordered_references':rr,'reference_record_origin':'reconstructed from exact promptroles and existingdraft/guide receipts'if i<=7 else 'actual invoked ordered toolarguments in this continuation','decision':status,'user_final_acceptance':False,'all_actions_approval':False})
report={'builtin_imagegen_jobs':len(rows),'authorization':'User explicitly permits builtintools through monthly ChatGPTplan; no further costquestion needed. No credits purchased or external paid provider invoked.','billing_per_builtin_call_observable':False,'raw_outputs_preserved':True,'jobs':rows,'all48pass':False}
(g/'generation-ledger.json').write_text(json.dumps(report,indent=2)+'\n');print('23prompt/raw/reference-hash records saved; no failed outputs lost')
