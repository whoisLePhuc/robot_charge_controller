# Firmware System Requirements Specification

## 1. Document control

| Field | Value |
|---|---|
| Document ID | `RCC-FW-SRS-001` |
| Project | Robot Charge Controller |
| Applicable hardware variant | Split Board Design — Control Board + Relay Board |
| Record revision | Draft 0.1 |
| Status | Under review |
| Prepared at | 2026-08-31, Asia/Bangkok (UTC+07:00) |
| Prepared by | Codex drafting support, based on explicit user-selected design decisions |
| Hardware source baseline | Git commit `fe85ff2` plus uncommitted hardware changes listed below |
| Firmware baseline | Pre-implementation architecture baseline; no firmware source revision exists yet |

This document records requirements and constraints. It does not certify the hardware, approve a release, or establish production safety.

### 1.1 Applicable uncommitted hardware changes

The hardware working tree is not a controlled release revision. At the time this document was drafted, the relevant modified artifacts were:

- `hardware/Split_Board_Design/Control_Board/MCU_Control.kicad_sch`
- `hardware/Split_Board_Design/Control_Board/control-board.kicad_pcb`
- `hardware/Split_Board_Design/Relay_Board/Output_Sensing.kicad_sch`

The firmware pin mapping in this document therefore remains tied to this working-tree baseline until a human-controlled hardware revision incorporates those changes.

## 2. Purpose and scope

The firmware shall supervise a high-power DC charging path for a mobile robot. It shall detect a charger request from the measured output voltage, control a DC-rated relay, measure charging voltage and current, expose telemetry, accept authorized commands, preserve safety-relevant state across reset, and provide service configuration and calibration.

The firmware runs on an ESP32-WROOM-32E using ESP-IDF and FreeRTOS.

### 2.1 In scope

- Autonomous detection of a charge request from `VOUT_MCU_ADC`.
- Relay control for the 60 VDC / 20 A maximum normal operating charge path.
- Voltage and bidirectional-current measurement processing.
- Charging-session state machine, completion detection, re-arm, inhibit, and fault handling.
- CAN, RS485, and 3.3 V UART application-level communication.
- Configuration, per-board calibration, diagnostic logging, reset classification, and persistent safety state.
- Host, target, HIL, and controlled bench verification requirements.

### 2.2 Out of scope

- Battery charging regulation, CC/CV control, or replacement of the charger or BMS.
- Design or supervision of the separate 24 V auxiliary source.
- Wi-Fi and Bluetooth operation in firmware v1.
- Final numeric hard-fault limits before sensing headroom, tolerance, response time, and bench evidence are available.
- Safety certification, compliance approval, and production release authorization.

## 3. System context and design status

| Area | Requirement or known value | Status |
|---|---|---|
| Primary function | Connect and disconnect the robot battery charging path while measuring VOUT and IOUT | Confirmed design intent |
| Maximum normal voltage | 60 VDC | Confirmed project requirement |
| Maximum normal current | 20 A | Confirmed project requirement |
| MCU | ESP32-WROOM-32E | Confirmed hardware selection |
| Operating model | Hybrid autonomous + remote command capability | Human-selected baseline |
| Safe relay state | Open / de-energized | Human-selected baseline |
| Charger request source | `VOUT_MCU_ADC` while relay is open | Human-confirmed behavior |
| Charging voltage source | `VOUT_MCU_ADC` while relay is closed | Human-confirmed behavior |
| Current measurement | `IOUT_MCU_ADC`, including required negative-current headroom | Human-selected requirement; range needs verification |
| Wireless interfaces | Disabled/not included in firmware v1 | Human-selected baseline |
| Hard fault thresholds | Must be derived from hardware evidence; 60 V and 20 A are not fault thresholds | Needs verification before detailed-design gate |
| Environmental and regulatory limits | Not yet supplied | Blocking for production/release assessment, not for architecture drafting |

## 4. Terminology

