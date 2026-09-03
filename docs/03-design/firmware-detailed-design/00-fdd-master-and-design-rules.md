# Firmware Detailed Design Master and Design Rules

## 1. Document control

| Field | Value |
|---|---|
| Document ID | `RCC-FW-FDD-000` |
| Project | Robot Charge Controller |
| Applicable hardware variant | Split Board Design — Control Board + Relay Board |
| Record revision | Draft 0.1 |
| Status | Under review |
| Prepared at | 2026-09-03, Asia/Bangkok (UTC+07:00) |
| Prepared by | Codex drafting support, based on the SRS, Architecture, ICD, and explicit user-selected design decisions |
| Requirements source | `RCC-FW-SRS-001`, Draft 0.1 |
| Architecture source | `RCC-FW-ARCH-001`, Draft 0.2 |
| Interface source | `RCC-FW-ICD-001`, Draft 0.1 |
| Platform API baseline | [ESP-IDF Programming Guide v6.1 — ESP32 API Reference](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32/api-reference/index.html) |
| Hardware source baseline | Git commit `fe85ff2` plus the uncommitted hardware changes identified in the SRS |
| Firmware source baseline | Pre-implementation; no firmware source revision exists yet |
| Authoritative language | English |

This document is the master index and common design-rule baseline for the Firmware
Detailed Design (FDD) document set. It does not approve hardware, certify safety or
compliance, accept residual risk, or authorize a production release.

### 1.1 Revision history

| Revision | Date | Change |
|---|---|---|
| Draft 0.1 | 2026-09-03 | Initial FDD document map, dependency order, and common design rules |

## 2. Purpose, scope, and document boundary

The FDD translates the approved requirements, architecture, and interface contracts
into implementation-ready module designs. This master document defines:

- the FDD document set and its implementation order;
- the precedence and change-control rules for design inputs;
- common rules for layering, APIs, data, memory, concurrency, time, safety, error
  handling, build profiles, and testing;
- permitted uses and restrictions for software design patterns;
- traceability, review, and completion criteria applied to every FDD document.

This document does not define the complete algorithm, exact C API, data layout,
FreeRTOS parameters, or test vectors of an individual module. Those details belong to
the corresponding subordinate FDD document. External wire semantics and transport
bindings remain controlled by the ICD.

### 2.1 In scope

- ESP-IDF and FreeRTOS firmware for the ESP32-WROOM-32E.
- The five-layer logical architecture and event-driven runtime model.
- Source-level dependency and component-boundary rules.
- Safety-control, measurement, persistence, command, transport, and diagnostic design
  constraints shared across modules.
- Host, target, HIL, and controlled-bench verification seams.
- Production and test build separation.

### 2.2 Out of scope

- Battery charge regulation, CC/CV control, or BMS behavior.
- Supervision of the separate 24 V auxiliary source.
- Detailed electrical design of the Control Board or Relay Board.
- Numeric hard-fault thresholds not yet derived from controlled hardware evidence.
- Complete product FMEA, cybersecurity approval, safety certification, EMC
  compliance, or production release authorization.

## 3. Normative language and artifact precedence

`Shall` identifies a mandatory design rule. `Should` identifies a recommendation that
requires recorded justification if not followed. `May` identifies an allowed option.

When artifacts disagree, the following precedence applies:

1. Controlled product safety, legal, and regulatory requirements.
2. `RCC-FW-SRS-001`.
3. `RCC-FW-ARCH-001`.
4. `RCC-FW-ICD-001` for external communication contracts.
5. This FDD master and design-rules document.
6. The responsible subordinate FDD document.
7. Firmware source code, build configuration, and tests.

A lower-level artifact shall not silently override a higher-level artifact. A conflict
shall be recorded as an open action, resolved in the controlling artifact, and then
propagated downward with revision traceability.

An unresolved numeric value shall be represented by a stable symbolic name and a
linked open action. A typical value, absolute-maximum rating, or placeholder shall not
be promoted to a safety limit or acceptance criterion without evidence.

## 4. Controlled FDD document set

The subordinate documents are intentionally divided by dependency and risk. Their
numbers define the preferred design sequence, not a run-time execution order.

