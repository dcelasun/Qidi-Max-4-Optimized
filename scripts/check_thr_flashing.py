#!/usr/bin/env python3
"""Check THR transfer safety offline; optionally execute a captured bootloader."""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import struct
import tempfile
from collections import deque
from pathlib import Path
from unittest.mock import patch

import flash_thr_firmware as tool


class NativeBoard:
    def __init__(self, boot: bytes, application: bytes):
        from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
        from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC
        self.r0, self.r1, self.r2 = UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2
        self.sp, self.lr, self.pc = UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC
        self.uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        for address, size in ((0x08000000, 0x20000), (0x20000000, 0x10000),
                              (0x40000000, 0x30000), (0xe000e000, 0x2000)):
            self.uc.mem_map(address, size)
        self.uc.mem_write(0x08000000, boot)
        self.uc.mem_write(0x08008000, application)
        self.boot = boot
        self.sent, self.erases, self.writes, self.jumps = [], [], [], []
        self.uc.hook_add(UC_HOOK_CODE, self.hook)
        self.call(0x08000c10)

    def call(self, address, *args):
        self.uc.reg_write(self.sp, 0x2000f000)
        self.uc.reg_write(self.lr, 0x2000fff1)
        for reg, value in zip((self.r0, self.r1, self.r2), args):
            self.uc.reg_write(reg, value)
        self.uc.emu_start(address | 1, 0x2000fff0, count=2000000)
        assert self.uc.reg_read(self.pc) == 0x2000fff0, "Bootloader execution bound exceeded"
        return self.uc.reg_read(self.r0)

    def ret(self, value=0):
        self.uc.reg_write(self.r0, value)
        self.uc.reg_write(self.pc, self.uc.reg_read(self.lr))

    def hook(self, uc, address, size, data):
        # Only flash-controller register operations and UART output are replaced.
        if address in (0x08000498, 0x08000508, 0x080004e0):
            self.ret()
        elif address == 0x080005c4:
            destination = uc.reg_read(self.r0)
            assert 0x08008000 <= destination <= 0x0801f800 and destination % 2048 == 0
            self.erases.append(destination)
            uc.mem_write(destination, b"\xff" * 2048)
            self.ret()
        elif address == 0x08000690:
            destination, value = uc.reg_read(self.r0), uc.reg_read(self.r1)
            assert 0x08008000 <= destination <= 0x0801fffc and destination % 4 == 0
            word = struct.pack("<I", value)
            previous = bytes(uc.mem_read(destination, 4))
            assert all((old & new) == new for old, new in zip(previous, word))
            uc.mem_write(destination, word)
            self.writes.append(destination)
            self.ret()
        elif address == 0x080016d4:
            raw = bytes(uc.mem_read(uc.reg_read(self.r0), uc.reg_read(self.r1)))
            assert int.from_bytes(raw[-2:], "big") == tool.crc16(raw[1:-2])
            self.sent.append(raw)
            self.ret()
        elif address == 0x08000b74:
            self.jumps.append(0x08008000)
            self.uc.reg_write(self.pc, 0x2000fff0)
            self.uc.emu_stop()

    def receive(self, raw):
        start = len(self.sent)
        self.uc.mem_write(0x20000458, raw)
        self.uc.mem_write(0x20000458 + 0x80a, b"\x01")
        self.uc.mem_write(0x2000003d, b"\x01")
        self.call(0x080014d8)
        assert bytes(self.uc.mem_read(0x08000000, 0x8000)) == self.boot
        return self.sent[start:]

    def application(self, size):
        return bytes(self.uc.mem_read(0x08008000, size))


