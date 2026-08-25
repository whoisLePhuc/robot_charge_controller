# Repository Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce one coherent repository tree containing both hardware variants, shared assets, accurate documentation, controlled source artifacts, and an automated organization check.

**Architecture:** Start from the existing One-Board branch content on `integration/repository-baseline`, add the Split-Board skeleton as a sibling, and keep shared libraries at `hardware/libraries/`. Repository documentation and automation describe and validate this coexistence model without changing KiCad sources.

**Tech Stack:** Markdown, Python 3 standard library, GitHub Actions, PowerShell file-copy verification, Git

## Global Constraints

- Do not edit KiCad source or library files.
- Do not commit, push, merge, rebase, or delete existing branches.
- Do not claim that either hardware design is verified or release-ready.
- Preserve binary source artifacts exactly when copying them into the repo.
- Use lowercase top-level path names in tracked files and documentation.
- Leave external review media and snapshots outside the repo until provenance is normalized.

---

### Task 1: Coexisting hardware variant tree

**Files:**
- Create: `hardware/Split_Board_Design/README.md`
- Create: `hardware/Split_Board_Design/Control_Board/README.md`
- Create: `hardware/Split_Board_Design/Relay_Board/README.md`
- Create: `hardware/Split_Board_Design/interface/README.md`
- Modify: `hardware/One_Board_Design/README.md`
- Modify: `hardware/README.md`

**Interfaces:**
- Consumes: Existing One-Board design and Split-Board overview from `design/split-board`.
- Produces: Both variants in one discoverable hardware tree with working cross-links.

- [x] **Step 1: Add the Split-Board overview and focused subdirectory READMEs**

Use the reviewed Split-Board overview and state explicitly that connector pinout, grounding, power, protection ownership, and electrical limits require a controlled interface contract.

- [x] **Step 2: Normalize hardware documentation paths**

Normalize documented top-level hardware paths to lowercase and describe both variants as sibling directories rather than branch-only content.

- [x] **Step 3: Verify both variants are discoverable**

Run:

```powershell
Test-Path hardware/One_Board_Design/README.md
Test-Path hardware/Split_Board_Design/README.md
```

Expected: both commands return `True`.

### Task 2: Controlled project artifacts

**Files:**
- Create: `components/bom/BOM.xlsx`
- Create: `components/bom/Full_BOM.xlsx`
- Create: `components/bom/README.md`
- Create: `docs/04-calculations/INA241A2IDDFR_Output_Calculation.pdf`
- Modify: `docs/04-calculations/README.md`
- Create: `docs/03-design/guides/relay_60V_20A_EMI_layout_component_guideline.md`
- Create: `docs/03-design/guides/robot-hv-charge-controller-2-layer-layout-routing-guide.md`
- Create: `docs/03-design/guides/robot-hv-charge-controller-netclass-guide.md`
- Create: `docs/03-design/guides/README.md`
- Modify: `components/README.md`

**Interfaces:**
- Consumes: Workspace-parent BOM, calculation, and three design-guide source files.
- Produces: Revision-visible artifact candidates inside the Git repository.

- [x] **Step 1: Copy source artifacts without transformation**

Use `Copy-Item -LiteralPath` and retain the original filenames.

- [x] **Step 2: Verify binary copies by SHA-256**

Run `Get-FileHash -Algorithm SHA256` on every binary source and destination pair. Expected: each pair has an identical hash.

- [x] **Step 3: Add artifact indexes**

Document source location, current evidence limitation, and the rule that release artifacts require a recorded revision and review.

### Task 3: Repository policy and navigation

**Files:**
- Create: `CHANGELOG.md`
- Modify: `README.md`
- Rewrite: `docs/workflow.md`
- Create: `docs/decisions/0001-coexisting-hardware-variants.md`
- Modify: `docs/README.md`

**Interfaces:**
- Consumes: Approved repository baseline design.
- Produces: Accurate navigation, UTF-8 workflow policy, and recorded architecture rationale.

- [x] **Step 1: Rewrite workflow policy**

Define `main` as a reproducible baseline, optional `develop` as integration, and `feature/*`, `fix/*`, and `docs/*` as short-lived branches. Explicitly state that hardware variants coexist in the tree.

- [x] **Step 2: Update root navigation and status**

Remove the nonexistent `hardware/kicad/` and unselected-license claims; link both variants, BOM, calculations, workflow, and ADR.

- [x] **Step 3: Add changelog and ADR**

Record the repository-baseline work under an `Unreleased` section and document the coexistence decision, alternatives, consequences, and migration rule.

### Task 4: Repository checker

**Files:**
- Create: `tools/check_repository.py`
- Modify: `tools/README.md`

**Interfaces:**
- Consumes: Repository root path determined from the script location.
- Produces: Exit code `0` on a valid baseline and nonzero with actionable diagnostics on violations.

- [x] **Step 1: Run the pre-implementation checks and record expected failures**

Run searches for mojibake, uppercase paths, missing Split-Board directories, and broken Markdown links. Expected: the current tree fails at least the mojibake and missing Split-Board checks.

- [x] **Step 2: Implement the checker using Python standard library only**

The checker must validate required paths, scan Markdown text for mojibake and uppercase path references, parse inline Markdown links, ignore HTTP/mailto/anchor links, resolve local paths relative to each document, and print a final error count.

- [x] **Step 3: Run the checker**

Run:

```powershell
python tools/check_repository.py
```

Expected: `Repository check: PASS` and exit code `0`.

### Task 5: Continuous integration

**Files:**
- Create: `.github/workflows/repository-quality.yml`

**Interfaces:**
- Consumes: `tools/check_repository.py` and Python 3.
- Produces: Repository checks on pushes and pull requests.

- [x] **Step 1: Add the workflow**

Use `actions/checkout@v4`, `actions/setup-python@v5`, Python `3.12`, and run `python tools/check_repository.py` on Ubuntu.

- [x] **Step 2: Validate workflow syntax structurally**

Parse the YAML with the bundled workspace Python YAML library when available, and confirm the referenced script exists.

### Task 6: Final scope and integrity verification

**Files:**
- Verify all changed and added files.

**Interfaces:**
- Consumes: Completed repository baseline.
- Produces: Evidence that organization checks pass and KiCad sources were untouched.

- [x] **Step 1: Run organization and whitespace checks**

Run `python tools/check_repository.py` and `git diff --check`. Expected: both exit `0`.

- [x] **Step 2: Confirm KiCad sources and libraries are unchanged**

Run:

```powershell
git diff --name-only -- '*.kicad_sch' '*.kicad_pcb' '*.kicad_pro' '*.kicad_sym' '*.kicad_mod' fp-lib-table sym-lib-table
```

Expected: no output.

- [x] **Step 3: Review scope**

Run `git status --short` and confirm changes are limited to repository organization, documentation, imported evidence artifacts, split-board scaffolding, and validation automation.
