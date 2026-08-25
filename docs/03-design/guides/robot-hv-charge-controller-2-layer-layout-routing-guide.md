# Hướng dẫn sắp xếp layout và routing trên PCB 2 lớp

## Robot HV Charge Controller — 60 V / 20 A, ESP32, nguồn phụ 24 V

**Artifact đầu vào:** `robot-hv-charge-controller(5).pdf`  
**Tài liệu đi kèm:** `robot-hv-charge-controller-netclass-guide.md`  
**Cấu hình đã chọn:** 2 lớp; đồng thành phẩm 2 oz trên F.Cu và B.Cu  
**Khoảng lệch hiện tại:** metadata KiCad vẫn ghi 0,035 mm (~1 oz) mỗi mặt; phải cập nhật qua Konnect trước khi xuất dữ liệu sản xuất  
**Ngày tổng hợp nguồn:** 2026-08-15  
**AI assessment:** `recommended_conditional_pass` để chuyển sang placement/routing thử nghiệm  
**Mức rủi ro tạm thời:** Level 3 — công suất khả dụng tới khoảng 1.2 kW, có rủi ro nhiệt, cháy, hư hỏng thiết bị và EMC nếu layout sai

> Tài liệu này là hướng dẫn kỹ thuật và checklist review. Người thiết kế chịu trách nhiệm chốt topology GND, stackup nhà sản xuất, tiêu chuẩn sản phẩm áp dụng và quyết định phát hành PCB.

---

## Mục lục sử dụng nhanh

- Mục 0–2: kết luận, giả định và cơ sở tiêu chuẩn.
- Mục 3: chia vùng chức năng trên mặt bo.
- Mục 4–8: stackup 2 lớp, chức năng từng mặt đồng và chiến lược thoát routing.
- Mục 9–17: routing theo return path và từng khối mạch.
- Mục 18–23: via, Rule Area, thứ tự routing và kiểm tra KiCad.
- Mục 24: kế hoạch thermal/EMC verification.
- Mục 25: ma trận nguồn, revision và giới hạn áp dụng.
- Mục 26–27: quyết định còn mở và gate disposition.

---

## 0. Kết luận thiết kế

### 0.1 Stackup chức năng đã chọn

| Lớp | Đồng | Chức năng chính | Không nên dùng cho |
|---|---:|---|---|
| **F.Cu** | 2 oz finished | Linh kiện; đường 60 V dương 20 A; buck hot loop; Kelvin sense; USB; CAN/RS485; tín hiệu nhạy cảm ngắn | Đổ đồng `BUCK_SW` diện tích lớn; trace chạy dưới anten; routing dài làm chia vùng chức năng |
| **B.Cu** | 2 oz finished | `VBAT_RETURN_20A`; GND/PGND reference liên tục tối đa có thể; power/slow-signal escape có kiểm soát | USB/clock nhanh; tín hiệu nhạy chạy qua khe plane; dòng 20 A đi qua vùng MCU/ADC |

Hai lớp không cung cấp một plane GND bên trong liên tục như stack 4 lớp. Vì vậy placement phải tạo các hành lang chức năng rõ ràng, giữ B.Cu liên tục tối đa có thể dưới tín hiệu nhanh/nhạy, và giữ cặp dòng đi–về 20 A gần nhau mà không ép dòng tải chạy qua vùng điều khiển. Đây là lựa chọn có đánh đổi EMC/SI và phải được kiểm chứng trên layout/prototype.

### 0.2 Cách chạy cặp dòng 20 A được khuyến nghị

| Phương án | Hình học | Đánh giá |
|---|---|---|
| **A — khuyến nghị có điều kiện** | Positive trên F.Cu, dedicated return trên B.Cu, chồng hình học dọc mép bo | Loop nhỏ, dùng hai mặt 2 oz; cần tách net return và review topology GND/reference |
| **B — fallback** | Positive và return song song trên F.Cu | Đơn giản, dễ kiểm tra; chiếm nhiều diện tích và khoảng cách tâm hai đường lớn hơn |
| **C — không khuyến nghị** | Positive F.Cu, return phân tán qua B.Cu `GND_CTRL` | Dòng 20 A không kiểm soát, tạo shared impedance và nhiễu ground |

Phương án A là **engineering inference** từ nguyên tắc giảm loop area và kiểm soát return path; chưa được xác nhận trên PCB thật. Cần kiểm tra với geometry thực, thermal/current solver và prototype. Đây không phải một topology bắt buộc trực tiếp bởi IPC/IEC.

Nếu đã tách được `VBAT_RETURN_20A` khỏi `GND_CTRL`:

- F.Cu: `VBAT_PROTECTED_P` → relay → shunt → `VBAT_OUT_P`.
- B.Cu: `VBAT_RETURN_20A` đi trực tiếp từ đầu ra âm về đầu vào âm.
- Hai hành lang F.Cu/B.Cu bám theo cùng một mép bo và chồng hình học lên nhau càng nhiều càng tốt.
- Giữ hành lang này ngoài vùng GND reference của MCU/ADC/communication; không để copper pour tạo nhánh hồi 20 A song song qua vùng điều khiển.
- Chỉ nối `VBAT_RETURN_20A` với `GND_CTRL` tại điểm đã được quyết định ở cấp hệ thống.

Nếu chưa thể tách hai net GND:

- Chạy cả đường đi và đường về 20 A song song trên cùng lớp 2 oz, ưu tiên F.Cu.
- Không dùng toàn bộ B.Cu làm đường hồi tải không kiểm soát.
- Dùng Rule Area để ngăn zone GND vô tình tạo đường 20 A song song qua vùng MCU.

### 0.3 Ba nguyên tắc không được phá vỡ

1. **Không phá B.Cu tùy tiện.** Mọi track/zone trên B.Cu phải được review về đường hồi của USB, UART0, CAN/RS485, ADC và decoupling.
2. **Không cho dòng 20 A đi qua vùng GND điều khiển.** Net Class không kiểm soát được điều này nếu tất cả cùng tên `GND`.
3. **Mọi tín hiệu nhanh/nhạy cảm phải có return path liên tục.** Nếu B.Cu bị ngắt, phải đổi placement/routing thay vì chấp nhận đường hồi vòng.

---

## 1. Phạm vi, dữ liệu đã biết và dữ liệu còn thiếu

### 1.1 Đã biết

- Điện áp bus chính tối đa: 60 V DC.
- Dòng liên tục và dòng đỉnh thiết kế: 20 A.
- Bus chính đóng cắt bằng relay.
- Nguồn phụ: 24 V.
- Buck LV14340: 24 V → 5 V.
- LDO: 5 V → 3.3 V.
- MCU: ESP32-WROOM-32E.
- Đo dòng: INA240A1 + shunt R41 khoảng 2 mΩ theo schematic hiện tại.
- Giao tiếp: USB Full-Speed qua CH340C, CAN, RS485, UART ngoài.
- I/O: hai switch 24 V và ba ngõ ra tải LED 24 V.
- PCB baseline: 2 lớp; 2 oz finished copper trên F.Cu/B.Cu; không cần HDI/microvia.

