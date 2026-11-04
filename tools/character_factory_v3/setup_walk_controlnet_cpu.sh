#!/usr/bin/env bash
# Ephemeral research setup; no writes to the repository or existing venv.
set -euo pipefail
astra_python=${ASTRA_PYTHON:-/workspace/.venvs/astraeon-cutouts/bin/python}
astra_root=${ASTRA_CONTROLNET_ROOT:-/tmp/astra-controlnet-replay}
if [ -e "$astra_root" ] || [ -L "$astra_root" ]; then printf '%s\n' 'Choose a fresh ASTRA_CONTROLNET_ROOT; existing data is not overwritten.' >&2; exit 1; fi
mkdir -p "$astra_root/py" "$astra_root/cache"
"$astra_python" -m pip install --no-cache-dir --no-deps --target "$astra_root/py" 'diffusers==0.36.0' 'transformers==4.57.3' 'accelerate==1.12.0' 'huggingface-hub==0.36.0' 'requests==2.32.5' 'regex==2025.11.3' 'tokenizers==0.22.1' 'tqdm==4.67.1' 'urllib3==2.5.0' 'idna==3.11' 'certifi==2025.11.12' 'charset-normalizer==3.4.4' 'httpx==0.28.1' 'httpcore==1.0.9' 'anyio==4.16.0' 'h11==0.16.0' 'typing_extensions==4.16.0'
HF_HUB_DISABLE_XET=1 HF_HOME="$astra_root/cache" PYTHONPATH="$astra_root/py" "$astra_python" - <<'PY'
import os
from huggingface_hub import snapshot_download
base_repo=os.environ.get('ASTRA_BASE_REPO','stable-diffusion-v1-5/stable-diffusion-v1-5')
base_revision=os.environ.get('ASTRA_BASE_REVISION','451f4fe16113bff5a5d2269ed5ad43b0592e9a14')
control_repo=os.environ.get('ASTRA_CONTROL_REPO','lllyasviel/control_v11p_sd15_canny')
control_revision=os.environ.get('ASTRA_CONTROL_REVISION','115a470d547982438f70198e353a921996e2e819')
items=[(base_repo,base_revision,['model_index.json','scheduler/*','tokenizer/*','text_encoder/config.json','text_encoder/model.fp16.safetensors','unet/config.json','unet/diffusion_pytorch_model.fp16.safetensors','vae/config.json','vae/diffusion_pytorch_model.fp16.safetensors']),(control_repo,control_revision,['config.json','diffusion_pytorch_model.fp16.safetensors'])]
for repo,revision,patterns in items:print(snapshot_download(repo,revision=revision,allow_patterns=patterns,max_workers=2),flush=True)
PY
printf 'Research setup: %s\n' "$astra_root"