| Order | Document ID | File | Primary responsibility | Required inputs | Exit evidence |
|---:|---|---|---|---|---|
| 00 | `RCC-FW-FDD-000` | `00-fdd-master-and-design-rules.md` | FDD map, common rules, gates, and traceability conventions | SRS, Architecture, ICD baseline | Reviewed common-rule baseline and carried open actions |
| 01 | `RCC-FW-FDD-001` | `01-common-types-and-module-ports.md` | Shared types, public ports, status model, ownership, units, and component boundaries | 00, Architecture core data models | API review, dependency check, host-compilable contract tests |
| 02 | `RCC-FW-FDD-002` | `02-measurement-pipeline-design.md` | ADC DMA acquisition, channel association, calibration application, filtering, validity, freshness, and publication | 01, analog evidence as available | Algorithm vectors, target acquisition tests, evidence-linked timing limits |
| 03 | `RCC-FW-FDD-003` | `03-persistence-and-session-guard-design.md` | Versioned records, atomic generations, priority, session write-ahead guard, recovery, and power-cut behavior | 01, NVS behavior evidence | Host model tests, target NVS tests, power-cut/failure-injection matrix |
| 04 | `RCC-FW-FDD-004` | `04-fault-inhibit-reset-design.md` | Fault registry, qualification, inhibit mask, reset classification, clearing, recurrence, and escalation | 01–03, hardware/system fault evidence | Complete transition table and fault-injection tests |
| 05 | `RCC-FW-FDD-005` | `05-control-state-machine-design.md` | Control states, event precedence, guards, actions, session establishment, completion, re-arm, and relay ownership | 01–04 | State/transition coverage, host sequence tests, HIL safety-path tests |
| 06 | `RCC-FW-FDD-006` | `06-configuration-calibration-manager-design.md` | Staging, validation, commit, schema compatibility, service lock, and calibration workflow | 01, 02, 03; Configuration and Calibration Specification | Schema tests, invalid-update tests, target commit tests |
| 07 | `RCC-FW-FDD-007` | `07-command-router-design.md` | Authorization, validation, normalization, duplicates, result lifecycle, urgent STOP routing, and overload behavior | 01, 04–06, ICD common model | Command matrix tests, duplicate/overflow/authority tests |
| 08 | `RCC-FW-FDD-008` | `08-transport-adapter-design.md` | CAN, RS485, operational UART, service UART, framing, segmentation, recovery, and trusted metadata | 01, 07, resolved ICD binding items | Golden vectors, driver/loopback tests, HIL interoperability tests |
| 09 | `RCC-FW-FDD-009` | `09-runtime-task-and-ipc-design.md` | Task creation, core affinity, priorities, queues, notifications, snapshots, watchdogs, and overload budgets | 01–08 | Static resource table, target load tests, measured scheduling evidence |
| 10 | `RCC-FW-FDD-010` | `10-boot-time-diagnostics-build-design.md` | Safe boot, initialization order, diagnostics, event log, time service, build profiles, and test-backend isolation | 01–09 | Boot-failure matrix, profile inspection, target recovery tests |
| 11 | `RCC-FW-FDD-011` | `11-integration-budgets-and-traceability.md` | End-to-end timing, memory, CPU, NVS endurance, interface load, verification, and final traceability | 00–10 plus controlled measurement evidence | Closed budget tables, verification matrix, integration gate assessment |

`README.md` may provide navigation but shall not replace the controlled scope,
revision, or gate information in these documents.

## 5. Design progression and review gates

### 5.1 Dependency phases

| Phase | Documents | Design outcome | May begin when | Shall not pass its gate until |
|---|---|---|---|---|
| A — Foundation | 00–01 | Stable rules, types, ports, ownership, and source boundaries | Architecture and ICD drafts are available | Contradictory contracts are resolved or explicitly carried |
| B — Safety mechanisms | 02–04 | Trusted measurements, durable safety state, and deterministic fault/inhibit policy | 01 interfaces are stable enough for review | Affected analog, storage, reset, and fault evidence is linked |
| C — Control behavior | 05–06 | Complete charging state machine and controlled configuration/calibration lifecycle | Required outputs of 02–04 are baselined | Every relay-enabling guard and safe-exit path has verification coverage |
| D — External integration | 07–08 | Common command handling and transport adapters | Control/service contracts are stable | Applicable ICD open items and wire bindings are resolved |
| E — Runtime integration | 09–10 | Deployable task graph, boot flow, diagnostics, and isolated build profiles | Module interactions are known | Bounded resource and failure behavior is demonstrated on target |
| F — Closure | 11 | System budgets and end-to-end traceability | 00–10 are internally reviewed | Numeric budgets and verification evidence support the integration assessment |

Work may overlap where dependencies are stable, but no document shall claim an input
is closed merely because drafting has started. A downstream document shall list the
exact revision and status of every upstream input it uses.

### 5.2 Required content of every subordinate FDD

Each subordinate FDD shall contain, as applicable:

1. Document control, revision history, and exact source revisions.
2. Purpose, scope, exclusions, assumptions, and unresolved dependencies.
3. Responsibilities and explicit non-responsibilities.
4. Layer/component allocation and dependency direction.
5. Selected design patterns and the reason each is used.
6. Public interfaces, types, units, preconditions, postconditions, and error returns.
7. Private data, ownership, lifetime, mutability, and initialization rules.
8. Normal, degraded, fault, timeout, reset, and recovery flows.
9. Concurrency context, synchronization, ISR behavior, and overload handling.
10. Static and dynamic resource bounds.
11. Timing constraints and the evidence supporting numeric values.
12. Verification methods, numeric acceptance criteria, and traceability.
13. Open actions, residual risks, AI assessment, and human-decision boundary.

## 6. Non-negotiable system invariants