### 1.2 Chưa biết — phải giữ trạng thái `needs_verification`

- 24 V negative và 60 V negative có nối chung ở nguồn ngoài hay không.
- Điểm single-point connection giữa `VBAT_RETURN_20A` và `GND_CTRL`.
- Kích thước bo, vị trí cố định của connector/lỗ bắt vít/enclosure.
- Stackup chính thức: tổng độ dày, khoảng cách F.Cu–B.Cu, Dk/Df, finished copper và solder mask.
- Tốc độ CAN, RS485, UART và chiều dài cáp lớn nhất.
- Môi trường EMC đích: công nghiệp, light-industrial hay môi trường robot chuyên dụng.
- Nhiệt độ môi trường, airflow, enclosure và thời gian chạy 20 A.
- Cấu hình shield/chassis và điểm nối chassis với GND.

### 1.3 Phạm vi loại trừ

Tài liệu này không:

- Chứng minh đạt IPC/IEC.
- Thay thế field solver cho impedance USB.
- Chứng minh đường đồng 20 A đạt nhiệt độ yêu cầu.
- Phê duyệt topology nối đất hệ thống.
- Thay thế kiểm tra ERC/DRC trên project KiCad gốc.

---

## 2. Cơ sở tiêu chuẩn và cách sử dụng

### 2.1 Tiêu chuẩn thiết kế PCB

- **IPC-2221C** là tiêu chuẩn nền tảng cho thiết kế printed board.
- **IPC-2222B** bổ sung yêu cầu cho rigid organic PCB.
- **IPC-2152** cung cấp phương pháp xác định khả năng mang dòng, nhưng bảng revision chính thức của IPC hiện ghi tài liệu này là **No Longer Maintained**. Có thể dùng làm dữ liệu lịch sử/sàng lọc, không dùng như bằng chứng duy nhất cho 20 A.
- **IEC 60664-1:2020+A1:2025** là cơ sở insulation coordination; khoảng cách cuối cùng phụ thuộc pollution degree, material group, altitude, overvoltage và yêu cầu sản phẩm.

### 2.2 Tài liệu hãng

Tài liệu hãng được dùng để chốt constraint cục bộ:

- Espressif: reference layout ưu tiên plane GND liên tục và power distribution riêng; khi áp dụng cho bo 2 lớp phải giữ B.Cu liên tục tối đa có thể, đặt anten ở mép bo và tuân thủ keepout.
- TI LV14340: placement của CIN, diode, L, COUT, FB và ground hot loop.
- TI INA240: Kelvin/4-wire connection từ shunt.
- TI ESD guide: connector → TVS trực tiếp, không stub/via trước TVS, ground path cực ngắn.
- TI high-speed guide: tín hiệu nhanh không chạy qua split/void của reference plane.
- USB-IF: yêu cầu điện của USB 2.0 và quy trình compliance.
- CAN/RS485 application notes: topology bus, termination ở hai đầu và kiểm soát common-mode/return.

### 2.3 Tiêu chuẩn EMC chỉ là ứng viên đến khi xác định product class

Với môi trường robot/industrial, các tài liệu sau là ứng viên để lập kế hoạch test:

- IEC 61000-6-2:2016 — immunity cho môi trường công nghiệp.
- IEC 61000-6-4:2018 — emission cho môi trường công nghiệp.
- IEC 61000-4-2:2025 — ESD.
- IEC 61000-4-4:2012 — EFT/burst, đặc biệt liên quan relay và tải cảm.
- IEC 61000-4-5:2014 — surge.
- IEC 61000-4-6:2023 — conducted RF immunity trên cáp.

Không áp dụng level test cụ thể trước khi chốt môi trường và tiêu chuẩn sản phẩm/family standard.

---

## 3. Chia vùng chức năng trên mặt bo

### 3.1 Sơ đồ concept top view

```text
┌────────────────────────────────────────────────────────────────────┐
│ MÉP HV / DIRTY POWER                                               │
│ [60V IN]─[Protection]─[Relay]─[Shunt R41]─[60V OUT]                │
│             Hành lang +60 V / 20 A trên F.Cu                       │
│             Hành lang RETURN 20 A chồng dưới trên B.Cu             │
├───────────────────────┬───────────────────────┬────────────────────┤
│ 24 V POWER / BUCK     │ ANALOG MEASUREMENT    │ 24 V OUTPUT DRIVER │
│ [24V IN][TVS/Fuse]    │ [INA240][divider]     │ [relay/DO1..DO3]   │
│ [LV14340][LDO]        │ gần shunt, xa SW      │ gần connector tải  │
├───────────────────────┴──────────────┬────────┴────────────────────┤
│ CONTROL / QUIET                      │ FIELD COMMUNICATION         │
│ [ESP32][CH340][USB-C]                │ [CAN][RS485][UART][SW IN]   │
│ ESP32 antenna đặt ra mép bo          │ connector→TVS→transceiver   │
└──────────────────────────────────────┴─────────────────────────────┘
```

Đây là topology vùng, không phải tỷ lệ cơ khí cuối cùng.

### 3.2 Các vùng bắt buộc

| Vùng | Thành phần | Mục tiêu layout | Nguồn nhiễu/victim chính |
|---|---|---|---|
| `ZONE_HV_20A` | 60 V connector, protection, relay contact, R41 | Đường thẳng, rộng, ít đổi lớp | Nguồn từ trường, sụt áp, nhiệt |
| `ZONE_AUX_BUCK` | 24 V entry, LV14340, D8, L2, CIN/COUT | Hot loop cực nhỏ | `BUCK_SW`, diode current loop |
| `ZONE_CURRENT_SENSE` | R41, INA240, input/filter | Kelvin chính xác | Victim của magnetic/shared impedance |
| `ZONE_VOLTAGE_SENSE` | D15, R43–R45, RC ADC | Giữ phần HV sát boundary | Victim của switching/ESD |
| `ZONE_MCU_RF` | ESP32, decoupling, EN/BOOT | Anten ở mép bo | Victim của buck/relay/UART/USB |
| `ZONE_USB` | USB-C, ESD, CH340C | Chuỗi thẳng connector→protection→IC | ESD source và signal integrity |
| `ZONE_FIELD_BUS` | CAN, RS485, UART connector/protection/transceiver | Protection ở boundary | ESD/EFT/common-mode |
| `ZONE_OUTPUT_24V` | relay coil driver, DO1–DO3 | Driver sát connector tải | dI/dt và flyback |

### 3.3 Khoảng tách theo chức năng

Các giá trị dưới đây là **project placement margins**, không phải khoảng cách cách điện theo IEC:

- Mép `BUCK_SW` đến ADC/FB/Kelvin/anten: mục tiêu ≥ 5 mm nếu cơ khí cho phép.
- Hành lang HV switched đến MCU/anten/USB: mục tiêu ≥ 5 mm.
- Driver relay/DOx đến ADC/Kelvin: mục tiêu ≥ 3 mm.
- Trace analog chạy song song với đường switching: tránh hoàn toàn; nếu buộc phải cắt, cắt vuông góc và bảo đảm B.Cu reference liên tục.
- Vùng anten: theo footprint/datasheet module; enclosure nên có clearance ít nhất 15 mm theo hướng dẫn Espressif khi có thể.

