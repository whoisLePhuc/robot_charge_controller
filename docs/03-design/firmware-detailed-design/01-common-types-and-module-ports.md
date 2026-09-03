# Common Types and Module Ports Detailed Design

## 1. Document control

| Field | Value |
|---|---|
| Document ID | `RCC-FW-FDD-001` |
| Project | Robot Charge Controller |
| Applicable hardware variant | Split Board Design — Control Board + Relay Board |
| Record revision | Draft 0.1 |
| Status | Under review |
| Prepared at | 2026-09-03, Asia/Bangkok (UTC+07:00) |
| Prepared by | Codex drafting support, based on the controlled inputs and explicit selection of hybrid static interfaces |
| Requirements source | `RCC-FW-SRS-001`, Draft 0.1 |
| Architecture source | `RCC-FW-ARCH-001`, Draft 0.2 |
| Interface source | `RCC-FW-ICD-001`, Draft 0.1 |
| FDD master source | `RCC-FW-FDD-000`, Draft 0.1 |
| Platform API baseline | [ESP-IDF Programming Guide v6.1 — ESP32 API Reference](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32/api-reference/index.html) |
| Hardware source baseline | Git commit `fe85ff2` plus the uncommitted hardware changes identified in the SRS |
| Firmware source baseline | Pre-implementation; no firmware source revision exists yet |
| Authoritative language | English |

This document defines internal firmware contracts. It does not define an external wire
encoding, approve hardware, certify safety or compliance, accept residual risk, or
authorize a production release.

### 1.1 Revision history

| Revision | Date | Change |
|---|---|---|
| Draft 0.1 | 2026-09-03 | Initial common-type, module-boundary, and hybrid static-port baseline |

## 2. Purpose, scope, and exclusions

This document establishes the C-level contracts on which the remaining FDD documents
depend. It defines:

- the ESP-IDF component boundaries and intended source organization;
- common naming, scalar, status, identity, state, and bitmask types;
- the logical structure of measurement, system-state, command, persistence, event,
  and urgent-notification contracts;
- the hybrid static-interface model selected for hardware and test ports;
- relay, ADC, storage, communication, monotonic-time, and reset-reason port contracts;
- lifecycle, ownership, error, concurrency, compatibility, and verification rules.

### 2.1 In scope

- Public contracts shared by two or more firmware components.
- Interfaces required to isolate ESP-IDF and physical backends from portable logic.
- Compile-time and run-time rules that preserve the five-layer dependency direction.
- Test seams used by host, target, HIL, and controlled-bench verification.

### 2.2 Out of scope

- ADC conversion, calibration, filtering, qualification, and freshness algorithms.
- NVS record layout, generation-selection, and power-cut algorithms.
- Fault qualification, recurrence, escalation, and clearing algorithms.
- Control-state transition tables and relay timing.
- Configuration/calibration object schemas and validation rules.
- Command-specific payload unions, duplicate-cache implementation, and result timing.
- CAN, RS485, or UART wire framing, numeric registry values, bitrate, or addressing.
- Numeric task priorities, queue depths, stack sizes, timeouts, and end-to-end budgets.

Those subjects are owned by FDD-02 through FDD-11. This document defines the narrow
interfaces needed to design them without creating circular dependencies.

## 3. Design drivers and selected approach

### 3.1 Controlling constraints

| Driver | Consequence for this design |
|---|---|
| `FDD-RULE-LAYER-001` through `FDD-RULE-LAYER-006` | Public contracts have an explicit owner and dependencies remain downward |
| `FDD-RULE-SAFE-001` through `FDD-RULE-SAFE-012` | No port or common type grants relay authority or bypasses safety state |
| `FDD-RULE-API-001` through `FDD-RULE-API-010` | Fixed-width values, explicit units, ownership, error behavior, and serialization boundaries |
| Architecture Sections 8 and 9 | The shared contracts cover snapshots, queues, notifications, and persistence acknowledgments |
| `ICD-MSG-001` through `ICD-MSG-008` | Internal types support explicit codec conversion but are not native wire layouts |
| Production/test build separation | Test substitution occurs at port composition, never through a production runtime switch |
| ESP-IDF v6.1 for ESP32 | Each production backend shall be designed against the public API documented for this exact version/target rather than an older release or the moving `latest` branch |

### 3.2 Selected interface model

| Decision ID | Decision |
|---|---|
| `FDD-COMMON-ADR-001` | Use a hybrid static interface: immutable/value structs for shared data, opaque handles for stateful modules, and function-pointer interfaces only at physical/test port boundaries. |
| Selection source | The project user explicitly selected Option A during the FDD-01 design discussion on 2026-09-03. |
| Rationale | It isolates ESP-IDF and permits host mocks while keeping normal module calls direct, bounded, statically composed, and reviewable. |
| Alternatives not selected | Vtables for every module add unnecessary indirection and ownership complexity; direct concrete calls everywhere prevent clean host substitution and couple domain logic to ESP-IDF. |
| Reconsider when | A new platform, dynamic plugin requirement, formal toolchain restriction, or measured performance/resource issue invalidates the current tradeoff. |

The selected model is not a general dependency-injection framework. There is no
run-time service locator, reflective registration, mutable global registry, or dynamic
backend switching.

## 4. Layer and component allocation

### 4.1 Component baseline

