# Hướng dẫn chống nhiễu cho PCB có relay đóng cắt DC 60 V / 20 A

## 1. Mục đích

Tài liệu này tổng hợp các biện pháp **chọn linh kiện** và **layout PCB** nhằm giảm ảnh hưởng của nhiễu phát sinh khi relay đóng/cắt tải DC công suất cao, điển hình:

- Điện áp bus: **60 VDC**
- Dòng tải liên tục: **20 A**
- Điều khiển bằng MCU/ESP32
- Có các khối tín hiệu nhạy như:
  - ADC
  - Current sense
  - UART
  - CAN
  - RS485
  - GPIO
  - EN/RESET
  - DC/DC 60 V → 5 V / 3.3 V

Triết lý thiết kế:

> **Dập nhiễu ngay tại nơi sinh ra → giảm diện tích vòng dòng nhiễu → kiểm soát đường return → bảo vệ nguồn MCU → bảo vệ các tín hiệu nhạy.**

---

# 2. Các nguồn nhiễu chính

Khi relay đóng/cắt đường 60 V / 20 A, có thể xuất hiện:

1. **dI/dt lớn**
2. **dV/dt lớn**
3. **Contact bounce**
4. **Hồ quang điện tại contact**
5. **Overshoot và ringing**
6. **Ground bounce**
7. **Magnetic coupling**
8. **Capacitive coupling**
9. **Radiated EMI**
10. **Sụt nguồn MCU**
11. **Xung điện áp từ relay coil**

Relay tạo ra hai nhóm nhiễu độc lập:

```text
                RELAY
          ┌─────────────┐
MCU ─────►│ COIL        │
          │             │
60V/20A ─►│ CONTACT     │── Load
          └─────────────┘
               │
               ▼
      Hai nguồn nhiễu khác nhau
```

Do đó cần xử lý riêng:

- **Coil suppression**
- **Contact/load suppression**

---

# 3. Thứ tự ưu tiên xử lý

| Ưu tiên | Hạng mục |
|---|---|
| P0 | Chọn relay đúng khả năng đóng/cắt DC 60 V / 20 A |
| P0 | Kiểm soát đường dòng 20 A và đường return |
| P0 | Suppression cho relay coil |
| P0 | Suppression cho contact/tải cảm |
| P0 | Hot-loop của DC/DC |
| P1 | Bảo vệ nguồn 5 V / 3.3 V |
| P1 | EN/RESET của MCU |
| P1 | Current sense / ADC |
| P1 | CAN / RS485 / UART |
| P2 | Tối ưu EMI tổng thể, via stitching, shielding |

---

# 4. Chọn relay

## 4.1. Không dùng rating AC để suy ra rating DC

Relay phải có thông số đóng/cắt DC thực tế đáp ứng:

```text
VDC >= 60 V
IDC >= 20 A
```

Cần kiểm tra tối thiểu:

- Maximum switching voltage DC
- Maximum switching current DC
- Contact material
- DC breaking capacity
- Electrical endurance tại tải DC
- Inrush capability
- Contact resistance
- Coil voltage
- Release time

> DC khó ngắt hơn AC vì dòng không có điểm zero-cross tự nhiên.

Nếu datasheet chỉ ghi:

```text
250 VAC / 20 A
```

không được mặc định rằng relay đó có thể ngắt:

```text
60 VDC / 20 A
```

---

# 5. Dập nhiễu relay coil

## 5.1. Flyback diode

Cấu trúc đơn giản:

```text
+24V
  │
Relay Coil
  │
  ├────|<|────┐
  │           │
 MOSFET       │
  │           │
 GND──────────┘
```

### Ưu điểm

- Đơn giản
- Rẻ
- Clamp tốt
- Bảo vệ MOSFET driver

### Nhược điểm

Dòng coil suy giảm chậm → relay có thể nhả chậm.

---

## 5.2. Diode + Zener hoặc TVS

Nếu muốn relay nhả nhanh hơn:

```text
Relay Coil
    │
    ├── Diode ─ Zener ──┐
    │                    │
  MOSFET                 │
    │                    │
   GND───────────────────┘
```

Hoặc dùng TVS.

### Ưu điểm

