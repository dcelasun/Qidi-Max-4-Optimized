## MODIFIED Requirements

### Requirement: Filament and QIDI Box state lifecycle
Optimized macros SHALL keep external-spool runout policy independent from vendor Box recovery, retain filament only when the saved preference equals `1` and physical Box state is provable, and normalize tool mappings only at safe lifecycle boundaries. Box-dependent behavior SHALL use one transport-independent Box-availability definition.

#### Scenario: Box availability is transport-independent
- **WHEN** a QIDI Box is attached through either the legacy USB configuration or the RS-485 Box stack
- **THEN** optimized start, retention, unload, cleanup, runout, and resume paths take their Box branches
- **AND** with no attached Box they take their non-Box branches even though firmware always loads Box controller objects

#### Scenario: External runout pause is independently switchable
- **WHEN** automatic external-spool pause is disabled
- **THEN** sensor events and exhausted status remain visible while automatic external pause is suppressed
- **AND** QIDI Box runout, reload, status, and resume remain vendor-controlled
- **AND** the setting returns enabled after Klipper restart

#### Scenario: Resume follows vendor recovery unless the operator overrides the sensor
- **WHEN** a paused print is resumed
- **THEN** an active Box print resumes through the vendor Box resume command
- **AND** an external-spool print with automatic external pause disabled resumes without a filament-present gate
- **AND** an external-spool print with automatic external pause enabled resumes only through a path that refuses to continue while the toolhead sensor reports no filament

#### Scenario: Absent runtime preference disables retention
- **WHEN** `tltg_keep_loaded_between_prints` is absent from Klipper saved variables or does not equal `1`
- **THEN** normal optimized print completion clears retained-filament state and delegates cutting and unloading to the existing QIDI Box sequence
- **AND** runout sensors are disabled before the intentional end-of-print unload so it cannot pause the remaining shutdown routine
- **AND** optimized print start does not reuse retained filament

#### Scenario: Retention follows the synchronized physical slot
- **WHEN** `tltg_keep_loaded_between_prints` equals `1`
- **AND** normal end-print retention runs with Box filament loaded
- **THEN** retained tool, slot, material, and vendor identity derive from the synchronized physical slot and current mapping
- **AND** unload clears retained state before vendor unload while preserving caller motion and extrusion modes

#### Scenario: Retention preference is operator-controlled
- **WHEN** the operator saves `1` or `0` to `tltg_keep_loaded_between_prints`
- **THEN** subsequent optimized starts and normal completions respectively enable or disable retention until the saved value changes
- **AND** installation initializes an absent preference to `1` and does not overwrite an existing value

#### Scenario: Start repairs only missing active mappings
- **WHEN** print start requires active Box mappings
- **THEN** missing or empty active mappings become identity mappings before filament preparation
- **AND** every existing non-empty mapping is preserved
- **AND** non-Box start remains available

#### Scenario: Normal completion restores predictable mappings
- **WHEN** slicer end G-code completes retention or unloading
- **THEN** cooldown begins before existing mappings are normalized to identity
- **AND** missing mappings are created only for active Box slots
- **AND** normalization completes before print-end cleanup

#### Scenario: Interrupted prints preserve operator recovery state
- **WHEN** cancellation, error, power loss, or another interruption bypasses normal slicer end G-code
- **THEN** current tool mappings are not normalized
- **AND** manual mapping reset is permitted only while the printer is idle

### Requirement: Safe print transitions and helpers
Optimized cut, purge, cooldown, cleaning, calibration, and cancellation helpers SHALL preserve caller state, guard optional hardware, and avoid delayed or error-path actions that can affect a subsequent print. Print-start cleaning SHALL preserve staged cooldown wiping with mixed-speed pre-scrape motion and use fast finishing after the cooled rear-bed scrape, with detailed motion and branch ordering controlled by `openspec/contracts/gcode-paths/start-print.path.json`.

#### Scenario: Cut and cleanup preserve caller state
- **WHEN** optimized cut, purge, chute, chamber, or Box-heater helpers run
- **THEN** motion modes, extrusion modes, and temporary acceleration are restored
- **AND** optional Box objects are called only when available and valid
- **AND** fixed waits are reduced without replacing required motion completion waits

#### Scenario: Slicer filament change avoids a double cut on every firmware
- **WHEN** an optimized slicer filament change runs
- **THEN** exactly one cut occurs: the optimized cut when the vendor tool-change flow is absent, or the vendor flow's cut when it is present
- **AND** the same slicer G-code remains correct with older installed optimized macros and with older supported firmware

#### Scenario: Optimized cut keeps the vendor reliability sequence
- **WHEN** the optimized filament cut or the stock-named cutter macro used by vendor flows runs
- **THEN** the extruder stepper is released and allowed to settle before the cutter strike
- **AND** the cutter approach, strike, and post-cut retraction match the newest supported stock cut sequence
- **AND** only the stock idle dwell after the toolhead leaves the cutter is omitted
- **AND** the stock-named cutter macro leaves the same modal state as stock for vendor callers