| Component | Layer | Public responsibility | Principal private implementation | Allowed dependencies |
|---|---:|---|---|---|
| `rcc_base` | L2 foundation | Portable scalar aliases, status, identity, and common utility contracts | Checked arithmetic and validation helpers | C standard headers only |
| `rcc_port_contracts` | L2 | Abstract relay, ADC, storage, communication, time, and reset contracts | No physical backend | `rcc_base` |
| `rcc_platform_esp32` | L2 | Production implementations of the L2 ports | ESP-IDF GPIO, ADC continuous, NVS, TWAI/UART, timer, and reset APIs | `rcc_base`, `rcc_port_contracts`, ESP-IDF |
| `rcc_persistence` | L3 | Versioned durable-record service and acknowledgments | Record selection, CRC, atomic generations, priority handling | `rcc_base`, `rcc_port_contracts` |
| `rcc_time` | L3 | Boot identity, event sequence, monotonic/optional UTC service | Synchronization and controlled persistence boundaries | `rcc_base`, `rcc_port_contracts`, optionally `rcc_persistence` |
| `rcc_diagnostics` | L3 | Bounded RAM events, counters, and persistent summaries | Coalescing/rate limiting | `rcc_base`, `rcc_time`, optionally `rcc_persistence` |
| `rcc_transport_contracts` | L3 | Trusted source identity and transport-neutral ingress metadata | No driver or charging policy | `rcc_base` |
| `rcc_protocol_codec` | L3 | Explicit application-object encoding/decoding | Version, length, byte-order, integrity processing | `rcc_base` |
| `rcc_transport_can` | L3 | CAN binding and trusted source metadata | Frame segmentation, Rx/Tx, recovery | `rcc_base`, `rcc_port_contracts`, `rcc_transport_contracts`, `rcc_protocol_codec` |
| `rcc_transport_rs485` | L3 | RS485 binding and trusted source metadata | Framing, turnaround, Rx/Tx, recovery | `rcc_base`, `rcc_port_contracts`, `rcc_transport_contracts`, `rcc_protocol_codec` |
| `rcc_transport_uart` | L3 | Operational/service UART bindings and trusted port identity | Framing, Rx/Tx, recovery | `rcc_base`, `rcc_port_contracts`, `rcc_transport_contracts`, `rcc_protocol_codec` |
| `rcc_domain_contracts` | L4 | Measurement, state, command, fault, inhibit, and event value contracts | No mutable run-time state | `rcc_base`, `rcc_port_contracts`, `rcc_transport_contracts` |
| `rcc_measurement` | L4 | Measurement processing and snapshot publication | Calibration application, filters, validity, qualification | `rcc_base`, `rcc_port_contracts`, `rcc_domain_contracts`, `rcc_time` |
| `rcc_config` | L4 | Operational configuration lifecycle | Staging and validation | `rcc_base`, `rcc_domain_contracts`, `rcc_persistence` |
| `rcc_calibration` | L4 | Per-board calibration lifecycle | Staging, fit, validation | `rcc_base`, `rcc_domain_contracts`, `rcc_persistence` |
| `rcc_fault` | L4 | Fault/inhibit/reset policy evaluated in control context | Qualification and escalation state | `rcc_base`, `rcc_domain_contracts` |
| `rcc_control` | L4 | Control state machine and sole run-time relay owner | Guards, actions, sessions, completion, re-arm | L4 contracts/modules and narrow L2/L3 public ports/services assigned by Architecture |
| `rcc_command_router` | L5 | Authorization, normalization, duplicates, routing, and results | Bounded request cache and reply correlation | `rcc_base`, L3 protocol/transport contracts, L4 public contracts |
| `rcc_app` | L5 | Safe boot and static composition root | Initialization order, task creation, ownership handoff | Required public contracts from L2–L5 |
| `rcc_build_profile` | L5 | Compile-time selection and profile identity | Production/test composition checks | `rcc_base`; selected backends only |

`rcc_base` is placed at the L2 contract foundation; it does not contain hardware
access or domain charging policy. Domain-specific types remain in
`rcc_domain_contracts` so lower layers do not learn control states, fault policy, or
command semantics.

`rcc_platform_esp32` shall use public APIs documented by the ESP-IDF v6.1 ESP32 API
Reference. Any proposed private, internal, unstable, experimental, or deprecated API
requires an explicit design finding, rationale, compatibility boundary, and
replacement/upgrade plan. If the installed headers and the v6.1 documentation do not
match, implementation shall stop at that API boundary until the actual SDK tag,
target, configuration, and documentation revision are reconciled.

### 4.2 Planned source organization

```text
Firmware/
├── CMakeLists.txt
├── sdkconfig.defaults
├── main/
│   ├── CMakeLists.txt
│   └── app_main.c
├── components/
│   ├── rcc_base/
│   │   ├── include/rcc/base/
│   │   └── src/
│   ├── rcc_port_contracts/
│   │   └── include/rcc/ports/
│   ├── rcc_platform_esp32/
│   │   └── src/
│   ├── rcc_persistence/
│   ├── rcc_time/
│   ├── rcc_diagnostics/
│   ├── rcc_transport_contracts/
│   │   └── include/rcc/transport/
│   ├── rcc_protocol_codec/
│   ├── rcc_transport_can/
│   ├── rcc_transport_rs485/
│   ├── rcc_transport_uart/
│   ├── rcc_domain_contracts/
│   │   └── include/rcc/domain/
│   ├── rcc_measurement/
│   ├── rcc_config/
│   ├── rcc_calibration/
│   ├── rcc_fault/
│   ├── rcc_control/
│   ├── rcc_command_router/
│   ├── rcc_app/
│   └── rcc_build_profile/
├── test_support/
│   └── rcc_test_ports/
└── tests/
    ├── host/
    ├── target/
    └── hil/
```

This tree is a design baseline, not evidence that source files already exist.

### 4.3 Header ownership

| Header family | Owner | May contain | Shall not contain |
|---|---|---|---|
| `rcc/base/*.h` | `rcc_base` | Platform-independent scalar and status types | ESP-IDF, FreeRTOS, control policy |
| `rcc/ports/*.h` | `rcc_port_contracts` | Port structs, callbacks, raw/native descriptors | Domain state machine or protocol commands |
| `rcc/transport/*.h` | `rcc_transport_contracts` | Trusted interface identity and transport-neutral metadata | Hardware-driver implementation or charging policy |
| `rcc/domain/*.h` | `rcc_domain_contracts` | Domain value objects and stable symbolic identities | ESP-IDF handles or transport framing |
| Component public headers | Responsible component | Narrow callable service API | Private context fields or unrelated shared types |
| Component private headers | Responsible component | Internal state and backend details | Includes by unrelated components |

An umbrella header that includes all project types is prohibited. Consumers shall
include the narrow header that owns the required contract.

## 5. Common C conventions

### 5.1 Language and naming

- Public symbols use the `rcc_` prefix and lower snake case.
- Types use `_t`; enum constants and macros use upper snake case with `RCC_`.
- Structure fields containing quantities include units, such as `_mv`, `_ma`, `_ms`,
  or `_us`.
- Boolean names express a positive predicate. Public APIs shall not use `bool` to
  combine success/failure with returned data.
- Public headers are valid C headers with include guards, C++ linkage guards when
  required by test tooling, and only their direct includes.
- Implementation-private functions use a component-specific prefix and are not
  declared in public headers.

The exact C language revision, compiler warning profile, formatting tool, static
analysis, and coding-standard subset remain `FDD-COMMON-ACT-001`.

### 5.2 Public API contract annotations

Every public function shall document:

| Property | Required statement |
|---|---|
| Calling context | Pre-scheduler, task, owner task, any task, or ISR-safe |
| Blocking | Non-blocking or maximum wait controlled by a timeout argument |
| Reentrancy | Reentrant, serialized internally, or single-owner only |
| Inputs | Nullability, units, valid ranges, alignment, and lifetime |
| Outputs | Initialization on success and defined state on failure |
| Ownership | Borrowed, copied, transferred, or returned view |
| Side effects | Relay action, persistent commit, queue operation, counters, or none |
| Error result | Exact `rcc_status_t` categories and caller response |

Functions without an explicit timeout shall not perform an unbounded wait.

## 6. Foundation types

### 6.1 Scalar and identity types

The following declarations define semantic widths. They are not external wire or NVS
layouts.

