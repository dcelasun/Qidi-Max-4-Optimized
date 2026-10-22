# Design

## Context

The existing restricted serial tool admits two application hashes and one bootloader hash, and supports snapshots, bounded transfer, and complete readback verification. Live stationary measurements confirm the FIFO fix. Independent physical recovery through unpopulated RESET pads remains unverified.

## Goals / Non-Goals

**Goals:** add a per-invocation install option without changing default installation or unattended updates; preserve durable firmware evidence outside configuration ownership.

**Non-Goals:** automatic firmware enrollment, other boards, arbitrary images, configuration-driven firmware rollback, or claiming physical recovery from a successful serial transfer.

## Decisions

- Ask a default-No question during supported interactive installations; only an explicit y/yes opts in. `install --flash-thr-fifo` supplies equivalent per-run authorization, including with `--yes`. Do not persist permission. Reject explicit programming in automatic-update child processes and non-install modes; unattended installs never prompt.
- Run firmware work after configuration installation and source activation under the same installer lock. Report firmware failure without rolling back committed configuration.
- Package the restricted tool, patch manifest, and recovery instructions. Derive the patched application from admitted stock readback and verify the output hash, rather than downloading the full vendor archive or redistributing binary snapshots.
- Gate to firmware `01.01.07.01`; require strict idle/ready status and every reported heater target at zero before stopping serial owners. Preserve the original active/inactive service states; a missing optional update timer is not a serial owner.
- Store private backups and readback evidence outside `config/`. Create a durable firmware-operation marker before service changes. Clear it only after a verified application and restored readiness; all installer entrypoints reject unresolved firmware work.
- Treat an already-patched application as verified/no-transfer. Preserve the bootloader and do not reset or erase that board again.

## Risks / Trade-offs

- Transfer interruption can leave unusable firmware → retain the stock image and bootloader, leave serial owners stopped after ambiguous writes, and expose the recovery directory and blocker in the error.
- A software transfer does not establish physical recovery → warn before opt-in execution and retain the independent recovery limitation in operator documentation.
- Firmware cannot participate in configuration rollback → keep its backup/operation marker separate and leave the installed configuration result intact on firmware failure.
