# Tasks

## 1. Evidence and recovery boundary

- [x] 1.1 Read the installed THR application and bootloader without writes; verify the application against the pinned stock SHA-256 and preserve local backups.
- [x] 1.2 Record the recovered update protocol and recovery limits with source hashes; validate full stock/patched transfers and interruption behavior against the captured bootloader in bounded emulation.

## 2. Restricted operator tooling

- [x] 2.1 Implement snapshot, non-erasing probe, confirmed transfer, and readback verification with fail-closed admission; run offline protocol and rejection checks against both admitted images.
- [x] 2.2 Document service ownership, active-print/heater checks, backup preservation, transfer/readback, and recovery; exercise documented non-writing commands on the idle printer.

## 3. Hardware readiness

- [x] 3.1 Confirm restored printer readiness, a non-erasing live bootloader handshake, and application return without changed flash bytes.
- [ ] 3.2 Establish a board-specific recovery-entry procedure and audit all prerequisites before claiming flashing readiness; retain any unverified recovery dependency as a blocker.
