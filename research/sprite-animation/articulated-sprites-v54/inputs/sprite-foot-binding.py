"""Hash only inputs consumed by the flat-foot diagnostic, independently of head/body art."""
import hashlib,json

def normalize_numbers(value):
    # Browser JSON evaluation serializes integral Number values (including -0) as integers.
    if isinstance(value,float) and value.is_integer():return int(value)
    if isinstance(value,list):return [normalize_numbers(v) for v in value]
    if isinstance(value,dict):return {k:normalize_numbers(v) for k,v in value.items()}
    return value

def foot_binding(data):
 names=[n for n,d in data['definitions'].items() if d.get('kind')=='chain' and d.get('role')=='leg']
 if len(names)!=2:raise ValueError('Expected exactly two authored leg layers')
 nodes=sorted({n for name in names for n in data['definitions'][name]['nodes']})
 selected={'definitions':{n:data['definitions'][n] for n in sorted(names)},'poses':[{n:p[n] for n in nodes} for p in data['poses']],'world_offsets':data['world_offsets'],'source_sha256':data['source_sha256']}
 return hashlib.sha256(json.dumps(normalize_numbers(selected),sort_keys=True,separators=(',',':')).encode()).hexdigest()