| Term | Definition |
|---|---|
| Charger present/request | Relay is open and `VOUT_MCU_ADC` is within the configured request window for the required validation time |
| Charging session | Interval beginning with an accepted start transition and ending with completion, STOP, fault, or interrupted power |
| Autonomous start | A valid charger request can begin a session without a new external command |
| Active control interface | The one external interface selected in NVS to issue operational commands |
| Monitor-only interface | An interface allowed to read status/telemetry but not issue operational control commands |
| Inhibit | A deliberate lock that keeps the relay open and suppresses autonomous start even if a charge request is present |
| Recoverable fault | A fault that opens the relay and requires a new-session action before another attempt |
| Latched fault | A fault that requires service-UART `CLEAR_FAULT` and successful safety re-evaluation |
| Session guard | Persistent write-ahead record proving that a charging session was armed or active and has not yet ended cleanly |

## 5. Hardware and signal interfaces

### 5.1 ADC pin assignment

| Signal | ESP32 module pin | GPIO | ADC channel | Direction | Requirement |
|---|---:|---:|---|---|---|
| `IOUT_MCU_ADC` | 6 | GPIO34 | ADC1_CH6 | Analog input | Measure calibrated signed charge-path current |
| `VOUT_MCU_ADC` | 7 | GPIO35 | ADC1_CH7 | Analog input | Measure charger request voltage with relay open and charge/battery voltage with relay closed |

At the system boundary, the source signal is also referred to as `VOUT_SENSE_ADC`; `VOUT_MCU_ADC` is the corresponding MCU-side net name. The connector/net mapping between the Relay Board and Control Board shall be verified against the controlled split-board hardware revision.

The hardware revision and `CAL_DATA` revision shall change when this pin mapping or either analog signal chain changes.

### 5.2 Relay interface

| Property | Requirement |
|---|---|
| Default state | OFF/open during reset, boot, uninitialized operation, service lock, inhibit, and fault |
| Software ownership | Only `ControlSafetyTask` may command the relay driver |
| Permitted ON states | `RELAY_CLOSING`, `CHARGE_VERIFY`, and `CHARGING` only |
| Opening order | Physical open command first; persistence and diagnostic logging afterward |
| Closing order | Successful precheck and confirmed persistent `SESSION_ARMED` commit before relay ON |

### 5.3 ADC acquisition constraints

- ADC1 continuous mode with DMA shall sample ADC1_CH6 and ADC1_CH7 in a fixed alternating pattern.
- The ADC ISR shall only acknowledge/collect minimum driver state and notify `AdcAcquisitionTask`.
- The sampling rate shall be fixed for a given hardware revision. It shall not be runtime-NVS-configurable or adaptive.
- The numeric sampling rate, analog settling requirement, and filter bandwidth shall be bound to the hardware revision after analog characterization.
- Control shall consume an age-stamped, self-consistent measurement snapshot rather than accessing ADC driver buffers directly.
- A stale, missing, saturated, or implausible measurement shall be handled according to the fault matrix.

## 6. Platform and runtime architecture requirements

| Requirement ID | Requirement | Verification |
|---|---|---|
| `FW-ARC-001` | Firmware shall use ESP-IDF and FreeRTOS. | Build inspection |
| `FW-ARC-002` | Firmware v1 shall not initialize Wi-Fi or Bluetooth. | Build/config inspection and target test |
| `FW-ARC-003` | The architecture shall be event-driven with one task owning the control state machine and relay output. | Static review and target test |
| `FW-ARC-004` | `ControlSafetyTask` and `AdcAcquisitionTask` shall be pinned to Core 1. | Target inspection/test |
| `FW-ARC-005` | Communication, command routing, persistence, and logging shall execute on Core 0. | Target inspection/test |
| `FW-ARC-006` | Communication, logging, and persistence work shall not block the control path. | Load/fault-injection test |
| `FW-ARC-007` | Control and ADC tasks shall be monitored by the task watchdog. | Target fault-injection test |
| `FW-ARC-008` | A watchdog, panic, or brownout reset shall cause reset inhibit rather than autonomous restart. | Reset-reason test |