```c
typedef uint64_t rcc_monotonic_us_t;
typedef uint32_t rcc_duration_ms_t;
typedef uint32_t rcc_revision_t;
typedef uint32_t rcc_generation_t;
typedef uint64_t rcc_boot_id_t;
typedef uint32_t rcc_event_seq_t;
typedef uint32_t rcc_request_id_t;
typedef uint32_t rcc_session_id_t;
typedef uint32_t rcc_source_node_t;
typedef uint16_t rcc_command_code_t;
typedef uint16_t rcc_reason_code_t;
typedef uint16_t rcc_fault_id_t;
typedef uint32_t rcc_fault_mask_t;
typedef uint32_t rcc_inhibit_mask_t;
```

`rcc_monotonic_us_t` supports driver and latency measurements. Configuration and
external non-negative durations remain `uint32_t` milliseconds unless a controlled
contract explicitly needs finer resolution. Elapsed-time helpers shall use
rollover-safe unsigned arithmetic and shall not mix UTC with monotonic time.

### 6.2 Common status

```c
typedef enum {
    RCC_STATUS_OK = 0,
    RCC_STATUS_INVALID_ARGUMENT = 1,
    RCC_STATUS_INVALID_STATE = 2,
    RCC_STATUS_NOT_READY = 3,
    RCC_STATUS_BUSY = 4,
    RCC_STATUS_TIMEOUT = 5,
    RCC_STATUS_IO_ERROR = 6,
    RCC_STATUS_INTEGRITY_ERROR = 7,
    RCC_STATUS_VERSION_MISMATCH = 8,
    RCC_STATUS_NO_SPACE = 9,
    RCC_STATUS_NOT_SUPPORTED = 10,
    RCC_STATUS_INTERNAL_ERROR = 11
} rcc_status_t;
```

`rcc_status_t` reports a local API outcome. It is not an ICD result, reason code,
fault level, or fault ID. Adapter code shall translate `esp_err_t` into this set while
retaining platform detail in bounded diagnostics where appropriate.

### 6.3 Checked numeric conversion

All conversions among raw codes, intermediate fixed-point values, millivolts,
milliamperes, and durations shall define intermediate width, rounding, saturation,
and overflow behavior. `rcc_base` shall provide checked helpers rather than allowing
implementation-defined narrowing. Silent wraparound of an engineering quantity is
prohibited.

## 7. Cross-layer identity and state types

### 7.1 Source interfaces

```c
typedef enum {
    RCC_SOURCE_NONE = 0,
    RCC_SOURCE_CAN = 1,
    RCC_SOURCE_RS485 = 2,
    RCC_SOURCE_OPERATIONAL_UART = 3,
    RCC_SOURCE_SERVICE_UART = 4
} rcc_source_interface_t;
```

These values are owned by the L3 `rcc_transport_contracts` component and consumed by
L4/L5. They are internal symbolic values. The codec shall map them explicitly if an
external schema exposes a corresponding field. A sender cannot supply or override
the trusted source value. Autonomous initiation is a domain session origin, not a
transport interface.

### 7.2 Top-level and operational states

```c
typedef enum {
    RCC_TOP_STATE_BOOT_SAFE = 0,
    RCC_TOP_STATE_SELF_TEST = 1,
    RCC_TOP_STATE_SERVICE_LOCK = 2,
    RCC_TOP_STATE_CONFIG_MODE = 3,
    RCC_TOP_STATE_OPERATIONAL = 4,
    RCC_TOP_STATE_INHIBITED = 5,
    RCC_TOP_STATE_LATCHED_FAULT = 6
} rcc_top_state_t;

typedef enum {
    RCC_OP_STATE_NONE = 0,
    RCC_OP_STATE_IDLE = 1,
    RCC_OP_STATE_VREQ_VALIDATE = 2,
    RCC_OP_STATE_PRECHECK = 3,
    RCC_OP_STATE_RELAY_CLOSING = 4,
    RCC_OP_STATE_CHARGE_VERIFY = 5,
    RCC_OP_STATE_CHARGING = 6,
    RCC_OP_STATE_COMPLETE = 7,
    RCC_OP_STATE_WAIT_REARM = 8
} rcc_operational_state_t;

typedef enum {
    RCC_SESSION_START_NONE = 0,
    RCC_SESSION_START_AUTONOMOUS = 1,
    RCC_SESSION_START_REMOTE_COMMAND = 2
} rcc_session_start_kind_t;
```

`RCC_OP_STATE_NONE` shall be published whenever the top-level state is not
`RCC_TOP_STATE_OPERATIONAL`. Relay ON remains permitted only in the three states
defined by `FDD-RULE-SAFE-003`; enum values grant no permission by themselves.

### 7.3 Relay command and observation

```c
typedef enum {
    RCC_RELAY_COMMAND_OFF = 0,
    RCC_RELAY_COMMAND_ON = 1
} rcc_relay_command_t;

typedef enum {
    RCC_RELAY_FEEDBACK_UNKNOWN = 0,
    RCC_RELAY_FEEDBACK_OPEN = 1,
    RCC_RELAY_FEEDBACK_CLOSED = 2,
    RCC_RELAY_FEEDBACK_CONFLICT = 3
} rcc_relay_feedback_t;
```

Command and observed feedback are separate. Where hardware feedback does not exist,
the backend reports `RCC_RELAY_FEEDBACK_UNKNOWN`; it shall not echo the command as
independent confirmation. These mechanism types are owned by L2
`rcc_port_contracts`; their values do not grant domain permission to energize the
relay.

### 7.4 Inhibit bits

```c
#define RCC_INHIBIT_REMOTE   (UINT32_C(1) << 0)
#define RCC_INHIBIT_RESET    (UINT32_C(1) << 1)
#define RCC_INHIBIT_RECOVERY (UINT32_C(1) << 2)
#define RCC_INHIBIT_KNOWN_MASK \
    (RCC_INHIBIT_REMOTE | RCC_INHIBIT_RESET | RCC_INHIBIT_RECOVERY)
```

Bits 3 through 31 are reserved for controlled extension. Unknown persisted bits cause
conservative handling and shall not be cleared automatically. ICD wire values are
assigned by the ICD registry and encoded explicitly rather than by serializing this
mask directly.

### 7.5 Reset classification

```c
typedef enum {
    RCC_RESET_CLASS_UNKNOWN = 0,
    RCC_RESET_CLASS_POWER_ON = 1,
    RCC_RESET_CLASS_EXPLICIT_SOFTWARE = 2,
    RCC_RESET_CLASS_WATCHDOG = 3,
    RCC_RESET_CLASS_PANIC = 4,
    RCC_RESET_CLASS_BROWNOUT = 5,
    RCC_RESET_CLASS_OTHER = 6
} rcc_reset_class_t;
```

The L2 backend reports a platform-neutral raw classification. Boot policy combines it
with the persistent session guard and safety records; the port itself never decides
whether `RESET_INHIBIT` is required. This classification type is owned by
`rcc_port_contracts`, not by a higher-layer fault module.

## 8. Shared value contracts

The declarations below define the common fields and ownership. Subordinate FDDs may
add versioned fields before source implementation is baselined, but shall not change
existing meaning, signedness, or units silently.

### 8.1 Measurement channel status