class Peer:
    def __init__(self, mode="normal", board=None):
        self.mode, self.board = mode, board
        self.queue = bytearray(b"noise\xa5\xff\xff\xff")
        self.now = 0.0
        self.sent = []
        self.pages = {}
        self.injected = False
        self.erased = False
        self.fragments = deque((1, 2, 5, 3, 11))

    def clock(self):
        return self.now

    def flush(self):
        pass

    def read(self, count):
        self.now += 0.05
        chunk_size = self.fragments[0]
        self.fragments.rotate(-1)
        count = min(count, chunk_size)
        chunk = bytes(self.queue[:count])
        del self.queue[:count]
        return chunk

    def write(self, raw):
        assert raw[0] == 0xa5
        assert int.from_bytes(raw[2:4], "big") + 6 == len(raw)
        assert int.from_bytes(raw[-2:], "big") == tool.crc16(raw[1:-2])
        kind, payload = raw[1], raw[4:-2]
        self.sent.append((kind, payload))
        if kind == 1 and len(payload) == 6:
            self.erased = True
        if self.mode == "silent":
            return len(raw)
        if self.mode == "wrong-board":
            self.queue.extend(tool.encode(0, b"\x01\x03\x01\x02"))
            return len(raw)
        corrupt = kind == 2 and self.mode == "bad-data" and not self.injected
        transmitted = raw[:-1] + bytes([raw[-1] ^ 1]) if corrupt else raw
        if self.board:
            replies = self.board.receive(transmitted)
        elif kind == 0:
            replies = [bytes.fromhex("a5000004010201025235")]
        elif kind == 1:
            replies = [tool.encode(1, b"\x01\x01" if len(payload) == 6 else b"\x02\x01")]
        else:
            index = int.from_bytes(payload[:4], "big")
            assert int.from_bytes(payload[4:6], "big") == len(payload) - 6
            if not corrupt:
                if index in self.pages:
                    assert self.pages[index] == payload[6:]
                self.pages[index] = payload[6:]
            replies = [tool.encode(2, payload[:6] + (b"\x02" if corrupt else b"\x01"))]
        inject_here = (kind == 2 and not self.injected
                       and (int.from_bytes(payload[:4], "big") == 1
                            or self.mode in ("bad-data", "first-bad-reply", "first-lost-ack")))
        if inject_here:
            if self.mode in ("bad-reply", "first-bad-reply"):
                replies = [reply[:-1] + bytes([reply[-1] ^ 1]) for reply in replies]
                self.injected = True
            elif self.mode in ("lost-ack", "first-lost-ack"):
                replies = []
                self.injected = True
            elif self.mode == "stale-ack":
                replies = [tool.encode(2, b"\x00\x00\x00\x99\x04\x00\x01")]
                self.injected = True
            elif corrupt:
                self.injected = True
        if kind == 1 and ((self.mode == "lost-start-ack" and len(payload) == 6)
                          or (self.mode == "lost-end-ack" and len(payload) == 2)):
            replies = []
        self.queue.extend(b"".join(replies))
        return len(raw)


def check_admission(stock, patched, boot, manifest):
    with tempfile.TemporaryDirectory(prefix="thr-transfer-check-") as temporary:
        root = Path(temporary)
        backup = root / "backup"
        backup.mkdir()
        tool.save_snapshot(backup, boot, stock)
        stock_path, patched_path = root / "stock.bin", root / "patched.bin"
        stock_path.write_bytes(stock)
        patched_path.write_bytes(patched)
        invalid = root / "unknown.bin"
        invalid.write_bytes(patched[:-1] + bytes([patched[-1] ^ 1]))
        cases = [
            ["transfer", "--image", str(invalid), "--confirm-write", "--backup-dir", str(backup)],
            ["transfer", "--image", str(patched_path), "--backup-dir", str(backup)],
            ["transfer", "--image", str(patched_path), "--confirm-write"],
            ["transfer", "--image", str(patched_path), "--confirm-write", "--backup-dir", str(backup)],
            ["probe", "--backup-dir", str(backup)],
            ["snapshot", "--output-dir", str(backup)],
            ["snapshot", "--output-dir", str(root / "new")],
        ]
        if tool.digest(boot) == tool.BOOT_SHA256:
            for args in cases:
                with patch.object(tool.subprocess, "run", side_effect=AssertionError("Admission opened service access")):
                    with contextlib.redirect_stderr(io.StringIO()):
                        assert tool.main(args) == 1
            result = tool.verify_readback(stock, backup, manifest)
            assert result["verified"]
            try:
                tool.verify_readback(patched, backup, manifest)
            except ValueError:
                pass
            else:
                raise AssertionError("Mismatched readback was accepted")
            for filename, damaged in (("bootloader.bin", boot[:-1]), ("application.bin", stock[:-1])):
                target = backup / filename
                original = target.read_bytes()
                target.write_bytes(damaged)
                try:
                    with patch.object(tool.subprocess, "run", side_effect=AssertionError("Invalid backup opened service access")):
                        with contextlib.redirect_stderr(io.StringIO()):
                            assert tool.main(["transfer", "--image", str(patched_path), "--confirm-write",
                                              "--backup-dir", str(backup), "--printer-idle-confirmed"]) == 1
                finally:
                    target.write_bytes(original)
            for state in ("active", "activating", "deactivating", "failed", ""):
                with patch.object(tool.subprocess, "run", return_value=type("Result", (), {"stdout": state, "returncode": 0})()):
                    with contextlib.redirect_stderr(io.StringIO()):
                        assert tool.main(["transfer", "--image", str(patched_path), "--confirm-write",
                                          "--backup-dir", str(backup), "--printer-idle-confirmed"]) == 1

            def absent_timer(command, **kwargs):
                missing = command[2] == "tltg-optimized-auto-update.timer"
                output = "not-found" if "--property=LoadState" in command else "inactive"
                return type("Result", (), {"stdout": output, "returncode": 1 if missing else 0})()
            with patch.object(tool.subprocess, "run", side_effect=absent_timer):
                tool.require_ownership(True)