### 6.1 Task ownership

| Task/module | Core | Relative priority | Responsibility |
|---|---:|---|---|
| `ControlSafetyTask` | 1 | Critical | State machine, fault/inhibit policy, precheck, session decisions, sole relay owner |
| `AdcAcquisitionTask` | 1 | High | ADC DMA consumption, calibration, filtering, freshness/plausibility, measurement publication |
| `CommandRouterTask` | 0 | High | Version, source authorization, duplicate detection, payload validation, normalized commands |
| CAN/RS485/UART transport tasks | 0 | Medium | Transport framing, CRC, segmentation, Rx/Tx |
| `PersistenceTask` | 0 | Medium/Low | Atomic NVS records, session guard, configuration, calibration, safety state |
| `TelemetryLogTask` | 0 | Low | Telemetry snapshots, RAM event ring, bounded persistent summaries |

Numeric FreeRTOS priorities shall be assigned only after a timing budget is established. The relative ordering above is a controlled architectural constraint.

### 6.2 Inter-task data contracts

| Contract | Producer → consumer | Mechanism | Requirement |
|---|---|---|---|
| Measurement snapshot | ADC → Control | Double buffer + sequence counter | Reader shall reject inconsistent or stale data |
| Urgent notifications | ADC/Command Router → Control | Direct task-notification bits | STOP and urgent faults shall not depend on normal command-queue availability |
| Control command queue | Command Router → Control | Bounded queue | Overflow shall reject non-urgent commands explicitly |
| System-state snapshot | Control → communications | Immutable/latest snapshot | Telemetry readers shall not lock or block Control |
| Persistence requests | Control/config → Persistence | Prioritized bounded queue | Safety records outrank diagnostic records |
| Persistence acknowledgment | Persistence → Control | Response notification | Relay close shall wait for `SESSION_ARMED` ACK while relay remains OFF |
| Event log | All modules → Logger | Bounded queue | Diagnostic loss shall not delay a safe physical action |

## 7. Operating modes and state machine

### 7.1 Top-level states

| State | Relay | Purpose and exit condition |
|---|---:|---|
| `BOOT_SAFE` | OFF | Establish safe outputs before peripheral initialization |
| `SELF_TEST` | OFF | Validate reset reason, active config, CAL_DATA, NVS safety records, ADC availability, and interlocks |
| `SERVICE_LOCK` | OFF | Allow service UART configuration/calibration when required data or persistent storage is invalid |
| `CONFIG_MODE` | OFF | Stage/validate/commit configuration only while the charger is absent |
| `OPERATIONAL` | State-dependent | Execute the autonomous/remote charging state machine |
| `INHIBITED` | OFF | Block autonomous start until all active inhibit reasons are validly cleared |
| `LATCHED_FAULT` | OFF | Require service-UART clear request and successful safety re-evaluation |

### 7.2 Operational substates

| State | Entry/behavior | Normal transition |
|---|---|---|
| `IDLE` | Relay OFF; observe VOUT request | Valid request → `VREQ_VALIDATE` |
| `VREQ_VALIDATE` | Require VOUT window continuously for `TREQ_VALID` | Valid dwell → `PRECHECK`; invalid → `IDLE` |
| `PRECHECK` | Validate config, calibration, sensors, inhibit/fault state, and VOUT | Commit session guard → `RELAY_CLOSING` |
| `RELAY_CLOSING` | Relay ON; wait mechanical settling interval | Settle elapsed → `CHARGE_VERIFY` |
| `CHARGE_VERIFY` | Require established current before timeout | Current established → `CHARGING`; timeout → recoverable fault |
| `CHARGING` | Monitor current, voltage, completion, timeout, STOP, and faults | Completion → `COMPLETE`; STOP/fault → safe exit |
| `COMPLETE` | Relay OFF; record session result | → `WAIT_REARM` |
| `WAIT_REARM` | Require charger removal dwell | Valid removal → `IDLE` |