The following rules restate and specialize the architecture invariants. Subordinate
designs shall reference these IDs rather than restating them with changed semantics.

| Rule ID | Mandatory rule |
|---|---|
| `FDD-RULE-SAFE-001` | `ControlSafetyTask` is the sole owner of the control state machine and the only task permitted to command `relay_port`. |
| `FDD-RULE-SAFE-002` | The relay default is OFF/open during reset, boot, incomplete initialization, service lock, inhibit, and fault. |
| `FDD-RULE-SAFE-003` | Relay ON is permitted only in `RELAY_CLOSING`, `CHARGE_VERIFY`, and `CHARGING`. |
| `FDD-RULE-SAFE-004` | STOP, fault, inhibit, and shutdown paths issue the physical relay-OFF action before persistence or diagnostic work. |
| `FDD-RULE-SAFE-005` | Relay close is forbidden until precheck succeeds and a correlated persistent `SESSION_ARMED` commit is acknowledged. |
| `FDD-RULE-SAFE-006` | Missing, stale, saturated, inconsistent, or implausible safety measurements are invalid inputs and shall not be substituted with last-known-good values for relay-enabling decisions. |
| `FDD-RULE-SAFE-007` | Urgent STOP and urgent measurement faults shall not depend on capacity in the normal command queue. |
| `FDD-RULE-SAFE-008` | Communication loss, congestion, malformed traffic, logging, or UTC synchronization shall not block control progression or autonomous operation. |
| `FDD-RULE-SAFE-009` | Invalid required configuration, calibration, or safety persistence shall retain relay OFF and enter the specified conservative state. |
| `FDD-RULE-SAFE-010` | Production firmware shall contain no mock physical backend or test fault-injection command. |
| `FDD-RULE-SAFE-011` | Runtime configuration shall not change hardware-bound sampling, hard safety limits, or fault-escalation policy. |
| `FDD-RULE-SAFE-012` | The values 60 V and 20 A are maximum normal operating values; they shall not be used as hard-fault thresholds without a controlled derivation. |

Any requested exception to these rules requires a change to the controlling SRS or
Architecture and a separate responsible-human decision. This FDD cannot waive them.

## 7. Five-layer dependency rules

The five logical layers remain independent from the number of FreeRTOS tasks. One
task may coordinate modules from more than one layer through their public interfaces;
one layer may contain multiple tasks or no dedicated task.

| Layer | Name | Allowed content | Prohibited authority |
|---:|---|---|---|
| `L1` | Platform | ESP-IDF, FreeRTOS, vendor peripheral and system primitives | Project charging policy |
| `L2` | Hardware Abstraction and Device Drivers | ADC, relay, storage, communication, time/reset primitives | Permission to start/continue charging |
| `L3` | Infrastructure Services | Persistence, transports, codec, diagnostics, and time services | Direct state transition or relay command |
| `L4` | Domain and Safety | Measurement interpretation, configuration/calibration rules, state machine, fault/inhibit policy | Transport-specific framing or unmediated vendor-driver access |
| `L5` | Application and Integration | Boot composition, command routing, protocol model, and build-profile composition | Bypass of L4 safety decisions |

| Rule ID | Dependency rule |
|---|---|
| `FDD-RULE-LAYER-001` | Compile-time dependencies shall point downward: `L5 → L4 → L3 → L2 → L1`. |
| `FDD-RULE-LAYER-002` | A higher layer may skip a lower layer only through a documented public interface and only when the Architecture assigns that dependency. |
| `FDD-RULE-LAYER-003` | A lower layer shall not include or link to a concrete higher-layer implementation. Runtime information may travel upward only through a defined event, callback contract, queue item, notification, or immutable snapshot. |
| `FDD-RULE-LAYER-004` | Circular component dependencies are prohibited. A cycle shall be broken by moving the shared contract downward or introducing a narrow port. |
| `FDD-RULE-LAYER-005` | `L4` domain logic should avoid ESP-IDF-specific types. Adapter boundaries shall translate `esp_err_t`, driver events, and platform handles into project-defined contracts. |
| `FDD-RULE-LAYER-006` | Access to a driver or transport does not grant safety authority. Authorization and physical capability remain separate concerns. |

## 8. Component and source organization rules

The final directory tree is controlled by FDD-01, but the following rules apply to
its design:

- An ESP-IDF component shall represent a cohesive, independently testable
  responsibility. Trivial files shall not each become separate components.
- Public headers shall expose only the minimum stable contract. Private headers,
  state, FreeRTOS handles, and backend details shall remain internal to the component.
- `REQUIRES` and `PRIV_REQUIRES` shall express the dependency graph. Public
  dependencies shall not be declared merely for build convenience.
- Component initialization shall be explicit, ordered, fallible, and idempotent where
  retry is supported. No component shall rely on C static initialization order for a
  safety-relevant side effect.
- Hardware pins, channel patterns, hard limits, and build identity shall be
  release-controlled data associated with the hardware/firmware revision.
