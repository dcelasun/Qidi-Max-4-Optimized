# Proposal

## Why

The verified Max 4 THR FIFO fix needs an installer entrypoint that preserves the normal configuration lifecycle. Firmware programming must remain a separate, explicitly selected operation rather than a default or unattended update action.

## What Changes

- Ask interactive installers whether to flash THR, defaulting to No; retain an install-only `--flash-thr-fifo` option for explicit CLI authorization. `--yes` alone never accesses THR firmware.
- Gate the operation to the supported Max 4 release and exact application/bootloader hashes, preserve stock recovery files, and verify complete readback.
- Keep interrupted or unverified firmware work blocked separately from a committed configuration installation.
- Package the existing restricted protocol tool and patch manifest, with operator documentation and lifecycle coverage.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `installer-lifecycle`: explicit, non-persistent THR firmware opt-in and recoverable firmware-operation boundaries.

## Impact

Installer CLI/runtime, release bundle allowlist, firmware tooling, operator documentation, tests, and package version/changelog. No default firmware access, automatic firmware updates, other-board programming, configuration rollback of MCU firmware, or additional live printer flashing during implementation.
