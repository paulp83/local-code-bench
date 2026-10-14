# Rig report 2026-10-03

Hardware: 2x consumer 32 GB cards. Same prompt set for every config.

## Config `tp2-fp8`

Measured: decode 108.5 tok/s, prefill 5,837 tok/s. Peak VRAM was 29,777 MiB per card.

## Config `tp2-awq`

Measured: decode 88.8 tok/s, prefill 8,803 tok/s. Peak VRAM was 21,520 MiB per card.

## Config `single-q4`

Measured: decode 88.2 tok/s, prefill 9,574 tok/s. Peak VRAM was 27,875 MiB per card.

## Config `pp2-q6`

Decode ran at 91.7 tok/s (median of 5). Prefill was 7,460 tok/s. Peak VRAM 23.7 GiB per card.

## Config `offload-q8`

Loaded fine, then died on the first long prompt: CUDA out of memory. No numbers.

## Corrections

The first `tp2-awq` decode run overlapped with a log rotation job. Re-run result: decode 84.5 tok/s. Use this and drop the earlier figure. Prefill and VRAM from the first run stand.