```c
#define RCC_MEAS_STATUS_PRESENT        (UINT32_C(1) << 0)
#define RCC_MEAS_STATUS_FRESH          (UINT32_C(1) << 1)
#define RCC_MEAS_STATUS_CALIBRATED     (UINT32_C(1) << 2)
#define RCC_MEAS_STATUS_IN_RANGE       (UINT32_C(1) << 3)
#define RCC_MEAS_STATUS_NOT_SATURATED  (UINT32_C(1) << 4)
#define RCC_MEAS_STATUS_PLAUSIBLE      (UINT32_C(1) << 5)
typedef uint32_t rcc_measurement_status_t;
```

The flags are positive facts. A consumer shall compare against the required mask for
its decision; absence of a bit is not automatically a specific fault ID. FDD-02 owns
qualification and the exact mapping from missing facts to measurement/fault inputs.

### 8.2 Raw ADC statistics

```c
typedef struct {
    uint32_t latest_code;
    uint32_t minimum_code;
    uint32_t maximum_code;
    uint32_t mean_code;
    uint32_t sample_count;
} rcc_adc_raw_stats_t;
```

Raw statistics are diagnostic inputs only. Domain decisions use calibrated values and
validity status defined by FDD-02.

### 8.3 Measurement snapshot

```c
typedef struct {
    uint32_t schema_version;
    uint32_t sequence;
    rcc_monotonic_us_t acquisition_started_us;
    rcc_monotonic_us_t acquisition_completed_us;
    rcc_monotonic_us_t published_us;
    uint32_t vout_mv;
    int32_t iout_ma;
    uint32_t vout_filtered_mv;
    int32_t iout_filtered_ma;
    rcc_measurement_status_t vout_status;
    rcc_measurement_status_t iout_status;
    uint32_t snapshot_status;
    uint32_t fast_condition_mask;
    rcc_monotonic_us_t earliest_fast_condition_us;
    rcc_adc_raw_stats_t vout_raw;
    rcc_adc_raw_stats_t iout_raw;
    rcc_revision_t hardware_revision;
    rcc_revision_t calibration_revision;
} rcc_measurement_snapshot_t;
```

The snapshot is written only by `AdcAcquisitionTask`/`rcc_measurement`, then published
as an immutable latest value. `sequence` is a publication identity, not a timestamp.
The reader computes age using `published_us` or the FDD-02-defined acquisition time;
it does not trust a producer-supplied mutable `age` field.

### 8.4 System-state snapshot

```c
typedef struct {
    uint32_t schema_version;
    uint32_t sequence;
    rcc_monotonic_us_t published_us;
    rcc_top_state_t top_state;
    rcc_operational_state_t operational_state;
    rcc_relay_command_t relay_command;
    rcc_relay_feedback_t relay_feedback;
    rcc_session_id_t session_id;
    rcc_session_start_kind_t session_start_kind;
    rcc_source_interface_t session_source_interface;
    bool charging_established;
    rcc_monotonic_us_t session_started_us;
    rcc_duration_ms_t session_elapsed_ms;
    rcc_inhibit_mask_t inhibit_mask;
    rcc_fault_mask_t active_fault_mask;
    rcc_fault_id_t primary_fault;
    rcc_reset_class_t reset_class;
    uint32_t vout_mv;
    int32_t iout_ma;
    rcc_measurement_status_t vout_status;
    rcc_measurement_status_t iout_status;
    rcc_revision_t config_revision;
    rcc_revision_t calibration_revision;
    rcc_revision_t hardware_revision;
    rcc_revision_t firmware_revision;
    rcc_boot_id_t boot_id;
    rcc_event_seq_t latest_event_seq;
    bool time_synchronized;
} rcc_system_state_snapshot_t;
```

Only `ControlSafetyTask` publishes this snapshot. Telemetry may omit or transform
fields through an explicit codec, but no telemetry reader may mutate it or hold a lock
owned by Control.

### 8.5 Trusted source and reply token

```c
typedef struct {
    rcc_source_interface_t interface_id;
    rcc_source_node_t node_id;
    rcc_monotonic_us_t received_us;
    uint32_t transport_status;
} rcc_trusted_source_t;

typedef struct {
    uint16_t route_slot;
    uint16_t route_generation;
} rcc_reply_token_t;
```

`rcc_reply_token_t` is an opaque value owned by Command Router. It is not a pointer,
transport handle, or authority claim. Stale generation, unknown slot, or reset causes
a controlled no-route result and diagnostic; it never redirects a result to another
peer.

### 8.6 Object reference

```c
typedef struct {
    uint16_t pool_id;
    uint16_t slot;
    uint32_t generation;
    uint32_t length_bytes;
    uint32_t object_crc32;
} rcc_object_ref_t;
```

Large staged configuration/calibration data moves by an immutable bounded-pool
reference, not a task-stack or transport-buffer pointer. The owning service validates
pool, slot, generation, length, and access state before use. FDD-03, FDD-06, and
FDD-07 define allocation, release, timeout, and stale-reference behavior.

### 8.7 Control command header

```c
typedef struct {
    uint32_t schema_version;
    rcc_command_code_t command_code;
    rcc_request_id_t request_id;
    rcc_trusted_source_t source;
    uint16_t authorization_class;
    uint16_t payload_tag;
    uint32_t request_fingerprint;
    rcc_reply_token_t reply_token;
} rcc_control_command_header_t;
```

FDD-07 shall define a fixed-size discriminated payload union and the final
`rcc_control_command_t`. The queue item shall contain no unbounded data and no borrowed
pointer. `authorization_class` is a router result, not permission to bypass Control
guards.

### 8.8 Persistence request and acknowledgment

```c
typedef enum {
    RCC_PERSISTENCE_PRIORITY_SAFETY = 0,
    RCC_PERSISTENCE_PRIORITY_CONFIGURATION = 1,
    RCC_PERSISTENCE_PRIORITY_DIAGNOSTIC = 2
} rcc_persistence_priority_t;

typedef enum {
    RCC_PERSISTENCE_DURABILITY_NONE = 0,
    RCC_PERSISTENCE_DURABILITY_COMMITTED = 1
} rcc_persistence_durability_t;

typedef struct {
    uint32_t request_id;
    uint16_t record_domain;
    uint16_t operation;
    rcc_persistence_priority_t priority;
    rcc_generation_t expected_generation;
    rcc_object_ref_t object;
} rcc_persistence_request_t;

typedef struct {
    uint32_t request_id;
    rcc_status_t status;
    uint16_t record_domain;
    uint16_t operation;
    rcc_generation_t committed_generation;
    rcc_persistence_durability_t durability;
} rcc_persistence_ack_t;
```

An acknowledgment with `RCC_STATUS_OK` is sufficient for relay-enabling logic only
when `durability == RCC_PERSISTENCE_DURABILITY_COMMITTED`, the request is correlated,
and the record/operation is the required `SESSION_ARMED` transaction. FDD-03 defines
the registry and exact durable boundary.

### 8.9 Diagnostic event header

