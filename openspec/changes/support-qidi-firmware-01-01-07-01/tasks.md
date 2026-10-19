## 1. Live `.07.01` Evidence Capture

- [x] 1.1 After the operator updates the printer, run the mandatory idle-print guard and stop if the printer is printing, paused, or its state is unknown.
- [x] 1.2 Confirm `/home/qidi/update/firmware_manifest.json` reports SOC `01.01.07.01`.
- [x] 1.3 Copy `config/printer.cfg`, `config/box.cfg`, and any Box files it includes to a local scratch directory; redact hardware identifiers before recording anything in the repository.
- [x] 1.4 Record whether `.07.01` regenerated `box.cfg` and whether it still defines `[box_extras]`, `T{n}`, `UNLOAD_T{n}`, and `UNLOAD_FILAMENT`.
- [x] 1.5 Capture the registered command list and object list through Moonraker, and confirm whether `CUT_FILAMENT`, `UNLOAD_T{n}`, `EXTRUDER_LOAD`, `EXTRUDER_UNLOAD`, `T_MANAGER`, `UNLOAD_FILAMENT`, `UNLOAD_FILAMENT_CONTROL`, `TRY_RESUME_PRINT`, `INIT_RFID_READ`, and `CLEAR_FLUSH` are registered.
- [x] 1.6 Query `box_extras`, `box2base`, `box485`, and `multi_color_controller` status plus `box_count`, `enable_box`, and `value_t*` saved variables; identify which fields distinguish an attached Box on each transport from no Box.
- [x] 1.7 Review a small `klippy.log` startup tail for Box transport, config-merge, or duplicate-command errors.
- [x] 1.8 With operator approval, verify `TRY_RESUME_PRINT` external-spool behavior with the toolhead sensor empty and Box disabled. Operator decision 2026-10-19: assume `.07.01` `TRY_RESUME_PRINT` keeps the previous external-spool filament gate; not separately tested.
- [x] 1.9 With operator approval and the operator present, run a short two-color Box print on stock `.07.01` while tailing `klippy.log` to confirm `T_MANAGER` performs cut, unload, load, and wipe after `TOOL_CHANGE_START`, and that end-print `UNLOAD_FILAMENT T=` cuts and unloads; record any heater or wipe side effects.
  - Tool change confirmed 2026-10-19: one flow cut, unload, and load attempt; load failures were filament-quality `QDE_004_006` pauses. End-print `UNLOAD_FILAMENT` cut once and unloaded to the Box.
- [x] 1.10 Decide whether `.07.01` replaces stock `CUT_FILAMENT_1` (design option B): approved.

## 2. Firmware Baseline and Snapshot

- [x] 2.1 Build the `.07.01` stock snapshot under `installer/stock/qidi-max4-defaults/firmwares/01.01.07.01/config/` from the `qidi-max4-firmware-01.01.07.01-0cc97445…` tag, using existing translation and redaction conventions, keeping QIDI's comments as in earlier snapshots.
- [x] 2.2 Verify the snapshot excludes `MCU_ID.cfg`, `box.cfg`, `fluidd.cfg`, and `saved_variables.cfg`.
- [x] 2.3 Update `installer/stock/qidi-max4-defaults/README.md` with `.07.01` provenance and the bundle snapshot checks.
- [x] 2.4 Resynchronize `config/` to `.07.01`: stock content with LF line endings and stock whitespace, Chinese comments translated (reusing existing translations), previously translated macro descriptions and console text retained, upstream emails redacted, the optimized include retained, and `config/box.cfg` replaced with the redacted `.07.01`-generated two-Box file. `config/fluidd.cfg`, `config/MCU_ID.cfg`, and `config/saved_variables.cfg` are unchanged. The nine `bed_mesh.cfg` console strings are translated with operator approval; `config/` is a repository reference and is not shipped in the installer bundle.

## 3. Installer Manifest and Compatibility Metadata

- [x] 3.1 Add `01.01.07.01` to `installer/package.yaml firmware.supported` and extend every unchanged `set_options`, `homing_override`, and `_km_apply_print_offset` variant to it.
- [x] 3.2 Add `.07.01` delete-section variants for `filament_switch_sensor` (`4466d081…`) and `RESUME` (`866bc3a0…`).
- [x] 3.3 Add the `.07.01` `qidi_homing` variant using the `.06.05` preimage and sync-reset payload hashes.
- [x] 3.4 Extend `installer/supported_upgrade_sources.yaml` with `.07.01` source provenance.

## 4. Transport-Independent Box Detection

- [x] 4.1 Choose the Box-availability predicate from task 1.6 evidence (`box_extras` defined, or `multi_color_controller`/`box485` `box_count` above zero).
- [x] 4.2 Replace every `printer["box_extras"] is defined` and `printer["box_extras"]` use in `installer/klipper/tltg-optimized-macros/` with the predicate.
- [x] 4.3 Update `openspec/contracts/gcode-paths/start-print.path.json` and add a check that every optimized macro uses the same predicate.
- [x] 4.4 Update `installer/runtime/box_enablement.py` Box detection to accept a live `multi_color_controller` or `box485` `box_count` as well as `[box_extras]`.

