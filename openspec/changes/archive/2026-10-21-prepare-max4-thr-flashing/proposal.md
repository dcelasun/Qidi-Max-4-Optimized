# Proposal

## Why

The patched Max 4 THR image needs a component-only installation path with a stock recovery image and flash readback. A full vendor update also replaces unrelated firmware and printer configuration.

## What Changes

- Add a restricted THR snapshot, bootloader-probe, and image-transfer tool using the recovered Max 4 serial protocol.
- Admit only known stock/patched images and the observed bootloader; require explicit write confirmation and stopped serial-owning services.
- Check complete transfers and recovery behavior against the captured bootloader in bounded emulation, and document the remaining hardware-validation boundary.

## Capabilities

### New Capabilities

- `thr-firmware-transfer`: guarded THR-only backup, serial transfer, and installation verification.

### Modified Capabilities

None.

## Impact

Standalone scripts and firmware documentation only. No macro-installer integration, other-board flashing, configuration replacement, or automatic publication.
