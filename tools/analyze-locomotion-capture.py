"""Analyze observed per-RAF pose selection, roots and transition timing.

Produce unmodified gameplay-crop previews at recorded and quarter speed.
No asset generation/replacement, joint inference or animation approval.
"""
import argparse,json,math,statistics
from pathlib import Path
from PIL import Image,ImageDraw
ap=argparse.ArgumentParser();ap.add_argument('input',type=Path);args=ap.parse_args();source=args.input;records=[]
def analyze(timeline,transition=False):
    intervals=[];changes=[];skips=[];mismatch=[];holds=0;previous=None;strategy_changes=[];ground_distance=0;phase_travel=0;state_changes=[]
    for i,s in enumerate(timeline):
        a=s.get('actor',s);simulation=s.get('simulation',{});frame=a.get('frame');t=s['time'];intervals.append(s.get('intervalMs',0))
        if not frame:continue
        if simulation.get('activeStrategy'):
            expected=math.floor((simulation.get('gait',0)%1)*8)
            if frame['clip'].startswith('warrior-') and any(k in frame['clip'] for k in ['walk','run','sprint']) and frame['column']!=expected:mismatch.append({'index':i,'expected':expected,'actual':frame['column']})
        if previous:
            old=previous.get('actor',previous);old_sim=previous.get('simulation',{});old_frame=old.get('frame')
            displacement=math.dist(a['root'][:2],old['root'][:2]);ground_distance+=displacement
            if old_frame and frame['clip']==old_frame['clip']:
                phase_travel+=(simulation.get('gait',0)-old_sim.get('gait',0)) if frame['clip'].startswith('warrior-') else (simulation.get('distance',0)-old_sim.get('distance',0))/2.1
            if simulation.get('state')!=old_sim.get('state'):state_changes.append({'index':i,'time':t,'from':old_sim.get('state'),'to':simulation.get('state'),'stateTime':simulation.get('stateTime'),'transition':simulation.get('transition'),'frame':frame})
            if math.dist(a['root'][:2],old['root'][:2])>1e-5 and math.dist(a['renderedRoot'][:2],old['renderedRoot'][:2])<1e-5:holds+=1
            if old_frame and frame!=old_frame:
                # Tight-crop bounds and clip changes count as actual selections.
                if frame['clip']==old_frame['clip'] and frame['row']==old_frame['row']:
                    advance=(frame['column']-old_frame['column'])%8
                    if advance>1:skips.append({'index':i,'from':old_frame,'to':frame,'advance':advance,'intervalMs':s.get('intervalMs')})
                changes.append({'index':i,'time':t,'frame':frame,'state':simulation.get('state'),'gait':simulation.get('gait'),'speed':a['speed']})
            if simulation.get('activeStrategy')!=old_sim.get('activeStrategy'):
                gait=simulation.get('gait',0)%1;strategy_changes.append({'index':i,'time':t,'from':old_sim.get('activeStrategy'),'to':simulation.get('activeStrategy'),'phase':gait,'distanceToContact':min(gait,abs(gait-.5),1-gait),'boundaryEvent':simulation.get('strategyTransition'),'frame':frame})
        previous=s
    speeds=[s.get('actor',s)['speed'] for s in timeline if s.get('actor',s).get('speed',0)>.02]
    durations=[(b['time']-a['time'])*1000 for a,b in zip(changes,changes[1:]) if a['frame']['clip']==b['frame']['clip'] and a['frame']['row']==b['frame']['row']]
    return {'samples':len(timeline),'meanMovingSpeed':statistics.mean(speeds) if speeds else 0,'observedGroundDistance':ground_distance,'observedDisplayCycles':phase_travel,'groundDistancePerDisplayCycle':ground_distance/phase_travel if phase_travel and not transition else None,'frozenRenderedRootFrames':holds,'observedSkippedSelections':skips,'phaseSelectionMismatches':mismatch,'poseDurationMs':{'median':statistics.median(durations) if durations else None,'min':min(durations) if durations else None,'max':max(durations) if durations else None},'maxCapturedIntervalMs':max(intervals),'strategyChanges':strategy_changes,'stateChanges':state_changes,'changes':changes,'scope':'Observed capture timing/selection only; capture itself adds overhead. Roots and crop rectangles do not prove anatomical contacts.'}
for folder in sorted((source/'motion-series').iterdir()) if (source/'motion-series').exists() else []:
    if not folder.is_dir():continue
    timeline=json.loads((folder/'runtime-timeline.json').read_text());result=analyze(timeline);result['case']=folder.name
    frames=json.loads((folder/'frames.json').read_text());pictures=[]
    for i,f in enumerate(frames):
        image=Image.open(folder/f'{i:03d}.png').convert('RGB');canvas=Image.new('RGB',(432,510),(34,45,56));canvas.paste(image.resize((432,480),Image.Resampling.NEAREST),(0,30));draw=ImageDraw.Draw(canvas);pose=f.get('selectedPose') or {};draw.text((8,8),f'{i}: {pose.get("clip")} / {pose.get("row")} / {pose.get("column")}',fill='white');pictures.append(canvas)
    durations=[max(10,round((b['time']-a['time'])*1000)) for a,b in zip(frames,frames[1:])]
    if pictures:
        durations.append(round(statistics.median(durations)) if durations else 100)
        pictures[0].save(folder/'recorded.gif',save_all=True,append_images=pictures[1:],duration=durations,loop=0)
        pictures[0].save(folder/'quarter-speed.gif',save_all=True,append_images=pictures[1:],duration=[d*4 for d in durations],loop=0)
        sheet=Image.new('RGB',(1296,1530),(34,45,56))
        for i,picture in enumerate(pictures[:9]):sheet.paste(picture,(i%3*432,i//3*510))
        sheet.save(folder/'first-nine-transitions.png')
    records.append(result)
transition_file=source/'transitions/runtime-timeline.json'
transition=analyze(json.loads(transition_file.read_text()),True) if transition_file.exists() else None
report={'candidateOnly':True,'locomotionApproved':False,'assetsChanged':False,'cases':records,'transitions':transition,'limits':['Anatomical feet/pelvis/weapon/costume and exact painted contact/stride require frame inspection.','Dropped selections are observed during instrumented capture, not a claim about uninstrumented performance.']}
(source/'locomotion-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'cases':len(records),'skippedSelections':sum(len(r['observedSkippedSelections']) for r in records),'phaseMismatches':sum(len(r['phaseSelectionMismatches']) for r in records),'rootHolds':sum(r['frozenRenderedRootFrames'] for r in records),'strategyChanges':transition['strategyChanges'] if transition else []}))
