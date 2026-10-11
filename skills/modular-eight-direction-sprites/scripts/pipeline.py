#!/usr/bin/env python3
"""Isolated, repeatable review builds for the original rigged-parts adapter.

This adapter never emits an approved release. Failed builds retain their logs;
current.json changes only after all required mechanical checks pass.
"""
import argparse
import fcntl
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
import zipfile

SKILL = Path(__file__).resolve().parents[1]
ADAPTER = SKILL / 'studies/rigged-parts'
SCHEMA = 'modular-sprite-review-build-v1'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        temporary.write_text(json.dumps(value, indent=2) + '\n')
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def read(path):
    return json.loads(path.read_text())


def contained(root, relative):
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise ValueError('Unsafe relative artifact path: ' + str(relative))
    result = root / path
    if any(p.is_symlink() for p in [result, *result.parents] if p != root.parent):
        raise ValueError('Symlink artifact rejected: ' + str(relative))
    if not result.resolve().is_relative_to(root.resolve()):
        raise ValueError('Artifact escapes output root: ' + str(relative))
    return result


def doctor():
    tools = {}
    for name in ('blender', 'node', 'chromium'):
        executable = shutil.which(name)
        if not executable:
            raise RuntimeError('Required executable missing: ' + name)
        result = subprocess.run([executable, '--version'], capture_output=True, text=True, check=True)
        tools[name] = {'path': executable, 'version': result.stdout.splitlines()[0]}
    for module, distribution in [('PIL', 'Pillow'), ('numpy', 'numpy'), ('OpenEXR', 'OpenEXR'), ('playwright', 'playwright')]:
        try:
            __import__(module)
            tools[module] = importlib.metadata.version(distribution)
        except (ImportError, importlib.metadata.PackageNotFoundError) as exc:
            raise RuntimeError('Required Python dependency missing: ' + module + '; install it in your environment or set PYTHONPATH') from exc
    tools['python'] = sys.version.split()[0]
    return tools


def inputs(tools):
    files = sorted([*ADAPTER.glob('*.py'), *ADAPTER.glob('*.mjs'), *ADAPTER.glob('runtime/*'),
                    SKILL / 'studies/motion-lab/motion.mjs', Path(__file__).resolve()])
    source = {str(p.relative_to(SKILL)): digest(p) for p in files if p.is_file()}
    value = {'schema': SCHEMA, 'adapter': 'original-rigged-parts-attack', 'sources': source, 'tools': tools}
    key = hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
    return key, value


def inventory(root):
    return {str(p.relative_to(root)): digest(contained(root, p.relative_to(root)))
            for p in sorted(root.rglob('*')) if p.is_file() and p.name != 'pipeline-receipt.json'
            and 'logs' not in p.relative_to(root).parts and p.suffix != '.blend1'}


def gates(root):
    quality = read(root / 'quality-report.json')
    source = read(root / 'source-rig-check.json')
    contract = read(root / 'contract-check.json')
    browser = read(root / 'browser-qa.json')
    guide = read(root / 'pose-guides.json')
    mechanical = {
        'independent_visibility': quality['independent_full_scene_comparisons'] == 96 and all(
            quality[k] == 0 for k in ['total_differing_part_owner_pixels', 'total_differing_alpha_pixels', 'total_packed_depth_differing_pixels']),
        'canvas_and_trail_phases': not quality['canvas_edge_contacts'] and not quality['unexpected_trail_frames'],
        'actual_right_hand_source': source['reopened_editable_source'] and not source['manual_pose_assignment_in_check']
            and source['weapon_parent'] == 'right.hand' and len(source['baked_keys']) == 8
            and all(c['baked_grip_error_world'] < 1e-5 and c['hand_parent_error_world'] < 1e-5 for c in source['baked_keys']),
        'contracts_and_bad_fixtures': contract['baseline'] == 'PASS' and contract['strips_checked'] == 272
            and len(contract['negative_fixtures']) == 6 and all(c['rejected'] for c in contract['negative_fixtures']),
        'actual_browser': len(browser['checks']) >= 31 and all(c['pass'] for c in browser['checks']) and not browser['page_errors'],
        'projected_pose_guides': len(guide['poses']) == 64 and guide['checks']['right_grip_max_error_px'] < 1e-3
            and guide['checks']['bone_lengths_max_error_world'] < 1e-5,
    }
    blockers = []
    if quality['total_differing_source_pixels'] != 0:
        blockers.append('Exact-color reconstruction fails at ' + str(quality['total_differing_source_pixels']) + ' source pixels')
    blockers += ['Character art and animation have not been accepted',
                 'Walk/idle and remaining action families are not implemented by this adapter',
                 'Translucent trail shape/overlap is unapproved', 'Production game renderer integration is unverified']
    return {'mechanical': mechanical, 'review_ready': all(mechanical.values()), 'release_ready': False, 'release_blockers': blockers}


