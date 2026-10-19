# QIDI Max 4 stock config snapshots

Source repository: https://github.com/thelegendtubaguy/Qidi-Max4-Defaults

Runtime restore path: `installer/runtime/legacy_manual_install.py`.

Bundled restore roots:

- `installer/stock/qidi-max4-defaults/firmwares/01.01.06.03/config/`
- `installer/stock/qidi-max4-defaults/firmwares/01.01.06.04/config/`
- `installer/stock/qidi-max4-defaults/firmwares/01.01.06.05/config/`
- `installer/stock/qidi-max4-defaults/firmwares/01.01.07.01/config/`

Firmware `01.01.06.05` uses defaults commit `c75c0b662d1d4fd2a7dd19e49843b91e6544a1ed`, release archive `QD_MAX4_01.01.06.05_20260804_Release.zip` with SHA-256 `b1826d1aed274c7233b4a23a3a3e5c0b4e9655c5d03188a8b6f3561f0d3f2de7`, firmware-manifest SHA-256 `486056fb9a39417d50c9e9691a79839aaf48911b1486bdd8b88957a078ead564`, and SOC payload SHA-256 `3df20701bf6e3a2914b0e2511e18bb5a3ec17b1170797dc3d503608c20efc893`.

Firmware `01.01.07.01` uses defaults commit `a92b41236ea8942e12e748106393bb8b32f31c54`, release archive `QD_MAX4_01.01.07.01_20261016_Release.zip` with SHA-256 `0cc97445e77295116adaa665ff463e77608d4929520bd7cd46e732fbb0a6ecf2`, firmware-manifest SHA-256 `dc7355726be2741fd48c1aa8dcc43e53d33da48687ff8faef76365e31844c10b`, and SOC payload SHA-256 `668c65bf6a1f40252d81c93e6962fcd7e09b2486291ef7665d9c4aa22e108854`.

Legacy manual-install reset selects the restore root by detected firmware.

Excluded runtime files: `config/MCU_ID.cfg`, `config/box.cfg`, `config/fluidd.cfg`, and `config/saved_variables.cfg`.
