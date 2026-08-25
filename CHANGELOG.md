# Changelog

All notable repository changes are documented in this file. The project has not declared a versioned hardware release yet.

## Unreleased

### Added

- Coexisting `One_Board_Design` and `Split_Board_Design` repository structure.
- Split-Board Control Board, Relay Board, and interface-contract scaffolds.
- Controlled-location candidates for BOM workbooks, engineering calculations, and PCB design guides.
- Repository organization checker and continuous-integration workflow.
- Architecture decision record for the hardware-variant layout.

### Changed

- Repository workflow from long-lived product branches to directory-based variants and short-lived change branches.
- Documentation paths normalized to lowercase top-level names.
- Repository navigation and license status aligned with the actual tree.

### Fixed

- Corrupted UTF-8 documentation text.
- Broken cross-variant README links caused by keeping each variant on a separate branch.
