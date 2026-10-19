## Context

Firmware `01.01.07.01` is represented by `Qidi-Max4-Defaults` tag `qidi-max4-firmware-01.01.07.01-0cc97445e77295116adaa665ff463e77608d4929520bd7cd46e732fbb0a6ecf2` (commit `a92b41236ea8942e12e748106393bb8b32f31c54`), archive `QD_MAX4_01.01.07.01_20261016_Release.zip`.

### Static comparison against `.06.05`

- `config/printer.cfg` adds `[box485]` (USB-serial RS-485 bus, `115200` baud, dynamic Box addresses `1`–`127`, Hall trigger `2000`, provisional `extrude_timeout`/`extrude_length`) and `[box2base]`. `runout_gcode` no longer requires `printer["box_extras"]` before Box auto-reload.
- `pause_resume_cancel.cfg` `RESUME` calls `TRY_RESUME_PRINT` for every paused print; the external-spool filament-present branch moved into compiled code.
- `globals.cfg` runs `INIT_RFID_READ` at startup regardless of Box state.
- `filament.cfg` adds `T0`–`T15` macros calling `T_MANAGER T=n`, plus `TRY_INTO_EXTRUDER`, `MOVE_ANOTHER_POINT_CHANGE_FILAMENT`, `DROP_TRASH`, and `WIPE_NOZZLE_DROP`.
- `CUT_FILAMENT_1` disables the extruder stepper and waits `400 ms` before the cut, approaches from `X30`, strikes at `F20000`, and retracts `4 mm` at `F1800` after the cut instead of before it.
- New compiled modules: `box2base`, `box_device`, `box_protocol`, `box485_multicolor`, `box485_buffer`, `box485_rack`. `box_extras.so` lost its `CUT_FILAMENT`, `INIT_RFID_READ`, `RETRY`, `DISABLE_BOX_DRY`, `TRY_RESUME_PRINT`, `AUTO_RELOAD_FILAMENT`, `BOX_PRINT_START`, and `TOOL_CHANGE_START`/`END` handlers; the surviving public commands moved to `multi_color_controller.so`.
- `toolhead.py` adds `feed_move`/`unload_move`, which block the toolhead during remote Box feed/unload, watch Box online/error state, and report `QDE_004_042`, `_043`, `_055`, `_056`, and `_057`.
- `homing.py`, `kinematics.cfg` `homing_override`, `start_end.cfg` `_km_apply_print_offset`, and every guarded `set_options` value are unchanged from `.06.05`.

Normalized section hashes computed with `installer/runtime/klipper_cfg.normalized_section_sha256`:

| Section | `.07.01` hash |
|---|---|
| `filament_switch_sensor filament_switch_sensor` | `4466d08166d675b207e2256e4072b1b79ca5b3d83b07a272efc2bef4d41ab4cc` (identical to `.06.03`) |
| `gcode_macro RESUME` | `866bc3a0ab78901653e69116a13ad723f700622dd5df0d0541fcfac12099293b` |
| `homing_override` | `6a924478b351dea193bf1060f5747b151bba3de4c5627c7faac741ad7b164cf4` (unchanged) |
| `gcode_macro _km_apply_print_offset` | `ea8be4dae3bc5bbe881b8e3ca5c49e0b28a74b17cb9a4d8515d598bd006ce3a7` (unchanged) |

### Live `.07.01` evidence (2026-10-19, printer idle, two legacy USB Boxes, no RS-485 adapter)