---

## 4. Thiết kế stackup trước khi route

### 4.1 Cấu trúc chức năng

```text
F.Cu  2 oz finished ─ Components + critical signals + HV positive
                     + buck local copper + local power
        dielectric/core and Dk defined by fabricator
B.Cu  2 oz finished ─ HV return corridor + GND/PGND reference
                     + limited slow-signal/power escape
```

Độ dày bo danh nghĩa là 1,6 mm, nhưng không dùng con số danh nghĩa để suy ra impedance. Với cấu trúc 2 lớp, khoảng cách signal-to-reference lớn; USB 90 Ω có thể cần geometry rộng/khó chế tạo và phải được fabricator hoặc field solver xác nhận.

### 4.2 Thông tin phải yêu cầu nhà sản xuất

Trước khi khóa USB width/gap và đường 20 A, phải nhận:

- Finished board thickness và tolerance.
- Khoảng cách copper-to-copper F.Cu–B.Cu, loại laminate và Dk/Df.
- 2 oz là base copper hay finished copper sau plating; tolerance chiều dày đồng.
- Minimum trace/space, annular ring và solder-mask web với đồng 2 oz.
- Minimum drill, finished hole, barrel plating và aspect ratio.
- Controlled-impedance capability/tolerance cho cấu trúc 2 lớp.
- Quy tắc copper balance, thieving, bow/twist và khả năng tent/fill via dưới thermal pad.

### 4.3 Điều cần chốt với fabricator

- Hai mặt 2 oz phải được xác nhận trong quotation/fab notes; không chỉ dựa vào tên file.
- USB target 90 Ω differential phải tính lại từ finished geometry và solder-mask model.
- Kiểm tra capability vì đồng dày làm giảm khả năng etch trace/space nhỏ và thay đổi geometry impedance.
- Không dùng công thức IPC-2141 cũ làm kết quả cuối; IPC hiện ghi IPC-2141 là No Longer Maintained.

---

## 5. F.Cu: component side và routing ưu tiên

### 5.1 Các net nên ở F.Cu

- `VBAT_PROTECTED_P`, `VBAT_RELAY_OUT_P`, `VBAT_OUT_P`.
- `BUCK_SW`, `BUCK_BOOT`, vòng CIN–U9–D8–GND.
- Hai nhánh Kelvin từ R41 tới INA240.
- `USB_*` và các cặp CAN/RS485 từ connector qua TVS tới transceiver.
- Tín hiệu ADC/FB ngắn và decoupling loop của ESP32, CH340C, CAN, RS485.

### 5.2 Quy tắc F.Cu

- Ưu tiên đường ngắn có B.Cu reference liên tục hơn quy tắc “route ngang/dọc”.
- Dùng local GND pour và stitching xuống B.Cu, nhưng không đổ vào antenna, SW hoặc HV keepout.
- Không để tín hiệu điều khiển chui qua khe giữa pad của đường 20 A.
- Không route dưới relay contact/high-current shunt trừ nhánh Kelvin đã kiểm soát.
- Không đặt test point trên USB D+/D−.

### 5.3 Hành lang 20 A trên F.Cu

- Dùng zone/polygon 8–10 mm hoặc lớn hơn theo kết quả nhiệt; 8 mm chỉ là starting point.
- Mỗi thay đổi hướng dùng polygon mượt/45°, tránh cổ chai.
- Review tiết diện hẹp nhất tại connector, relay, fuse/protection, shunt và pad throat.
- Không dùng thermal relief cho pad dòng chính nếu quy trình hàn đã được xử lý phù hợp.
- Không rải ground via sát hai cạnh hành lang nếu việc đó tạo coupling dòng xung vào GND điều khiển.

---

## 6. B.Cu: return công suất và reference điều khiển

### 6.1 Thứ tự ưu tiên

1. `VBAT_RETURN_20A` theo hành lang đã chốt ở cấp hệ thống.
2. GND/PGND reference liên tục tối đa có thể dưới vùng MCU, USB, CAN/RS485, ADC và decoupling.
3. Heat spreading và power/slow-signal escape chỉ khi không phá hai mục trên.

### 6.2 `VBAT_RETURN_20A` trên B.Cu

- Chồng dưới hành lang dương F.Cu để giảm loop area khi topology cho phép.
- Giữ width tương đương hoặc lớn hơn đường đi; không neck-down ở connector âm.
- Không cho GND pour tạo nhánh hồi song song qua vùng điều khiển.
- Tránh via; connector THT nên nối trực tiếp vào copper bằng pad đủ lớn.
- Chỉ nối với GND điều khiển tại điểm đã được người thiết kế xác định; nếu schematic dùng chung một net, phải điều khiển hình học bằng placement, zone và Rule Area.

### 6.3 GND/PGND reference trên B.Cu

- Không xẻ plane để “tách analog/digital” theo thói quen.
- Không để khe/track/power island nằm dưới USB, CAN, RS485, UART, ADC hoặc decoupling loop.
- Antenna keepout áp dụng cho cả hai lớp.
- Keepout dưới `BUCK_SW` chỉ giới hạn đúng switch node; không tạo moat chia đôi vùng GND.
- Mỗi tụ decoupling và TVS cần đường xuống B.Cu ngắn, via sát pad, inductance thấp.

---

## 7. Phân phối +24 V, +5 V và +3V3 trên bo 2 lớp

### 7.1 Chiến lược

- Dùng track/zone cục bộ trên F.Cu theo dòng thực; chỉ đổi sang B.Cu cho đoạn ngắn đã review.
- `+24V`: từ sau bảo vệ tới buck, relay và output theo các nhánh riêng, tránh đi xuyên vùng MCU/ADC.
- `+5V`: từ buck output tới LDO/CH340C bằng hành lang ngắn, tránh buck SW.
- `+3V3`: ưu tiên F.Cu/local pour trong vùng logic; giữ decoupling loop ngắn.

### 7.2 Điều cấm

- Không đặt `BUCK_SW` trên B.Cu.
- Không dùng via đơn cho rail có dòng đáng kể.
- Không để power trace trên B.Cu cắt đường hồi của USB hoặc tín hiệu nhạy.
- Không route rail hoặc tín hiệu dưới anten ESP32.

---

## 8. Đổi lớp và thoát routing

### 8.1 Tín hiệu được phép đổi lớp

Chỉ đổi lớp khi placement không thể giải quyết và phải kiểm tra return path:

- GPIO/control chậm.
- UART nội bộ ngắn.
- ADC output sau filter, xa switching zone.
- Power branch cục bộ có đủ via song song theo dòng và plating thực.

### 8.2 Tín hiệu nên giữ trên F.Cu

- USB D+/D−; nếu buộc đổi lớp, cả cặp đổi đối xứng và có return-via strategy.
- Kelvin sense; ưu tiên không via.
- `BUCK_SW` và feedback nhạy.
- CAN/RS485 từ connector đến transceiver nếu B.Cu reference bị gián đoạn ở mặt dưới.