### 7.3 Global state invariants

| Requirement ID | Requirement |
|---|---|
| `FW-SM-001` | Relay ON shall be impossible outside `RELAY_CLOSING`, `CHARGE_VERIFY`, and `CHARGING`. |
| `FW-SM-002` | Any transition to inhibit or fault shall command relay OFF before NVS/log operations. |
| `FW-SM-003` | A latched fault clear shall return to `SELF_TEST`, never directly to `IDLE` or a relay-enabled state. |
| `FW-SM-004` | Communication loss shall create diagnostic status only and shall not stall the state machine or terminate a valid session. |
| `FW-SM-005` | `START` acceptance shall mean the request was queued/validated; it shall not assert that the relay is closed. |

## 8. Charge-request and session requirements

### 8.1 Configurable request window

The active operational configuration shall satisfy:

`0 mV <= VREQ_OFF < VREQ_ON < VREQ_MAX <= 60000 mV`

| Requirement ID | Requirement |
|---|---|
| `FW-REQ-001` | With relay open, VOUT within `[VREQ_ON, VREQ_MAX]` shall represent a candidate charge request. |
| `FW-REQ-002` | A request shall become valid only after remaining continuously in the window for `TREQ_VALID`. |
| `FW-REQ-003` | VOUT below `VREQ_ON` or above `VREQ_MAX` before validation completes shall cancel the candidate request. |
| `FW-REQ-004` | A valid autonomous request may start without a new external `START` command when no inhibit, fault, or interlock blocks it. |
| `FW-REQ-005` | With relay closed, VOUT shall be interpreted as charge/battery voltage rather than a separate request signal. |

### 8.2 Session establishment

| Requirement ID | Requirement |
|---|---|
| `FW-SES-001` | Precheck shall validate active config, CAL_DATA, measurement freshness/plausibility, VOUT request, active faults, and inhibit mask. |
| `FW-SES-002` | After precheck, firmware shall atomically commit `SESSION_ARMED` before commanding relay ON. |
| `FW-SES-003` | NVS commit failure shall prevent relay closure and invoke the fail-closed storage policy. |
| `FW-SES-004` | After relay settling, current shall reach `ICHG_ESTABLISH_MIN` before `T_ESTABLISH`. |
| `FW-SES-005` | Failure to establish current shall raise `CHARGE_NOT_ESTABLISHED`; it shall not be treated as charge completion. |

### 8.3 Completion and maximum duration

| Requirement ID | Requirement |
|---|---|
| `FW-END-001` | Completion shall require VOUT to remain in the configured valid charging window while IOUT remains below `ICHG_END` continuously for `TEND`. |
| `FW-END-002` | Completion logic shall be enabled only after a session has successfully established charging current. |
| `FW-END-003` | `TCHARGE_MAX` shall provide an independent maximum-session-duration limit. |
| `FW-END-004` | Reaching `TCHARGE_MAX` without completion shall end the session according to its fault-matrix entry and shall not report successful completion. |

### 8.4 Re-arm

| Requirement ID | Requirement |
|---|---|
| `FW-RAR-001` | After normal completion, firmware shall open the relay and enter `WAIT_REARM`. |
| `FW-RAR-002` | Re-arm shall require `VOUT <= VREQ_OFF` continuously for `TREARM`. |
| `FW-RAR-003` | A new autonomous session shall not begin before re-arm completes. |
| `FW-RAR-004` | If VOUT measurement itself is faulty or untrusted, VOUT-based re-arm shall not clear the associated inhibit. |

## 9. Remote command behavior