def check_transfer(stock, patched, boot, manifest):
    results = []
    for image in (stock, patched):
        for mode in ("normal", "bad-data", "bad-reply", "lost-ack", "stale-ack"):
            board = NativeBoard(boot, stock) if boot else None
            peer = Peer(mode, board)
            result = tool.Bootloader(peer, peer.clock).transfer(image, manifest)
            assert result["transfer_acknowledged"] and not result["verified"]
            actual = board.application(len(image)) if board else b"".join(peer.pages[index] for index in sorted(peer.pages))
            assert actual == image
            assert len(peer.sent) == (38 if mode == "normal" else 39)
            if board:
                assert board.erases == list(range(0x08008000, 0x08020000, 2048))
                assert board.application(0x18000)[len(image):] == b"\xff" * (0x18000 - len(image))
            results.append({"image_sha256": tool.digest(image), "mode": mode, "packets": len(peer.sent)})
    for mode in ("first-lost-ack", "first-bad-reply"):
        board = NativeBoard(boot, stock) if boot else None
        peer = Peer(mode, board)
        try:
            tool.Bootloader(peer, peer.clock).transfer(patched, manifest)
        except TimeoutError:
            assert len(peer.sent) == 3
            if board:
                assert len(board.writes) == 256
        else:
            raise AssertionError("Ambiguous packet-zero acknowledgement was retried")
    for mode, expected_packets in (("lost-start-ack", 2), ("lost-end-ack", 38)):
        board = NativeBoard(boot, stock) if boot else None
        peer = Peer(mode, board)
        try:
            tool.Bootloader(peer, peer.clock).transfer(patched, manifest)
        except TimeoutError:
            assert len(peer.sent) == expected_packets
        else:
            raise AssertionError("Incomplete transfer was reported as acknowledged")
    for mode, error in (("wrong-board", ValueError), ("silent", TimeoutError)):
        peer = Peer(mode)
        try:
            tool.Bootloader(peer, peer.clock).transfer(patched, manifest)
        except error:
            assert not peer.erased
        else:
            raise AssertionError("Unsafe bootloader handshake was accepted")
    peer = Peer(board=NativeBoard(boot, stock) if boot else None)
    tool.Bootloader(peer, peer.clock).probe()
    assert not peer.erased and not peer.pages
    if peer.board:
        peer.board.uc.mem_write(0x20000034, b"\x00" * 4)
        peer.board.call(0x080014d8)
        peer.board.uc.mem_write(0x20000008, b"\x00" * 4)
        peer.board.call(0x080014d8)
        assert peer.board.jumps
        assert peer.board.application(len(stock)) == stock and not peer.board.erases
    return results


def check_interruption(stock, patched, boot, manifest):
    board = NativeBoard(boot, stock)
    assert board.receive(tool.encode(0, b"\x01\x00"))
    assert board.receive(tool.encode(1, b"\x01\x00" + len(patched).to_bytes(4, "big")))
    data = patched[:1024]
    assert board.receive(tool.encode(2, b"\x00\x00\x00\x00\x04\x00" + data))
    partial = board.application(0x18000)
    board.uc.mem_write(0x20000034, b"\x00" * 4)
    board.call(0x080014d8)
    assert board.application(2048) == b"\xff" * 2048
    peer = Peer(board=board)
    tool.Bootloader(peer, peer.clock).transfer(stock, manifest)
    assert board.application(len(stock)) == stock
    cold = NativeBoard(boot, partial)
    cold.uc.mem_write(0x20000034, b"\x00" * 4)
    cold.call(0x080014d8)
    cold.uc.mem_write(0x20000008, b"\x00" * 4)
    cold.call(0x080014d8)
    assert cold.jumps, "Cold startup behavior changed; re-audit recovery assumptions"
    return {"link_timeout_stock_recovery": True, "cold_start_can_jump_to_partial_application": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-image", required=True, type=Path)
    parser.add_argument("--patched-image", required=True, type=Path)
    parser.add_argument("--bootloader-backup", type=Path)
    args = parser.parse_args()
    manifest = json.loads(tool.MANIFEST.read_text())
    stock, patched = args.stock_image.read_bytes(), args.patched_image.read_bytes()
    assert tool.admitted_image(stock, manifest) == manifest["thr"]["stock_sha256"]
    assert tool.admitted_image(patched, manifest) == manifest["thr"]["patched_sha256"]
    boot = args.bootloader_backup.read_bytes() if args.bootloader_backup else None
    if boot is not None:
        assert len(boot) == 0x8000 and tool.digest(boot) == tool.BOOT_SHA256
        check_admission(stock, patched, boot, manifest)
    else:
        fixture = b"\x00" * 0x8000
        with patch.object(tool, "BOOT_SHA256", tool.digest(fixture)):
            check_admission(stock, patched, fixture, manifest)
    report = {"native_bootloader": bool(boot), "transfers": check_transfer(stock, patched, boot, manifest)}
    if boot:
        report["interruption"] = check_interruption(stock, patched, boot, manifest)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
