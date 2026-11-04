# Craft Anything pilot: Walk pixel audit and browser preview

Craft Anything **0.3.0** was installed from its official Linux x86_64 release into a temporary directory. Archive SHA-256 `674ec59ffbdaefbd577917e07c9d464562043b275a3889ba4f60239a12f03d53` matches the release's SHA256SUMS; CLI SHA-256 `4db1afe78c0365f1192de776edf3a66a3e5c26fdc78f4b9d63128bf3d6d609eb`. Source: https://github.com/storytold/craft-anything/releases/tag/v0.3.0 (MIT OR Apache-2.0). No binaries are committed. No external image generation or AI backend was configured. CLI inspection and its MCP self-test work; this session uses the CLI without changing global Codex registrations.

## Actual findings

1. The pixel comparison audited all sixteen original/revised Walk frames: thirteen unchanged; frames 02/03/04 changed by 7,835 / 7,100 / 7,069 pixels. See [summary](summary.json). A separate identical-image check returns zero differences, and a synthetic 1px translation returns exactly twenty changed pixels, [control](positive-control.json). These prove pixel comparison operation and edit scope, not anatomy or animation acceptance.
2. A real headless Chromium walkthrough loaded the existing local `sprite-preview.html` and selected paused playback. Both scripted steps succeeded, yet the page requested `/assets/characters/swordsman-proof/sprite.json?spriteDev=1` with HTTP **404**, leaving the preview blank. The favicon also returned 404, which is unrelated to character loading. See [browser screenshot](browser.png) and [network/console/DOM evidence](browser-evidence.json). This finding applies to this local checkout and this development preview, not every game entry point or the latest remote checkout.
3. Craft Anything can supply an independent pixel comparator and browser evidence. It has not demonstrated a sprite-painting or temporal-anatomy evaluator, nor fixed the missing asset. Passing step statuses must be checked alongside asset requests and rendered output.

## Replay

From repository root, choose fresh temporary directories:

```sh
bash tools/character_factory_v3/install_craftanything_audit.sh /tmp/astra-craft-audit
python tools/character_factory_v3/audit_walk_with_craftanything.py \
  --cli /tmp/astra-craft-audit/craft-anything-0.3.0-linux-x86_64/bin/craft-anything-cli \
  --output /tmp/astra-craft-walk-results
```

The installer was run from an empty directory and passed both pinned checksum checks. The committed runner was executed across all sixteen frames. It retains raw per-frame evidence and input PNGs in the chosen output, without altering artwork. The `summary.json` here is from the committed runner replay. The binary and installation are temporary; rerun the installer in a new workspace.

For the browser pilot, serve the repository on loopback port 8769, then run the saved [walkthrough parameters](walkthrough.json) with `web-walkthrough-record`, `--deep --allow-run --project <temporary .cany path>`. The scope is our own local preview. Browser evidence includes the screenshot metadata and its separately saved PNG; base64 image data was removed from the JSON to avoid duplication. The capture ran Chromium 151.0.7922.173 at 1280x720. No gameplay encounter, latest painted Walk playback, asset swaps or all-class acceptance was tested. The server was stopped afterward.

Coverage remains **2/96 technical imports, 0/6 completed characters**. This is tooling validation, not a new completed character action.