| Requirement ID | Requirement |
|---|---|
| `FW-RCMD-001` | One external interface selected in NVS shall be the active operational control interface. |
| `FW-RCMD-002` | Non-selected interfaces shall remain monitor-only except for explicitly defined service behavior. |
| `FW-RCMD-003` | Valid `STOP_CHARGE` shall open the relay and set persistent `REMOTE_INHIBIT`. |
| `FW-RCMD-004` | `REMOTE_INHIBIT` may be cleared by a valid new-session `START_CHARGE` or a valid charger-removal/re-arm cycle. |
| `FW-RCMD-005` | A valid `START_CHARGE` shall re-evaluate all interlocks before any relay-enabled transition. |
| `FW-RCMD-006` | `STOP_CHARGE` shall be idempotent and shall use an urgent path independent of the normal command queue. |
| `FW-RCMD-007` | A repeated request with the same source and `request_id` shall return the cached result without repeating the action. |
| `FW-RCMD-008` | `CLEAR_FAULT` shall be accepted only from the service UART and only when its physical/logical clear conditions are satisfied. |

## 10. Fault, inhibit, and reset policy

### 10.1 Fault levels

| Level | Required behavior |
|---|---|
| `WARNING` | Record/report degradation without opening the relay unless a separate hard requirement demands it |
| `RECOVERABLE` | Open relay, persist `RECOVERY_INHIBIT`, and require valid new-session authorization/re-arm |
| `LATCHED` | Open relay, persist the fault where storage is healthy, and require service-UART clearing followed by `SELF_TEST` |

### 10.2 Inhibit bitmask

Multiple inhibit causes shall coexist in a persistent bitmask. The system shall remain `INHIBITED` while any active bit remains uncleared.

| Bit | Typical source | Allowed clearing policy |
|---|---|---|
| `REMOTE_INHIBIT` | Valid `STOP_CHARGE` | Valid `START_CHARGE` or verified charger removal/re-arm |
| `RESET_INHIBIT` | Watchdog, panic, brownout, or interrupted session guard | Valid `START_CHARGE` or verified charger removal after successful self-test |
| `RECOVERY_INHIBIT` | Recoverable fault | Fault condition inactive plus fault-specific valid START/re-arm policy |

Clearing an inhibit shall not erase the diagnostic event history.

### 10.3 Reset classification

| Reset class | Required boot behavior |
|---|---|
| Normal power-on with no incomplete session/safety record | `SELF_TEST`, then eligible for `IDLE` and autonomous request evaluation |
| Explicit user/software reset classified as normal | Same as normal boot after `SELF_TEST` |
| Watchdog, panic, or brownout | Set/retain `RESET_INHIBIT` |
| Boot with incomplete `SESSION_ARMED/ACTIVE` guard | Set/retain `RESET_INHIBIT` regardless of apparent current relay state |
| Boot with invalid safety NVS/config/calibration data | Enter `SERVICE_LOCK` or `LATCHED_FAULT` according to the storage fault policy |

### 10.4 Fault escalation

- Each recoverable fault shall define its own recurrence count, observation window, and escalation destination.
- Escalation parameters shall be fixed for a firmware/hardware revision and shall not be ordinary runtime configuration.
- Exact escalation values shall be justified by fault mechanism, relay/power-path cycling limits, and verification evidence before the detailed-design gate can pass.

## 11. Persistent storage requirements

### 11.1 Record classes

| Record | Persistence | Integrity/atomicity |
|---|---|---|
| Active operational configuration | Required | Version, CRC, staging, validate, atomic commit |
| Per-board `CAL_DATA` | Required | Independent version/CRC and atomic commit |
| Inhibit bitmask | Required | Safety record with atomic generation |
| Latched fault state | Required when storage is healthy | Safety record with atomic generation |
| Session guard | Required | Write-ahead commit confirmed before relay ON |
| Boot identity/counters | Required at controlled event boundaries | Monotonic generation or sequence |
| Detailed telemetry | Not persistent | Latest snapshot/stream only |
| Current-boot diagnostic detail | RAM ring | Bounded |
| Critical event summaries | Bounded persistent ring | Rate-limited/coalesced, versioned |

### 11.2 Fail-closed storage behavior

