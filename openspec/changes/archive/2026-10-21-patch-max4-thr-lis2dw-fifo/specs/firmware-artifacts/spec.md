# Spec Delta

## Purpose

Generate narrowly patched Max 4 firmware artifacts while preserving vendor components outside the approved fix.

## ADDED Requirements

### Requirement: Firmware generation is bound to a known release
The generator SHALL accept only the supported vendor archive and THR image, preserve the input, reject existing output destinations, and emit separately identified artifacts with checksums and provenance. Unknown, modified, or already-patched inputs MUST fail without producing a firmware package.

#### Scenario: Known release produces traceable artifacts
- **WHEN** the operator supplies the recognized vendor archive and a new output destination
- **THEN** generation produces a patched firmware ZIP, standalone THR image, checksums, and a provenance report identifying the input and output hashes
- **AND** the original archive remains unchanged

#### Scenario: Unsafe input or destination is rejected
- **WHEN** the input is unrecognized, modified, already patched, or the destination already exists
- **THEN** generation fails without overwriting existing data or emitting a firmware package

### Requirement: THR changes are limited to the FIFO correction
The generated THR SHALL immediately request another task when the LIS2DW FIFO contains samples and rearm polling when it is empty, preserving scheduler wake semantics. The package MUST preserve every other component payload, the firmware manifest, internal filenames, and vendor version identities. Generation MUST NOT flash hardware or invoke the macro installer.

#### Scenario: FIFO handling changes without replacing vendor components
- **WHEN** a recognized package is patched and verified
- **THEN** the THR differs only at the approved instruction edits and handles empty and nonempty FIFO states correctly
- **AND** sample reporting and overflow accounting remain intact
- **AND** all other archive members and the THR protocol dictionary are byte-identical to the input