Mỗi via/track trên B.Cu tiêu tốn diện tích reference. Nếu routing hoàn tất nhưng B.Cu bị chia thành các đảo hoặc cổ chai, phải quay lại placement thay vì chỉ thêm stitching via.

---

## 9. Kiến trúc return path và nối đất

### 9.1 Không chia “analog ground” và “digital ground” bằng khe plane

Bo này không cần AGND/DGND plane rời. Cách đúng là:

- Một vùng `GND_CTRL` liên tục tối đa có thể trên B.Cu ở khu vực điều khiển.
- Tách nguồn nhiễu bằng placement và loop geometry.
- Dòng switching của buck khép vòng cục bộ trên F.Cu.
- Dòng relay/DO tải đi trong đường riêng về connector/power entry.
- Tín hiệu analog đi trên F.Cu với B.Cu reference yên tĩnh.

### 9.2 Tách return công suất 20 A khỏi GND điều khiển

`VBAT_RETURN_20A` và `GND_CTRL` nên là hai net hình học khác nhau nếu mục tiêu là ép dòng 20 A đi đúng hành lang. Điểm nối phải được xác định từ sơ đồ nguồn toàn hệ thống.

#### Điểm cần quyết định bởi người thiết kế

- Hai nguồn 24 V và 60 V đã nối common-negative bên ngoài hay chưa?
- Có kết nối chassis/PE hay không?
- Voltage divider 60 V tham chiếu tại điểm nào?
- Dòng ESD từ connector sẽ trở về chassis hay `GND_CTRL`?
- Có đường nối thứ hai qua cáp USB/CAN/RS485 tạo ground loop hay không?

Không đặt Net-Tie ngẫu nhiên chỉ để ERC/DRC hết lỗi.

### 9.3 Ground của buck

Theo LV14340 datasheet:

- Ground của diode, CIN và COUT dùng localized top-side planes.
- Local power ground nối vào system GND tại một điểm có chủ đích, ưu tiên gần COUT ground theo reference của TI.
- Thermal pad U9 nối copper GND và thermal vias; không để No-Connect.
- FB sense tránh SW và có shielding plane giữa khi đổi lớp.

### 9.4 Ground của ESD protection

- Nếu có chassis: TVS/chassis path phải ngắn và ở sát connector.
- Nếu không có chassis: TVS ground đi ngay vào F.Cu GND pour và via sát pad xuống B.Cu.
- Không route trace không được bảo vệ trong đoạn connector → TVS.
- Không đặt via trước TVS trên đường tín hiệu nếu tránh được.

---

## 10. Routing khối 60 V / 20 A

### 10.1 Thứ tự vật lý

```text
60V_IN_P
  → protection/fuse/reverse/TVS theo schematic
  → main relay contact
  → shunt R41
  → 60V_OUT_P

60V_OUT_N
  → VBAT_RETURN_20A
  → 60V_IN_N
```

### 10.2 Quy tắc đường đi

- Toàn bộ conductor chính ở F.Cu/B.Cu 2 oz finished.
- Route theo dòng thực, không theo ratsnest ngắn nhất nếu làm loop lớn.
- Không đổi lớp giữa connector, relay, shunt và output.
- Kiểm tra copper width tại pad throat, không chỉ kiểm tra đoạn giữa.
- Đặt test point đo sụt áp ngoài hành lang dòng hoặc dùng pad đo riêng; không khoan thủng đường dòng bằng via test nhỏ.
- Nếu bắt buộc dùng via array, phải tính/đo theo finished plating của fab; một via đơn không được coi là mang 20 A.

### 10.3 Nhiệt

- 8 mm là routing starting point từ Net Class, không phải minimum đã được chứng minh.
- Dùng IPC-2152 như sàng lọc lịch sử, sau đó kiểm bằng thermal solver hoặc prototype.
- Đo nhiệt ở connector, relay, shunt, pad throat và copper neck-down.
- Acceptance criterion phải do dự án đặt từ giới hạn component, ambient và enclosure; không chỉ dùng “sờ không nóng”.

### 10.4 Clearance và creepage

- Dùng 1.00 mm project clearance cho nhóm 60 V theo Net Class hiện tại.
- Không tuyên bố IEC 60664 compliance từ con số 1.00 mm.
- Giữ HV copper xa mounting hole/chassis/connector metal theo hệ thống cơ khí.
- Solder mask không được tính như một khoảng cách cách điện độc lập nếu tiêu chuẩn sản phẩm không cho phép.

---

## 11. Routing buck LV14340 24 V → 5 V

### 11.1 Placement theo vòng dòng

Thứ tự ưu tiên placement:

1. U9.
2. High-frequency CIN sát VIN–GND U9.
3. D8 sát SW/GND.
4. L2 sát SW.
5. COUT sát L2/diode return.
6. C7 bootstrap sát BOOT–SW.
7. FB divider sát FB, ở phía quiet.
8. RT/SS sát chân IC và xa SW/L2.

### 11.2 Các vòng phải thu nhỏ

```text
Hot loop ON/OFF:
CIN+ → U9 internal switch → SW → D8/GND → CIN−

Output ripple loop:
SW/D8 → L2 → COUT → local GND → D8
```

### 11.3 Phân bổ lớp

- F.Cu: toàn bộ hot loop, `BUCK_SW`, BOOT, CIN/D8/L2/COUT local copper.
- B.Cu: local GND dưới CIN/COUT/control, nhưng keepout trực tiếp dưới copper `BUCK_SW`.
- `+24 V` feed và `+5 V` distribution đi trên F.Cu hoặc đoạn B.Cu ngắn đã review; không cắt reference của tín hiệu nhạy.
- Không route tín hiệu analog trên B.Cu dưới U9/cuộn cảm L2/D8.

### 11.4 Quy tắc `BUCK_SW`

- Không via.
- Không test point lớn nếu không thực sự cần đo.
- Copper đủ cho dòng nhưng diện tích nhỏ nhất có thể để giảm electric-field coupling.
- Không route `BUCK_FB`, ADC, EN/BOOT MCU hoặc anten ở lớp bất kỳ ngay dưới/đi cạnh SW.

### 11.5 Feedback

- Lấy VOUT sense tại điểm sạch sau L2 và COUT.
- Divider sát FB pin.
- Nếu phải đổi lớp, route qua phía có shielding GND giữa FB và switch node.
- Không lấy feedback từ đầu đường +5 V đang mang xung dòng tải.

---

## 12. Routing INA240 và shunt R41

### 12.1 Placement

- R41 nằm thẳng trong đường dòng chính, không đặt kiểu nhánh chữ T.
- INA240 đặt gần shunt nhưng ngoài copper nóng và xa relay/buck.
- Input/filter components sát chân IN+/IN− nếu schematic sử dụng.
- Bypass 100 nF sát VS–GND của INA240.

### 12.2 Kelvin sense

