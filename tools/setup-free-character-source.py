"""Fetch a pinned MPFB source release into a workspace-local tool cache.

No global Blender preferences or provider credentials are changed.
"""
from pathlib import Path
import hashlib
import json
import zipfile
import requests

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / '.character-tools' / 'mpfb-2.0.17'
URL = 'https://codeload.github.com/makehumancommunity/mpfb2/zip/refs/tags/v2.0.17'
EXPECTED_SHA256 = 'd08e726c798fdc4eefb02b06b6c4efe37d40b5439777e53cf96dce0e5073297d'
DEST.mkdir(parents=True, exist_ok=True)
archive = DEST / 'release.zip'
if not archive.exists():
    response = requests.get(URL, timeout=60)
    response.raise_for_status()
    if hashlib.sha256(response.content).hexdigest() != EXPECTED_SHA256:
        raise ValueError('Pinned release archive changed; inspect upstream before using')
    archive.write_bytes(response.content)
if hashlib.sha256(archive.read_bytes()).hexdigest() != EXPECTED_SHA256:
    raise ValueError('Local MPFB archive does not match pinned checksum')
with zipfile.ZipFile(archive) as bundle:
    for entry in bundle.infolist():
        target = (DEST / entry.filename).resolve()
        if not target.is_relative_to(DEST.resolve()):
            raise ValueError('Archive path escapes dedicated cache')
    bundle.extractall(DEST)
receipt = {
    'tool': 'MPFB', 'version': '2.0.17', 'url': URL,
    'archiveBytes': archive.stat().st_size,
    'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
    'installScope': 'Workspace-local source; loaded only by authoring scripts',
    'codeLicense': 'GPL-3.0-or-later',
    'coreAssetsLicense': 'CC0-1.0',
    'licenseReference': 'https://github.com/makehumancommunity/mpfb2/blob/v2.0.17/LICENSE.md',
}
(DEST / 'download-receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(json.dumps(receipt, indent=2))