- Clamp điện áp driver
- Coil demagnetization nhanh hơn
- Relay release nhanh hơn
- Có thể giảm thời gian hồ quang contact

### Khuyến nghị

Đối với relay công suất cao, nên **chừa footprint** cho:

- Flyback diode
- Zener / TVS

để có thể thử nghiệm thực tế.

---

# 6. Dập transient tại contact relay

## 6.1. Tải cảm DC

Nếu tải là cuộn dây có polarity cố định:

```text
Relay ───── Lload ───── GND
              │   │
              └─|<|─┘
               Diode
```

Có thể dùng:

- Flyback diode
- TVS
- Diode + Zener

---

## 6.2. RC snubber

RC snubber có thể đặt:

- Qua contact relay
- Qua tải
- Gần connector tải

```text
           Relay
60V ──────o/ o──────── Load
           │ │
           R C
           │ │
           └─┘
          Snubber
```

RC snubber giúp:

- Giảm ringing
- Giảm dV/dt
- Giảm contact arcing
- Giảm EMI

### Lưu ý

Không nên chọn RC hoàn toàn theo cảm tính.

Giá trị cuối cùng nên được tune sau khi đo:

- Tần số ringing
- Biên độ overshoot
- Năng lượng tải

---

# 7. Chọn TVS cho bus 60 V

TVS phải thỏa:

```text
VRWM > điện áp bus lớn nhất trong vận hành bình thường
```

và:

```text
VCLAMP < giới hạn điện áp của phần tử cần bảo vệ
```

Cấu trúc mong muốn:

```text
Vbus,max
   ↓
VRWM
   ↓
VBR
   ↓
VCLAMP
   ↓
Absolute Maximum của linh kiện
```

## 7.1. Không nên thiết kế sát ngưỡng

Nếu:

```text
Bus = 60 V
Thiết bị phía sau chỉ chịu tối đa = 60 V
```

thì gần như không còn margin để TVS hoạt động đúng.

Nên có khoảng dự trữ giữa:

- Điện áp vận hành
- Điện áp bắt đầu avalanche TVS
- Điện áp clamp
- Absolute maximum của MOSFET/IC/tải

---

# 8. Layout đường 60 V / 20 A

## 8.1. Tách khu vực công suất và logic

Bố trí tổng thể nên theo dạng:

```text
┌──────────────────────────────────────────────┐
│ HIGH ENERGY / DIRTY AREA                    │
│                                              │
│ 60V IN → Protection → Relay → Shunt → OUT   │
│                                              │
├──────────────────────────────────────────────┤
│ POWER CONVERSION                             │
│                                              │
│             60V → 5V → 3V3                  │
│                                              │
├──────────────────────────────────────────────┤
│ SENSITIVE ANALOG                             │
│                                              │
│        Shunt → INA → RC → ADC               │
│                                              │
├──────────────────────────────────────────────┤
│ CLEAN DIGITAL                                │
│                                              │
│ ESP32    CAN    RS485    UART               │
└──────────────────────────────────────────────┘
```

Mục tiêu:

> Dòng công suất không được chạy xuyên qua khu vực MCU.

---

# 9. Giảm diện tích vòng dòng công suất

Điều quan trọng không chỉ là track rộng.

Cần giảm:

```text
Loop Area
```

Ví dụ không tốt:

```text
+60V ==============================> Relay
                                      │
                                      │
LOAD <===============================┘
```

Loop lớn → inductance lớn → EMI lớn.

Tốt hơn:

```text
+60V ==========================>
RETURN <========================
```

Hai đường đi và về nên:

- Gần nhau
- Ngắn
- Có diện tích vòng nhỏ

---

# 10. Kiểm soát đường return 20 A

## Không nên

```text
20A LOAD
   │
   ↓
=========================== GND
          ↑
        ESP32
          ↑
         ADC
```

Dòng 20 A chạy qua impedance chung sẽ tạo:

- Ground bounce
- ADC error
- False triggering
- MCU reset

## Nên

```text
                 POWER ENTRY
                     ★
                    / \
                   /   \
        High-current    Logic
           return       return
              │            │
            Relay        ESP32
              │            │
             Load         ADC
```

Điểm quan trọng:

> Không nhất thiết phải chia GND thành nhiều net khác nhau.