- Wi-Fi and Bluetooth components shall not be initialized or linked into firmware v1
  unless the SRS is revised.

### 8.1 Naming baseline

Until FDD-01 closes `FDD-OPEN-002`, the following naming baseline shall be used for
draft interfaces:

| Item | Rule | Example |
|---|---|---|
| Source/header/component | Lower snake case | `measurement_pipeline.c` |
| Public C symbol | `rcc_` prefix plus lower snake case | `rcc_measurement_get_latest()` |
| Type | Lower snake case with `_t` suffix | `rcc_measurement_snapshot_t` |
| Enumeration constant/macro | Upper snake case with `RCC_` prefix | `RCC_FAULT_ADC_STALE` |
| Boolean/predicate | Positive, unambiguous condition | `measurement_valid` |
| Quantity field | Unit included in the name | `voltage_mv`, `current_ma`, `age_us` |
| Stable design/test ID | Document-scoped uppercase identifier | `FDD-MEAS-ALG-001` |

Names shall distinguish physical raw values, calibrated engineering values, filtered
values, and decision-qualified states. Generic names such as `value`, `timeout`, or
`status` shall not cross a public boundary without contextual qualification.

## 9. C API and data-contract rules

| Rule ID | Rule |
|---|---|
| `FDD-RULE-API-001` | Public contracts shall use fixed-width integer types for quantities, counters, revisions, IDs, persistence, and external-interface data. |
| `FDD-RULE-API-002` | Voltage shall use millivolts, signed current shall use milliamperes, and non-negative durations shall use milliseconds unless a documented driver or timing contract requires microseconds. |
| `FDD-RULE-API-003` | Public functions shall state caller/callee ownership, object lifetime, thread/ISR context, blocking behavior, timeout, and reentrancy. |
| `FDD-RULE-API-004` | Mutable global variables and externally writable module state are prohibited. Read-only build constants may be exposed through const data or accessors. |
| `FDD-RULE-API-005` | Input pointers shall be `const` when the callee does not modify the object. Nullability and valid ranges shall be explicit. |
| `FDD-RULE-API-006` | Native C structure layout shall not be serialized directly to NVS or a communication interface. Encoding shall define field order, width, byte order, version, and integrity coverage. |
| `FDD-RULE-API-007` | Recoverable run-time errors shall be returned through project-defined status/reason data. Assertions shall not be the sole production response to an external, storage, sensor, or resource failure. |
| `FDD-RULE-API-008` | A public function shall not hide relay actions, NVS commits, unbounded waits, or other consequential side effects behind an apparently observational name. |
| `FDD-RULE-API-009` | Enums and bitmasks crossing persistence or communication boundaries shall have explicit values, reserved ranges, and unknown-value behavior. |
| `FDD-RULE-API-010` | Every schema shall define compatibility behavior for older, newer, truncated, duplicated, corrupt, and unsupported input. |

## 10. Data ownership, memory, and resource bounds

### 10.1 Ownership and lifetime

- Each mutable object shall have exactly one writer/owner at a time.
- Relay state and state-machine variables are private to `ControlSafetyTask`.
- ADC DMA buffers are private to `AdcAcquisitionTask` and `adc_port`.
- NVS access is serialized by `PersistenceTask` after persistence-service startup.
- Duplicate-request cache state is owned by `CommandRouterTask`.
- Published measurement and system-state snapshots use single-writer/multiple-reader
  semantics and are immutable to readers.
- A pointer to task-local stack storage shall never outlive the publishing call.
- Ownership transfer through a queue or service request shall be explicit and shall
  define behavior on send failure, timeout, cancellation, and shutdown.

### 10.2 Allocation and capacity

| Rule ID | Resource rule |
|---|---|
| `FDD-RULE-RES-001` | Safety-path queues, buffers, caches, timers, and task objects shall have finite declared capacities. |
| `FDD-RULE-RES-002` | Safety-critical run-time behavior shall use static or startup-time allocation. Unbounded or repeated heap allocation in the control and acquisition paths is prohibited. |
| `FDD-RULE-RES-003` | Every allocation failure shall have an explicit conservative response and diagnostic outcome. |
| `FDD-RULE-RES-004` | Queue-full behavior shall be defined per message class. Urgent STOP and urgent faults shall retain their independent notification path. |
| `FDD-RULE-RES-005` | Task stack sizes shall be justified using measured high-water marks under representative worst-case load plus documented margin. |
| `FDD-RULE-RES-006` | RAM, flash, NVS writes, queue depth, duplicate cache, reassembly buffers, and persistent-ring capacity shall be included in FDD-11 budgets. |

No exact margin percentage is imposed by this draft. The selected margin shall state
the workload, instrumentation, compiler/profile, evidence revision, and invalidating
conditions.

## 11. Concurrency and inter-task communication

Only these three interaction forms are part of the baseline:

