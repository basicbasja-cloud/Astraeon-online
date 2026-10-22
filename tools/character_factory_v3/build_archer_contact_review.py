"""Build source-motion evidence; mannequin GIFs never count as painted coverage."""
import argparse,json,math,sys
from pathlib import Path
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).parent))
from build_fixed_grid_sequence_review import gif


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--guide',type=Path,required=True);p.add_argument('--before',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--viewport',type=int,nargs=4,default=[378,454,1158,1234]);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((a.guide/'manifest.json').read_text());first=next(iter(manifest['views'].values()))['frames'];timestamps=[];entry=sum('transition_from' in f for f in first);intervals={'Ranged_Bow_Draw':tuple(manifest['job']['source_ranges']['Ranged_Bow_Draw']),'Ranged_Bow_Release':(0,max(f['source_frame']for f in first if f['action']=='Ranged_Bow_Release'))}
    for i,f in enumerate(first):
        if 'transition_from' in f:t=i/24
        elif f['action']=='Ranged_Bow_Draw':t=entry/24+(f['source_frame']-8)/24
        elif f['action']=='Ranged_Bow_Release':t=entry/24+1+f['source_frame']/24
        else:raise ValueError('Unsupported source timeline')
        timestamps.append(t*1000)
    durations=[max(10,round(timestamps[i+1]-timestamps[i]))for i in range(len(first)-1)]+[300]
    allviews=[];beforeafter=[];records=[];world_disagreements=[];baseline=first
    for direction,view in manifest['views'].items():
        frames=[];pairs=[];toe_errors=[];clamps=[];edge=[]
        for i,f in enumerate(view['frames']):
            im=Image.open(a.guide/direction/f'{i:03d}.png').convert('RGBA');crop=im.crop(a.viewport).resize((768,768),Image.Resampling.LANCZOS);frames.append(crop)
            old=Image.open(a.before/direction/f'{i:03d}.png').convert('RGBA').crop(a.viewport).resize((768,768),Image.Resampling.LANCZOS)
            pair=Image.new('RGBA',(1536,800),'#e8e8e8');pair.alpha_composite(old,(0,32));pair.alpha_composite(crop,(768,32));draw=ImageDraw.Draw(pair);draw.text((12,10),'PREVIOUS ROTATION TRANSFER',fill='black');draw.text((780,10),'AUTHORED CONTACT ADAPTER - SOURCE REVIEW',fill='black');pairs.append(pair)
            b=im.getchannel('A').getbbox()
            if b and (b[0]<a.viewport[0] or b[1]<a.viewport[1] or b[2]>a.viewport[2] or b[3]>a.viewport[3]):edge.append(i)
            contact=f.get('contact_world',{})
            if contact:
                toe_errors.extend(abs(contact['target_toes'][s][2]-contact['donor_toes'][s][2]) for s in ['l','r'])
            c=f['weapon_guide'].get('archery_contact',{}).get('reach',{})
            clamps.extend(c[s]['reach_clamp_m'] for s in ['l','r'] if s in c)
            for name,v in f['world_landmarks'].items():
                error=math.dist(v,baseline[i]['world_landmarks'][name])
                if error>1e-5:world_disagreements.append({'direction':direction,'index':i,'landmark':name,'error_m':error})
        target=a.output/direction;target.mkdir(exist_ok=True);gif(frames,target/'normal.gif',durations);gif(frames,target/'slow.gif',[d*3 for d in durations]);gif(pairs,target/'before-after.gif',durations)
        frames[0].save(target/'normal.webp',save_all=True,append_images=frames[1:],duration=durations,loop=0,lossless=True,method=4)
        seam=max(math.dist(view['frames'][0]['world_landmarks'][n],view['frames'][-1]['world_landmarks'][n]) for n in baseline[0]['world_landmarks'])
        visible=[f['frame'] for f in view['frames']if f['weapon_guide']['arrow_visible']]
        record={'direction':direction,'frames':len(frames),'max_toe_height_error_m':max(toe_errors)if toe_errors else None,'max_arm_reach_clamp_m':max(clamps)if clamps else None,'first_last_body_landmark_error_m':seam,'nocked_arrow_visible_indices':visible,'viewport_clipped_frames':edge};records.append(record);allviews.append(frames)
    combined=[]
    for i in range(len(first)):
        canvas=Image.new('RGBA',(1536,1536),'#e8e8e8')
        for k,frames in enumerate(allviews):canvas.alpha_composite(frames[i],((k%2)*768,(k//2)*768))
        combined.append(canvas)
    gif(combined,a.output/'four-view-normal.gif',durations)
    receipt={'status':'SOURCE_CONTACT_DIAGNOSTIC_NOT_FINAL_ART','guide_job':manifest['job']['id'],'shared_viewport':a.viewport,'source_fps':24,'pose_times_ms':timestamps,'preview_durations_ms':durations,'last_idle_hold_ms':300,'source_intervals':intervals,'per_frame_image_registration':False,'world_camera_disagreements':world_disagreements,'directions':records,'limitations':['Toe joints matching donor heights is not a full mesh sole or collision audit.','Contact adaptation is authored 3D motion, not unchanged donor mocap.','Source mannequin captures are not painted sprites or final character acceptance.'],'owner_approved':False,'runtime_admitted':False}
    (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