| Requirement ID | Requirement |
|---|---|
| `FW-PST-001` | A runtime failure to persist a safety state or configuration shall command/retain relay OFF and create in-RAM `NVS_WRITE_FAILED` latched status. |
| `FW-PST-002` | A boot-time failure to validate required NVS records shall enter `SERVICE_LOCK`. |
| `FW-PST-003` | Diagnostic-log write failure may create a warning but shall not delay a physical safe action. |
| `FW-PST-004` | Power interruption at any commit boundary shall yield either the previous valid generation or the new valid generation, never a partially accepted record. |
| `FW-PST-005` | If the terminal session record cannot be committed after relay OFF, the incomplete guard shall cause conservative inhibit on the next boot. |

## 12. Configuration and calibration

### 12.1 Configuration tiers

| Tier | Contents | Change mechanism |
|---|---|---|
| Operational configuration | Request/completion thresholds, dwell times, selected control interface, telemetry behavior | Staging → validate → atomic NVS commit |
| Hard safety configuration | Hard limits, response deadlines, escalation rules, ADC sample rate tied to hardware revision | Compile-time/release-controlled only |

Only one active operational configuration shall exist. A partial or invalid update shall leave the previous active configuration unchanged.

### 12.2 Configuration mode

- `CONFIG_MODE` shall be entered only with relay OFF and verified charger absence (`VOUT <= VREQ_OFF` for the required dwell).
- `START_CHARGE` shall be rejected in `CONFIG_MODE`.
- Service UART shall remain available for commissioning/recovery when active configuration is missing or invalid.
- After valid configuration exists, operational START/STOP authority shall remain with the selected control interface.

### 12.3 Engineering units and numeric representation

| Quantity | Representation |
|---|---|
| Voltage | `uint32`, millivolts |
| Signed current | `int32`, milliamperes |
| Non-negative duration | `uint32`, milliseconds unless a test/driver contract explicitly requires finer resolution |
| Counters/revisions | Fixed-width unsigned integers with defined rollover handling |

Floating-point wire formats shall not be required for configuration or commands.

### 12.4 Per-board calibration

Calibration shall be layered:

1. ESP-IDF ADC calibration support for the MCU ADC transfer characteristic.
2. Two-point end-to-end VOUT calibration.
3. Negative-zero-positive end-to-end IOUT calibration.
4. Intermediate verification points not reused as fit points.

`CAL_DATA` shall be independent from operational configuration and shall include hardware revision, schema version, CRC, coefficients, calibration conditions, and validation status.

For every operational decision threshold, residual calibrated measurement error at relevant verification points shall not exceed 25% of the nearest associated hysteresis or decision margin. If this condition is not met, `CAL_DATA` shall not be considered valid for operation.

## 13. Application communication model

### 13.1 Common command envelope

| Field | Logical type | Requirement |
|---|---|---|
| `protocol_version` | `uint8` | Application protocol version |
| `message_type` | Enum | `COMMAND`, `COMMAND_RESULT`, or `EVENT` |
| `request_id` | `uint32` | Transaction identity and duplicate detection |
| `command_code` | `uint16` | Stable command code independent of transport |
| `flags` | `uint16` | ACK/segmentation/application options |
| `payload_length` | `uint16` | Decoded payload length |
| `payload` | Command-specific | Integer engineering-unit fields |
| `object_crc32` | Optional | Required for multi-frame config/calibration objects |

Transport adapters shall supply trusted `source_interface` and `source_node` metadata. A sender shall not gain authority by asserting a role inside its payload.

### 13.2 Standard result fields

| Field | Requirement |
|---|---|
| `request_id` | Match the initiating command |
| `command_code` | Identify the command |
| `result` | `ACCEPTED`, `REJECTED`, `COMPLETED`, or `FAILED` |
| `reason_code` | Stable machine-readable explanation |
| `system_state` | Current state-machine state |
| `inhibit_mask` | Current inhibit causes |
| `primary_fault` | Highest-priority active fault |
| `response_data` | Command-specific data |

### 13.3 Command groups and permissions