```c
typedef struct {
    uint32_t schema_version;
    uint16_t event_code;
    uint16_t severity;
    rcc_boot_id_t boot_id;
    rcc_event_seq_t event_seq;
    rcc_monotonic_us_t occurred_us;
    rcc_request_id_t origin_request_id;
    rcc_session_id_t session_id;
} rcc_event_header_t;
```

The event payload is a bounded discriminated union owned by FDD-10. Enqueue failure
shall not delay a physical safe action.

### 8.10 Urgent notification bits

```c
#define RCC_URGENT_STOP_REQUEST      (UINT32_C(1) << 0)
#define RCC_URGENT_MEASUREMENT_FAULT (UINT32_C(1) << 1)
#define RCC_URGENT_CONTROL_FAULT     (UINT32_C(1) << 2)
typedef uint32_t rcc_urgent_notification_t;
```

Bits are level-like actionable indications, not event counters. Producers retain the
underlying condition or correlated data until Control processes it. FDD-09 assigns
FreeRTOS notification indices and atomic publication details.

## 9. Hybrid static-port model

### 9.1 Port instance form

Each physical/test boundary uses a typed immutable port instance:

```c
typedef struct {
    const rcc_example_port_api_t *api;
    void *context;
} rcc_example_port_t;
```

The concrete backend owns `context`. Both the context storage and API table have a
declared lifetime of the complete application run. A consumer receives a pointer to a
const port instance during initialization and does not replace it later.

### 9.2 Port rules

| ID | Rule |
|---|---|
| `FDD-COMMON-PORT-001` | Port instances and API tables are statically composed by `rcc_app`; there is no mutable service locator. |
| `FDD-COMMON-PORT-002` | Production composition supplies only `rcc_platform_esp32` physical backends. Test backends are not compiled or linked into `PRODUCTION`. |
| `FDD-COMMON-PORT-003` | Every required callback is non-null. Optional capability is reported by a capability mask and returns `RCC_STATUS_NOT_SUPPORTED`, never by calling a null function pointer. |
| `FDD-COMMON-PORT-004` | Callback functions use `rcc_status_t`, fixed-width values, explicit units, and caller-provided bounded storage. |
| `FDD-COMMON-PORT-005` | Port methods contain physical mechanism only. They do not authorize commands, evaluate charging policy, set inhibit, or choose control transitions. |
| `FDD-COMMON-PORT-006` | A test backend shall implement the same contract and error behavior as the production backend at the abstraction boundary. |
| `FDD-COMMON-PORT-007` | Port context shall not point to task-local or temporary storage. |
| `FDD-COMMON-PORT-008` | Port calls document owner task, ISR suitability, maximum blocking, and partial-initialization behavior. |

### 9.3 Stateful module handles

Stateful L3–L5 modules expose opaque handles with direct functions. Instance storage
is module-owned static storage or a build-time bounded module pool initialized before
normal operation. No run-time heap allocation is required. The composition root
receives the opaque handle and passes it only to the assigned owner.

A module with an architectural single instance may expose one explicit initialization
function returning its opaque handle. This is not permission for arbitrary global
access: no public `get_instance()` service locator is allowed, and all calls still
require the handle supplied during composition.

## 10. Relay port

### 10.1 Contract shape

```c
typedef struct {
    rcc_relay_command_t commanded_state;
    rcc_relay_feedback_t feedback_state;
    uint32_t driver_status;
} rcc_relay_port_status_t;

typedef struct {
    rcc_status_t (*initialize_safe)(void *context);
    rcc_status_t (*set_command)(void *context, rcc_relay_command_t command);
    rcc_status_t (*get_status)(void *context,
                               rcc_relay_port_status_t *out_status);
} rcc_relay_port_api_t;

typedef struct {
    const rcc_relay_port_api_t *api;
    void *context;
} rcc_relay_port_t;
```

### 10.2 Ownership and behavior

| Operation | Authorized caller/context | Required behavior |
|---|---|---|
| `initialize_safe` | `rcc_app` before run-time ownership handoff | Configure the physical output to the de-energized OFF level before enabling normal task operation; idempotent OFF attempts are required |
| `set_command(OFF)` | `ControlSafetyTask` after handoff | Issue physical OFF without waiting for persistence, logging, telemetry, or external acknowledgment |
| `set_command(ON)` | `ControlSafetyTask` after all L4 guards | Issue ON mechanism only; the port does not verify session permission |
| `get_status` | Control or controlled diagnostics through owner-mediated access | Return command and genuine feedback/driver state; do not invent feedback |

The build graph shall prevent transports, command router, persistence, diagnostics,
and measurement components from depending on the relay port. `rcc_app` may access
only the safe-initialization surface before handing the run-time instance to
`ControlSafetyTask`. FDD-05 defines the final API split or private wrapper that
enforces this distinction.

If `initialize_safe` or an OFF command reports failure, software still records the
failure and remains in a conservative state. The report does not prove that a welded
contact or shorted driver physically opened; hardware-level detection remains an open
system-safety item.

## 11. ADC port

### 11.1 Raw acquisition types

```c
typedef enum {
    RCC_ADC_CHANNEL_IOUT = 0,
    RCC_ADC_CHANNEL_VOUT = 1
} rcc_adc_channel_t;

typedef struct {
    rcc_adc_channel_t channel;
    uint32_t raw_code;
} rcc_adc_raw_sample_t;

typedef struct {
    const rcc_adc_raw_sample_t *samples;
    uint32_t sample_count;
    uint32_t acquisition_sequence;
    rcc_monotonic_us_t acquisition_started_us;
    rcc_monotonic_us_t acquisition_completed_us;
    uint32_t driver_status;
    bool overrun_detected;
} rcc_adc_batch_view_t;

typedef struct {
    rcc_status_t (*initialize)(void *context);
    rcc_status_t (*start)(void *context);
    rcc_status_t (*wait_batch)(void *context,
                               rcc_duration_ms_t timeout_ms,
                               rcc_adc_batch_view_t *out_batch);
    rcc_status_t (*release_batch)(void *context,
                                  const rcc_adc_batch_view_t *batch);
    rcc_status_t (*stop)(void *context);
} rcc_adc_port_api_t;

typedef struct {
    const rcc_adc_port_api_t *api;
    void *context;
} rcc_adc_port_t;
```

### 11.2 Contract rules

- The production backend configures ADC1 continuous DMA with the fixed alternating
  sequence ADC1_CH6 (`IOUT_MCU_ADC`) then ADC1_CH7 (`VOUT_MCU_ADC`).
- The sequence, sampling rate, attenuation, conversion mode, and DMA geometry are
  hardware/build controlled, not NVS runtime configuration.
- `wait_batch` is task-context only and bounded by `timeout_ms`.
- The batch is a borrowed immutable view into ADC-owned storage. It remains valid only
  until the matching `release_batch`; the consumer shall not retain its pointer.
- Each raw sample carries a channel identity. The acquisition task validates the
  expected alternation and does not infer channel solely from array position after an
  overrun or malformed driver record.
