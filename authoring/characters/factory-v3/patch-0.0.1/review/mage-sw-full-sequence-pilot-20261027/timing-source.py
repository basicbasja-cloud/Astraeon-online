"""Recover review timing from explicit source ranges; never invent gameplay events."""
import math


def source_timing(manifest,direction,fps=24,terminal_hold_ms=200):
    if not math.isfinite(fps) or fps<=0 or terminal_hold_ms<=0:raise ValueError('Invalid review timing')
    job=manifest['job'];segments=job['source_actions'];ranges=job.get('source_ranges',{})
    if len(set(segments))!=len(segments):raise ValueError('Repeated source actions need explicit segment identity')
    offsets={};elapsed=0
    for action in segments:
        if action not in ranges:raise ValueError('Explicit source range required: '+action)
        start,end=ranges[action]
        if not all(math.isfinite(v) for v in [start,end]) or end<=start:raise ValueError('Invalid source range')
        offsets[action]=elapsed;elapsed+=(end-start)*1000/fps
    times=[]
    for frame in manifest['views'][direction]['frames']:
        if 'transition_from' in frame:raise ValueError('Authored transitions need a separate timing contract')
        action=frame['action'];value=frame['source_frame'];start,end=ranges[action]
        if not start<=value<=end:raise ValueError('Source frame outside declared range')
        times.append(offsets[action]+(value-start)*1000/fps)
    if len(times)<2 or any(b<=a for a,b in zip(times,times[1:])):raise ValueError('Source times must increase strictly')
    boundaries=[round(t/10)*10 for t in times]
    durations=[b-a for a,b in zip(boundaries,boundaries[1:])]+[terminal_hold_ms]
    if min(durations)<10:raise ValueError('GIF timing resolution insufficient for these samples')
    return {'source_fps':fps,'source_times_ms':times,'gif_durations_ms':durations,
            'source_motion_duration_ms':elapsed,'terminal_inspection_hold_ms':terminal_hold_ms,
            'gameplay_event_timing_approved':False}