| Group | Commands | Permission |
|---|---|---|
| Identification | `PING`, `GET_DEVICE_INFO` | All interfaces |
| Monitoring | `GET_STATUS`, `GET_MEASUREMENTS`, `GET_FAULTS`, `GET_EVENT_LOG` | All interfaces |
| Operational control | `START_CHARGE`, `STOP_CHARGE`, `SET_TIME` | Selected control interface |
| Configuration | `GET_CONFIG`, `ENTER_CONFIG_MODE`, `STAGE_CONFIG`, `VALIDATE_CONFIG`, `COMMIT_CONFIG`, `ABORT_CONFIG` | Selected control interface or service UART, subject to CONFIG_MODE |
| Calibration | `GET_CAL_DATA`, `BEGIN_CAL`, `CAL_POINT`, `VALIDATE_CAL`, `COMMIT_CAL`, `ABORT_CAL` | Service UART only |
| Latched recovery | `CLEAR_FAULT` | Service UART only |

The physical framing, bitrate, addressing, segmentation, transport CRC, termination, and timeout rules for CAN, RS485, and UART shall be defined in a separate Interface Control Document.

## 14. Diagnostics and timebase

### 14.1 Logging hierarchy

- Periodic telemetry shall not be written to flash.
- Detailed current-boot transitions shall use a bounded RAM ring.
- Persistent storage shall be limited to reset reason, session result, recoverable/latched faults, configuration/calibration changes, and bounded diagnostic summaries.
- Repeated events shall be coalesced or rate-limited.
- Safety-state persistence shall have priority over diagnostic persistence.

### 14.2 Time representation

Every event shall contain:

- `boot_id`
- `event_seq`
- monotonic time since boot
- `TIME_SYNCED` or `TIME_UNSYNCED`
- optional UTC time when supplied by an external system

UTC synchronization shall never be required to begin or continue autonomous operation.

## 15. Timing and hard-limit binding requirements

The following parameters affect safety or functional validity but do not yet have sufficient implementation evidence for numeric values:

| Parameter class | Examples | Binding evidence required |
|---|---|---|
| Urgent response limits | `T_STOP_MAX`, `T_ADC_FAULT_MAX` | Relay driver timing, scheduler worst case, measurement/filter latency, controlled bench results |
| ADC acquisition | Sample rate, settling, stale timeout, filter coefficients | Analog bandwidth/settling analysis and bench characterization |
| Relay sequence | `T_RELAY_SETTLE`, `T_ESTABLISH` | Relay datasheet, driver timing, charger/load behavior, bench measurement |
| Hard electrical faults | Overvoltage, overcurrent, reverse current, ADC saturation limits | Sensing headroom, tolerance chain, component operating limits, transient/bench evidence |
| Fault escalation | Recurrence count and time window per fault | Failure mechanism, relay/power-path cycling limits, validation evidence |

These values shall be version-controlled hard limits or validated operational parameters as assigned by their class. No verification gate may mark the corresponding requirement passed until the numeric value, tolerance, source, and acceptance criterion are recorded.

## 16. Build profiles and testability

| Profile | Requirement |
|---|---|
| `PRODUCTION` | Real hardware backends only; no fault-injection commands; distinct firmware identity |
| `TEST` | Mock/test backends and controlled fault injection; distinct firmware identity and prominent diagnostic indication |

The test profile shall inhibit relay operation by default until the controlled bench procedure explicitly enables it. The release/build process shall prevent a test image from being treated as a production image.

Core logic shall depend on testable interfaces for ADC, time, NVS, reset reason, and relay output. Fault-injection commands and mock backends shall not be linked into the production image.

## 17. Verification baseline