- Hai trace 0.20 mm xuất phát từ điểm trong pad shunt.
- Điểm lấy sense không nằm trên copper throat có dòng phân bố không đều.
- Route cùng lớp F.Cu, gần nhau và cân xứng.
- Không via nếu placement cho phép.
- Không chạy song song với đường 20 A, `BUCK_SW`, coil relay hoặc DOx.
- Rule Area phải cho phép nhánh Kelvin hẹp dù net gốc thuộc `HV60_20A_TRUNK`.

### 12.3 Output tới ADC

- `IOUT_SENSE_RAW` từ INA240 tới R47/RC filter ngắn.
- `IOUT_SENSE_ADC` sau filter ưu tiên F.Cu với B.Cu reference liên tục; chỉ đổi lớp khi return path đã được review.
- RC filter cuối cùng nên ở sát ADC ESP32 để shunt nhiễu tại receiver.
- Không route dưới anten hoặc dọc mép power island.

---

## 13. Routing mạch chia áp 60 V

### 13.1 Vùng HV

- D15 và đầu trên R43 đặt sát điểm `VBAT_OUT_P`.
- `VOUT_DIV_HV_IN`, `MID1`, `MID2` ở F.Cu trong boundary HV.
- Chuỗi resistor tạo khoảng cách vật lý, không gập trace để thu nhỏ vùng điện áp cao.

### 13.2 Biên HV → analog low voltage

- Sau phần tử chia áp cuối, tạo boundary rõ sang `VOUT_DIV_RAW`.
- RC/filter low-voltage đặt phía control của boundary.
- `VOUT_SENSE_ADC` route ngắn trên F.Cu, với B.Cu reference liên tục.
- Không chạy chuỗi divider qua vùng relay coil, DO drivers hoặc buck SW.

### 13.3 Ground reference

Đầu thấp của divider phải về `GND_CTRL` tại topology đã chốt. Nếu `VBAT_RETURN_20A` khác net, điểm nối hai miền phải bảo đảm ADC đo đúng mà không đưa dòng tải vào ground sense.

---

## 14. ESP32-WROOM-32E và anten

### 14.1 Placement module

- Đặt anten nhô ra ngoài mép baseboard là tốt nhất.
- Nếu không thể nhô, feed point sát mép và vùng trước/bên anten không có vật kim loại.
- Không đặt module ở giữa bo rồi khoét bốn phía.
- Chừa khoảng trống enclosure quanh anten; Espressif khuyến nghị ít nhất 15 mm theo mọi hướng khi có thể.

### 14.2 Keepout

- Không có copper, trace, via hoặc zone trên F.Cu/B.Cu dưới anten.
- Không trace, via, zone, test point hoặc mounting metal.
- Không route USB, UART, buck, relay coil và 20 A gần anten.
- Ground copper và stitching dày quanh phần thân module/ranh giới keepout, không xâm nhập vùng anten.

### 14.3 Nguồn 3.3 V

- Main 3.3 V feed tối thiểu theo Net Class 0.65 mm; Espressif khuyến nghị main power trace ≥ 25 mil ≈ 0.635 mm.
- Nếu đổi lớp, dùng ít nhất hai power vias cho main feed theo hướng dẫn Espressif.
- 10 µF/bulk và decoupling đặt tại entry của module.
- Ground via sát pad ground của tụ.

---

## 15. USB-C, CH340C và UART0

### 15.1 Chuỗi placement

```text
USB-C connector → ESD array → series resistors/choke nếu có → CH340C → UART0 → ESP32
```

- ESD gần connector hơn CH340C.
- Không có stub từ main path sang TVS.
- `CH340_V3` và tụ 100 nF đặt sát pin V3 sau khi sửa schematic.

### 15.2 Routing USB

- Route D+/D− trên F.Cu, với B.Cu GND reference liên tục tối đa có thể.
- Target 90 Ω differential; width/gap chốt bằng stackup thực.
- Giữ width/gap không đổi ngoài đoạn fan-out ngắn.
- Không via nếu có thể; nếu đổi lớp, cả hai dây đổi đối xứng và có return-via strategy.
- Không test point và không serpentine nếu không có yêu cầu skew cụ thể.
- Không đi gần oscillator, buck, relay, anten hoặc cạnh plane.

### 15.3 Tên net và KiCad differential router

KiCad nhận cặp vi sai khi hai net có cùng base name và hậu tố `P/N` hoặc `+/-`. Các tên `USB_DP` và `USB_DM` có thể không được nhận thành một cặp tự động.

Hai lựa chọn:

1. Giữ `USB_DP/USB_DM` và route thủ công như cặp.
2. Đổi thành `USB_CONN_P/USB_CONN_N` và `USB_IC_P/USB_IC_N` để dùng Differential Pair Router.

Nếu đổi tên, cập nhật đồng bộ schematic, Net Class pattern và tài liệu test.

### 15.4 UART0

- Series resistor TX đặt gần source/ESP32 theo hướng dẫn Espressif.
- UART0 ngắn và xa anten.
- Nếu đi dài, surround bằng GND pour/stitching nhưng không phá antenna keepout.

---

## 16. CAN và RS485

### 16.1 Placement

```text
Connector → TVS/CMC/termination option → transceiver → series R → MCU
```

- Protection ở sát connector.
- Transceiver gần protection và connector hơn MCU.
- Logic TX/RX hướng vào control zone.
- Termination option đặt ở phía bus, không sau một stub dài.

### 16.2 Routing bus pair

- CANH/CANL và A/B đi cùng F.Cu, gần nhau và cùng B.Cu reference.
- Tránh via; nếu có, chuyển cả hai dây đối xứng.
- Không đi qua split/void trên B.Cu reference.
- Không route dưới relay, buck inductor hoặc sát 24 V output drivers.
- Không length-tune cực đoan; topology ngắn, cân xứng và ít stub quan trọng hơn.

### 16.3 Termination

- CAN dùng cáp danh định 120 Ω và termination ở hai đầu vật lý của bus.
- RS485 cũng terminate theo characteristic impedance của cáp và chỉ tại bus ends.
- Node giữa bus không mặc định lắp 120 Ω.
- Nếu có jumper termination, silkscreen và BOM variant phải thể hiện rõ.

### 16.4 Tên cặp P/N trong KiCad

`CAN_H/L` và `RS485_A/B` không tự bảo đảm KiCad nhận thành differential pair.

- CAN có thể đổi thành `CAN_BUS_P` = CANH và `CAN_BUS_N` = CANL.
- Với RS485, không đổi A/B thành P/N trước khi kiểm tra polarity theo datasheet MAX3485 và định nghĩa connector; ký hiệu A/B giữa các hãng có thể gây nhầm.
- Route thủ công cũng chấp nhận được nếu vẫn kiểm soát gap/reference/return.

### 16.5 Common-mode và isolation

Board hiện không thể được coi là isolated chỉ vì dùng differential bus. Nếu cáp dài hoặc node có ground-potential difference lớn, cần đánh giá:

- Bus ground/reference conductor.
- Common-mode range của transceiver.
- Shield termination.
- TVS surge rating.
- Có cần isolated CAN/RS485 và isolated power hay không.

---

## 17. Relay, coil và ba ngõ ra 24 V

### 17.1 Placement

