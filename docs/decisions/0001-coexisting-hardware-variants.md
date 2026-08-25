# ADR-0001: Keep Hardware Variants in One Repository Tree

- **Status:** Accepted for the integration baseline
- **Date:** 2026-08-25
- **Scope:** Repository organization only

## Context

The One-Board and Split-Board architectures were developed on separate long-lived branches. Each branch contained only its own variant, which made cross-links fail, hid designs from users of the default branch, duplicated common documentation changes, and allowed branch histories to diverge.

Both variants already have distinct directory names and use the same project-local KiCad libraries. Directory isolation is therefore sufficient to let the designs coexist without relying on permanent product branches.

## Decision

Store all supported hardware variants under `hardware/` on the same baseline:

```text
hardware/
├── One_Board_Design/
├── Split_Board_Design/
├── libraries/
└── templates/
```

Use short-lived `feature/*`, `fix/*`, and `docs/*` branches for changes. `develop` may be used for integration but must not be the only location of an artifact required to reproduce a baseline.

## Alternatives Considered

### Permanent branch per hardware variant

Rejected because discoverability, cross-variant documentation, shared-library updates, release traceability, and common fixes become branch-dependent.

### Separate repository per hardware variant

Deferred because both variants currently share requirements, documentation, component assets, and KiCad libraries. Separate repositories would add synchronization and release-management overhead without an established need for independent ownership or lifecycle.

## Consequences

- A clone of the baseline exposes both variants and their status.
- Shared-library changes can be reviewed against every affected project in one tree.
- CI can enumerate hardware projects without checking out product branches.
- Repository size increases on the baseline because all supported design artifacts are present.
- Variant READMEs must clearly distinguish implemented, planned, and verified states.

## Migration Rule

The existing long-lived design branches remain unchanged for historical comparison until the integration baseline is reviewed. New development begins from the accepted baseline using short-lived branches. Branch deletion, merge, and release remain explicit human decisions.
