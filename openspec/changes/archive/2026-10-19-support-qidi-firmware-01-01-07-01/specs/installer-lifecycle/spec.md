## MODIFIED Requirements

### Requirement: Non-owning QIDI Box reconciliation
The installer SHALL keep an available QIDI Box usable without claiming ownership of vendor saved variables or silently replacing existing non-empty tool mappings. Box availability SHALL be recognized for every supported firmware's Box transport, including the legacy USB Box configuration and the RS-485 Box stack.

#### Scenario: Optional Box state is reconciled conservatively
- **WHEN** the Box stack is available
- **THEN** explicit interactive or `--yes` policy may enable it
- **AND** missing active mappings are created as identity mappings
- **AND** existing non-empty mappings change only after explicit interactive approval

#### Scenario: Box availability is transport-independent
- **WHEN** a QIDI Box is attached through either the legacy USB configuration or the RS-485 Box stack
- **THEN** Box enablement and tool-mapping reconciliation treat the Box as available
- **AND** a printer with no attached Box is not treated as Box-capable solely because firmware always loads Box controller objects

#### Scenario: Automatic reconciliation preserves vendor state
- **WHEN** noninteractive install or update observes Box topology while the printer is idle
- **THEN** missing active mappings are created and existing non-empty mappings are preserved
- **AND** busy, unavailable, or not-ready Klipper state causes no reconciliation writes
- **AND** every write uses Klipper's live `SAVE_VARIABLE` command through Moonraker, verifies its live value and, when a source-patch restart occurs, verifies it again after the replacement process; it never restores a whole saved-variable file during rollback
- **AND** saved-variable changes are excluded from installer ownership and uninstall