- ISR work is limited to driver servicing and notification. No calibration,
  filtering, fault policy, logging, or relay action occurs in ISR context.
- Overrun, malformed pattern, driver error, empty batch, and timeout are explicit
  health inputs to FDD-02; no stale batch is republished as fresh.

The exact rate, DMA capacity, batch size, ADC settling, and stale deadline remain
evidence-bound by `ARCH-ACT-001` and `FDD-OPEN-005`.

## 12. Storage port

### 12.1 Contract shape

```c
typedef uint16_t rcc_storage_key_t;

typedef struct {
    rcc_status_t (*initialize)(void *context);
    rcc_status_t (*read_blob)(void *context,
                              rcc_storage_key_t key,
                              uint8_t *destination,
                              uint32_t capacity_bytes,
                              uint32_t *out_length_bytes);
    rcc_status_t (*write_blob)(void *context,
                               rcc_storage_key_t key,
                               const uint8_t *source,
                               uint32_t length_bytes);
    rcc_status_t (*commit)(void *context);
    rcc_status_t (*get_health)(void *context, uint32_t *out_health);
} rcc_storage_port_api_t;

typedef struct {
    const rcc_storage_port_api_t *api;
    void *context;
} rcc_storage_port_t;
```

### 12.2 Contract rules

- `rcc_storage_port_t` exposes storage mechanism, not record validity or safety policy.
- `rcc_persistence` is the only normal run-time caller after service startup.
- Buffers are caller-owned and bounded. The port performs no unbounded allocation.
- `write_blob` prepares the backend write; `commit` returns `RCC_STATUS_OK` only when
  the ESP-IDF NVS commit call has completed successfully. FDD-03 defines the higher
  previous-or-new generation guarantee and power-cut recovery.
- A truncated destination returns a defined size/error result and never reports a
  partial blob as valid.
- Key numeric assignments, namespaces, record sizes, erasure/recovery, and endurance
  are defined by FDD-03 and FDD-11.
- Raw erase is not part of the general public port. Any service recovery erase shall
  be a separately authorized, narrowly exposed operation with conservative restart.

Storage `RCC_STATUS_OK` is implementation evidence only at the stated port boundary;
it is not by itself a valid-record, atomic-generation, or safety-state verification.

## 13. Communication ports

Transport adapters operate on native frames or bounded byte streams. During static
composition, each adapter receives both an L2 port instance and an immutable L3
trusted-source descriptor. The adapter attaches that descriptor after physical and
transport validation; payload data cannot select or change it.

### 13.1 CAN port

```c
typedef struct {
    uint32_t identifier;
    uint32_t flags;
    rcc_monotonic_us_t received_us;
    uint16_t data_length;
} rcc_can_rx_metadata_t;

typedef struct {
    uint32_t identifier;
    uint32_t flags;
    uint16_t data_length;
} rcc_can_tx_metadata_t;

typedef struct {
    rcc_status_t (*initialize)(void *context);
    rcc_status_t (*receive)(void *context,
                            uint8_t *data,
                            uint16_t capacity_bytes,
                            rcc_duration_ms_t timeout_ms,
                            rcc_can_rx_metadata_t *out_metadata);
    rcc_status_t (*send)(void *context,
                         const rcc_can_tx_metadata_t *metadata,
                         const uint8_t *data,
                         rcc_duration_ms_t timeout_ms);
    rcc_status_t (*recover)(void *context);
    rcc_status_t (*get_health)(void *context, uint32_t *out_health);
} rcc_can_port_api_t;

typedef struct {
    const rcc_can_port_api_t *api;
    void *context;
} rcc_can_port_t;
```

The caller provides frame storage so the port contract does not guess a final payload
capacity while `ICD-OPEN-006` remains unresolved. The backend rejects data lengths not
supported by the selected controller/configuration. `recover` performs controller
recovery mechanism only; it does not retry application commands or change authority.

### 13.2 Bounded byte-stream port

```c
typedef struct {
    rcc_status_t (*initialize)(void *context);
    rcc_status_t (*read)(void *context,
                         uint8_t *destination,
                         uint32_t capacity_bytes,
                         rcc_duration_ms_t timeout_ms,
                         uint32_t *out_length_bytes);
    rcc_status_t (*write)(void *context,
                          const uint8_t *source,
                          uint32_t length_bytes,
                          rcc_duration_ms_t timeout_ms,
                          uint32_t *out_length_bytes);
    rcc_status_t (*discard_receive)(void *context);
    rcc_status_t (*get_health)(void *context, uint32_t *out_health);
} rcc_byte_stream_port_api_t;

typedef struct {
    const rcc_byte_stream_port_api_t *api;
    void *context;
    uint32_t capabilities;
} rcc_byte_stream_port_t;
```

Separate immutable instances represent RS485, operational UART, and service UART.
Their L3 adapter identities come from build/hardware composition, not received bytes
or the L2 port type.
Half-duplex direction control, drain behavior, and recovery are backend/transport
responsibilities defined in FDD-08; a completed byte write is not an application ACK.

### 13.3 Common communication rules

- Receive and transmit waits are bounded and return explicit timeout/partial results.
- Partial byte-stream transfer is reported through `out_length_bytes`; the transport
  owns retry/framing behavior.
- Invalid addressing, frame integrity, segmentation, or protocol syntax is processed
  above L2 and cannot trigger a relay action in a port callback.
- Driver congestion or failure cannot back-pressure `ControlSafetyTask`.
- Buffer capacities, queues, frame sizes, recovery deadlines, and bitrates remain
  controlled by the ICD, FDD-08, FDD-09, and FDD-11.

## 14. Monotonic-time and reset port

```c
typedef struct {
    rcc_status_t (*initialize)(void *context);
    rcc_status_t (*get_monotonic_us)(void *context,
                                     rcc_monotonic_us_t *out_time_us);
    rcc_status_t (*get_reset_class)(void *context,
                                    rcc_reset_class_t *out_reset_class);
    rcc_status_t (*get_raw_reset_detail)(void *context,
                                         uint32_t *out_raw_detail);
} rcc_time_port_api_t;

typedef struct {
    const rcc_time_port_api_t *api;
    void *context;
} rcc_time_port_t;
```

- `get_monotonic_us` is non-blocking and monotonic within a boot.
- Control durations use this port or the L3 `rcc_time` wrapper; they never use UTC.
- `get_reset_class` performs platform translation only. L4 boot/fault policy decides
  inhibit behavior using the reset class and persistent state.
- `get_raw_reset_detail` is diagnostic and shall not be used as an undocumented
  substitute for the portable classification.
- Unknown/unmappable reset reasons return `RCC_RESET_CLASS_UNKNOWN`, which is handled
  conservatively by the boot design.

## 15. Initialization, ownership handoff, and shutdown

### 15.1 Initialization phases

