# Inter-Board Interface Contract

This directory will hold the controlled contract between the Control Board and Relay Board. It is intentionally free of invented pin assignments or electrical values.

The first approved interface revision must define:

- Connector family, pin numbering, keying, retention, and mating-cycle requirement.
- Producer and consumer for every signal and power rail.
- Voltage/current range, logic thresholds, reference node, direction, and default safe state.
- Startup, shutdown, brownout, hot-plug, and partial-power behavior.
- Relay command, feedback, watchdog, and fault-response behavior.
- Grounding, shielding, cable length, conductor size, routing, and EMC constraints.
- Ownership of sensing, filtering, isolation, transient protection, and current limiting.
- Behavior for missing, reversed, intermittent, open-circuit, and short-circuit connections.
- Mechanical constraints, test points, inspection method, and measurable acceptance criteria.

Until those fields are defined and reviewed, the interface status is **not defined** and neither board schematic should treat it as a stable dependency.