- Firmware manifest reports SOC `01.01.07.01`. Live `printer.cfg` is byte-identical to the stock package; the update removed the optimized include and `tltg-optimized-macros/` tree.
- `box.cfg` was regenerated at update time. It keeps `[box_config boxN]`, `[box_extras]`, `[box_autofeed]`, and `[mcu mcu_boxN]`, and no longer defines `T{n}`, `UNLOAD_T{n}`, or `UNLOAD_FILAMENT` macros. Stock `T0`–`T15` therefore take effect.
- Registered commands (`gcode.commands`, 406 entries): `CUT_FILAMENT` and `UNLOAD_T{n}` are **not registered**. `T_MANAGER`, `EXTRUDER_LOAD`, `EXTRUDER_UNLOAD`, `SLOT_UNLOAD`, `UNLOAD_FILAMENT`, `UNLOAD_FILAMENT_CONTROL`, `LOAD_FILAMENT_CONTROL`, `EJECT_FILAMENT_CONTROL`, `TRY_RESUME_PRINT`, `RESUME_PRINT`, `INIT_RFID_READ`, `CLEAR_FLUSH`, `CLEAR_OOZE`, `BOX_PRINT_START`, `TOOL_CHANGE_START`, `TOOL_CHANGE_END`, `AUTO_RELOAD_FILAMENT`, `DISABLE_BOX_HEATER`, `FLOW_RETRY`, `FLOW_STOP`, `INTERNAL_BOX_UNLOAD`, and `QUERY_CURRENT_BOX_CHANNEL_FILAMENT` are registered.
- QIDI's `gcode.py` comments out the `Unknown command` response, so unregistered commands are silently ignored. `_CG28`, called by stock and optimized cut macros, has never been defined in any captured firmware and has always been a silent no-op.
- `multi_color_controller` status exposes top-level `box_count` (`2`), `enable_box`, `box.identity` (`box_v1` for USB Boxes), `task` (flow state), and `operation.active_slot`. `box485` status reports `box_count: 0` with no RS-485 hardware. `box2base` has no status object but registers commands.
- `klippy.log` startup is clean apart from `box485` repeatedly logging that the RS-485 serial device is absent.
- The decompressed `multi_color_controller.so` string table shows `BoxAdapterV1` (USB), `BoxAdapterV2` (RS-485), and `ExternalAdapter`, each implementing cut, unload, load, wipe, eject, print start, tool change start/end, try-resume, and auto-reload. `T_MANAGER` and other public commands start `FlowTask` step sequences whose embedded scripts call stock `CUT_FILAMENT_1`, `MOVE_TO_TRASH`, `WIPE_NOZZLE_DROP`, and `DROP_TRASH`.
- QIDI Studio `v2.07.02.73` (released 2026-10-19) still emits `CUT_FILAMENT T=[current_extruder]`, `MOVE_TO_TRASH`, `UNLOAD_T[current_extruder]`, `T[next_extruder]` for filament change and `UNLOAD_FILAMENT T=[current_extruder]` at print end. On `.07.01` the first and third are ignored, so `T_MANAGER` performs the complete vendor tool change.

## Goals / Non-Goals

**Goals:**

- Install, restore, uninstall, and upgrade optimized configuration on `.07.01` with exact firmware-scoped provenance.
- Keep optimized Box start, retention, unload, cleanup, runout, and resume behavior working on the `.07.01` flow controller for both USB and RS-485 Boxes.
- Adopt QIDI's cut reliability sequence.
- Preserve the operator's ability to disable external-spool runout pausing and still resume.
- Keep one slicer pack per slicer that works on `.06.x` and `.07.01`.
- Record `.07.01` Box behavior as qualified observations.

**Non-Goals:**

- Patching or replacing firmware-managed compiled modules, `toolhead.py`, or `box.cfg`.
- Redefining stock `T0`–`T15`, `T_MANAGER`, `[box485]`, or `[box2base]`.
- Adopting `TRY_INTO_EXTRUDER`, `DROP_TRASH`, `WIPE_NOZZLE_DROP`, or `MOVE_ANOTHER_POINT_CHANGE_FILAMENT` into optimized paths; the vendor flow already calls them.
- Tuning `[box485]` values.

## Decisions

### One Box-availability definition

`.07.01` always loads `[multi_color_controller]` and `[box2base]`, so object presence does not prove an attached Box, and a future RS-485-only printer may have no `[box_extras]`. Optimized macros use:

```jinja
printer["box_extras"] is defined
or ("T_MANAGER" in printer.gcode.commands
    and ((printer.multi_color_controller|default({})).box_count|default(0)|int > 0
         or (printer.box485|default({})).box_count|default(0)|int > 0))
```

