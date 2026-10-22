# Design

## Context

The released Max 4 touchscreen implements THR serial flashing internally. The installed application was read through its existing Klipper debug-read command and matches the pinned stock image. A separate 32 KiB bootloader backup allows bounded execution of its real parser, erase bounds, programming loop, and replies.

## Goals / Non-Goals

**Goals:** explicit THR-only operations, immutable image admission, preserved recovery artifacts, and byte-based verification.

**Non-Goals:** automatic service management, a full vendor update, arbitrary firmware or devices, and claiming power-loss recovery from emulation alone.

## Decisions

- Restrict the serial device and application hashes to the known Max 4 THR. Reject unknown images before opening the device. Snapshot application and bootloader through the printer's existing Klipper libraries; do not add a host plugin or modify configuration.
- Require serial-owning services and the update timer to be inactive before UART access. The operator procedure owns the active-print/heater guard and restoration; the tool requires an explicit idle assertion and does not restart services on a failed transfer.
- Use the recovered 115,200-baud framed protocol with CRC validation, complete-frame buffering, bounded retries, exact packet-index/count acknowledgements, and explicit final acknowledgement. A start command erases the entire application region, not the bootloader.
- Separate non-erasing probes from confirmed writes. Use the same admitted stock image for recovery; never guess STM32 ROM commands or change bootloader contents.
- Treat complete application readback and unchanged bootloader hash as installation evidence. Unchanged vendor versions and transfer acknowledgements are not sufficient.

## Risks / Trade-offs

- Application erase/write interruption can leave unusable application firmware → preserve the stock image and bootloader, bound writes, and verify a physical reset/recovery entry before declaring the procedure ready.
- The bootloader has a bounded startup receive window → do not assume an entire-printer power cycle leaves enough time for Linux to start a recovery tool.
- Emulator flash-register and serial stubs do not establish electrical behavior → retain explicit hardware-validation tasks and block live operations when printer idle state is unknown.