Mục tiêu là **điều khiển hình học đường dòng hồi** để dòng tải không chạy qua vùng logic.

---

# 11. Không xẻ GND plane tùy tiện

Với PCB 2 lớp, tín hiệu vẫn cần đường hồi liên tục ngay dưới hoặc sát đường đi. B.Cu nên được giữ thành vùng GND/PGND reference liên tục tối đa có thể ở khu vực logic; mọi đoạn cắt bởi hành lang công suất hoặc routing khác phải được review theo dòng hồi thực tế.

Không nên đặt trace tín hiệu chạy qua:

```text
GND plane split
```

vì return current sẽ phải đi vòng.

Hậu quả:

- Loop tín hiệu lớn
- EMI tăng
- Crosstalk tăng
- Signal integrity giảm

Khuyến nghị:

> Giữ B.Cu liên tục tối đa có thể cho GND logic và điều khiển đường high-current return bằng placement/routing. Không để dòng tải 20 A chọn đường hồi qua MCU, ADC hoặc transceiver.

---

# 12. Stack-up 2 lớp đã chọn

Baseline sản xuất được chọn là đồng thành phẩm 2 oz trên cả hai mặt:

```text
F.Cu — Components + high-current corridor + buck hot loop
       + critical short signals

B.Cu — High-current return corridor + GND/PGND reference
       + limited slow-signal escape only where return path remains intact
```

Không có lớp plane bên trong. Vì vậy cần placement theo vùng, giữ đường đi/đường về 20 A gần nhau, hạn chế đổi lớp, và không xẻ vùng GND reference dưới USB/CAN/RS485/ADC. Geometry USB 90 Ω phải tính lại từ stackup 2 lớp thực của fabricator; đồng 2 oz và dielectric 1,6 mm danh nghĩa không đủ để tự suy ra width/gap.

Metadata KiCad hiện vẫn ghi khoảng 1 oz mỗi mặt; đây là khoảng lệch cấu hình cần cập nhật qua Konnect trước khi xuất Gerber. Finished copper, khả năng etch tối thiểu và thermal performance vẫn cần fabricator/prototype xác nhận.

---

# 13. Không chạy tín hiệu nhạy song song với HV switching trace

Không nên:

```text
60V/20A switching ==========================

ADC signal       --------------------------
```

Đặc biệt tránh với:

- ADC
- Current sense
- EN / RESET
- Crystal
- SPI clock
- UART
- Interrupt
- High impedance GPIO

Nếu bắt buộc giao cắt:

```text
Power =========>

                |
                |
Signal          |
```

ưu tiên giao gần **90°**.

---

# 14. Via stitching

Via stitching nên dùng tại:

- Biên vùng high-current
- Quanh DC/DC
- Gần connector
- Quanh relay driver
- Gần transceiver CAN/RS485
- Gần các tụ decoupling

Mục tiêu:

- Giảm impedance GND
- Rút ngắn return path
- Giảm EMI
- Tăng liên kết plane

Không nên đặt via stitching theo kiểu trang trí; cần đảm bảo chúng thực sự phục vụ đường return.

---

# 15. Bảo vệ nguồn MCU

Nguồn MCU nên có nhiều cấp lọc:

```text
60V
 │
Buck
 │
5V
 │
Filter
 │
3V3 regulator
 │
Filter + Decoupling
 │
ESP32
```

Ví dụ:

```text
3V3
 │
 ├── 10uF
 ├── 1uF
 └── 100nF
       │
     ESP32
```

Các tụ decoupling phải:

- Đặt sát chân nguồn
- Trace ngắn
- Via xuống GND sát pad
- Không dùng trace GND dài

---

# 16. Ferrite bead / LC filter

Có thể provision:

```text
3V3_MAIN ─ Ferrite ─ 3V3_MCU
                       │
                    Capacitors
                       │
                      GND
```

Mục tiêu:

- Ngăn nhiễu cao tần từ power section vào MCU
- Ngăn nhiễu RF từ MCU quay lại rail khác

Không nên thêm ferrite tùy tiện nếu chưa có mục tiêu về dải tần.

Nên:

1. Chừa footprint
2. Đo prototype
3. Quyết định DNP hoặc lắp

