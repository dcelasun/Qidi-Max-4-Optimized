# Max 4 THR FIFO fix

`max4-thr-lis2dw-fifo-v1` patches the LIS2DW FIFO-empty decision in the Max 4 THR `02.02.01.08` image shipped with QIDI firmware `01.01.07.01`. It applies the behavior of [upstream Klipper fix `6269dda56b`](https://github.com/Klipper3d/klipper/commit/6269dda56bb7c08263153b18715d08e2d964bcab), without the separate FIFO batching change.

The generator changes five THR image bytes at two instruction sites. Every other component payload, the firmware manifest, internal filenames, and vendor version strings stay unchanged. The ZIP container is repacked. Supported input and output image hashes are recorded in [`max4-thr-lis2dw-fifo-v1.json`](max4-thr-lis2dw-fifo-v1.json).

## Generate the package

Use Python 3.11 or newer on a development computer. Download the exact [Max 4 release archive](https://github.com/thelegendtubaguy/Qidi-Max4-Defaults/releases/tag/qidi-max4-firmware-01.01.07.01-0cc97445e77295116adaa665ff463e77608d4929520bd7cd46e732fbb0a6ecf2), then run from the repository root:

```bash
python3 scripts/build_thr_firmware.py \
  --stock-archive QD_MAX4_01.01.07.01_20261016_Release.zip \
  --output-dir dist/max4-thr-fifo-v1
```

The output directory must not exist. The generator rejects unknown, modified, and already-patched archives. It leaves the original archive untouched and creates:

- `QD_MAX4_01.01.07.01_20261016_TLTG_THR_FIFO_v1.zip`: the complete vendor package with the patched THR payload.
- `QD_MAX4_THR_02.02.01.08_20260303_TLTG_FIFO_v1.bin`: the same patched THR image on its own.
- `max4-thr-lis2dw-fifo-v1.report.json`: input provenance, instruction replacements, and output hashes.
- A `.sha256` sidecar for each artifact.

The patched THR SHA-256 is `9d2360ba47ebd720dbef07a0a4ebaf26004360bca090997d7b4a118c41460ac9`.

## Verify the package

Install the checking dependencies into a virtual environment:

```bash
python3 -m venv .venv-thr
.venv-thr/bin/python -m pip install -r firmware/check-requirements.txt
.venv-thr/bin/python scripts/check_thr_firmware.py \
  --stock-archive QD_MAX4_01.01.07.01_20261016_Release.zip \
  --patched-dir dist/max4-thr-fifo-v1
```

The checker compares every archive payload and the THR protocol dictionary, verifies artifact checksums and provenance, tests rejection boundaries, and emulates the stock and patched FIFO-query instructions across every FIFO status byte and two reporting-buffer states. SPI transfers, host reporting, and timer registration are stubbed; this does not measure live sampling rate or validate the printer's other firmware paths.

## Before flashing

Generation and checking do not contact or flash a printer. The optimized-macro installer offers a default-No interactive THR firmware question and an explicit `--flash-thr-fifo` option. It checks actual application bytes and skips programming when the fix is already installed. `--yes` alone and automatic updates do not authorize firmware programming.

The package retains QIDI's version strings and does not force a same-version THR reflash. A completed touchscreen update is not proof that the patched THR was flashed. These build checks do not establish installation or physical recovery. See [THR-only operations](FLASHING.md) for the restricted tool, readback verification, and required recovery-entry validation.

The ZIP is a **full QIDI update**, including the unchanged SOC and other MCU components. Installing it can replace printer configuration and remove optimized macros, as a stock update does. Keep the original archive for recovery and back up printer configuration before any firmware installation. Use the standalone image only with a verified Max 4 THR flashing and recovery procedure.
