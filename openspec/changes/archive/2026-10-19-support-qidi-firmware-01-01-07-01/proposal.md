## Why

QIDI Max 4 firmware `01.01.07.01` replaces the QIDI Box control stack with an RS-485 transport (`[box485]`, `[box2base]`) and a rewritten `multi_color_controller`, moves Box commands out of `box_extras`, adds stock `T0`–`T15` macros routed through `T_MANAGER`, delegates every resume to `TRY_RESUME_PRINT`, and changes the stock filament-cut motion for reliability. The installer rejects `.07.01`, and optimized macros still detect the Box through `printer["box_extras"]`, call commands whose `.07.01` registration is unconfirmed, and carry the superseded cut sequence.

## What Changes

- Admit firmware `01.01.07.01` while retaining `.06.03`, `.06.04`, and `.06.05` support.
- Extend unchanged guarded configuration targets to `.07.01`; add new `.07.01` stock variants for the changed `[filament_switch_sensor filament_switch_sensor]` and `[gcode_macro RESUME]` sections.
- Add the `.07.01` `homing.py` source variant; the stock preimage is unchanged from `.06.05`.
- Add a sanitized `.07.01` stock snapshot from the `Qidi-Max4-Defaults` firmware tag.
- Resynchronize the stock-mapped `config/` tree to `.07.01`, translating Chinese comments to English, keeping the optimized include, and replacing `config/box.cfg` with a redacted `.07.01`-generated example.
- Replace `box_extras`-based Box detection in optimized macros, the start-print contract, and installer Box reconciliation with detection that works on the `.07.01` RS-485 stack, using one shared definition.
- Adopt QIDI's `.07.01` filament-cut reliability sequence in `OPTIMIZED_CUT_FILAMENT` while keeping the optimized exit without the stock `2 s` dwell.
- Align optimized runout and resume with `.07.01` vendor ownership: Box recovery always goes through `TRY_RESUME_PRINT`, and `TLTG_FILAMENT_SENSOR ENABLE=0` still lets an external-spool print resume without a filament-present gate.
- On `.07.01`, where `CUT_FILAMENT` and `UNLOAD_T{n}` are no longer registered and `T{n}` runs the vendor `T_MANAGER` flow, hand slicer filament-change cut and unload to that flow and route optimized end-print unload to vendor `UNLOAD_FILAMENT`. The legacy path stays in place for `.06.x`.
- Advance the package version and add release notes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `installer-lifecycle`: QIDI Box reconciliation recognizes an available Box from the `.07.01` RS-485 stack as well as the legacy USB Box configuration.
- `optimized-printer-behavior`: Box availability, filament cutting, external-spool resume, and vendor-surface preservation change for the `.07.01` Box stack.

## Impact

Affected paths include `installer/package.yaml`, `installer/supported_upgrade_sources.yaml`, `installer/stock/qidi-max4-defaults/`, `installer/runtime/box_enablement.py`, `installer/klipper/tltg-optimized-macros/filament.cfg` and other optimized macros that test Box availability, `orcaslicer_gcode/change_filament.gcode`, `qidistudio_gcode/change_filament.gcode`, `scripts/check_optimized_slicer_macros.py`, `openspec/contracts/gcode-paths/start-print.path.json` and generated views, installer tests and fixtures, bundle smoke validation, `CHANGELOG.md`, and `openspec/observations/`. The stock-mapped `config/` tree is resynchronized to `.07.01` with Chinese comments translated to English. Firmware-managed compiled modules and `toolhead.py` are not modified.
