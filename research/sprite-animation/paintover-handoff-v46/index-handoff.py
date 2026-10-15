#!/usr/bin/env python3
"""Index retained research without executing historical scripts or inspecting credentials."""
from pathlib import Path
import ast, csv, hashlib, json, platform, re, subprocess
P=Path(__file__).resolve().parent; ROOT=P.parents[2]
def write_csv(path,rows,keys):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def main():
    out=P/'handoff';out.mkdir(exist_ok=True)
    cases=[]
    for c in sorted((ROOT/'research/sprite-animation').iterdir()):
        if not c.is_dir():continue
        readme=c/'README.md'; docs=sorted(q.name for q in c.glob('*.md'))
        text=readme.read_text(errors='replace') if readme.exists() else ''
        title=next((s.lstrip('# ') for s in text.splitlines() if s.startswith('#')),'No case README; see parent documentation')
        cases.append({'case':c.name,'entry':str(readme.relative_to(ROOT)) if readme.exists() else None,'title':title,'docs':docs,'status':'CURRENT_PAINT_REVIEW' if c==P else 'FROZEN_HISTORY_READ_CASE_SCOPE; no automatic approval transfer'})
    (out/'CASES.json').write_text(json.dumps(cases,indent=2)+'\n')
    lines=['# Every retained case\n','All paths below are relative to the repository root. Historical scripts may overwrite their own evidence: inspect; do not rerun in place. The current status decisions are in 01-STATUS-AND-DECISIONS.md.\n']
    for c in cases:
        lines+=['## '+c['case']+'\n',c['title']+'\n','Entry: `'+str(c['entry'] or 'research/sprite-animation/'+c['case'])+'`\n','Documents: '+', '.join('`'+d+'`' for d in c['docs'])+'\n']
    (out/'ALL-CASES.md').write_text('\n'.join(lines))
    rows=[]
    paths=list((ROOT/'skills/modular-eight-direction-sprites').rglob('*.py'))+list(P.glob('*.py'))
    for p in sorted(paths):
        try:
            tree=ast.parse(p.read_text()); doc=ast.get_docstring(tree) or '';flags=[]
            for n in ast.walk(tree):
                if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='add_argument':
                    flags.extend(a.value for a in n.args if isinstance(a,ast.Constant) and isinstance(a.value,str))
            rows.append({'path':str(p.relative_to(ROOT)),'purpose':doc[:1200],'declared_flags':' '.join(flags),'scope':'Historical diagnostic; inspect entry and strict gates; not a universal anatomy detector'})
        except (SyntaxError,UnicodeError): pass
    write_csv(out/'TOOLS.csv',rows,['path','purpose','declared_flags','scope'])
    tracked=set(subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines())
    cache=[]
    for base in [ROOT/'research/sprite-animation',ROOT/'skills/modular-eight-direction-sprites']:
        for p in base.rglob('*'):
            rel=str(p.relative_to(ROOT))
            if p.is_file() and rel not in tracked and P not in p.parents and '__pycache__' not in rel:
                cache.append({'path':rel,'bytes':p.stat().st_size,'portable_in_git':False})
    (out/'LOCAL-CACHE-REPORT.json').write_text(json.dumps({'scope':'Untracked historical research files only; no account or credential directories scanned','files':cache},indent=2)+'\n')
    # Exclude inventory itself and receipts generated AFTER inventory, preventing self-hash loops.
    excluded={str((out/x).relative_to(ROOT)) for x in ['FILES.json','FILES.csv','verification.json','browser-qa.json']}
    files=[]
    candidates={ROOT/p for p in tracked if p.startswith(('research/sprite-animation/','skills/modular-eight-direction-sprites/'))}
    candidates.update(q for q in P.rglob('*') if q.is_file() and '__pycache__' not in str(q))
    candidates.update([ROOT/'HANDOFF.md',ROOT/'AGENTS.md'])
    for p in sorted(candidates):
        rel=str(p.relative_to(ROOT))
        if not p.is_file() or rel in excluded:continue
        files.append({'path':rel,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scope':'current_delivery' if p==P or P in p.parents else 'retained_history_or_instructions'})
    (out/'FILES.json').write_text(json.dumps({'excludes':sorted(excluded),'files':files},indent=2)+'\n')
    write_csv(out/'FILES.csv',files,['path','bytes','sha256','scope'])
    print(json.dumps({'cases':len(cases),'tools':len(rows),'indexed_files':len(files),'local_only_files':len(cache)}))
if __name__=='__main__':main()