- Relay/DO driver gần connector tải.
- Flyback/clamp gần transistor và connector/coil loop.
- Đường `DO1_SINK..DO3_SINK` không đi qua vùng MCU/ADC.
- Return của tải về 24 V entry theo đường riêng; không đi qua ground via của ESP32.

### 17.2 Routing

- Route `+24V` cấp tải và sink return thành cặp dòng gần nhau.
- Dùng F.Cu hoặc B.Cu 2 oz cho đoạn có dòng tải; mọi đoạn trên B.Cu phải tránh cắt reference path của MCU/ADC/communication.
- Không chạy output switched song song với USB/Kelvin/ADC.
- Dùng 45°/curve ở đường ESD/flyback current, tránh loop lớn.

### 17.3 Relay contact và relay coil

Tách rõ:

- Contact path 60 V/20 A thuộc `ZONE_HV_20A`.
- Coil path 24 V thuộc `ZONE_OUTPUT_24V`.
- Không để copper coil/driver chui vào khe giữa hai pad contact và không dùng chung đoạn return với INA240/ESP32.

---

## 18. Via, stitching và thermal path

### 18.1 Signal via

- Theo Net Class: 0.60 mm pad / 0.30 mm drill cho logic/analog/USB nếu buộc dùng.
- USB/CAN/RS485: đổi cả hai thành viên đối xứng.
- ADC/Kelvin: tránh via.

### 18.2 Power via

- `+24V`: 1.00/0.50 mm theo Net Class.
- `+5V`, `+3V3`: 0.80/0.40 mm theo Net Class.
- Dùng nhiều via song song ở rail source/load thay vì một via duy nhất khi dòng đáng kể.
- ESP32 main 3.3 V đổi lớp dùng ít nhất hai via theo hướng dẫn Espressif.

### 18.3 Thermal via U9

- Thermal pad phải nối GND.
- Kích thước via, pitch, tent/fill và paste window phải chốt với assembler/fabricator.
- Starting point thường dùng khoảng 0.30 mm finished drill và 0.60 mm pad, nhưng đây không phải giá trị bắt buộc từ LV14340 datasheet; cần kiểm tra solder wicking và capability.
- Không dùng thermal relief giữa thermal pad và local GND copper.

### 18.4 Via cho 20 A

- Phương án mặc định: không có via.
- Nếu không thể tránh: tính theo finished barrel copper, temperature rise và current sharing; dùng coupon/prototype nếu cần.
- Không cộng dòng danh định của nhiều via theo phép nhân lý tưởng; via gần nhau nóng lẫn nhau và dòng không chia đều.

---

## 19. Keepout và Rule Area cần tạo trong KiCad

| Rule Area | Lớp/vùng | Mục đích |
|---|---|---|
| `RA_ESP32_ANTENNA` | Tất cả lớp | Cấm track, via, zone và component dưới/trước anten |
| `RA_HV_20A_CORRIDOR` | F.Cu/B.Cu dọc mép bo | Chỉ cho phép net HV/return; cấm control signal và GND bridge ngoài ý muốn |
| `RA_HV_RETURN_BOUNDARY` | B.Cu | Giới hạn return 20 A, ngăn nó lan qua vùng control |
| `RA_BUCK_SW` | F.Cu và vùng chiếu xuống B.Cu | Giới hạn copper SW; cấm via và trace nhạy cảm |
| `RA_INA_KELVIN` | F.Cu | Cho phép nhánh 0.20 mm/no-via trên net công suất |
| `RA_USB_FCU` | F.Cu/B.Cu reference | Ép USB lên F.Cu, cấm test point/via và cấm void trên B.Cu dưới cặp |
| `RA_ESD_ENTRY_USB` | Connector→TVS | Cấm unprotected trace và via trước TVS |
| `RA_ESD_ENTRY_CAN` | Connector→TVS | Tương tự cho CAN |
| `RA_ESD_ENTRY_RS485` | Connector→TVS | Tương tự cho RS485 |

KiCad 10 cho phép Rule Area hạn chế placement/zone fill và làm named area cho Custom Rules. Track width trong Net Class là default, không tự trở thành minimum; dùng Custom Rules để ép minimum cho 20 A.

---

## 20. Ánh xạ Net Class sang lớp routing

| Net Class | Lớp ưu tiên | Lớp cho phép có điều kiện | Cấm/không khuyến nghị |
|---|---|---|---|
| `HV60_20A_TRUNK` | F.Cu positive, B.Cu return | Cả hai cùng F.Cu nếu topology/diện tích yêu cầu | Đổi lớp bằng via đơn; vùng MCU/ADC |
| `HV60_SENSE_RAW` | F.Cu trong HV zone | B.Cu đoạn rất ngắn sau review | Antenna/buck zone |
| `PWR24_MAIN` | F.Cu distribution | B.Cu đoạn ngắn, đủ via và không cắt reference | USB/ADC reference corridor |
| `PWR24_SWITCHED` | F.Cu/B.Cu gần output | Theo geometry và dòng thực | Analog/MCU zone |
| `PWR5V` | F.Cu local/distribution | B.Cu short escape | USB reference corridor |
| `PWR3V3` | F.Cu local/distribution | B.Cu short escape | Antenna keepout |
| `BUCK_SW` | F.Cu duy nhất | Không | B.Cu và mọi vùng nhạy |
| `ANALOG_LV` | F.Cu | B.Cu đoạn ngắn với return đã review | Power corridor; noisy zones |
| `USB_FS_90R` | F.Cu | Không khuyến nghị đổi lớp | B.Cu, plane/zone split |
| `FIELD_BUS_120R` | F.Cu | B.Cu nếu reference/return được duy trì | HV/buck zone |
| `EXT_IO` | F.Cu connector zone | B.Cu slow route | Antenna/analog zone |
| `DEFAULT_LOGIC` | F.Cu | B.Cu khi không phá GND reference | Antenna keepout |
| `SHIELD_ESD` | F.Cu/B.Cu gần connector/chassis | Theo enclosure | Dây dài vào digital core |

---

## 21. Thứ tự placement và routing chính thức

### Gate A — trước placement

- [ ] Nhận outline, lỗ, connector fixed position và enclosure.
- [ ] Chốt topology `VBAT_RETURN_20A`/`GND_CTRL`.
- [ ] Nhận stackup sơ bộ từ fabricator.
- [ ] Tạo Net Class và Rule Area.

### Gate B — placement

1. Khóa connector, lỗ bắt vít, antenna edge.
2. Đặt chuỗi 60 V/20 A thành một đường thẳng.
3. Đặt buck theo hot loop.
4. Đặt INA240 sát shunt theo Kelvin.
5. Đặt USB connector–TVS–CH340 thành một chuỗi.
6. Đặt CAN/RS485 connector–TVS–transceiver.
7. Đặt ESP32 sao cho anten không hướng vào buck/HV.
8. Đặt 24 V output drivers sát connector.
9. Đặt decoupling trước khi route signal.

### Gate C — routing

