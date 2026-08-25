# Relay Board

This directory is reserved for the relay and high-current PCB of the Split-Board Design.

## Intended Scope

- DC-rated relay and the switched charging-current path.
- High-current connectors and copper paths.
- Local protection, sensing, and relay-drive functions assigned to this board by the architecture decision.
- Test access required for independent power-stage bring-up.

No KiCad project has been created. The board requirements must define normal current, fault current, transient environment, thermal limits, clearances, connectors, safe state, and the [inter-board interface contract](../interface/README.md) before schematic or PCB implementation.

The 60 VDC/20 A values are design requirements, not verified operating capability.
