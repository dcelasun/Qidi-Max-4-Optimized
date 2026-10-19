## 1. Implementation

- [x] 1.1 Add `_OPTIMIZED_CHUTE_DROP` and `OPTIMIZED_WIPE_NOZZLE_DROP` to the optimized filament macros.
- [x] 1.2 Replace every optimized wipe-plus-`CLEAR_FLUSH` pair, keeping wipe patterns, stages, and guards.
- [x] 1.3 Update the start-print contract, regenerate its views, and update macro integration coverage, including a check that optimized macros and slicer packs never call `CLEAR_FLUSH` or `CLEAR_OOZE`.
- [x] 1.4 Record `.07.01` chute-cleanup evidence in the QIDI Box observations.
- [x] 1.5 Bump the package version and add release notes.

## 2. Verification

- [ ] 2.1 Install on the printer and confirm a fresh Box start, a retained-filament start, and an end-print cleanup each wipe, leave the chute, and re-enter it with waste released.
