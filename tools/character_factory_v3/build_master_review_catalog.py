"""Index the isolated whole-master Walk review without changing runtime admission."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'authoring/characters/factory-v3/patch-0.0.1'


def build():
    guide = BASE / 'guides/4e519e1eadc69aaf28a2'
    output = BASE / 'painted-candidates/swordsman-walk-sw-color-guide-20261104/review'
    receipt = json.loads((output / 'receipt.json').read_text())
    source = json.loads((guide / 'manifest.json').read_text())
    if 'native GLB' not in receipt['timing_basis'] or len(receipt['frames']) != 16:
        raise ValueError('Complete native-timed review required')
    def path(p):
        if not p.is_file():
            raise ValueError('Missing real review asset: ' + str(p))
        return '../' + p.relative_to(ROOT).as_posix()
    result = {'status': 'WHOLE_MASTER_CANDIDATE_NOT_RUNTIME_ADMITTED',
              'frames': [path(output / 'masters' / f'{i:03}.png') for i in range(16)],
              'guides': [path(guide / 'SW' / f'{i:03}.png') for i in range(16)],
              'source_frames': [f['source_frame'] for f in source['views']['SW']['frames']],
              'durations_ms': [receipt['review_frame_ms']] * 16,
              'source_duration_ms': receipt['review_frame_ms'] * 16,
              'downloads': {k: path(output / v) for k, v in
                            {'normal': 'normal.gif', 'slow': 'slow.gif', 'receipt': 'receipt.json'}.items()},
              'reference': path(BASE / 'research/swordsman-walk-ip-baseline-reference-20261104/reference.png')}
    (ROOT / 'proof/swordsman-master-review.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    build()
