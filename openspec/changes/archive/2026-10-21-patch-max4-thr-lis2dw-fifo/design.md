# Design

## Context

The input is the hash-pinned Max 4 `01.01.07.01` release ZIP. Its THR `02.02.01.08` image contains the LIS2DW sample-count mask and inverted decision at file offsets `0x0bca` and `0x0bfe`. The image loads at `0x08008000`. The compiler also reuses the zero sample count when writing the scheduler's requested state.

## Goals / Non-Goals

**Goals:** preserve all vendor component payloads except the minimal THR fix, fail closed on unknown input, and make generated artifacts independently checkable.

**Non-Goals:** source rebuilding, batching changes, firmware-version changes, flashing, publishing, and installer integration.

## Decisions

- Keep exact archive/image hashes and instruction replacements in a versioned JSON manifest. Whole-input hashes prohibit applying offsets to a different image; preimage and output hashes guard the patch itself. Pattern scanning or force overrides would weaken that boundary.
- Change `bne.w` to `beq.w` at `0x0bfe`. Replace the following `strb.w r9, [r3, #8]` at `0x0c04` with `movs r2, #0; strb r2, [r3, #8]`. The corrected nonempty path has a nonzero `r9`, so branch inversion alone would corrupt the scheduler state. Five image bytes change, with no relocation or dictionary modification.
- Repack the ZIP using the original member order, names, metadata, and uncompressed payloads. Compression and container offsets can change. Keep the firmware manifest and internal component names byte-identical; distinguish community artifacts by external names and a sidecar report.
- Generate artifacts outside the installer bundle into a new output directory. Preserve the original archive and refuse existing output destinations. Keep compiler/emulator dependencies out of the generator; instruction validation uses separately pinned checking dependencies.
- Execute the actual stock and patched FIFO-query blocks in an ARM emulator with SPI, reporting, and timer-registration calls stubbed. Exercise every FIFO status byte with both a partial and a full reporting buffer. Verify wake versus timer rearm, scheduler state, sample copying, overflow counting, and reporting. This is bounded instruction evidence, not printer-runtime validation.

## Risks / Trade-offs

- A full vendor ZIP also contains the SOC and other firmware components → documentation identifies these contents and warns that a full update can reset optimized configuration.
- Unchanged vendor version strings do not force same-version reflashing → do not claim the touchscreen will install the patched THR or alter its policy.
- Static/emulated correctness does not establish live sampling rate or flash recovery → report that on-printer validation has not occurred; no automatic flashing or publication.
- Vendor payloads are not vendored into Git → build from the pinned release archive and retain its provenance in generated sidecars.
