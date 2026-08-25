# Firmware

This directory is reserved for ESP32 firmware that supervises the Robot Charge Controller.

## Structure

- include/: public headers and interfaces.
- src/: application source.
- lib/: focused reusable modules.
- test/: host-side and target-side tests.

The firmware implementation has not started. Hardware-safe states, interface contracts, fault handling, timing, and test strategy must be defined before control logic is implemented.