| Phase | Allowed action | Prohibited action |
|---|---|---|
| Static construction | Bind const API tables, contexts, build identity, and immutable descriptors | Hardware output change, task start, dynamic backend selection |
| Safe hardware initialization | Call relay `initialize_safe` and establish OFF before broad service startup | Relay ON or autonomous eligibility |
| Port initialization | Initialize time/reset, storage, ADC, and communication mechanisms in controlled order | Treat partial success as operational readiness |
| Service initialization | Validate persistence and construct L3/L4 opaque modules | Start charging before self-test |
| Task creation | Create bounded IPC and tasks, then transfer owners | Expose mutable handles to unrelated tasks |
| Operational handoff | `ControlSafetyTask` becomes sole run-time relay owner after self-test inputs are available | Further direct relay commands from composition code |

Each phase returns an explicit status and records which objects reached a valid state.
Failure unwinds toward relay OFF; cleanup shall not command ON or erase required safety
state.

### 15.2 Module lifecycle state

Every stateful module distinguishes at least `UNINITIALIZED`, `READY`, and `FAILED`.
Repeated initialization either returns the existing state without side effects or a
defined invalid-state error. Use-before-initialize and use-after-failure shall not
proceed with partially initialized data.

Normal firmware does not require a general run-time module destruction path. Test
fixtures may provide explicit reset functions compiled only in `TEST` when needed to
isolate cases.

## 16. Error translation and containment

| Boundary | Input error form | Output form | Rule |
|---|---|---|---|
| ESP-IDF → L2 backend | `esp_err_t`, driver event, raw reset cause | `rcc_status_t` plus bounded backend detail | Preserve cause for diagnostics; do not expose ESP-IDF types upward |
| L2 port → L3/L4 | Status and raw health | Service/domain outcome | Apply policy only in owning upper layer |
| Router → Control | Validated command plus trusted metadata | Admission/terminal domain result | Authorization does not bypass state or safety guards |
| Domain → ICD result | Domain status, reason, state, fault | Explicit ICD result/reason encoding | Never serialize an internal enum or struct by memory copy |
| Fault → safe action | Qualified condition | Relay OFF then persistence/diagnostic | Safe action precedes nonessential work |

Assertions are permitted for programmer invariants during development, but the
production behavior for null external input, malformed data, resource exhaustion,
driver failure, stale data, timeout, and storage failure shall be explicit.

## 17. Concurrency and memory rules

### 17.1 Ownership matrix

| Object | Sole writer/owner | Readers/consumers | Transfer/publication |
|---|---|---|---|
| ADC DMA/batch storage | `adc_port` and `AdcAcquisitionTask` | Measurement processing during borrowed view | `wait_batch`/`release_batch` |
| `rcc_measurement_snapshot_t` | `AdcAcquisitionTask`/`rcc_measurement` | Control and telemetry | Latest-value double buffer plus sequence protocol |
| Control state and relay command | `ControlSafetyTask` | Published snapshot consumers | Private state; relay port call |
| `rcc_system_state_snapshot_t` | `ControlSafetyTask` | Router, transports, diagnostics | Latest-value double buffer plus sequence protocol |
| Control-command queue item | `CommandRouterTask` before send; Control after successful copy | Control | Bounded by-value queue |
| Persistence request/object | Requester then Persistence under pool protocol | Persistence service | Bounded queue plus immutable object reference |
| Persistence ACK | Persistence producer; correlated requester consumer | Control/config/calibration | Bounded result/notification contract |
| Duplicate cache | `CommandRouterTask` | Router only | No direct sharing |
| Port contexts | Concrete backend | Assigned owner task/service | Const port handle; backend-controlled synchronization |

### 17.2 Snapshot requirements

The double-buffer/sequence implementation belongs to FDD-09. Its public read contract
shall guarantee that a successful read returns one self-consistent copy. A failed or
exhausted retry returns an explicit unavailable/inconsistent result; it shall not
return a torn value marked valid. Readers never retain internal buffer pointers.

### 17.3 Allocation rules

- Shared queue items and snapshots are fixed size at build time.
- Ports use caller-provided buffers or backend-owned static buffers with explicit
  borrowed lifetimes.
- Stateful-module instances and port contexts are allocated statically or from
  build-time bounded startup pools.
- No safety-path callback allocates from the heap during normal operation.
- Exact sizes, alignment, queue depth, pool count, stack use, and resource margin are
  closed by the owning FDD and FDD-11 before the integration gate.

## 18. Serialization and compatibility boundary

None of the C declarations in this document is a wire or NVS ABI. Explicit codecs
shall:

- write/read each field using the controlled width, byte order, and registry value;
- validate schema version, length, reserved values, range, integrity, and required
  fields before constructing a domain object;
- translate unknown values according to the controlling ICD or persistence policy;
- set reserved output fields to zero;
- prevent padding, alignment, compiler enum width, `bool` representation, and host
  endianness from affecting stored or transmitted bytes;
- provide golden vectors on host and ESP32.

Static assertions may verify expected internal widths and capacity bounds, but shall
not be used to justify native-structure serialization.

## 19. Production and test composition

### 19.1 Production

- `rcc_build_profile` binds every required port to `rcc_platform_esp32`.
- Missing required port, callback, or backend causes a build or safe-start failure.
- Test factories, mock contexts, fault injection, and test control commands are absent
  from the linked image.
- Port instances are immutable after composition.

### 19.2 Test

- `rcc_test_ports` supplies deterministic relay, ADC, storage, communication, time,
  and reset implementations with the same port types.
- Tests inject failures through defined port outcomes, not by modifying private domain
  state.
- Relay test ports default to OFF and record every command with monotonic ordering.
- Storage test ports model commit failure, corruption, old/new generations, timeout,
  and power interruption as defined by FDD-03.
- ADC test ports model valid data, missing channels, saturation, overrun, stale batches,
  and sequence errors as defined by FDD-02.

Test-only reset helpers and inspection APIs remain in `test_support` and are never
included by production components.

## 20. Verification baseline