---

# 17. ESP32 EN / RESET

EN/RESET là đường đặc biệt nhạy.

Nên:

```text
3V3
 │
 Rpull-up
 │
 ├──────── EN
 │
 C
 │
GND
```

Nguyên tắc:

- RC sát MCU
- EN trace rất ngắn
- Không route gần relay
- Không route gần buck SW node
- Không route song song 60 V switching trace

---

# 18. Current sense / ADC

## 18.1. Kelvin sensing

Dòng tải:

```text
20A
==========[ SHUNT ]==========
            │      │
            │      │
         Kelvin  Kelvin
            │      │
            └─ INA ┘
```

Không lấy sense từ copper power một cách ngẫu nhiên.

Kelvin trace phải:

- Đi trực tiếp vào hai đầu sense của shunt
- Không mang dòng tải
- Routing đối xứng
- Xa switching node

---

# 19. RC filter cho ADC

Ví dụ:

```text
INA OUT
   │
  100R
   │
   ├──────── ADC
   │
  10nF
   │
  GND
```

Tần số cutoff:

```text
fc = 1 / (2πRC)
```

Ví dụ:

```text
R = 1 kΩ
C = 10 nF

fc ≈ 15.9 kHz
```

Nếu chỉ đo dòng DC hoặc chậm:

- Có thể giảm bandwidth hơn nữa
- Nhưng phải kiểm tra settling time và yêu cầu điều khiển

---

# 20. UART / GPIO

Có thể provision điện trở series:

```text
ESP32 GPIO ──[22Ω … 100Ω]──── Signal
```

Tác dụng:

- Giảm ringing
- Giảm edge rate
- Giảm overshoot
- Giảm EMI

Nên chừa footprint cho:

- UART TX
- SPI clock
- GPIO đi xa
- Tín hiệu điều khiển ra connector

---

# 21. CAN / RS485

CAN và RS485 có lợi thế hơn UART trong môi trường nhiễu vì sử dụng truyền differential.

Bố trí:

```text
Connector
   │
  TVS
   │
Termination / filter
   │
Transceiver
   │
  MCU
```

TVS nên ở gần connector.

Không nên:

```text
Connector ───────── MCU ───── TVS
```

---

# 22. ESD protection tại connector

Các tín hiệu đi ra ngoài PCB nên được coi là đường đưa nhiễu vào hệ thống.

Nên bố trí:

```text
Outside world
     │
 Connector
     │
    TVS
     │
 Filter / Series R
     │
 Transceiver / MCU
```

TVS cần:

- Gần connector
- Đường discharge xuống GND ngắn
- Không để surge chạy sâu vào board rồi mới clamp

---

# 23. DC/DC 60 V → 5 V

Buck converter là một nguồn EMI lớn.

Hot-loop điển hình:

```text
Cin → Switch → Diode/FET → GND → Cin
```

Cần:

- Cin sát VIN/PGND
- SW node nhỏ
- Inductor gần switch
- Bootstrap components sát IC
- Cout gần inductor/load return
- Không route tín hiệu nhạy dưới SW node

Đặc biệt tránh:

- ADC
- EN
- UART
- Current sense
- Crystal

ở khu vực SW node.

---

# 24. Placement tổng thể đề xuất

```text
┌───────────────────────────────────────────────────────┐
│                   60V POWER AREA                      │
│                                                       │
│ J60V → Fuse → Protection → RELAY → Shunt → J60V_OUT  │
│                        │            │                  │
│                  TVS / Snubber      │                  │
│                                                       │
│              █████ HIGH CURRENT █████                 │
├───────────────────────────────────────────────────────┤
│                   POWER SUPPLY                        │
│                                                       │
│              60V → Buck → 5V → 3V3                   │
│                         │                             │
│                       Filters                         │
├───────────────────────────────────────────────────────┤
│                 SENSITIVE ANALOG                      │
│                                                       │
│ Shunt → Kelvin → Current Sense → RC Filter → ADC     │
├───────────────────────────────────────────────────────┤
│                       MCU                             │
│                                                       │
│                     ESP32                             │
│              Decoupling + EN RC                       │
│                                                       │
│                  Keepout RF Area                      │
├───────────────────────────────────────────────────────┤
│                 COMMUNICATION                         │
│                                                       │
│       CAN           RS485          UART               │
│        │              │              │                │
│       TVS            TVS            ESD               │
│        │              │              │                │
│                  CONNECTORS                           │
└───────────────────────────────────────────────────────┘
```

