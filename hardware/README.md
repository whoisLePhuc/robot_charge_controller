# Hardware

This directory contains the Robot Charge Controller hardware variants and their shared KiCad resources.

## Structure

| Path | Purpose | Status |
|---|---|---|
| [`One_Board_Design/`](One_Board_Design/README.md) | Integrated relay, sensing, power, controller, and communications PCB | KiCad project present; under review |
| [`Split_Board_Design/`](Split_Board_Design/README.md) | Separate Control Board and Relay Board architecture | Requirements scaffold; KiCad projects not started |
| [`libraries/`](libraries/README.md) | Shared symbols, footprints, and 3D models | Shared source of truth |
| [`templates/`](templates/README.md) | Reusable KiCad templates | Scaffold |

Both hardware variants coexist in the repository. Development work should use short-lived branches; a hardware variant must not be hidden permanently on a branch that users cannot discover from the default repository tree.

All KiCad source and library modifications must be made through the approved Konnect workflow. A directory being present does not mean its design has passed ERC, DRC, engineering review, or release gates.
