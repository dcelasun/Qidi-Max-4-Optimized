# Tasks

## 1. Installer firmware boundary

- [x] 1.1 Add the default-No interactive question, install-only CLI opt-in, and pending-operation admission; verify default/yes/automatic-mode rejection, calibration warnings, and dry-run behavior with CLI coverage.
- [x] 1.2 Implement guarded THR backup, patch generation, transfer, verification, and service restoration; cover known stock, already-patched, unsafe admission, interruption, and failed readback in lifecycle tests.

## 2. Release and operator interface

- [x] 2.1 Package the shared protocol tool, generator, manifest, and recovery instructions; document opt-in, required input shaper recalibration, and non-rollback behavior, and verify the extracted bundle interface in smoke coverage.
- [x] 2.2 Advance the package version and matching changelog; validate compatibility metadata and all changed installer/firmware paths with the core suite, firmware checkers, bundle smoke test, strict OpenSpec validation, and whitespace checks.