The first term keeps `.06.x` behavior unchanged; the flow-controller term recognizes `.07.01` USB and RS-485 Boxes without trusting any `.06.x` `multi_color_controller` count. Macros keep the expression inline because Klipper Jinja cannot share functions; the start-print contract and a checker enforce that every occurrence matches. `installer/runtime/box_enablement.py` applies the equivalent rule: a `[box_extras]` section in `box.cfg`, or a registered `T_MANAGER` with a live `multi_color_controller` or `box485` `box_count` above zero.

### Vendor flow detection

Paths whose command surface differs between firmware lines detect the `.07.01` flow controller by `"T_MANAGER" in printer.gcode.commands`. `.06.x` and `.07.01` both publish `multi_color_controller` `box_count` and `task` strings, so status keys do not distinguish them; QIDI's `gcode.py` has exposed `gcode.commands` throughout the captured firmware. This selects behavior by observed capability rather than firmware string.

### Filament change hands the cut to the vendor flow on `.07.01`

Slicer packs and installed macros are updated independently and have no version handshake, and QIDI's Klipper silently ignores unknown commands. A new slicer-only macro would therefore be skipped on printers with older installed macros, leaving `.06.x` tool changes without a cut or unload. Both slicer packs instead keep their existing sequence and add one parameter:

```gcode
OPTIMIZED_CUT_FILAMENT TOOLCHANGE=1
OPTIMIZED_MOVE_TO_TRASH
M106 P2 S0
UNLOAD_T[current_extruder]
T[next_extruder]
```

| Installed macros / firmware | Behavior |
|---|---|
| Older macros, any firmware | Unknown `TOOLCHANGE` is ignored; the optimized cut runs as before. |
| Current macros, `.06.x` | `T_MANAGER` is absent; the optimized cut, chute move, and `UNLOAD_T{n}` run as before. |
| Current macros, `.07.01` | `OPTIMIZED_CUT_FILAMENT` skips its cut; the ignored `UNLOAD_T{n}` and `T_MANAGER` leave cut, unload, and load to the vendor flow. |

Manual `OPTIMIZED_CUT_FILAMENT` calls without `TOOLCHANGE=1` always cut. A live stock `.07.01` print confirmed the vendor flow cuts once, unloads, and loads per change when nothing cut first. A live `.07.01` print using the `TOOLCHANGE=1` pack with current macros also produced exactly one cut, made by the vendor flow through the optimized `CUT_FILAMENT_1`.

### Replace stock `CUT_FILAMENT_1` (approved option B)

On `.07.01` the vendor flow calls `CUT_FILAMENT_1` by name, so `OPTIMIZED_CUT_FILAMENT` cuts only for legacy filament change and manual calls. To remove the stock `2 s` exit dwell from vendor tool changes, a guarded delete-section patch removes stock `CUT_FILAMENT_1` and the optimized tree defines a replacement with the same name, using the mechanism already used for `RESUME`.

- The replacement is the newest stock sequence with only the final `G4 P2000` removed. It keeps the stock exit speed and final `M400` and does not save or restore G-code state, because vendor flow scripts that follow it rely on the stock post-cut modal state (relative extrusion, `10000` acceleration).
- Optimized macros are static and Klipper merges duplicate sections, so the replacement cannot be firmware-scoped. The guarded delete covers every supported firmware (`.06.03`–`.06.05` share one stock hash; `.07.01` has its own), so stock `.06.x` callers of `CUT_FILAMENT_1` also receive the newest reliability sequence without the dwell.
- `gcode_macro CUT_FILAMENT_1` leaves `preflight.required_sections`; the guarded delete already requires the exact stock section, and a deleted section would otherwise fail reinstall preflight.

### Adopt the stock cut through the post-cut retract

`OPTIMIZED_CUT_FILAMENT` uses the `.07.01` `CUT_FILAMENT_1` sequence from the extruder disable through `G1 E-4 F1800`, including the `400 ms` settle, which is part of the reliability fix rather than idle dwell. It keeps its own exit (`G1 X15 F8000`), omits the stock final `M400`/`G4 P2000`, and continues to save and restore G-code state and acceleration. The extruder stepper re-enables automatically on the retract move, as in stock. `_CG28` remains in place to match stock even though it is a no-op.