1. Route F.Cu HV positive và B.Cu return đồng thời.
2. Review loop, neck-down và thermal trước khi route phần khác.
3. Route Kelvin INA240.
4. Route buck hot loop, SW, BOOT, FB.
5. Route USB.
6. Tạo B.Cu GND/PGND reference và kiểm tra mọi keepout/split/cổ chai.
7. Route `+24V/+5V/+3V3` trên F.Cu; chỉ dùng B.Cu escape đã review.
8. Route CAN/RS485.
9. Route ADC/analog.
10. Route relay coil/DO switched outputs.
11. Route logic còn lại.
12. Fill GND F.Cu/B.Cu và thêm stitching theo đường hồi thực tế.
13. Refill zones, DRC, inspect return paths thủ công.

Không route “tín hiệu dễ trước” rồi để đường 20 A/hot loop tự tìm chỗ còn lại.

---

## 22. Quy tắc kiểm tra return path thủ công

Với từng net quan trọng, trả lời đủ bốn câu:

1. Dòng đi ở đâu?
2. Dòng về ở đâu tại DC?
3. Dòng về ở đâu tại cạnh nhanh/high frequency?
4. Khi gặp via, plane edge hoặc connector, return chuyển đường bằng gì?

### Bảng kiểm tra

| Net/loop | Forward path | Return path mong muốn | Lỗi cần tìm |
|---|---|---|---|
| USB D+/D− | F.Cu pair | B.Cu image/common-mode return | B.Cu void, via không đối xứng |
| CAN/RS485 | F.Cu pair | B.Cu + cable pair | Stub, termination sai, TVS ground dài |
| ESP32 3.3 V transient | F.Cu feed | Local cap → B.Cu | Cap xa, ground via xa |
| Buck hot loop | F.Cu local | F.Cu local PGND | Loop lan vào B.Cu system ground |
| Relay coil | +24V → coil → driver | Dedicated 24 V return | Chung via/track với MCU GND |
| 20 A load | F.Cu positive | B.Cu/coplanar dedicated return | Dòng rẽ qua B.Cu vùng logic |
| INA240 sense | Kelvin F.Cu | Differential input pair | Lấy sense ngoài pad, share copper |
| ESD connector | Pin → TVS | TVS → chassis/B.Cu | Stub/via trước TVS, ground dài |

---

## 23. Kiểm tra DRC và visual inspection

### 23.1 DRC bắt buộc

- Minimum width cho HV trunk.
- Clearance 60 V.
- No-via cho `BUCK_SW` và Kelvin nếu có thể.
- USB DP width/gap sau khi nhận stackup.
- Cấm track/via/zone trong antenna keepout.
- Hạn chế signal trên B.Cu; cấm mọi đoạn làm cắt reference path quan trọng.
- Cấm control net trong HV corridor.
- Unconnected item, dangling track và isolated copper island.

### 23.2 Visual inspection không thể giao hết cho DRC

- Dòng 20 A có đi theo topology mong muốn hay không.
- Vùng GND reference B.Cu có bị chia thành island/moat/cổ chai không.
- Return path của mỗi lần đổi lớp.
- TVS có thực sự nằm trước protected IC theo hướng dòng ESD không.
- Neck-down ở pad/zone transition.
- Kelvin pick-off có nằm đúng điểm trong pad shunt không.
- FB có lấy tại clean output không.
- Antenna keepout có bị enclosure/connector kim loại xâm phạm không.

### 23.3 KiCad-specific

- Track width Net Class chỉ là optimal/default; Custom Rule mới ép minimum.
- Một net có thể nhận nhiều Net Class; kiểm tra effective aggregate class và priority.
- Nếu dùng DP router, tên net phải có common base và suffix `P/N` hoặc `+/-`.
- Dùng **Inspect → Net Inspector** và 3D Viewer cùng DRC.

---

## 24. Kế hoạch verification sau layout

### 24.1 Pre-fabrication

- [ ] Fabricator xác nhận stack 2 lớp, 2 oz finished copper trên F.Cu/B.Cu và tolerance.
- [ ] Fabricator cung cấp USB 90 Ω width/gap và tolerance.
- [ ] Review Gerber từng lớp, không chỉ xem PCB Editor.
- [ ] Dùng field solver/fab calculator cho USB.
- [ ] Dùng current/thermal solver hoặc calculation có điều kiện biên cho 20 A.
- [ ] Review solderability của pad 20 A và U9 thermal vias.

### 24.2 Bring-up điện

- [ ] Cấp 24 V với current limit, chưa nối bus 60 V.
- [ ] Kiểm tra 5 V/3.3 V ripple khi ESP32 Wi-Fi transmit.
- [ ] Kiểm tra buck SW ringing bằng ground spring.
- [ ] Kiểm tra ADC offset/noise khi relay và DO tắt.
- [ ] Sau đó đóng/cắt từng coil/output và quan sát reset/ADC/CAN/RS485.

### 24.3 Test 20 A

- [ ] Tăng tải theo bậc 2 A → 5 A → 10 A → 15 A → 20 A.
- [ ] Đo sụt áp bốn dây trên shunt và từng đoạn copper.
- [ ] Thermal soak đến trạng thái ổn định trong enclosure dự kiến.
- [ ] Ghi nhiệt connector, relay, shunt, track throat và U9.
- [ ] Lặp ở ambient cao nhất dự kiến.

### 24.4 EMC pre-compliance

- [ ] Near-field scan tại buck, relay, 20 A corridor, ESP32 và cáp.
- [ ] Conducted emission trên 24 V input.
- [ ] ESD tại USB, CAN, RS485, UART, switch/output connectors và enclosure.
- [ ] EFT/burst trên 24 V/cáp I/O theo môi trường đã chốt.
- [ ] Surge nếu system requirement yêu cầu.
- [ ] Kiểm tra functional performance: không reset, không latch, không sai relay state, ADC error trong giới hạn.

Tiêu chí pass/fail phải được viết trước test; “mạch vẫn chạy” chưa đủ nếu ADC sai hoặc communication mất gói quá giới hạn.

---

## 25. Ma trận nguồn và kết luận rút ra