| Interaction | Suitable data | Required behavior |
|---|---|---|
| Latest-value snapshot | Measurements and system state | Single writer; consistent read; stale/torn detection; skipped intermediate values allowed |
| Bounded queue | Commands, persistence requests, results, and diagnostic events | Declared depth; bounded wait; explicit overflow/degradation behavior |
| Urgent notification bits | STOP and urgent measurement/control faults | Independent from normal queue capacity; coalescing allowed only when the condition remains actionable |

Additional cross-task mechanisms require justification in the responsible FDD.

- Cross-core access shall use documented FreeRTOS/ESP-IDF synchronization with
  defined memory ordering. Ad hoc `volatile` sharing is prohibited.
- ISR code shall perform only the minimum driver acknowledgment/data capture and task
  notification. It shall not parse protocols, evaluate policy, access NVS, log, or
  command the relay.
- No safety task shall wait for telemetry transmission, an external communication
  acknowledgment, diagnostic-log flush, or UTC synchronization.
- `ControlSafetyTask` shall not hold a shared lock while requesting persistence.
- Any remaining lock graph shall be acyclic and documented with a single acquisition
  order. Busy-waiting is prohibited outside a justified, bounded hardware primitive.
- Timeouts and queue failures are observable outcomes; they shall not be converted to
  indefinite retries.

## 12. Time, scheduling, and deterministic behavior

| Rule ID | Timing rule |
|---|---|
| `FDD-RULE-TIME-001` | Safety and session decisions shall use a monotonic timebase, not UTC or wall-clock time. |
| `FDD-RULE-TIME-002` | Elapsed-time comparisons shall be rollover safe for the selected counter width. |
| `FDD-RULE-TIME-003` | Every blocking operation in a task or service shall have a documented upper bound or a documented non-blocking design. |
| `FDD-RULE-TIME-004` | Numeric task priorities, periods, watchdog timeouts, queue waits, NVS deadlines, relay settling, and STOP response shall be derived from an end-to-end timing budget. |
| `FDD-RULE-TIME-005` | Timing evidence shall identify build profile, clock configuration, interrupt load, bus load, compiler optimization, target revision, and measurement method. |
| `FDD-RULE-TIME-006` | Failure to meet a required freshness or response deadline shall produce the specified fault or conservative state; it shall not silently extend the deadline. |

Relative scheduling remains controlled by the Architecture: Control is critical and
ADC acquisition is high on Core 1; command routing, transports, persistence, and
logging execute on Core 0. FDD-09 assigns exact values only after evidence is
available.

## 13. Safety, fault, and error-handling rules

- Designs shall use guard-first control flow: validate state, data, authority,
  freshness, inhibit, fault, configuration, calibration, and persistence conditions
  before a relay-enabling action.
- Safe physical action shall precede nonessential bookkeeping.
- A fault record shall define initiating condition, detection, qualification,
  severity, relay action, inhibit effect, persistence, clearing, recurrence,
  escalation, timing bound, and verification.
- Recoverable and latched conditions shall not be collapsed into a generic error.
- Multiple inhibit reasons shall coexist in a persistent bitmask. Clearing one reason
  shall not clear unrelated reasons or erase diagnostic history.
- A service command may request recovery but shall not bypass measurement,
  configuration, calibration, persistence, or relay-state interlocks.
- Communication authority shall be derived from trusted adapter metadata, never from
  a role asserted by the payload.
- If software response cannot provide the required diagnostic coverage or response
  time, the design shall record the need for independent hardware protection rather
  than claiming software coverage.

### 13.1 Error taxonomy

Each subordinate FDD shall map failures to the narrowest applicable category:

| Category | Meaning | Typical representation |
|---|---|---|
| API status | Immediate success/failure of a local operation | Project-defined status enum |
| Reason code | Machine-readable explanation for a command/result | ICD reason registry |
| Warning | Degradation without a mandatory relay-open action | Diagnostic/event state |
| Recoverable fault | Relay OFF plus `RECOVERY_INHIBIT` and a defined re-arm policy | Fault registry entry |
| Latched fault | Relay OFF plus service clearing and `SELF_TEST` | Persistent fault state |
| Programmer invariant | Internal defect that should be impossible with valid inputs | Development assertion plus defined production containment |

Errors shall not be silently downgraded between categories. Translation across layers
shall preserve the original diagnostic cause where practical without exposing private
platform details as the public domain contract.

## 14. Design-pattern policy

