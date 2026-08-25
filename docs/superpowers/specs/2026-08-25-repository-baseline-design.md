# Repository Baseline Design

## Objective

Prepare a single, self-describing repository tree from which both hardware variants can continue development. The baseline will be assembled on `integration/repository-baseline`; `main`, `develop`, and the existing design branches will not be merged, rewritten, pushed, or deleted by this change.

## Repository Model

Both supported variants will coexist under `hardware/`:

- `hardware/One_Board_Design/` contains the existing integrated KiCad design.
- `hardware/Split_Board_Design/` contains a planned Control Board, Relay Board, and controlled inter-board interface area.
- `hardware/libraries/` remains the single shared source for project symbols, footprints, and 3D models.
- `hardware/templates/` remains available for future reusable KiCad templates.

Future work uses short-lived `feature/*`, `fix/*`, and `docs/*` branches. `develop` is optional as an integration branch, while `main` must contain every artifact required to reproduce a selected baseline. Hardware variants are directories, not permanent product branches.

## Documentation Changes

- Rewrite `docs/workflow.md` as valid UTF-8 Vietnamese and align it with the coexistence model.
- Normalize documented repository paths to lowercase top-level names.
- Update the root and hardware READMEs to describe the implemented tree rather than an aspirational or branch-dependent tree.
- Correct the root license statement to MIT.
- Add `CHANGELOG.md` using Keep a Changelog-style sections without inventing released versions.
- Add an architecture decision record explaining why variants coexist in one tree.

## Split-Board Skeleton

The existing Split-Board overview will be imported from `design/split-board`. Three focused subdirectories will be added:

- `Control_Board/README.md`: scope of the future controller PCB.
- `Relay_Board/README.md`: scope of the future relay/high-current PCB.
- `interface/README.md`: required ownership and interface-contract fields; no electrical values or pinout will be invented.

## Controlled Artifact Import

Copy the current workspace BOM files into `components/bom/` and the INA241A2 calculation PDF into `docs/04-calculations/`. Add index READMEs that record the source filenames and state that the files require revision control and technical verification before release.

Import the three project layout/netclass Markdown guides into `docs/03-design/guides/`. Do not import the external review image set or snapshots in this change because their revision and provenance have not been normalized.

## Automated Repository Check

Add `tools/check_repository.py` and a GitHub Actions workflow. The checker will:

- Require the baseline directories and variant README files.
- Reject known mojibake markers in Markdown.
- Validate relative Markdown links that point to local files or directories.
- Reject uppercase forms of the documented top-level `docs/` and `hardware/` paths in Markdown.
- Run without third-party Python dependencies.

The workflow will run this checker on pushes and pull requests. KiCad ERC/DRC will remain a documented engineering gate rather than a passing CI gate in this baseline because the existing board currently has unresolved violations.

## Constraints

- Do not edit KiCad source or library files.
- Do not commit, push, merge, rebase, or delete existing branches.
- Do not claim that either hardware design is verified or release-ready.
- Preserve binary source artifacts exactly when copying them into the repo.
- Leave external review media and snapshots in the workspace parent until provenance and revision are reviewed.

## Acceptance Criteria

- Both hardware variant directories exist in the same working tree.
- Root documentation matches the actual repository tree and MIT license.
- Workflow documentation is readable UTF-8 and uses consistent lowercase paths.
- BOM, calculation, and selected design-guide artifacts are tracked candidates inside the repo.
- The repository checker exits successfully and all local Markdown links resolve.
- `git diff --check` reports no whitespace errors.
- No KiCad source or shared library file is modified.
