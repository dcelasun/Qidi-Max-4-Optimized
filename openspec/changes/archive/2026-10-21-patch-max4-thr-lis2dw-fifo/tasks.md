# Tasks

## 1. Guarded package generation

- [x] 1.1 Add the versioned patch manifest and generator; build from the pinned Max 4 archive and verify the image's exact output hash and five-byte delta.
- [x] 1.2 Document build commands, artifact identity, preserved vendor contents, same-version flashing limitations, and full-update configuration effects; run the documented build command.

## 2. Independent validation

- [x] 2.1 Add a standalone archive/image checker with bounded ARM emulation and safety rejection checks; verify all FIFO statuses, reporting boundaries, scheduler wake state, and untouched payloads against the real archive.
- [x] 2.2 Add a path-scoped CI check and pinned check dependencies; run the same build/check commands locally and confirm repeat builds have identical hashes.

## 3. Integration audit

- [x] 3.1 Validate OpenSpec, installer release metadata, and the unchanged installer bundle; inspect the final diff and generated artifacts, with no flashing or publishing.