---

# 25. Những linh kiện nên chừa footprint

Nên provision footprint cho:

## Relay contact

- TVS
- RC snubber
- Optional MOV nếu phù hợp điện áp và môi trường

## Relay coil

- Flyback diode
- Zener
- TVS

## MCU supply

- Ferrite bead
- 10 uF
- 1 uF
- 100 nF
- Optional LC

## ADC

- Series resistor
- Filter capacitor

## UART / GPIO

- 0 Ω / 22–100 Ω series resistor
- TVS nếu đi ra connector

## CAN / RS485

- TVS
- Common-mode choke nếu cần
- Termination resistor
- Split termination nếu phù hợp

Việc chừa footprint giúp có thể tune EMI trên prototype mà không cần sửa PCB ngay.

---

# 26. Những linh kiện không nên thêm một cách máy móc

Không nên thêm chỉ vì “mạch chống nhiễu thường có”:

- Ferrite bead ở mọi rail
- Common-mode choke ở mọi interface
- RC snubber không tính toán
- TVS chọn sai VRWM
- Tụ điện lớn tại mọi vị trí
- Chia quá nhiều loại GND
- Ground split không kiểm soát

Mỗi linh kiện suppression cần có mục tiêu cụ thể.

---

# 27. Checklist schematic

- [ ] Relay có DC breaking rating đáp ứng 60 V / 20 A
- [ ] Relay coil có suppression
- [ ] Có provision TVS / snubber cho contact
- [ ] TVS có VRWM phù hợp bus
- [ ] MOSFET có voltage margin
- [ ] DC/DC có đủ input/output decoupling
- [ ] ESP32 có local decoupling
- [ ] EN/RESET có cấu hình chống nhiễu phù hợp
- [ ] Current sense dùng Kelvin connection
- [ ] ADC có provision RC filter
- [ ] CAN/RS485 có termination phù hợp
- [ ] Connector ngoài board có ESD/TVS
- [ ] UART/GPIO dài có provision series resistor

---

# 28. Checklist placement

- [ ] Relay gần connector công suất
- [ ] Fuse / protection gần đầu vào
- [ ] TVS gần nơi cần clamp
- [ ] Coil suppression gần coil/driver
- [ ] Đường 20 A không chạy qua MCU
- [ ] Buck cách xa ADC/current sense
- [ ] ESP32 cách xa relay contact
- [ ] ESP32 antenna cách xa copper HV
- [ ] Current sense gần shunt
- [ ] CAN/RS485 transceiver gần connector
- [ ] ESD protection gần connector

---

# 29. Checklist routing

- [ ] Đường 20 A ngắn
- [ ] Copper đủ rộng
- [ ] Loop high-current nhỏ
- [ ] Return high-current không đi qua logic
- [ ] B.Cu giữ GND reference liên tục tối đa có thể dưới vùng logic/tín hiệu nhạy
- [ ] Không route signal qua GND split
- [ ] ADC tránh xa relay
- [ ] EN tránh xa relay và SW node
- [ ] Kelvin trace không mang dòng tải
- [ ] Differential pair CAN/RS485 routing hợp lý
- [ ] Không chạy signal nhạy song song HV switching
- [ ] Via stitching được đặt theo đường return thực tế

---

# 30. Checklist đo kiểm prototype

Sau khi PCB hoàn thiện, không nên chỉ kiểm tra rằng “MCU chạy”.

Cần đo tại các điểm:

## 30.1. Bus 60 V

Đo:

- Overshoot
- Undershoot
- Ringing

Trong các trường hợp:

- Relay ON không tải
- Relay OFF không tải
- Relay ON tải nhỏ
- Relay OFF tải nhỏ
- Relay ON full load
- Relay OFF full load

---

## 30.2. Relay coil

Đo:

```text
VDS MOSFET driver
```

khi coil bị ngắt.

Kiểm tra:

- Clamp voltage
- Ringing
- MOSFET margin

