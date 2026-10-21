# Spec Delta

## ADDED Requirements

### Requirement: THR firmware programming requires per-run opt-in
The installer SHALL ask supported interactive installations whether to flash the THR FIFO fix, defaulting to No. An explicit yes or install-only CLI option SHALL authorize only that invocation. `--yes` alone, unattended updates, restore, and uninstall MUST NOT program MCU firmware or persist permission to do so.

#### Scenario: Firmware option is absent
- **WHEN** the operator declines, submits an empty answer, reaches end of input, or runs unattended without the explicit firmware option
- **THEN** no THR serial session, firmware backup, reset, or programming occurs

#### Scenario: Firmware option is explicitly selected
- **WHEN** an operator explicitly accepts the interactive question or selects the install-only THR firmware option
- **THEN** the installer explains the firmware/recovery risk and performs the operation under the installer lock after configuration installation and required activation
- **AND** the interactive question and README warn that input shaper calibration must be rerun after flashing; the installer does not initiate calibration
- **AND** dry-run reports the proposed firmware work without service changes, serial access, or firmware backup creation

### Requirement: Optional THR transfer is admitted and byte-verified
The optional operation SHALL require supported firmware, idle ready state, zero heater targets, exclusive service ownership, and exact known THR application/bootloader identities. It MUST preserve stock recovery files before erase and verify the complete resulting application and unchanged bootloader before success.

#### Scenario: Known stock or patched application is detected
- **WHEN** safe preconditions hold and readback matches an admitted image
- **THEN** stock firmware receives only the pinned THR patch with retained recovery files
- **AND** an already-patched board is verified without another erase or transfer
- **AND** only previously active services are restored and printer readiness is checked

#### Scenario: Admission fails or firmware work is interrupted
- **WHEN** firmware admission fails or firmware work does not reach verified readback
- **THEN** no unknown image is programmed and verified configuration installation is preserved
- **AND** potentially changed or unverified firmware retains recovery evidence, stopped serial-owning services, and a durable blocker against later installer operations
- **AND** configuration restore and uninstall never claim to revert MCU firmware
