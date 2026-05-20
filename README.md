# Subgen (Qwen3-ASR Fork)

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/donate/?hosted_button_id=SU4QQP6LH5PF6)
<img src="https://raw.githubusercontent.com/McCloudS/subgen/main/icon.png" width="200">

This is a fork of [McCloudS/subgen](https://github.com/McCloudS/subgen) that replaces **faster-whisper** with **[Qwen3-ASR](https://github.com/QwenLM/Qwen3-ASR)** for multilingual speech recognition (ASR).

Qwen3-ASR supports 52 languages and dialects with state-of-the-art accuracy, including automatic language detection and optional timestamp prediction via its forced aligner model.

## Features

- **Multilingual ASR** — 30 spoken languages + 22 Chinese dialects
- **Language auto-detection** — Qwen3-ASR can automatically detect the spoken language
- **Timestamp prediction** — Optional forced aligner support for word-level timestamps
- **Integrations** — Bazarr (ASR provider), Plex, Emby, Jellyfin, Tautulli webhooks
- **Batch processing** — Recursively transcribe media folders
- **Docker support** — GPU (NVIDIA CUDA / AMD ROCm) and CPU images

## Models

| Model | Size | Description |
|-------|------|-------------|
| `Qwen/Qwen3-ASR-0.6B` | 0.6B | Fast, lightweight ASR model |
| `Qwen/Qwen3-ASR-1.7B` | 1.7B | Higher accuracy ASR model |
| `Qwen/Qwen3-ForcedAligner-0.6B` | 0.6B | Optional: word-level timestamps |

## Quick Start

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ASR_MODEL` | `Qwen/Qwen3-ASR-0.6B` | Qwen3-ASR model path (HuggingFace) |
| `FORCED_ALIGNER_MODEL` | (empty) | Enable timestamps: `Qwen/Qwen3-ForcedAligner-0.6B` |
| `USE_FORCED_ALIGNER` | `False` | Set to `True` to use the forced aligner |
| `TRANSCRIBE_DEVICE` | `cpu` | `cpu` or `cuda` |
| `TRANSCRIBE_OR_TRANSLATE` | `transcribe` | `transcribe` (translate not supported by Qwen3-ASR) |
| `WEBHOOK_PORT` | `9000` | HTTP server port |
| `CONCURRENT_TRANSCRIPTIONS` | `2` | Number of concurrent workers |
| `ASR_THREADS` | `4` | CPU thread count for inference |

> **Backward compatibility**: `WHISPER_MODEL` and `WHISPER_THREADS` are still supported as aliases for `ASR_MODEL` and `ASR_THREADS`.

### Docker (NVIDIA GPU)

```bash
docker run -d \
  --name=qwen3-subgen \
  --gpus all \
  -p 9000:9000 \
  -v /path/to/media:/media \
  -e ASR_MODEL=Qwen/Qwen3-ASR-0.6B \
  -e TRANSCRIBE_DEVICE=cuda \
  -e TRANSCRIBE_FOLDERS=/media \
  mccloud/subgen:latest
```

### Docker (CPU only)

```bash
docker run -d \
  --name=qwen3-subgen \
  -p 9000:9000 \
  -v /path/to/media:/media \
  -e ASR_MODEL=Qwen/Qwen3-ASR-0.6B \
  -e TRANSCRIBE_DEVICE=cpu \
  -e TRANSCRIBE_FOLDERS=/media \
  mccloud/subgen:cpu
```

### Local Installation

```bash
pip install -r requirements.txt
python launcher.py
```

## Bazarr Integration

Add Subgen as a custom Whisper provider in Bazarr:

1. Go to Bazarr Settings → Subtitles → Whisper
2. Set "Whisper Provider" to `http://subgen:9000/asr`
3. Configure language detection settings as needed

## Differences from upstream Subgen

- **Engine**: Qwen3-ASR replaces faster-whisper + stable-ts
- **No translation**: Qwen3-ASR only supports transcription, not translation to English
- **No `regroup`**: The stable-ts regrouping feature is not available
- **No `compute_type`**: Qwen3-ASR uses standard PyTorch dtypes (bfloat16/float32)
- **No progress callback**: Real-time progress percentage is not available with Qwen3-ASR

## License

MIT — same as the upstream project. Qwen3-ASR models are under Apache 2.0.