### End-print unload uses the vendor unload on the flow controller

`OPTIMIZED_UNLOAD_FILAMENT` keeps clearing retained state first. In its Box branch, the legacy command surface keeps `CUT_FILAMENT`, chute move, `UNLOAD_T{T}`, and the optional cleanup. The flow controller calls `UNLOAD_FILAMENT T={T}`, matching QIDI Studio's end G-code; a live stock `.07.01` print confirmed it cuts once and unloads to the Box. The optional optimized cleanup (`CLEANUP=1`, manual unloads) still runs afterward on both paths, so a vendor wipe, if any, is at worst repeated. End-print unload passes `CLEANUP=0` and relies on the staged cooldown wipes. Without this change `.07.01` would leave filament loaded, because `UNLOAD_T{T}` is ignored.

### Resume routing preserves the external-spool override (approved)

| Condition | Command |
|---|---|
| Box available, `box_count >= 1`, and `enable_box == 1` | `TRY_RESUME_PRINT` |
| No active Box and `TLTG_FILAMENT_SENSOR` pausing disabled | `RESUME_PRINT` (no filament-present gate) |
| No active Box and pausing enabled, flow controller present | `TRY_RESUME_PRINT` |
| No active Box and pausing enabled, legacy firmware | `RESUME_PRINT` only when the toolhead sensor reports filament; otherwise `M118 Please load filament` |

On legacy firmware without a Box, `TRY_RESUME_PRINT` is not registered and would be silently ignored, so the legacy row keeps the previous local gate. This matches stock for every case except the operator override, which exists so a print can continue when the toolhead sensor is unreliable. If live testing shows `TRY_RESUME_PRINT` does not refuse an external-spool resume with the toolhead sensor empty, the third row keeps the local `filament_detected` gate and `M118 Please load filament`. The `ExternalAdapter` string table contains `No filament detected. Please insert filament and try again.`, which suggests the gate exists. The optimized `[gcode_macro RESUME]` still replaces the stock section through the guarded `pause_resume_cancel_resume` delete-section patch.

### Runout follows the `.07.01` gate

`OPTIMIZED_FILAMENT_SENSOR_RUNOUT` uses `enable_box == 1` together with the shared Box-availability predicate, so RS-485 Boxes reach `AUTO_RELOAD_FILAMENT`. External-spool pause suppression is unchanged.

### Extend unchanged variants, add discrete variants for changed sections

As in the `.06.05` change, unchanged `set_options` and delete-section variants list `.07.01` alongside `.06.04`/`.06.05`. `filament_switch_sensor` and `RESUME` get new `.07.01` variants with the hashes above. `qidi_homing` gets a discrete `.07.01` entry with the `.06.05` hashes because installed-state trust is firmware-scoped.

## Risks / Trade-offs

- [`T_MANAGER` may behave differently when the optimized chute move precedes it] → Stock G-code confirmed the flow cuts once, unloads, and loads; verify the optimized pack during task 9.8 before release.
- [The vendor `UNLOAD_FILAMENT` may change hotend targets before staged cooldown] → `OPTIMIZED_END_NOZZLE_COOLDOWN_START` already falls back to current temperature; verify during task 9.8.
- [`.07.01` `feed_move` blocks the toolhead until the Box finishes] → No fixed waits are added around vendor loads.
- [RS-485 Boxes are unavailable for testing] → The predicate's RS-485 term is covered by static checks only and recorded as unverified in observations.
- [The firmware update removes the optimized install] → Operators must reinstall after updating; covered by the existing post-update recovery behavior once `.07.01` is admitted.

## Open Questions

- Does `T_MANAGER` still cut exactly once when the optimized chute move precedes it? Stock G-code confirmed one cut, unload, and load per change (task 1.9).
- Does `TRY_RESUME_PRINT` refuse an external-spool resume with the toolhead sensor empty? The operator accepted the assumption that it keeps the previous gate (task 1.8); untested.
