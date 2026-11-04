#!/usr/bin/env bash
# Creates and cleans only its own fresh temporary cache; no existing data touched.
set -euo pipefail
astra_python=${ASTRA_PYTHON:-/workspace/.venvs/astraeon-cutouts/bin/python}
astra_packages=${ASTRA_CONTROLNET_PY:-/tmp/astra-controlnet-py}
astra_root=${ASTRA_IP_ROOT:-/dev/shm/astra-ipadapter-replay}
if [ -e "$astra_root" ] || [ -L "$astra_root" ]; then printf '%s\n' 'Choose a fresh ASTRA_IP_ROOT; existing data is not overwritten.' >&2; exit 1; fi
mkdir -p "$astra_root/cache" "$astra_root/models/image_encoder"
HF_HUB_DISABLE_XET=1 HF_HOME="$astra_root/cache" PYTHONPATH="$astra_packages" "$astra_python" - <<'PY'
from huggingface_hub import snapshot_download
print(snapshot_download('h94/IP-Adapter',revision='018e402774aeeddd60609b4ecdb7e298259dc729',allow_patterns=['models/image_encoder/config.json','models/image_encoder/model.safetensors','models/ip-adapter_sd15.safetensors'],max_workers=2),flush=True)
PY
astra_source="$astra_root/cache/hub/models--h94--IP-Adapter/snapshots/018e402774aeeddd60609b4ecdb7e298259dc729/models"
printf '%s  %s\n' '6ca9667da1ca9e0b0f75e46bb030f7e011f44f86cbfb8d5a36590fcd7507b030' "$astra_source/image_encoder/model.safetensors" | sha256sum --check --status
cp "$astra_source/image_encoder/config.json" "$astra_root/models/image_encoder/config.json"
cp "$astra_source/ip-adapter_sd15.safetensors" "$astra_root/models/ip-adapter_sd15.safetensors"
"$astra_python" "$(dirname "$0")/convert_safetensors_fp32_to_fp16.py" "$astra_source/image_encoder/model.safetensors" "$astra_root/models/image_encoder/model.safetensors"
printf '%s  %s\n' '6914c90a48f1fa3c2c415ccf3361a38bfcbd9cbd0c15f39f1dbbafb3b4da598d' "$astra_root/models/image_encoder/model.safetensors" | sha256sum --check --status
# Only the cache created inside this fresh root is removed, after validation.
"$astra_python" - "$astra_root/cache" <<'PY'
import shutil,sys
shutil.rmtree(sys.argv[1])
PY
printf 'Research adapter: %s\n' "$astra_root"
