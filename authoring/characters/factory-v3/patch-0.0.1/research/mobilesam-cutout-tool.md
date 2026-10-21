# Optional mask proposal tool

MobileSAM: https://github.com/ChaoningZhang/MobileSAM, Apache-2.0.
Pinned source commit: f706ad9c4eb7f219c00d9050e46328518ffb65d2.
Checkpoint mobile_sam.pt SHA-256: 6dbb90523a35330fedd7f1d3dfc66f995213d81b29a5ca8108dbcdd4e37d6c2f.

Local checkout: /workspace/.tools/MobileSAM. Isolated environment: /workspace/.venvs/astraeon-cutouts. CPU torch 2.14.1+cpu, torchvision 0.29.1+cpu, numpy 2.5.2, Pillow 12.3.0, timm and opencv-python-headless. Checkpoint and environment are not vendored.

Run tools/character_factory_v3/refine_cutout_heads.py using this environment. Prompts use manually authored boxes, hair and skin positives, and scarf negatives. Original pixels are preserved; proposals only assign visible pixels to layers. Exact recomposition is a mechanical check, not semantic boundary approval. IoU prediction scores do not certify art quality. Current outputs require manual review of hair strands, ears, neck and scarf boundaries before import.