| Verification ID | Requirement/design IDs | Level | Method and stimulus | Acceptance criterion | Status |
|---|---|---|---|---|---|
| `FDD-COMMON-VER-001` | `FDD-RULE-LAYER-001` through `006`; Section 4 | Build/static review | Generate component dependency graph for both profiles | No cycle or prohibited upward/concrete dependency | Planned |
| `FDD-COMMON-VER-002` | `FDD-RULE-API-001` through `010`; Sections 5–8 | Host compile/static analysis | Compile public headers alone and in randomized include order | No missing direct include, width failure, warning, or ESP-IDF leakage into domain headers | Planned |
| `FDD-COMMON-VER-003` | `FDD-COMMON-PORT-001` through `008` | Host unit | Instantiate each deterministic test port and exercise all outcomes | Required callbacks non-null; bounded success/error semantics match contract | Planned |
| `FDD-COMMON-VER-004` | `FDD-RULE-SAFE-001`, Sections 4 and 10 | Build/link/static review | Inspect dependency and symbol references | Only safe startup composition and `rcc_control` can reference the relay actuation surface; no transport/service reference | Planned |
| `FDD-COMMON-VER-005` | Section 8 snapshots | Host concurrency model | Force publication interleavings and sequence changes | Reader returns one consistent snapshot or explicit failure; never a torn snapshot marked valid | Planned |
| `FDD-COMMON-VER-006` | Sections 8.5–8.8 | Host boundary | Use stale tokens, pool generations, wrong lengths, and mismatched ACK IDs | Every invalid correlation/reference is rejected without action or misrouting | Planned |
| `FDD-COMMON-VER-007` | Sections 11–14 | Target integration | Exercise port initialize, timeout, error, partial-transfer, and recovery cases | Every call terminates within its bound and maps driver results deterministically | Planned |
| `FDD-COMMON-VER-008` | `FDD-RULE-SAFE-010`, Section 19 | Build inspection | Compare production map/symbol/component list with forbidden test registry | No mock, injector, test command, or test reset symbol/component in production image | Planned |
| `FDD-COMMON-VER-009` | Section 18; `ICD-MSG-001` through `008` | Host + target | Encode/decode controlled golden vectors and corrupt variants | Identical bytes across host/target; invalid inputs rejected before domain construction | Planned; exact vectors owned by ICD/FDD-08 |
| `FDD-COMMON-VER-010` | Sections 10 and 15 | Target + HIL | Inject partial initialization and relay-port failures | OFF is attempted first; operational handoff and ON eligibility remain blocked | Planned |

Execution of these tests belongs to the implementation/verification phase. Their
presence here does not mean the requirement has been verified.

## 21. Traceability

| Design area | Controlling inputs | Downstream owner |
|---|---|---|
| Component/layer boundaries | Architecture 5–6; `FDD-RULE-LAYER-001` through `006`; `ADR-FW-010` | All FDDs and build system |
| Hybrid static ports | `ADR-FW-009`; FDD-00 Sections 8, 14, and 17 | FDD-02, 03, 05, 08, 10 |
| Measurement types and ADC port | SRS 5.1 and 5.3; Architecture 8, 9.1, and 14; `ADR-FW-003`, `ADR-FW-004` | FDD-02 and FDD-09 |
| Relay port and ownership | SRS 5.2; `FW-SM-001` through `FW-SM-003`; `ARCH-INV-001` through `ARCH-INV-004` | FDD-05, FDD-09, FDD-10 |
| Persistence types and storage port | SRS 11; Architecture 9.4, 11–13, and 17 | FDD-03, FDD-05, FDD-06 |
| Fault, inhibit, and reset types | SRS 10; Architecture 15 and 20 | FDD-04, FDD-05, FDD-10 |
| Command/source/reply types | SRS 9 and 13; ICD 4–13 | FDD-07 and FDD-08 |
| Communication ports | ICD 4.2, 16–19, and open interface actions | FDD-08 and FDD-09 |
| Snapshots, queues, urgent notifications | SRS 6.2; Architecture 7–8 and 19 | FDD-02, FDD-05, FDD-07, FDD-09 |
| Production/test separation | SRS 16; Architecture 21; `FDD-RULE-SAFE-010` | FDD-09, FDD-10, FDD-11 |

## 22. Open actions

| Action ID | Required decision or evidence | Affected gate/document | Acceptance evidence | Confidence |
|---|---|---|---|---|
| `FDD-COMMON-ACT-001` | ESP-IDF API baseline is selected as v6.1 for ESP32; record the exact installed SDK release/tag and bundled toolchain, then select C language revision, warnings-as-errors policy, formatter, static analyzer, and coding-standard subset | FDD-01/Foundation; closes master `FDD-OPEN-001` and contributes to `FDD-OPEN-003` | Reproducible `idf.py --version`/SDK commit and toolchain record, official v6.1 API links, and clean policy run | `needs_verification` |
| `FDD-COMMON-ACT-002` | Review and baseline the proposed `Firmware/` component tree, `rcc_` prefix, and public/private header ownership | FDD-01/Foundation; closes master `FDD-OPEN-002` | Responsible-human review plus generated acyclic dependency graph | `needs_verification` |
| `FDD-COMMON-ACT-003` | Define final fault ID/mask registry, reason registry mapping, and reserved ranges | FDD-04, FDD-07, ICD | Controlled registries and unknown-value tests | `needs_verification` |
| `FDD-COMMON-ACT-004` | Define final command payload union, event payload union, and bounded object-pool lifetimes/capacities | FDD-03, FDD-06, FDD-07, FDD-10, FDD-11 | Compilable types, static budget, stale-reference and capacity tests | `needs_verification` |
| `FDD-COMMON-ACT-005` | Derive exact ADC batch/DMA bounds and communication native-buffer capacities | FDD-02, FDD-08, FDD-09, FDD-11 | Hardware/ICD binding plus measured load and memory evidence | `needs_verification` |
| `FDD-COMMON-ACT-006` | Choose and verify the snapshot atomic/sequence implementation for ESP32 dual-core and host tests | FDD-09 | Memory-order design, stress test, and target evidence | `needs_verification` |
| `FDD-COMMON-ACT-007` | Define the enforcement split between relay safe initialization and private run-time actuation surface | FDD-05 and FDD-10 | Build dependency/symbol test showing no unauthorized run-time caller | `needs_verification` |
| `FDD-COMMON-ACT-008` | Bind reset-cause translation to the selected ESP-IDF version and verify brownout/panic/watchdog classification | FDD-04 and FDD-10 | Target reset-injection matrix with raw and portable classifications | `needs_verification` |

Open numeric capacities and timings remain symbolic. This is deliberate and does not
permit unbounded implementation.

## 23. FDD-01 review gate

| Field | Value |
|---|---|
| Gate ID | `FW-GATE-FDD-001` |
| Gate definition | Common types, ownership, component boundaries, and module ports are suitable as the foundation for FDD-02 through FDD-11 |
| Artifact assessed | `RCC-FW-FDD-001`, Draft 0.1 |
| Scope | Hybrid static-interface choice, component tree, common types, shared value contracts, L2 ports, lifecycle, concurrency, error translation, build composition, and verification seams |
| AI assessment | `recommended_conditional_pass` |
| Assessment basis | SRS Draft 0.1; Architecture Draft 0.2; ICD Draft 0.1; FDD master Draft 0.1; explicit user selection of Option A |
| Open conditions | Resolve or assign `FDD-COMMON-ACT-001` through `FDD-COMMON-ACT-008` to their owning downstream gates; complete the planned contract/build checks when source exists |
| Residual risks | Port timing and resource bounds are not measured; physical relay feedback/coverage is incomplete; ADC analog behavior and transport bindings remain unverified |
| Human decision | `pending_human_decision` |
| Approved by | `pending_human_decision` |
| Decision timestamp | `pending_human_decision` |
| Release authorization | `pending_human_decision` |

The conditional recommendation means this interface baseline is coherent enough for
review and for drafting dependent FDD documents if the responsible human accepts the
revision risk. It is not a safety approval, residual-risk acceptance, implementation
verification, or production-readiness claim.
