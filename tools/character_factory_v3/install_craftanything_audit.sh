#!/usr/bin/env bash
set -euo pipefail
astra_craft_root="${1:-/tmp/astra-craftanything-audit-v030}"
if [ -e "$astra_craft_root" ]; then
  echo 'Choose a fresh install directory.' >&2
  exit 1
fi
mkdir -p "$astra_craft_root"
curl -fL --retry 2 https://github.com/storytold/craft-anything/releases/download/v0.3.0/craft-anything-0.3.0-linux-x86_64.tar.gz -o "$astra_craft_root/package.tar.gz"
python - "$astra_craft_root/package.tar.gz" <<'PY'
import hashlib,sys
from pathlib import Path
p=Path(sys.argv[1])
assert hashlib.sha256(p.read_bytes()).hexdigest()=='674ec59ffbdaefbd577917e07c9d464562043b275a3889ba4f60239a12f03d53', 'Archive SHA-256 mismatch'
PY
tar -xzf "$astra_craft_root/package.tar.gz" -C "$astra_craft_root" craft-anything-0.3.0-linux-x86_64/bin/craft-anything-cli
python - "$astra_craft_root/craft-anything-0.3.0-linux-x86_64/bin/craft-anything-cli" <<'PY'
import hashlib,sys
from pathlib import Path
p=Path(sys.argv[1])
assert hashlib.sha256(p.read_bytes()).hexdigest()=='4db1afe78c0365f1192de776edf3a66a3e5c26fdc78f4b9d63128bf3d6d609eb', 'CLI SHA-256 mismatch'
print(p)
PY
