# Control Board

This directory is reserved for the low-voltage controller PCB of the Split-Board Design.

## Intended Scope

- ESP32 supervision and state control.
- Low-voltage logic power required by the controller electronics.
- USB/programming support and diagnostic access.
- CAN, RS485, and 3.3 V UART communication interfaces.
- External low-voltage inputs and outputs assigned to this board by the interface decision.

No KiCad project has been created. Schematic capture must wait until the [inter-board interface contract](../interface/README.md) defines power, signal, reference-ground, startup, shutdown, and fault behavior.

The final allocation of sensing analog front ends, relay-coil drive, and auxiliary field outputs remains an open architecture decision.