def verify(root):
    receipt = read(root / 'pipeline-receipt.json')
    if receipt.get('schema') != SCHEMA or receipt.get('status') != 'REVIEW_READY_RELEASE_BLOCKED':
        raise ValueError('Build has no completed review receipt')
    expected = receipt['artifacts']
    if inventory(root) != expected:
        raise ValueError('Artifact integrity failed: missing, changed or unexpected files; rebuild instead of trusting this cache')
    current_gates = gates(root)
    if current_gates != receipt['gates'] or not current_gates['review_ready']:
        raise ValueError('Mechanical gate report is inconsistent or failed')
    return receipt


def selected(root):
    pointer = read(root / 'current.json')
    target = contained(root, pointer['build'])
    if target.parent != root / 'builds':
        raise ValueError('Current pointer must identify one immutable build')
    receipt = verify(target)
    if receipt['fingerprint'] != pointer['fingerprint']:
        raise ValueError('Current pointer fingerprint mismatch')
    return target, receipt


def run_stage(root, label, command, env):
    print('stage: ' + label, flush=True)
    log = root / 'logs' / (label + '.log')
    log.parent.mkdir(exist_ok=True)
    with log.open('w') as stream:
        result = subprocess.run(command, env=env, cwd=SKILL, stdout=stream, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(label + ' failed (exit ' + str(result.returncode) + '); inspect ' + str(log))


def build(output, force=False):
    # Unchanged valid builds reuse receipts, never filename existence alone.
    tools = doctor()
    key, provenance = inputs(tools)
    output.mkdir(parents=True, exist_ok=True)
    with (output / '.build.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError('Another build holds this output lock') from exc
        if not force and (output / 'current.json').exists():
            try:
                old, receipt = selected(output)
                if receipt['fingerprint'] == key:
                    print(json.dumps({'cache': 'VERIFIED_HIT', 'build': str(old), 'gates': receipt['gates']}, indent=2))
                    return
            except (ValueError, OSError, KeyError) as exc:
                print('cache rejected: ' + str(exc), flush=True)
        (output / 'builds').mkdir(exist_ok=True)
        run = Path(tempfile.mkdtemp(prefix=key[:12] + '-', dir=output / 'builds'))
        started = time.monotonic()
        env = dict(os.environ, SPRITE_OUTPUT_ROOT=str(run), SPRITE_CHROMIUM=tools['chromium']['path'])
        for item in ADAPTER.glob('runtime/*'):
            shutil.copyfile(item, run / item.name)
        commands = [
            ('poses', [tools['node']['path'], str(ADAPTER / 'rig-poses.mjs')]),
            ('render-parts', [tools['blender']['path'], '-b', '--python-exit-code', '2', '--factory-startup', '-t', '4', '--python', str(ADAPTER / 'build-character.py'), '--', 'batch']),
            ('independent-references', [tools['blender']['path'], '-b', '--python-exit-code', '2', '-t', '4', '--python', str(ADAPTER / 'render-owner-checks.py')]),
            ('compose', [sys.executable, str(ADAPTER / 'compose-proof.py')]),
            ('source-check', [tools['blender']['path'], '-b', '--python-exit-code', '2', '-t', '4', '--python', str(ADAPTER / 'check-source.py')]),
            ('contracts', [tools['node']['path'], str(ADAPTER / 'validate-contract.mjs')]),
            ('pose-guides', [tools['blender']['path'], '-b', '--python-exit-code', '2', '-t', '4', '--python', str(ADAPTER / 'export-pose-guides.py')]),
            ('draw-guides', [sys.executable, str(ADAPTER / 'draw-guides.py')]),
            ('browser', [sys.executable, str(ADAPTER / 'browser-check.py'), '--offline']),
        ]
        try:
            for label, command in commands:
                run_stage(run, label, command, env)
            # A file edited while rendering invalidates the entire build.
            if inputs(tools)[0] != key:
                raise RuntimeError('Source changed during build; previous current build retained')
            result = gates(run)
            if not result['review_ready']:
                raise RuntimeError('Mechanical gates failed: ' + json.dumps(result['mechanical']))
            receipt = {'schema': SCHEMA, 'status': 'REVIEW_READY_RELEASE_BLOCKED', 'fingerprint': key,
                       'inputs': provenance, 'gates': result, 'seconds': round(time.monotonic() - started, 2), 'artifacts': inventory(run)}
            atomic_json(run / 'pipeline-receipt.json', receipt)
            verify(run)
            atomic_json(output / 'current.json', {'build': str(run.relative_to(output)), 'fingerprint': key, 'release_ready': False})
            print(json.dumps({'cache': 'CLEAN_BUILD', 'build': str(run), 'gates': result, 'seconds': receipt['seconds']}, indent=2))
        except BaseException as exc:
            atomic_json(run / 'pipeline-receipt.json', {'schema': SCHEMA, 'status': 'FAILED', 'error': str(exc), 'fingerprint': key})
            raise


def package(output, archive, mode):
    root, receipt = selected(output)
    if mode == 'release' and not receipt['gates']['release_ready']:
        raise ValueError('Release blocked: ' + '; '.join(receipt['gates']['release_blockers']))
    archive = archive.resolve()
    if archive.is_relative_to(root):
        raise ValueError('Archive must be outside its immutable source build')
    # Review contains editable source, guides, standalone runtime, proof GIFs and reports.
    # No raw EXRs, redundant per-part frames, caches or external reference artwork.
    files = [p for p in sorted(root.rglob('*')) if p.is_file() and (
        p.parent == root and p.suffix in {'.json', '.blend', '.mjs', '.html', '.gif', '.png', '.md'}
        or p.relative_to(root).parts[0] in {'strips', 'guides'} and p.suffix == '.png')]
    entries = {str(p.relative_to(root)): digest(contained(root, p.relative_to(root))) for p in files}
    note = {'schema': 'modular-sprite-review-package-v1', 'mode': mode, 'release_ready': False,
            'fingerprint': receipt['fingerprint'], 'gates': receipt['gates'], 'sha256': entries,
            'scope': 'Standalone review and editable source. Not a release. Full raw build inventory in pipeline-receipt.json is not included; regenerate to reproduce independent comparisons.'}
    archive.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='sprite-review-', suffix='.zip', dir=archive.parent)
    os.close(fd)
    try:
        with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
            for name in sorted(entries):
                item = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                item.compress_type = zipfile.ZIP_DEFLATED
                bundle.writestr(item, (root / name).read_bytes())
            item = zipfile.ZipInfo('package-manifest.json', (1980, 1, 1, 0, 0, 0))
            bundle.writestr(item, json.dumps(note, indent=2) + '\n')
        with zipfile.ZipFile(temporary) as bundle:
            if bundle.testzip() or any(hashlib.sha256(bundle.read(name)).hexdigest() != value for name, value in entries.items()):
                raise ValueError('Package integrity verification failed')
        os.replace(temporary, archive)
        print(json.dumps({'archive': str(archive), 'sha256': digest(archive), 'files': len(entries), 'release_ready': False}, indent=2))
    finally:
        Path(temporary).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor')
    for name in ['build', 'check', 'pack']:
        p = sub.add_parser(name)
        p.add_argument('--output', type=Path, required=True, help='Dedicated pipeline output directory, not the older v4 proof directory')
        if name == 'build':
            p.add_argument('--force', action='store_true')
        if name == 'pack':
            p.add_argument('--archive', type=Path, required=True)
            p.add_argument('--mode', choices=['review', 'release'], default='review')
    args = parser.parse_args()
    try:
        if args.command == 'doctor':
            print(json.dumps(doctor(), indent=2))
        elif args.command == 'build':
            build(args.output.resolve(), args.force)
        elif args.command == 'check':
            target, receipt = selected(args.output.resolve())
            print(json.dumps({'build': str(target), 'integrity': 'PASS', 'gates': receipt['gates']}, indent=2))
        else:
            package(args.output.resolve(), args.archive, args.mode)
    except (RuntimeError, ValueError, OSError, KeyError, subprocess.CalledProcessError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
