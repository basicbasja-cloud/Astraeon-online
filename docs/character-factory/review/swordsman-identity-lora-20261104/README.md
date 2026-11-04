# Protected-art identity LoRA study

**Research adapter, not approved character artwork.** A rank-8 UNet attention LoRA was trained locally on CPU for 96 steps using sixteen actual original Swordsman BasicAttack master images (four real diagonal views × indices 0/4/8/15). Every dataset hash matches the protected baseline. One fixed 384×384 crop is applied to all training images; there is no mirroring or independent per-image fitting. This training crop is not an authoring/runtime scale or newly painted detail.

Base: `Lykon/dreamshaper-8` revision `a7e52b98680b1ba8ff7bce97c7f9f2e2e5337917`, CreativeML OpenRAIL-M. [Adapter, study metadata, logs, license and modification notice](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-identity-lora-20261104/). Only the 6.2MB adapter is distributed, not the base model. Its modification notice and upstream license/model card remain alongside it.

Training completed in 1,019.12 seconds on the available CPU. All 1,594,368 trainable values are finite. Loss and gradient norm were finite in all 96 steps. A separate initial three-step run and the full run produced exactly the same first-three loss/gradient values. The full 96-step run has not been rerun for identical final weights; optimization metrics do not establish image quality or geometry.

All four held-out Walk A/B keys (00/03/08/15) were captured with matched input, seed and control. The adapter changes the result, but the painted chest, hands, face and armor remain inconsistent with the protected design. **The outputs are rejected for production.**

A longer costume caption was found to exceed CLIP's 77-token context, silently dropping intended constraints. That trial is retained as a failed diagnostic. The new caption contract rejects truncation before model loading. The corrected cloth caption uses 59 tokens and its negative caption 46. Corrected DreamShaper and a compatible Anything V5 base still alter costume/body details; neither is accepted. The adapter was trained on DreamShaper; transfer to Anything V5 is an experiment, not an approved interchangeable base. No further sparse model trials are scheduled from these results.

[All captured outputs and receipts](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-identity-lora-20261104/held-out/) remain available. Anything V5 is pinned to `stablediffusionapi/anything-v5` revision `095f2abb647d239d7988e34ea236d20153f11573`; its original safetensors were SHA-verified and converted to temporary fp16 files without pickle. The setup receipt records both hashes. A different public model returned HTTP 401 and was not used. The helper never changes credentials or bypasses access controls.

## Replay

Use the existing pinned ControlNet CPU setup, selecting DreamShaper 8 and the OpenPose control. This environment used torch 2.14.1+cpu, diffusers 0.36.0, transformers 4.57.3, accelerate 1.12.0 and PEFT 0.17.1; Pillow/NumPy come from the existing cutout environment. No paid service or external generation account was used. Adapt the Python/model paths to the temporary installation; the exact executed training command was:

```sh
PYTHONPATH=/tmp/astra-controlnet-py /workspace/.venvs/astraeon-cutouts/bin/python \
  tools/character_factory_v3/train_swordsman_identity_lora.py \
  --base /tmp/astra-controlnet-cache/hub/models--Lykon--dreamshaper-8/snapshots/a7e52b98680b1ba8ff7bce97c7f9f2e2e5337917 \
  --output /tmp/astra-swordsman-lora-096 --steps 96 --save-every 32
```

Choose a fresh output. The optional `--resume` argument is a weights-only warm start; it resets optimizer and random-generator state and is not exact training resumption. No warm start was used in the recorded 96-step run.

The evaluation script pairs identical input/guide/seed/strength settings with and without this adapter at Walk frames 00,03,08,15. This motion was not a training source, but the initial draft already carries the character design, so the experiment is not an unconditional identity benchmark. No art source, cutout or runtime file is overwritten. Coverage remains 2/96 technical imports and 0/6 completed characters.