| Verification ID | Requirement area | Minimum method | Acceptance summary |
|---|---|---|---|
| `FW-BOOT-001` | Boot-safe relay behavior | Target + bench | Relay remains OFF until explicitly permitted |
| `FW-VREQ-001` | Request window/hysteresis | Host + HIL | Correct dwell and no threshold chatter |
| `FW-SESS-001` | Session guard | Target + power-cut | No close before ACK; incomplete guard inhibits next boot |
| `FW-EST-001` | Current establishment | Host + HIL | No-current case produces fault, not completion |
| `FW-COMP-001` | Completion | Host + HIL | Combined VOUT/IOUT dwell required |
| `FW-REARM-001` | Re-arm | Host + HIL | Valid charger-removal dwell required |
| `FW-STOP-001` | Urgent STOP | Target + HIL | Relay opens within bound under communication load |
| `FW-ADC-001` | ADC stale/implausible | Target + HIL | Relay opens within bound and correct inhibit/fault is recorded |
| `FW-FAULT-001` | Escalation/clear | Host + target | Fault-specific escalation and UART-only clear |
| `FW-RESET-001` | Reset classification | Target + HIL | Normal and abnormal resets enter required states |
| `FW-NVS-001` | Atomic storage | Target + fault injection | Old or new valid generation only |
| `FW-CMD-001` | Command authority/idempotency | Host + target | Unauthorized/duplicate behavior matches contract |
| `FW-CONFIG-001` | Config/CAL integrity | Host + target | Invalid records rejected; active record remains intact |
| `FW-LOAD-001` | Saturation/starvation | Target + HIL | Control deadlines retained; STOP urgent path remains effective |
| `FW-CAL-001` | Calibration accuracy | Bench | Residual error stays within the 25%-of-margin rule |
| `FW-LOG-001` | Logging behavior | Host + target | No telemetry flash writes; ordering/rate-limit correct |
| `FW-PROFILE-001` | Build separation | Build + target | Production contains no test-injection command |
| `FW-BENCH-001` | Physical timing/measurement | Bench | Measured results satisfy the bound timing and accuracy budget |

Every verification result shall identify hardware revision, firmware version/hash, active configuration revision, CAL_DATA revision, setup, instruments, raw evidence, acceptance criterion, and result. Tool execution, test execution, criterion pass, and requirement verification are distinct statuses.

## 18. Open evidence actions

These are explicit evidence dependencies rather than implied design values:

| Action ID | Required evidence | Blocks |
|---|---|---|
| `FW-EVID-001` | Characterize VOUT and IOUT analog range, headroom, tolerance, noise, settling, and negative-current capability on the revised board | ADC sample/filter values, hard measurement limits, final CAL acceptance |
| `FW-EVID-002` | Measure relay-driver assertion/release timing and physical relay close/open behavior across operating conditions | `T_RELAY_SETTLE`, `T_STOP_MAX`, fault-response budget |
| `FW-EVID-003` | Define charger/load behavior required to distinguish established current, completion, open circuit, and abnormal current | `ICHG_ESTABLISH_MIN`, `T_ESTABLISH`, `ICHG_END`, `TEND` |
| `FW-EVID-004` | Establish component- and system-supported hard voltage/current/reverse-current thresholds with tolerance and temperature margin | Hard fault table and detailed-design gate |
| `FW-EVID-005` | Identify applicable product safety/EMC/regulatory requirements and responsible human reviewers | Production/release assessment |
| `FW-EVID-006` | Assign a controlled hardware revision containing the ADC pin changes and bind the CAL_DATA schema to it | Firmware/hardware traceability |

## 19. AI assessment and human review boundary

| Field | Value |
|---|---|
| Scope assessed | Firmware requirements and architecture baseline for Split Board Design |
| AI assessment | `recommended_conditional_pass` for requirements/architecture documentation |
| Basis | Operating model, state machine, task ownership, command model, persistence policy, and verification strategy were explicitly selected during design discussion |
| Conditions | Close `FW-EVID-001` through `FW-EVID-006` as applicable before claiming detailed-design, verification, compliance, or release readiness |
| Human decision | Pending explicit review of this written artifact |

This assessment is not a hardware approval, safety certification, waiver, residual-risk acceptance, or release authorization.
