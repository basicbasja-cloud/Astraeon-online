"""Fetch only Quaternius's explicitly free Standard packs; receipt and safe extraction.

Uses the creator's zero-price itch.io download flow. No account, checkout, paid
tier, uploaded character, or archive-supplied program is involved.
"""
import hashlib, html, http.cookiejar, json, re, urllib.parse, urllib.request, zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / '.character-tools/free-assets/quaternius-motions'
DEST.mkdir(parents=True, exist_ok=True)
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
records = []
for name in ['universal-animation-library', 'universal-animation-library-2']:
    url = 'https://quaternius.itch.io/' + name
    page = opener.open(url, timeout=30).read().decode()
    assert 'CC0 License' in page and 'Standard' in page
    csrf = html.unescape(re.search(r'<meta name="csrf_token" value="([^"]+)"', page)[1])
    req = urllib.request.Request(url + '/download_url', data=urllib.parse.urlencode({'csrf_token': csrf}).encode())
    free_url = json.loads(opener.open(req, timeout=30).read())['url']
    downloads = opener.open(free_url, timeout=30).read().decode()
    # Free-download pages expose a download button only for the unlocked tier.
    candidates = re.findall(r'data-upload_id="(\d+)"', downloads)
    assert len(candidates) == 1, 'Ambiguous free upload; inspect the creator download page.'
    upload_id = candidates[0]
    req = urllib.request.Request(url + '/file/' + upload_id + '?source=game_download&as_props=1', data=b'')
    asset_url = json.loads(opener.open(req, timeout=30).read())['url']
    archive = DEST / (name + '-standard.zip')
    if not archive.exists():
        archive.write_bytes(opener.open(asset_url, timeout=60).read())
    extracted = DEST / name
    with zipfile.ZipFile(archive) as z:
        for entry in z.infolist():
            target = (extracted / entry.filename).resolve()
            assert target.is_relative_to(extracted.resolve()), 'Archive traversal'
            if entry.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(z.read(entry))
    record = {'creator': 'Quaternius', 'sourceURL': url, 'tier': 'Standard', 'pricePaid': 0,
              'license': 'CC0-1.0', 'licenseURL': 'https://creativecommons.org/publicdomain/zero/1.0/',
              'retrievedAt': datetime.now(timezone.utc).isoformat(), 'uploadId': upload_id,
              'archive': str(archive.relative_to(ROOT)), 'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
              'files': [{'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                        for p in sorted(extracted.rglob('*')) if p.is_file()]}
    records.append(record)
    print('FREE_MOTION_DOWNLOADED ' + json.dumps({'pack': name, 'bytes': archive.stat().st_size,
                                               'files': len(record['files']), 'sha256': record['sha256']}), flush=True)
out = ROOT / 'authoring/characters/swordsman-production/fantasy-base-01/factory/free-motion-sources.json'
out.write_text(json.dumps({'packs': records, 'scope': 'Animation donor data only; supplied fantasy geometry is retained.'}, indent=2)+'\n')