Design patterns are vocabulary and implementation aids, not requirements or safety
evidence. The categories in
[Refactoring.Guru — Creational Patterns](https://refactoring.guru/design-patterns/creational-patterns),
[Structural Patterns](https://refactoring.guru/design-patterns/structural-patterns), and
[Behavioral Patterns](https://refactoring.guru/design-patterns/behavioral-patterns)
may be considered selectively. Determinism, explicit ownership, bounded resources,
and traceability take priority over pattern purity.

| Pattern | Intended use | Mandatory constraint |
|---|---|---|
| State | Charging/control state machine | Implement with explicit enum, transition table or static handlers; relay authority remains singular and transitions remain reviewable |
| Command | Normalized application commands | Commands are bounded data objects; physical actions are not presented as generally undoable operations |
| Strategy | Filter, calibration, validation, or transport policies | Selection is compile-time or controlled configuration; safety policy cannot be replaced arbitrarily at run time |
| Observer | Immutable snapshots and bounded events | No unbounded subscriber list and no synchronous callback that can block Control |
| Mediator | Command Router and controlled task coordination | Shall not become a generic unbounded event bus or a second control authority |
| Adapter | HAL ports and CAN/RS485/UART bindings | Converts concrete interfaces to stable contracts without embedding domain policy |
| Facade | Narrow measurement, persistence, diagnostic, and relay service APIs | Shall not hide consequential blocking, persistence, or relay side effects |
| Bridge | Separation of abstract ports from production/test backends | Production composition can select only approved real physical backends |
| Abstract Factory / Factory | Build-time composition of production and test implementations | No run-time switch can expose a mock or injection backend in production |
| Builder | Staged configuration/calibration object construction | The built object is validated completely before atomic commit; partial state never becomes active |

The following uses require a specific recorded justification and design review:

- Singleton used as mutable global access. A single owner does not imply a Singleton.
- Chain of Responsibility on a safety path where handler order or termination becomes
  unclear.
- Decorator, Composite, Visitor, Prototype, or Flyweight without a concrete need that
  improves testability or resource use.
- Dynamic object graphs, run-time registration, reflection-like dispatch, or other
  mechanisms that obscure worst-case execution time, state ownership, or build
  contents.

Each subordinate FDD shall list its patterns, the problem each solves, rejected
simpler alternatives, resource implications, and invalidating conditions.

## 15. Configuration, calibration, and persistence rules

### 15.1 Configuration and calibration

- Exactly one validated operational configuration generation is active.
- Updates follow staging, validation, and atomic commit. A failed update leaves the
  previous valid generation active.
- Hard safety limits, ADC sample rate, and escalation policy are compile-time or
  release-controlled and bound to firmware/hardware identity.
- `CAL_DATA` is independent from operational configuration and is bound to hardware
  revision, schema version, CRC/integrity, calibration conditions, and validation
  status.
- Configuration/calibration command payload schemas are controlled jointly by the
  Configuration and Calibration Specification and the ICD.
- Engineering values use integers at public boundaries; intermediate calculation
  precision and overflow behavior shall be explicitly analyzed.

### 15.2 Persistence

- Safety records use versioned schemas, integrity checks, generation identity, and an
  atomic previous-or-new commit model.
- Safety requests outrank configuration and diagnostic requests.
- An acknowledgment states the exact durability boundary reached and correlates to
  the request and committed generation.
- Failure to persist a required safety state retains relay OFF and applies the SRS
  fail-closed policy.
- Periodic telemetry is not written to flash. Persistent diagnostic summaries are
  bounded, rate-limited or coalesced, and subordinate to safety writes.
- NVS endurance and worst-case latency are budgeted in FDD-11; a successful API call
  alone is not evidence of power-cut atomicity or endurance suitability.

## 16. External-interface and command rules

- All operational transports use the common application command model defined by the
  ICD. Transport adapters do not define independent command semantics.
- Exactly one configured operational interface has control authority; non-selected
  operational interfaces are monitor-only unless a controlled service rule applies.
- Trusted `source_interface`, `source_node`, and receive-time metadata are attached by
  the adapter and cannot be overridden by payload data.
- Authorization precedes entry of a normal command into `ControlCommandQueue`.
- `STOP_CHARGE` is idempotent and uses the independent urgent path.
- Duplicate handling shall not repeat a consequential action.
- Frame, reassembly, queue, cache, retry, and in-flight command counts are bounded.
- FDD-08 shall not assign final wire values or transport parameters that remain open
  in `RCC-FW-ICD-001`.

The current interface model provides source/port authority, not cryptographic
authentication. Threat-model and authentication decisions remain controlled open
items and shall not be implied by successful CRC or framing validation.

## 17. Boot, diagnostics, and build profiles

### 17.1 Boot and recovery

Boot design shall first establish relay OFF, then classify reset/session state and
validate required persistence, configuration, calibration, measurement, and
interlocks before operational eligibility. A watchdog, panic, brownout, or incomplete
session guard shall retain `RESET_INHIBIT`. A latched clear returns to `SELF_TEST`,
never directly to an enabled state.

### 17.2 Diagnostics and time

- Every event has `boot_id`, `event_seq`, monotonic time, and time-validity state.
- UTC is optional and shall not be an autonomous-operation interlock.
- Detailed current-boot diagnostics use a bounded RAM ring.
- Persistent event summaries are bounded and shall not delay a safe action.
- Diagnostic loss, coalescing, rate limiting, and overflow shall be observable.

### 17.3 Build profiles

| Property | `PRODUCTION` | `TEST` |
|---|---|---|
| Physical backends | Real ADC, relay, storage, reset, and time backends only | Mock/test backends allowed |
| Fault injection | Not compiled or linked | Controlled injection allowed |
| Identity | Release-controlled production marker | Distinct and conspicuous test marker |
| Relay default | OFF | OFF plus controlled bench enable conditions |
| Verification | Build-content inspection and target test | Host, target, HIL, and bench support |

The build system shall fail rather than silently fall back to a test backend when a
production backend is missing. FDD-10 shall define artifact inspection that proves
test symbols, commands, and mock backends are absent from a production image.

## 18. Verification and testability rules

### 18.1 Verification levels

| Level | Primary purpose | Typical subjects |
|---|---|---|
| Host unit/model | Deterministic logic and boundary cases without target hardware | State transitions, filtering, qualification, record selection, command validation |
| Target integration | ESP-IDF drivers, FreeRTOS behavior, memory, reset, and NVS | ADC DMA, queues, notification latency, watchdog, storage failure |
| HIL | End-to-end scheduling and interface behavior with controlled stimuli | VOUT/IOUT sequences, STOP load, transport overload, reset/re-arm |
| Controlled bench | Physical analog and relay binding | Accuracy, noise/headroom, relay timing, hardware response limits |

### 18.2 Common verification rules

- Each mandatory design rule, algorithm branch, transition, failure path, timeout,
  and overload behavior shall map to at least one verification item.
- Tests shall include invalid, stale, saturated, duplicated, corrupt, out-of-order,
  overflow, timeout, reset, and power-interruption cases as applicable.
- Test ports shall exercise the same domain logic as production; a separate simplified
  safety algorithm for tests is prohibited.
- Numeric acceptance criteria shall cite their requirement, derivation, units,
  tolerance, and controlled evidence revision.
- Tool execution, run convergence, measurement evaluation, criterion passing, and
  requirement verification are distinct statuses.
- A host pass does not verify target scheduling or physical response. A bench result
  does not waive a normative requirement.

## 19. Traceability and identifier conventions

### 19.1 Stable identifiers

Subordinate FDDs shall use stable identifiers with this form:

`FDD-<AREA>-<TYPE>-<NNN>`

Recommended area codes are `COMMON`, `MEAS`, `PST`, `FAULT`, `CTRL`, `CFGCAL`,
`CMD`, `TRN`, `RT`, `BOOT`, and `INT`. Recommended type codes include `REQ`, `API`,
`DATA`, `ALG`, `STATE`, `TIME`, `RES`, `TEST`, and `ACT`.

Identifiers shall not be reused after publication. Removed items are marked
superseded or obsolete and retain a pointer to their replacement.

### 19.2 Required trace links

Every subordinate FDD shall provide mappings for:

- upstream SRS requirements and Architecture invariants/decisions;
- applicable ICD interface, command, reason, event, or open-item IDs;
- FDD rules and module design IDs;
- source component/file/function once implementation exists;
- verification IDs, setup/DUT revision, evidence, result, and status;
- open action, owner, due gate, and closure evidence.

The traceability matrix shall distinguish a planned test from executed evidence and a
passed criterion from a verified requirement.

## 20. Review rules and definition of done

A subordinate FDD is implementation-ready only when all applicable statements below
are true:

- Scope, non-responsibilities, inputs, outputs, and dependencies are unambiguous.
- Public interfaces include units, ranges, ownership, lifetime, context, errors, and
  blocking bounds.
- Normal, degraded, fault, reset, recovery, timeout, and overload flows are defined.
- Relay-affecting actions preserve every `FDD-RULE-SAFE-*` invariant.
- Shared data has a single writer and a documented consistency mechanism.
- All queues, buffers, caches, retries, waits, and allocations are bounded.
- Numeric timing and thresholds cite controlled evidence or remain explicitly open.
- Production/test separation and required test seams are defined.
- Traceability covers the relevant requirements, risks, algorithms, and tests.
- Open actions have an owner, affected gate, acceptance criterion, and status.
- Review findings are resolved or explicitly carried without implied waiver.

Code implementation may begin against an under-review FDD when the responsible human
accepts the rework risk, but the document shall not be called controlled or complete
until its gate conditions are met.

## 21. Initial cross-document traceability

| FDD area | Primary controlling inputs | Responsible document |
|---|---|---|
| Layering, relay ownership, safe action order | `ARCH-INV-001` through `ARCH-INV-010`; `ADR-FW-002`, `ADR-FW-010` | 00, 01, 05 |
| ADC and measurement validity | SRS 5.3; `FW-REQ-001` through `FW-REQ-005`; `ADR-FW-003`, `ADR-FW-004` | 01, 02 |
| Session guard and atomic persistence | `FW-SES-001` through `FW-SES-003`; `FW-PST-001` through `FW-PST-005`; `ADR-FW-008` | 01, 03, 05 |
| Fault, reset, and inhibit | `FW-ARC-007`, `FW-ARC-008`; SRS 10; Architecture 15 and 20 | 04, 05, 10 |
| Establishment, completion, and re-arm | `FW-SES-004`, `FW-SES-005`; `FW-END-001` through `FW-END-004`; `FW-RAR-001` through `FW-RAR-004` | 02, 04, 05 |
| Configuration and calibration | SRS 11–12; Architecture 17–18; `ICD-OPEN-014` | 02, 03, 06 |
| Command model and authority | `FW-RCMD-001` through `FW-RCMD-008`; ICD 4–15 | 01, 04–07 |
| Transport bindings | ICD 16–19; `ICD-OPEN-001` through `ICD-OPEN-017` as applicable | 08 |
| Scheduling and overload | `FW-ARC-003` through `FW-ARC-007`; Architecture 7–8 and 19 | 09 |
| Boot, diagnostics, and build isolation | SRS 14 and 16; Architecture 11, 20–21 | 10 |
| Numeric budgets and verification closure | SRS 15 and 17–18; `ARCH-ACT-001` through `ARCH-ACT-008` | 11 |

## 22. Open actions

| Action ID | Required decision or evidence | Affected documents/gate | Acceptance evidence | Confidence |
|---|---|---|---|---|
| `FDD-OPEN-001` | ESP-IDF API baseline is selected as v6.1 for ESP32; select the exact SDK release/tag and bundled toolchain, C language revision, compiler warning policy, formatting, and static-analysis baseline | 01 and all implementation | Reproducible version/toolchain record, link to the v6.1 API used by each platform design, and clean policy check | `needs_verification` |
| `FDD-OPEN-002` | Finalize the ESP-IDF component/source tree, public symbol prefix, and dependency declarations | 01; Foundation gate | Reviewed component graph with no cycles | `needs_verification` |
| `FDD-OPEN-003` | Select the project coding standard and determine whether/how CERT C, MISRA C, or project-specific rules apply | 00–11 and implementation review | Controlled rule set, deviations process, and tool coverage | `needs_verification` |
| `FDD-OPEN-004` | Derive RAM, task-stack, queue, cache, reassembly, flash, and NVS-endurance budgets | 03, 07–11 | Static budget plus measured target evidence and margin | `needs_verification` |
| `FDD-OPEN-005` | Derive WCET/latency, freshness, relay, persistence, watchdog, and urgent STOP timing budgets | 02–05, 07–11 | End-to-end timing analysis plus target/HIL/bench measurements | `needs_verification` |
| `FDD-OPEN-006` | Select host unit-test, target integration, HIL, coverage, and evidence-capture tooling | All document gates | Reproducible verification environment and report schema | `needs_verification` |
| `FDD-OPEN-007` | Resolve the ICD open items required by each command and transport design, including `ICD-OPEN-017` | 07–08 | Revised ICD plus golden vectors/interoperability criteria | `needs_verification` |
| `FDD-OPEN-008` | Close or carry `ARCH-ACT-001` through `ARCH-ACT-008`, including analog, relay, hard-limit, connector, timing, and fault-matrix evidence | 02, 04–05, 08–11 | Controlled analysis, hardware review, and bench/HIL evidence | `needs_verification` |
| `FDD-OPEN-009` | Complete the interface threat model and decide authentication, anti-replay, and service-access requirements | 07–08, 10 | Controlled threat assessment and responsible-human decision | `needs_verification` |
| `FDD-OPEN-010` | Create and baseline the separate Configuration and Calibration Specification referenced by FDD-06 and the ICD | 02–03, 06–08 | Reviewed schemas, validation rules, and compatibility/power-cut tests | `needs_verification` |

Open actions are not waivers. A document may carry an action only when the affected
behavior remains conservative and its gate explicitly records the unresolved scope.

## 23. Master FDD review gate

| Field | Value |
|---|---|
| Gate ID | `FW-GATE-FDD-000` |
| Gate definition | Common FDD structure and design rules are suitable as the baseline for subordinate detailed-design drafting |
| Artifact assessed | `RCC-FW-FDD-000`, Draft 0.1 |
| Scope | Document map, dependency sequence, five-layer constraints, safety invariants, API/data/resource/concurrency/timing rules, pattern policy, verification, and traceability |
| AI assessment | `recommended_conditional_pass` |
| Assessment basis | `RCC-FW-SRS-001` Draft 0.1; `RCC-FW-ARCH-001` Draft 0.2; `RCC-FW-ICD-001` Draft 0.1; explicit user-selected architecture decisions |
| Open conditions | Review this master baseline and close or explicitly assign `FDD-OPEN-001` through `FDD-OPEN-010` to the affected subordinate-document gates |
| Residual risks | High-energy 60 V / 20 A path; unbound analog and relay behavior; unbound hard limits and timing; incomplete physical-interface and system fault evidence |
| Human decision | `pending_human_decision` |
| Approved by | `pending_human_decision` |
| Decision timestamp | `pending_human_decision` |
| Release authorization | `pending_human_decision` |

The conditional recommendation means this document is coherent enough to be reviewed
and used to structure the next FDD drafts if the responsible human accepts it. It is
not a safety approval, residual-risk acceptance, or production-readiness claim.