## 5. Filament Cut, Runout, and Resume

- [x] 5.1 Port the `.07.01` `CUT_FILAMENT_1` sequence through the post-cut retract into `OPTIMIZED_CUT_FILAMENT`, keeping the optimized exit, state restore, and no final `G4 P2000`.
- [x] 5.2 Add guarded `CUT_FILAMENT_1` delete-section variants for every supported firmware, an optimized `CUT_FILAMENT_1` equal to newest stock without `G4 P2000`, the upgrade-envelope target, and removal from preflight required sections.
- [x] 5.3 Gate `OPTIMIZED_FILAMENT_SENSOR_RUNOUT` Box handling on `enable_box` and the shared predicate.
- [x] 5.4 Rewrite the optimized `RESUME` per the design's routing table, adjusting the external-spool row if task 1.8 shows `TRY_RESUME_PRINT` lacks the filament gate.

## 6. Unload and Slicer Filament Change

- [x] 6.1 Add `TOOLCHANGE=1` handling to `OPTIMIZED_CUT_FILAMENT`: skip the cut only when `T_MANAGER` is registered; manual calls and legacy firmware always cut.
- [x] 6.2 Pass `TOOLCHANGE=1` from `orcaslicer_gcode/change_filament.gcode` and `qidistudio_gcode/change_filament.gcode`, keeping `UNLOAD_T[current_extruder]` and `T[next_extruder]` for `.06.x` and for older installed macros.
- [x] 6.3 Route `OPTIMIZED_UNLOAD_FILAMENT` to `UNLOAD_FILAMENT T={T}` when `T_MANAGER` is registered, keeping retained-state clearing first, the legacy path unchanged, and optional optimized cleanup on both paths.
- [x] 6.4 Keep `scripts/check_optimized_slicer_macros.py` expectations valid and add a contract test for the shared slicer filament-change sequence.

## 7. Tests

- [x] 7.1 Extend installer fixture helpers with `.07.01` and run the firmware-cleanup recovery and drift tests on `.07.01`; the `.07.01` homing preimage and payload are identical to `.06.05`, so the source-patch matrix keeps its existing cases.
- [x] 7.2 Extend `test_optimized_macro_contract.py` for the cut sequence, resume routing, and absence of `box_extras` checks in optimized macros.
- [x] 7.3 Extend Box-enablement coverage for an RS-485-only Box configuration and a no-Box `.07.01` configuration.
- [x] 7.4 Require the `.07.01` snapshot root in bundle smoke validation.

## 8. Specifications, Observations, and Release

- [x] 8.1 Update `openspec/observations/qidi-platform.md` and `openspec/observations/qidi-box/` with qualified `.07.01` evidence: RS-485 topology, module split, `feed_move`/`unload_move` blocking and error codes, resume delegation, stock `T_MANAGER` macros, and new stock motion macros.
- [x] 8.2 Run `python3 scripts/bump_installer_version.py <version>` and add the matching `CHANGELOG.md` section.

## 9. Validation

- [x] 9.1 `python3 scripts/format_klipper_configs.py`
- [x] 9.2 `python3 scripts/check_installer_known_versions.py`
- [x] 9.3 `python3 scripts/check_optimized_slicer_macros.py`
- [x] 9.4 `python3 scripts/check_gcode_paths.py --write` then `python3 scripts/check_gcode_paths.py`
- [x] 9.5 `python3 scripts/run_installer_core_tests.py`
- [x] 9.6 `python3 scripts/build_installer_bundle.py --output-dir dist --channel dev --build-id local --smoke-test`
- [x] 9.7 `openspec validate support-qidi-firmware-01-01-07-01 --strict` and `openspec validate --all --strict`
- [ ] 9.8 On the printer: install, run a Box print with a filament change, an external-spool pause/resume with `TLTG_FILAMENT_SENSOR ENABLE=0` and `ENABLE=1`, and an end-print unload.
  - 2026-10-19: local dev bundle `26.10.19.1` installed with `--yes` on the `.07.01` printer; `homing.py`, guarded patches, `CUT_FILAMENT_1`, and the optimized tree verified active after a Klipper service restart. The first run left the service restart pending because printer state could not be verified; a second run verified the restart and cleared the marker. Live print checks remain. A follow-up print using the `TOOLCHANGE=1` pack (profile start G-code still echoes the stale `TLTG Slicer 26.09.09.1` string) cut once, by the vendor flow, at its first tool change, then paused on a load failure unrelated to the cut and was cancelled. Remaining: a complete multi-color print with end-print unload and staged cooldown, and external-spool pause/resume with `TLTG_FILAMENT_SENSOR`.
- [ ] 9.9 Review the diff for unredacted identifiers, excluded printer files, `config/fluidd.cfg` edits, and claims about compiled vendor behavior that lack evidence.