| Nguồn | Revision/ngày | Locator/claim dùng trong tài liệu | Mức bằng chứng | Giới hạn áp dụng |
|---|---|---|---|---|
| [IPC-2221C](https://shop.electronics.org/ipc-2221/ipc-2221-standard-only/Revision-c/english) | Rev C, 2023-12 | Generic printed-board design foundation | Normative design reference | Nội dung chi tiết cần bản tiêu chuẩn hợp pháp |
| [IPC-2222B](https://shop.electronics.org/ipc-2222/ipc-2222-standard-only/Revision-b/english) | Rev B, 2020-10 | Rigid organic PCB requirements | Normative design reference | Không thay fab capability |
| [IPC revision table](https://www.electronics.org/ipc-document-revision-table) | Truy cập 2026-08-15 | IPC-2141/2152 marked No Longer Maintained; IPC-2221C/2222B current revision shown | `confirmed` | Chỉ trạng thái tài liệu, không chứa rule chi tiết |
| [IPC-2152](https://shop.electronics.org/ipc-2152/ipc-2152-standard-only/Revision-0/english) | Original, 2009-08 | Current-carrying/thermal factors | Historical analytical support | Không dùng làm bằng chứng duy nhất cho 20 A |
| [IEC 60664-1:2020+A1:2025](https://webstore.iec.ch/en/publication/107319) | Ed. 3.1, 2025-05-06 | Creepage/clearance phụ thuộc insulation coordination, altitude, material, pollution | Normative safety framework | Chưa biết product/environment inputs |
| [Espressif ESP32 PCB Layout](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/pcb-layout-design.html) | Latest, truy cập 2026-08-15 | Reference layout ưu tiên GND plane/power organization; main 3.3 V ≥25 mil; antenna edge/keepout | `datasheet_supported` | Khuyến nghị multilayer không chứng minh bo 2 lớp tương đương; RF cần test trong enclosure |
| [TI LV14340 datasheet](https://www.ti.com/lit/gpn/LV14340) | SNVSAD7C, Rev C, 2024-12 | Section 7.4: CIN, L, D, COUT, FB và local ground placement | `datasheet_supported` | Phải áp dụng đúng package/footprint |
| [TI AN-1149](https://www.ti.com/lit/pdf/snva021) | SNVA021C, 2013-04 | Switching supply loop/layout rationale | Supporting manufacturer guide | General guide, LV14340 datasheet ưu tiên |
| [TI INA240 datasheet](https://www.ti.com/lit/gpn/INA240) | SBOS662C, Rev C, 2021-12 | Sections 9.3/11.1: Kelvin/4-wire shunt routing | `datasheet_supported` | Accuracy cuối cần đo trên PCB thật |
| [TI High-Speed Interface Layout Guidelines](https://www.ti.com/lit/pdf/spraar7) | SPRAAR7J, 2023-02 | Solid GND reference; không cross plane split/void; pair symmetry | Supporting manufacturer guide | Một số rule hướng tới tốc độ cao hơn USB FS |
| [TI ESD Protection Layout Guide](https://www.ti.com/lit/an/slva680b/slva680b.pdf) | SLVA680A, 2022-04 | Connector→TVS trực tiếp; no stub/via; TVS ground low inductance | Supporting manufacturer guide | TVS selection vẫn cần datasheet cụ thể |
| [USB 2.0 Specification](https://www.usb.org/document-library/usb-20-specification) | Trang cập nhật 2025-06-03 | USB 2.0 base specification | Interface normative reference | CH340C chỉ Full-Speed nhưng layout vẫn cần SI tốt |
| [USB 2.0 Electrical Compliance v1.08](https://www.usb.org/document-library/usb-20-electrical-compliance-test-specification) | 2026-04-21 | Electrical test criteria | Verification reference | Không thay product qualification plan |
| [TI Controller Area Network Physical Layer Requirements](https://www.ti.com/lit/pdf/slla270) | SLLA270 | CAN physical layer/cable/stub factors | Supporting manufacturer guide | Data rate/cable length chưa được cung cấp |
| [TI Top Design Questions About Isolated CAN](https://www.ti.com/lit/pdf/slla486) | 2026 | 120 Ω cable and termination at extreme ends | Supporting manufacturer guide | Isolation need remains system decision |
| [ADI AN-960 RS-485/RS-422 Guide](https://www.analog.com/en/resources/app-notes/an-960.html) | Manufacturer app note | Balanced pair, industrial implementation, termination | Supporting manufacturer guide | Check exact MAX3485/common-mode conditions |
| [KiCad PCB Editor 10.0](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html) | 10.0 | Net Class default vs Custom Rule; Rule Area; DP router naming | Tool-authoritative | UI may differ if project uses KiCad 8/9 |
| [IEC 61000-6-2:2016](https://webstore.iec.ch/en/publication/25630) | Ed. 3.0, 2016 | Generic industrial immunity candidate | Normative candidate | Chỉ dùng nếu không có product-family standard |
| [IEC 61000-6-4:2018](https://webstore.iec.ch/en/publication/26622) | Ed. 3.0, 2018 | Generic industrial emission candidate | Normative candidate | Product environment chưa chốt |
| [IEC 61000-4-2:2025](https://webstore.iec.ch/en/publication/68954) | Ed. 3.0, 2025 | ESD test method | Basic EMC test reference | Test level do product standard/project chọn |
| [IEC 61000-4-4:2012](https://webstore.iec.ch/en/publication/4222) | Ed. 3.0, 2012 | EFT/burst test method | Basic EMC test reference | Đặc biệt liên quan switched inductive loads |
| [IEC 61000-4-5:2014](https://webstore.iec.ch/en/publication/4223) | Ed. 3.0, 2014 | Surge test method | Basic EMC test reference | Applicability/test level chưa chốt |
| [IEC 61000-4-6:2023](https://webstore.iec.ch/en/publication/65586) | Ed. 5.0, 2023 | Conducted RF immunity on cables | Basic EMC test reference | Cần CDN/clamp/test plan phù hợp port |

---

## 26. Quyết định còn cần người thiết kế chốt

### Quyết định 1 — return 20 A

**Khuyến nghị:** dùng `VBAT_RETURN_20A` riêng trên B.Cu, chồng dưới positive trên F.Cu và giữ hành lang ở mép bo.  
**Điều kiện:** xác nhận topology common-negative và single-point connection.

### Quyết định 2 — stackup fabricator

**Khuyến nghị:** yêu cầu fab xác nhận stack 2 lớp, 2 oz finished copper hai mặt và calculate 90 Ω USB từ geometry thực.  
**Không được làm:** tự khóa DP width/gap từ stackup giả định.

### Quyết định 3 — chuẩn EMC đích

**Khuyến nghị tạm thời:** nếu robot dùng trong môi trường công nghiệp và không có product-family standard, đánh giá IEC 61000-6-2/6-4 làm baseline.  
**Điều kiện:** product owner/qualified compliance engineer xác nhận jurisdiction và môi trường.

### Quyết định 4 — tên differential pair

**Khuyến nghị:** đổi USB sang hậu tố P/N nếu muốn dùng KiCad Differential Pair Router; CAN/RS485 chỉ đổi sau khi mapping polarity được kiểm tra.

---

## 27. Gate disposition

### AI assessment: `recommended_conditional_pass`

Có thể bắt đầu **placement và routing concept** trên 2 lớp theo kiến trúc trong tài liệu. Chưa nên khóa Gerber hoặc đặt sản xuất cho đến khi đóng các điều kiện:

1. Chốt `VBAT_RETURN_20A` và điểm nối `GND_CTRL`.
2. Nhận stackup chính thức và impedance USB từ fabricator.
3. Sửa thermal pad U9, `CH340_V3` và các lỗi schematic đã nêu trong tài liệu Net Class.
4. Tạo đầy đủ Rule Area ở mục 19.
5. Review return path từng interface và corridor 20 A.
6. Có kế hoạch thermal/EMC verification với tiêu chí pass/fail định lượng.

**Human decision:** để trống; người chịu trách nhiệm thiết kế phải ghi quyết định, revision PCB, ngày và các residual risks được chấp nhận trong hồ sơ dự án.
