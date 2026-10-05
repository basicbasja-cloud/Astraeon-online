"""Run every Node check in its own process and retain individual test counts.

Some managed Node24 hosts report only file-level success with the default
process-isolated test runner. Separate invocations with isolation disabled keep
the tests' globals independent while exposing every registered assertion.
"""
import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--node', default='node')
parser.add_argument('--output', type=Path,
                    default=Path(tempfile.gettempdir()) / 'astraeon-node-checks')
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
reports = []
for test in sorted((ROOT / 'tests').glob('*.test.cjs')):
    result = subprocess.run([args.node, '--test', '--test-isolation=none',
                             '--test-reporter=tap', str(test)], cwd=ROOT,
                            capture_output=True, text=True)
    (args.output / (test.stem + '.log')).write_text(result.stdout + result.stderr)
    counts = {}
    for name in ('tests', 'pass', 'fail'):
        match = re.search(r'^# ' + name + r' (\d+)$', result.stdout, re.M)
        counts[name] = int(match.group(1)) if match else None
    report = {'file': test.relative_to(ROOT).as_posix(), 'exitCode': result.returncode, **counts}
    reports.append(report)
    print(json.dumps(report), flush=True)
    if result.returncode or not counts['tests'] or counts['fail']:
        print(result.stdout + result.stderr)
        raise SystemExit(result.returncode or 1)
summary = {'files': reports, 'totalTests': sum(r['tests'] for r in reports),
           'failures': sum(r['fail'] for r in reports)}
(args.output / 'report.json').write_text(json.dumps(summary, indent=2) + '\n')
print('PASS', summary['totalTests'], 'individual Node checks;', args.output, flush=True)
