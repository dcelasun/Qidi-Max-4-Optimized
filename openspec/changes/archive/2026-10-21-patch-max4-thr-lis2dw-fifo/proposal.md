# Proposal

## Why

The Max 4 firmware `01.01.07.01` THR image contains an inverted LIS2DW FIFO-empty test. Correcting that test allows queued accelerometer samples to be drained without waiting for the next polling interval.

## What Changes

- Add a hash-locked generator that patches only the released Max 4 THR image and repacks the vendor ZIP.
- Produce a separately named package, standalone patched THR image, checksums, and provenance report without changing vendor version identities.
- Verify the exact byte delta, preservation of other components, and FIFO/scheduler decisions through bounded ARM instruction emulation.
- Document package generation and its limits; do not flash, publish, or integrate MCU flashing into the macro installer.

## Capabilities

### New Capabilities

- `firmware-artifacts`: guarded generation and verification of community-patched Max 4 firmware packages.

### Modified Capabilities

None.

## Impact

New firmware metadata and documentation under `firmware/`, local build/check scripts, and a firmware-specific CI check. Existing installer bundles, stock configuration, macros, and slicer G-code are unchanged.