#### Scenario: Pre-scrape wiping retains the cooldown stages
- **WHEN** a fresh Box or external-spool start reaches an existing guarded pre-scrape chute wipe
- **THEN** each wipe uses two broad alternating-speed cycles followed by three finishing cycles at commanded 100 mm/s
- **AND** existing repeated cooldown wipe stages, temperature thresholds, conditional execution, purge quantities, and waste-release positioning are preserved rather than collapsed into one wipe
- **AND** the existing cooled rectangular rear-bed scrape is followed by three small circles with its cable-chain orientation and temperature safety gate intact

#### Scenario: Cooled scraping finishes with fast chute wiping
- **WHEN** a fresh Box or external-spool start completes its rear-bed scrape and guarded chute cleanup is available
- **THEN** the nozzle lifts clear and returns safely to the chute before performing four back-and-forth finishing cycles at commanded 200 mm/s
- **AND** waste-release positioning completes before leveling
- **AND** unavailable vendor cleanup objects are not called

#### Scenario: Optimized cleanup uses fast non-extruding silicone wipes
- **WHEN** retained-filament startup, non-start purge cleanup, unload cleanup, or staged end cleanup reaches an existing silicone-wiper pass
- **THEN** it retains four back-and-forth finishing cycles at commanded 200 mm/s and its existing exit motion
- **AND** no mixed-speed pre-scrape pattern is substituted into these unrelated cleanup paths

#### Scenario: Wipe motion preserves state and unrelated cleanup
- **WHEN** either optimized wipe pattern executes with the nozzle already positioned at the rear wiper
- **THEN** it preserves caller motion and extrusion modes, feed settings, and acceleration
- **AND** the wipe itself performs no extrusion, Y/Z repositioning, heater changes, fixed dwell, or bed scraping
- **AND** retained-filament startup, non-start purge cleanup, manual loading, unload cleanup, staged end cleanup, vendor cleanup commands, and slicer filament-change sequences retain their existing behavior
- **AND** retained-filament startup does not gain a rear-bed scrape or post-scrape sequence

#### Scenario: End-print performs staged cooldown safely
- **WHEN** normal slicer end G-code runs
- **THEN** the toolhead reaches the chute, filament preparation and heater shutdown occur, and staged cooling and wiping complete before print end
- **AND** bed lowering follows the shared slicer rule
- **AND** delayed fan shutdown cannot turn off a fan used by a new or paused print
- **AND** OrcaSlicer may apply configured completion exhaust while QIDI Studio passes zero and omits unsupported indexed completion-air placeholders

#### Scenario: Error cancellation is motion-free
- **WHEN** optimized error cancellation executes
- **THEN** heaters, fans, optional Box heat, pause state, and print state are cleaned up before base cancellation
- **AND** no parking, wiping, or other toolhead motion occurs

#### Scenario: Operator helpers remain guarded and available
- **WHEN** optimized macros load
- **THEN** supported bed-screw, probe-accuracy, Box-temperature, mapping-reset, and startup reporting helpers are available
- **AND** each helper validates required printer state and hardware bounds before acting

### Requirement: Firmware and vendor compatibility surfaces
Optimized configuration SHALL preserve firmware-scoped peripheral ownership, stock integration names, and fan-failure safety while applying guarded hardware optimizations.

#### Scenario: Polar cooler ownership remains firmware-compatible
- **WHEN** firmware uses the direct polar-cooler output
- **THEN** optimized pause and resume do not change its state or recreate removed smart-pin objects
- **AND** existing direct control remains available to approved start, cooling, end, and cancellation paths

#### Scenario: Hotend fan sampling preserves protection
- **WHEN** the supported hotend-fan baseline is installed
- **THEN** the guarded polling interval declared by the package retains sampling margin above measured fan speed
- **AND** fan output, RPM reporting, and zero-RPM shutdown behavior remain unchanged
- **AND** uninstall restores the owned firmware preimage while preserving user drift

#### Scenario: Electronics temperatures are exposed without modifying Fluidd
- **WHEN** optimized configuration is installed
- **THEN** Moonraker and Fluidd receive temperature sensors named `AP_Board_SOC`, `Toolhead_MCU`, and `Mainboard_MCU`
- **AND** the AP-board sensor reads the Linux SoC thermal zone
- **AND** the toolhead sensor reads the THR MCU internal sensor
- **AND** the confirmed GD32F425 mainboard uses the datasheet's uncalibrated typical conversion instead of Klipper's incompatible STM32F407 calibration path
- **AND** the approximate mainboard sensor is observational and uses broad bounds so normal readings do not trigger a machine shutdown

#### Scenario: Stock integration surfaces remain intact
- **WHEN** optimized configuration is installed
- **THEN** stock-named macros required by QIDI software remain available
- **AND** the active vendor Box stack and vendor command names are not redefined
- **AND** stock tool-selection macros and Box transport sections, including `T0`–`T15`, `[box485]`, and `[box2base]` where firmware provides them, are neither redefined nor retuned
- **AND** optimized filament-change and unload paths invoke only commands the detected firmware registers
- **AND** `config/fluidd.cfg` and unproven externally consumed stock globals remain unmodified