---

## 30.3. Nguồn MCU

Đo:

- 5 V
- 3.3 V

khi relay đóng/cắt.

Kiểm tra:

- Voltage dip
- Ripple
- HF transient

---

## 30.4. ESP32 EN

Đo trực tiếp:

```text
EN to local MCU GND
```

khi relay đóng/cắt.

Nếu MCU reset nhưng 3.3 V vẫn ổn thì EN là một trong các điểm cần kiểm tra đầu tiên.

---

## 30.5. ADC / current sense

Quan sát:

- Spike khi relay đóng
- Spike khi relay ngắt
- ADC offset
- Settling time

---

# 31. Thứ tự debug khi ESP32 reset lúc relay đóng/cắt

Nếu ESP32 reset:

## Bước 1

Đo:

```text
3.3 V
```

Nếu 3.3 V sụt → xử lý nguồn.

## Bước 2

Nếu 3.3 V ổn, đo:

```text
EN / RESET
```

Nếu EN bị spike → xử lý routing/filter.

## Bước 3

Nếu nguồn và EN đều ổn:

- Kiểm tra ground bounce
- Kiểm tra brownout detector log
- Kiểm tra watchdog
- Kiểm tra EMI vào flash / clock / GPIO

## Bước 4

Thử:

- Tăng suppression relay coil
- Lắp snubber
- Lắp TVS
- Tách dây tải
- Thay vị trí dây power

Nếu lỗi thay đổi rõ rệt → nguồn nhiễu đã được định vị.

---

# 32. Mười việc quan trọng nhất

1. Chọn relay có **DC rating thực sự ≥ 60 V / 20 A**.
2. Thêm suppression cho relay coil.
3. Chừa TVS / RC snubber tại contact/load.
4. Đặt relay và connector HV trong vùng công suất riêng.
5. Đường 20 A phải ngắn, rộng và có loop nhỏ.
6. Không cho return 20 A chạy qua vùng MCU/ADC.
7. Giữ một reference GND plane liên tục cho tín hiệu.
8. Filter và decouple tốt nguồn MCU.
9. Giữ EN/RESET/ADC/current sense xa relay và SW node.
10. Đo transient thực tế bằng oscilloscope và tune suppression trên prototype.

---

# 33. Nguyên tắc cuối cùng

Không nên cố gắng chống EMI chỉ bằng cách:

```text
thêm nhiều TVS
+ thêm nhiều ferrite
+ thêm nhiều tụ
```

Một thiết kế chống nhiễu tốt thường bắt đầu từ:

```text
Placement
   ↓
Current path
   ↓
Return path
   ↓
Loop area
   ↓
Suppression
   ↓
Filtering
   ↓
Protection
```

Tức là:

> **Layout đúng trước, linh kiện suppression hỗ trợ sau.**

Nếu geometry của dòng công suất sai, việc thêm nhiều linh kiện lọc thường chỉ chữa triệu chứng chứ không giải quyết nguyên nhân.

---

# 34. Tài liệu tham khảo

Các nhóm tài liệu nên tham khảo khi thiết kế:

- Texas Instruments — EMI reduction and PCB layout for power converters
- Texas Instruments — Current sense amplifier layout / Kelvin sensing
- Analog Devices — Inductive load switching and demagnetization
- Analog Devices — Switching regulator PCB layout
- TE Connectivity — Relay contact arc and coil suppression
- Espressif — ESP32 Hardware Design Guidelines

Nên ưu tiên datasheet và application note chính thức của nhà sản xuất linh kiện đang dùng trên schematic.

---

## Kết luận

Đối với PCB có relay đóng/cắt **60 VDC / 20 A**, ba vấn đề quan trọng nhất là:

1. **Dập transient ngay tại relay / tải**
2. **Kiểm soát loop và return path của dòng 20 A**
3. **Giữ MCU, ADC và signal khỏi vùng high-energy switching**

Nếu ba yếu tố này được xử lý tốt từ schematic và placement ban đầu, khả năng gặp lỗi như:

- ESP32 reset
- ADC spike
- UART lỗi
- CAN/RS485 lỗi
- false GPIO
- hỏng MOSFET driver
- cháy contact relay

sẽ giảm đáng kể.
