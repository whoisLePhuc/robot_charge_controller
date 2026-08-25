# Robot Charge Controller

An ESP32-based controller for switching, monitoring, and supervising a high-power DC charging path for mobile robots. The project supports two hardware architectures that coexist in this repository and share the same project-local KiCad libraries.

> [!WARNING]
> This project targets a charging path of up to **60 VDC and 20 A**. This energy level can cause arcing, overheating, fire, equipment damage, or personal injury. Both hardware variants are prototypes under development and have not been validated for production or safety-critical use.

## Hardware Variants

| Variant | Description | Current state |
|---|---|---|
| [One-Board Design](hardware/One_Board_Design/README.md) | Relay path, sensing, auxiliary power, ESP32 control, and communications on one PCB | KiCad schematic and PCB present; engineering checks remain open |
| [Split-Board Design](hardware/Split_Board_Design/README.md) | Control Board and Relay Board connected through a controlled interface | Requirements scaffold present; KiCad projects not started |

Both variants are directories in the same repository. Branches are used for temporary changes, not as the only place where a hardware variant can be discovered.

## Design Targets

| Item | Target | Evidence status |
|---|---:|---|
| Main bus voltage | Up to 60 VDC | Project requirement |
| Continuous current | Up to 20 A | Requires electrical and thermal verification |
| Auxiliary input | 24 VDC | Project requirement |
| Controller | ESP32-WROOM-32E | Present in the One-Board Design |
| Communications | CAN, RS485, and 3.3 V UART | Present in the One-Board Design |
| PCB baseline | Two layers, nominal 1.6 mm, 2 oz finished copper on F.Cu and B.Cu | Selected baseline; fabricator stack-up and finish require review |

This project does not replace a battery charger or battery management system. Battery-chemistry charging control, cell balancing, and pack-level protection remain the responsibility of the external charger and BMS.

## Repository Structure

~~~text
robot_charge_controller/
├── README.md
├── CHANGELOG.md
├── LICENSE
├── components/
│   └── bom/                       # BOM workbook candidates and index
├── docs/
│   ├── 01-requirements/
│   ├── 02-architecture/
│   ├── 03-design/
│   ├── 04-calculations/
│   ├── 05-reviews/
│   ├── 06-verification/
│   ├── decisions/                 # Architecture decision records
│   └── workflow.md
├── firmware/
├── hardware/
│   ├── One_Board_Design/
│   ├── Split_Board_Design/
│   ├── libraries/                 # Shared KiCad symbols, footprints, and 3D models
│   └── templates/
├── manufacturing/
├── simulation/
├── test/
└── tools/
~~~

## Getting Started

1. Read the [development workflow](docs/workflow.md).
2. Select a hardware variant from the table above.
3. Review the variant README, requirements, open findings, and shared-library path rules.
4. Open a KiCad project only from its variant directory and keep `hardware/libraries/` in the repository layout.
5. Run the repository organization check:

   ~~~sh
   python tools/check_repository.py
   ~~~

6. Before any hardware gate decision, regenerate ERC/DRC reports and record the exact board revision and open findings.

## Project Evidence

- [BOM candidates](components/bom/README.md)
- [Engineering calculations](docs/04-calculations/README.md)
- [Design guides](docs/03-design/guides/README.md)
- [Architecture decisions](docs/decisions/README.md)
- [Verification records](docs/06-verification/README.md)
- [Manufacturing records](manufacturing/README.md)

## Status

| Area | State |
|---|---|
| Repository baseline | Established; both hardware variants coexist in the repository tree |
| One-Board schematic and PCB | Present; unresolved review actions remain |
| Split-Board requirements | Initial scaffold present |
| Split-Board schematic and PCB | Not started |
| Firmware | Scaffold only |
| Simulation | Scaffold only |
| Prototype verification | Not confirmed by controlled repository evidence |
| Production release | Not authorized |

## License

This repository is licensed under the [MIT License](LICENSE). Component models, third-party libraries, datasheets, and imported engineering artifacts may have separate terms that must be reviewed before redistribution.
