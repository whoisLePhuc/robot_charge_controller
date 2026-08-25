# Hướng dẫn đặt tên net và sử dụng Net Class

## Robot HV Charge Controller — 60 V / 20 A, ESP32, PCB 2 lớp

**Tài liệu áp dụng cho:** `robot-hv-charge-controller(5).pdf`  
**Cấu hình PCB đã chọn:** 2 lớp; đồng thành phẩm 2 oz trên F.Cu và B.Cu  
**Khoảng lệch hiện tại:** metadata trong file PCB vẫn ghi 0,035 mm (~1 oz) mỗi mặt; phải cập nhật qua Konnect trước khi xuất dữ liệu sản xuất  
**Mục đích:** chuẩn hóa tên net, Net Class, thứ tự routing và kiểm tra DRC trước khi bắt đầu layout  
**Trạng thái:** hướng dẫn thiết kế để review; chưa phải xác nhận đạt EMC, an toàn điện hoặc sản xuất hàng loạt

---

## 0. Phạm vi và giả định

Tài liệu được lập từ bản PDF schematic, chưa có file project/netlist KiCad để truy vấn connectivity tự động. Vì vậy:

- Tên net và chân linh kiện được đối chiếu trực quan từ schematic; cần xác nhận lại bằng ERC/Net Inspector trong project gốc.
- Chưa có stackup, dielectric thickness, Dk, solder-mask model và capability table của nhà sản xuất.
- Chưa có nhiệt độ môi trường, enclosure, airflow, duty cycle tải và profile xung/surge chính thức.
- Chưa xác nhận hai nguồn 24 V và 60 V có chung cực âm.
- Các kích thước trong tài liệu là design starting point có margin, không phải chứng chỉ IPC/IEC hay kết quả field solver.

Mọi chỗ ghi “bắt buộc” có nghĩa là bắt buộc đối với gate review nội bộ của thiết kế này; người thiết kế vẫn chịu trách nhiệm chốt với yêu cầu hệ thống và nhà sản xuất.

---

## 1. Kết luận áp dụng nhanh

Thiết kế nên dùng 12 Net Class chính và một class tùy chọn:

1. `HV60_20A_TRUNK`
2. `HV60_SENSE_RAW`
3. `PWR24_MAIN`
4. `PWR24_SWITCHED`
5. `PWR5V`
6. `PWR3V3`
7. `BUCK_SW`
8. `ANALOG_LV`
9. `USB_FS_90R`
10. `FIELD_BUS_120R`
11. `EXT_IO`
12. `DEFAULT_LOGIC`
13. `SHIELD_ESD` — chỉ tạo nếu schematic có net shield/chassis riêng

Net Class chỉ là lớp quy tắc ban đầu. Các trường hợp dưới đây bắt buộc phải có thêm **Rule Area hoặc Custom DRC Rule**:

- Hành lang dòng chính 60 V / 20 A.
- Hai nhánh Kelvin từ shunt R41 đến INA240.
- Nút chuyển mạch `BUCK_SW` của LV14340.
- Vùng keepout anten của ESP32-WROOM-32E.
- Cặp USB nếu nhà sản xuất cung cấp stackup để kiểm soát 90 Ω vi sai.

Không đưa toàn bộ `GND` vào `HV60_20A_TRUNK`. Dòng hồi 20 A phải được kiểm soát theo hình học, còn mặt phẳng GND điều khiển phải liên tục dưới MCU, USB, CAN và RS485.

---

## 2. Net Class làm được gì và không làm được gì

### 2.1 Net Class làm được

Trong KiCad, một Net Class cung cấp các giá trị mặc định cho:

- Clearance giữa track/via/pad của net với các đối tượng đồng khác.
- Track Width khi bắt đầu route.
- Via Size và Via Hole.
- Kích thước microvia nếu công nghệ HDI được bật.
- Differential Pair Width và Differential Pair Gap.
- Tuning Profile cho công cụ length tuning.
- Màu hiển thị để nhận biết net khi layout.

### 2.2 Net Class không tự bảo đảm

- `Track Width` là giá trị route mặc định, không phải lúc nào cũng là bề rộng tối thiểu bắt buộc.
- Net Class không biết đoạn nào là Kelvin sense nếu nhánh sense cùng net với đường công suất.
- Net Class không tự cấm via trên `BUCK_SW`.
- Net Class không tự tạo vùng keepout anten.
- Net Class không chứng minh nhiệt độ đường 20 A đạt yêu cầu.
- DP Width/Gap không tự tạo đúng trở kháng nếu chưa có stackup thực của nhà sản xuất.
- PCB Color chỉ phục vụ hiển thị; không ảnh hưởng DRC hoặc sản xuất.

Vì vậy, workflow đúng là:

```text
Tên net rõ nghĩa
    ↓
Gán Net Class
    ↓
Rule Area / Custom DRC cho ngoại lệ quan trọng
    ↓
Placement và routing
    ↓
DRC + kiểm tra hình học + đo nhiệt/EMC trên prototype
```

---

## 3. Các vấn đề schematic phải xử lý trước khi gán class

### 3.1 Quyết định kiến trúc GND trước khi layout

Trong schematic hiện tại, `60V_GND` và `GND` xuất hiện trên cùng một dây. Cần chọn rõ một trong hai phương án:

#### Phương án A — khuyến nghị khi 24 V và 60 V dùng chung mass

- Đổi đường hồi công suất J5-N → J7-N thành `VBAT_RETURN_20A`.
- Dùng `GND_CTRL` hoặc `GND` cho phần điều khiển, MCU, analog, USB, CAN và RS485.
- Nối `VBAT_RETURN_20A` với `GND_CTRL` tại một điểm tap có chủ đích bằng Net-Tie hoặc cấu trúc tương đương.
- Không cho dòng tải 20 A đi xuyên qua linh kiện Net-Tie nhỏ. Điểm Net-Tie chỉ định nghĩa topology; hành lang đồng công suất phải đi trực tiếp giữa các đầu nối/tải.
- Giữ vùng B.Cu dưới khối điều khiển thành GND reference liên tục tối đa có thể; không để hành lang return 20 A hoặc power escape cắt đường hồi của USB/ADC/communication.

#### Phương án B — nếu toàn bo chỉ dùng một GND

- Xóa tên `60V_GND`, giữ một tên `GND` duy nhất.
- Dùng Rule Area/keepout để ép dòng hồi 20 A đi trong hành lang riêng.
- Không thể dùng Net Class để phân biệt “đoạn GND công suất” và “đoạn GND tín hiệu” vì chúng là cùng một net.

Trước khi chọn, phải xác nhận nguồn 24 V có chung cực âm với nguồn 60 V hay không. Không tự nối hai nguồn nếu tài liệu hệ thống chưa xác nhận.

### 3.2 Sửa pad tản nhiệt của U9

Pad exposed/thermal pad của LV14340 không được để No-Connect. Pad này phải nối vào mặt phẳng GND theo datasheet, dùng vùng đồng và thermal vias phù hợp. Đây vừa là đường tản nhiệt vừa là đường hồi dòng chuyển mạch.

### 3.3 Sửa nguồn V3 của CH340C

Không nối chung chân V3 của CH340C với `V_USB` 5 V:

- VCC pin 16 → `V_USB`.
- V3 pin 4 → net cục bộ `CH340_V3`.
- `CH340_V3` → tụ 100 nF xuống GND, đặt sát chân IC.

Nếu CH340C chạy ở 5 V, cần xác nhận mức logic TXD đi vào ESP32. Không mặc định ESP32 chịu được mức 5 V; dùng cấu hình nguồn hoặc chuyển mức phù hợp.

### 3.4 Xử lý hai net LED UART đang treo

`USB_UART_RX_LED` và `USB_UART_TX_LED` hiện chỉ xuất hiện tại D13/D12 và chưa thể hiện một nguồn điều khiển hoàn chỉnh. Chọn một trong ba cách:

- Bỏ LED và xóa net nếu không cần.
- Điều khiển LED bằng transistor/buffer để tránh tải trực tiếp đường UART.
- Kết nối đúng vào logic activity chuyên dụng nếu thiết kế có mạch tạo xung activity.

Không chỉ đặt tên để che lỗi ERC.

---

## 4. Quy ước đặt tên net

### 4.1 Hậu tố đề xuất

| Hậu tố | Ý nghĩa | Ví dụ |
|---|---|---|
| `_RAW` | Tín hiệu trước lọc hoặc trước bảo vệ | `IOUT_SENSE_RAW` |
| `_ADC` | Nút trực tiếp đi vào ADC | `VOUT_SENSE_ADC` |
| `_IC` | Phía IC của điện trở nối tiếp/bảo vệ | `CAN_TX_IC` |
| `_CONN` | Phía đầu nối | `USB_DP_CONN` |
| `_SW` | Nút switching công suất | `BUCK_SW` |
| `_FB` | Nút feedback nguồn | `BUCK_FB` |
| `_BOOT` | Bootstrap | `BUCK_BOOT` |
| `_DRV_BASE` | Nút điều khiển base transistor | `RELAY_DRV_BASE` |
| `_GATE_CLAMPED` | Gate sau điện trở/kẹp bảo vệ | `SW1_GATE_CLAMPED` |
| `_RETURN` | Đường dòng hồi có chủ đích | `VBAT_RETURN_20A` |

### 4.2 Loại label nên dùng

- **Hierarchical Label:** chỉ dùng cho net đi qua biên sheet.
- **Local Label:** dùng cho nút nội bộ của một sheet, ví dụ `BUCK_SW`, `BUCK_FB`, `CH340_V3`.
- **Global Label:** chỉ dùng cho rail thật sự toàn cục như `+24V`, `+5V`, `+3V3`, `GND`.
- `PWR_FLAG` chỉ thông báo cho ERC rằng rail có nguồn cấp; nó không đặt tên net.
- Không đặt hai tên khác nhau lên cùng một dây dẫn. KiCad có thể chọn một tên hiệu lực ngoài ý muốn hoặc báo conflict.

### 4.3 Không tạo net Kelvin giả

Hai đầu sense của INA240 nối tới hai pad của shunt R41 vẫn là hai nhánh của các net công suất tương ứng:

- Phía trước shunt: `VBAT_RELAY_OUT_P`.
- Phía sau shunt: `VBAT_OUT_P`.

Không nên đặt `ISENSE_P`/`ISENSE_N` lên nhánh dây nếu chúng vẫn nối điện trực tiếp với cùng pad/net công suất. Đặt tên mới không biến chúng thành net riêng. Để điều khiển routing Kelvin, dùng Rule Area/Custom Rule. Nếu muốn net tách biệt thật sự, phải dùng shunt 4 chân/Kelvin footprint hoặc cấu trúc Net-Tie đã được review.

---

## 5. Các tên net cần bổ sung

### 5.1 Sheet gốc / đường công suất 60 V

| Tên net | Vị trí/điểm nối | Mức ưu tiên | Ghi chú |
|---|---|---:|---|
| `VBAT_RETURN_20A` | Đường hồi J5-N → J7-N | Bắt buộc sau khi chốt topology | Chỉ tạo nếu tách return công suất khỏi GND điều khiển |

Các tên đã có và nên giữ:

- `VBAT_PROTECTED_P`
- `VBAT_RELAY_OUT_P`
- `VBAT_OUT_P`
- `MAIN_RELAY_COIL_N`

### 5.2 Sheet Auxiliary Power — LV14340

| Tên net | Vị trí/điểm nối | Class |
|---|---|---|
| `AUX24_PRE_FUSE` | Giữa D3 và F3 | `PWR24_MAIN` |
| `BUCK_BOOT` | U9 pin 1 ↔ C7 | `ANALOG_LV` |
| `BUCK_SW` | U9 pin 8 ↔ D8 ↔ L2 ↔ C7 | `BUCK_SW` |
| `BUCK_FB` | U9 pin 5 ↔ R11/R48 | `ANALOG_LV` |
| `BUCK_RT_SYNC` | U9 pin 4 ↔ R10 | `ANALOG_LV` |
| `BUCK_SS` | U9 pin 6 ↔ C6 | `ANALOG_LV` |

`BUCK_BOOT` dùng class analog về bề rộng/clearance, nhưng placement phải cực ngắn giữa BOOT và SW. Không route nó như một tín hiệu analog thông thường đi xa khỏi U9.

### 5.3 Sheet Output / đo dòng và đo áp

| Tên net | Vị trí/điểm nối | Class |
|---|---|---|
| `IOUT_SENSE_RAW` | U2 INA240 OUT pin 8 ↔ R47 | `ANALOG_LV` |
| `VOUT_DIV_HV_IN` | D15 ↔ R43 | `HV60_SENSE_RAW` |
| `VOUT_DIV_HV_MID1` | R43 ↔ R44 | `HV60_SENSE_RAW` |
| `VOUT_DIV_HV_MID2` | R44 ↔ R45 | `HV60_SENSE_RAW` |

Các tên đã có và nên giữ:

- `VOUT_DIV_RAW` — nút thấp áp sau chuỗi chia áp, trước lọc ADC.
- `VOUT_SENSE_ADC` — nút tại ADC ESP32.
- `IOUT_SENSE_ADC` — nút tại ADC ESP32.

### 5.4 Sheet MCU / USB

| Tên net | Vị trí/điểm nối | Class |
|---|---|---|
| `USB_VBUS_RAW` | J1 VBUS ↔ phía trước F2 | `PWR5V` |
| `CH340_V3` | U15 pin V3 ↔ tụ 100 nF | `ANALOG_LV` |

Tên tùy chọn phục vụ debug:

- `USB_CC1`
- `USB_CC2`
- `AUTO_PROG_EN_BASE`
- `AUTO_PROG_BOOT_BASE`

Các net USB nên giữ cấu trúc tên theo hai phía linh kiện nối tiếp/bảo vệ:

- `USB_DP_CONN`, `USB_DM_CONN` — phía connector/ESD.
- `USB_DP`, `USB_DM` — phía CH340C.

### 5.5 Sheet Communication

| Tên net | Vị trí/điểm nối | Class |
|---|---|---|
| `SW1_GATE_CLAMPED` | Nút R12/R13/D18/C33/Q11 gate | `EXT_IO` |
| `SW2_GATE_CLAMPED` | Nút R38/R39/D24/C35/Q12 gate | `EXT_IO` |

Tên tùy chọn phục vụ debug:

- `CAN_TX_IC`, `CAN_RX_IC` — phía U12 sau R53/R54.
- `CAN_SLOPE_CTRL` — U12 S ↔ R55.
- `RS485_DIR_IC` — U3 DE/RE ↔ R9 nếu cần phân biệt hai phía.

Giữ các net hiện có:

- `CAN_H`, `CAN_L`, `CAN_TX`, `CAN_RX`.
- `RS485_A`, `RS485_B`, `RS485_TX`, `RS485_RX`, `RS485_DIR`.
- `UART_EXT_TX_MCU`, `UART_EXT_TX_CONN`.
- `UART_EXT_RX_MCU`, `UART_EXT_RX_CONN`.
- `SW1_EXT`, `SW2_EXT`, `SW1_SENSE_N`, `SW2_SENSE_N`.

Nếu schematic hiện dùng cả `CANH/CANL` và `CAN_H/CAN_L`, chỉ giữ hai nhóm tên khi chúng thực sự nằm ở hai phía của linh kiện nối tiếp hoặc bảo vệ. Nếu là cùng một dây, chuẩn hóa về một tên duy nhất.

### 5.6 Sheet Output Drivers

Tên tùy chọn để probe/debug:

- `RELAY_DRV_BASE`
- `DO1_DRV_BASE`
- `DO2_DRV_BASE`
- `DO3_DRV_BASE`

Giữ các net hiện có:

- `DO1_CMD`, `DO2_CMD`, `DO3_CMD`.
- `DO1_SINK`, `DO2_SINK`, `DO3_SINK`.
- `MAIN_RELAY_COIL_N`.

---

## 6. Bảng thông số Net Class để nhập vào KiCad

Tất cả kích thước trong bảng dưới đây dùng đơn vị **mm**.

| Net Class | Clearance | Track Width | Via Size | Via Hole | μVia Size | μVia Hole | DP Width | DP Gap | Tuning Profile | PCB Color |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `HV60_20A_TRUNK` | 1.00 | 8.00 | 1.20 | 0.60 | 0.30 | 0.10 | 0.20 | 0.25 | Default | `#E53935` |
| `HV60_SENSE_RAW` | 1.00 | 0.25 | 0.80 | 0.40 | 0.30 | 0.10 | 0.20 | 0.25 | Default | `#FB8C00` |
| `PWR24_MAIN` | 0.50 | 1.00 | 1.00 | 0.50 | 0.30 | 0.10 | 0.20 | 0.25 | Default | `#F9A825` |
| `PWR24_SWITCHED` | 0.50 | 0.60 | 0.80 | 0.40 | 0.30 | 0.10 | 0.20 | 0.25 | Default | `#8E24AA` |
| `PWR5V` | 0.25 | 1.00 | 0.80 | 0.40 | 0.30 | 0.10 | 0.20 | 0.25 | Default | `#FDD835` |
| `PWR3V3` | 0.25 | 0.65 | 0.80 | 0.40 | 0.30 | 0.10 | 0.20 | 0.25 | Default | `#43A047` |
| `BUCK_SW` | 0.50 | 0.80 | 0.80 | 0.40 | 0.30 | 0.10 | 0.20 | 0.25 | Default | `#D81B60` |
| `ANALOG_LV` | 0.30 | 0.20 | 0.60 | 0.30 | 0.30 | 0.10 | 0.20 | 0.25 | Default | `#00ACC1` |
| `USB_FS_90R` | 0.20 | 0.20 | 0.60 | 0.30 | 0.30 | 0.10 | 0.20 | 0.20 | Default | `#1E88E5` |
| `FIELD_BUS_120R` | 0.30 | 0.25 | 0.60 | 0.30 | 0.30 | 0.10 | 0.25 | 0.25 | Default | `#3949AB` |
| `EXT_IO` | 0.30 | 0.25 | 0.60 | 0.30 | 0.30 | 0.10 | 0.20 | 0.25 | Default | `#6D4C41` |
| `DEFAULT_LOGIC` | 0.20 | 0.25 | 0.60 | 0.30 | 0.30 | 0.10 | 0.20 | 0.25 | Default | `#757575` |
| `SHIELD_ESD` (tùy chọn) | 0.50 | 1.00 | 1.00 | 0.50 | 0.30 | 0.10 | 0.20 | 0.25 | Default | `#37474F` |

Các giá trị USB và field bus là giá trị khởi đầu để thao tác, không phải kết quả tính impedance. Phải thay DP Width/Gap sau khi nhận stackup thực tế từ nhà sản xuất.

### 6.1 Microvia

Bo 2 lớp này không cần HDI. Trong Board Setup nên tắt blind/buried via và microvia. Các cột μVia chỉ là placeholder vì giao diện Net Class yêu cầu có giá trị; chúng không được dùng khi microvia đã tắt.

### 6.2 Clearance 60 V

Clearance 1.00 mm cho nhóm 60 V là margin thiết kế nội bộ phù hợp với môi trường đóng cắt nhiễu, nhưng không phải tuyên bố đạt một tiêu chuẩn cách điện cụ thể. Creepage/clearance chính thức còn phụ thuộc:

- Điện áp làm việc và quá áp xung.
- Pollution degree.
- Material group/CTI của laminate.
- Độ cao vận hành.
- Coating và yêu cầu sản phẩm cuối.

---

## 7. Ánh xạ net → Net Class

### 7.1 `HV60_20A_TRUNK`

Gán cho:

- `VBAT_PROTECTED_P`
- `VBAT_RELAY_OUT_P`
- `VBAT_OUT_P`
- `VBAT_RETURN_20A` — nếu đã tách return theo phương án A

Không gán toàn bộ `GND` cho class này.

### 7.2 `HV60_SENSE_RAW`

Gán cho:

- `VOUT_DIV_HV_IN`
- `VOUT_DIV_HV_MID1`
- `VOUT_DIV_HV_MID2`

### 7.3 `PWR24_MAIN`

Gán cho:

- `VAUX_IN_P`
- `AUX24_PRE_FUSE`
- `+24V`

Nếu có net 24 V ở phía connector và phía sau diode/fuse khác tên, liệt kê rõ từng net; không dựa hoàn toàn vào wildcard.

### 7.4 `PWR24_SWITCHED`

Gán cho:

- `MAIN_RELAY_COIL_N`
- `DO1_SINK`
- `DO2_SINK`
- `DO3_SINK`

Các net này có cạnh chuyển mạch và dòng tải lớn hơn logic, nhưng không được route gần anten, ADC hoặc feedback buck.

### 7.5 `PWR5V`

Gán cho:

- `+5V`
- `AUX_5V`
- `V_USB`
- `USB_VBUS_RAW`

Các tên trên có thể thuộc các miền nguồn khác nhau dù dùng cùng Net Class. Không nối chúng với nhau chỉ vì cùng class.

### 7.6 `PWR3V3`

Gán cho:

- `+3V3`
- `AUX_3V3`

Nếu `AUX_3V3` và `+3V3` là cùng rail, chuẩn hóa tên. Nếu được tách qua ferrite bead hoặc switch, giữ tên riêng để thấy rõ biên nguồn.

### 7.7 `BUCK_SW`

Gán duy nhất cho:

- `BUCK_SW`

Không dùng class này cho `BUCK_BOOT`, `BUCK_FB`, `BUCK_SS` hoặc `BUCK_RT_SYNC`.

### 7.8 `ANALOG_LV`

Gán cho:

- `BUCK_BOOT`
- `BUCK_FB`
- `BUCK_RT_SYNC`
- `BUCK_SS`
- `IOUT_SENSE_RAW`
- `IOUT_SENSE_ADC`
- `VOUT_DIV_RAW`
- `VOUT_SENSE_ADC`
- `CH340_V3`

Với `BUCK_BOOT`, class chỉ quy định hình học cơ bản; route vật lý phải cực ngắn và nằm trong vòng switching cục bộ.

### 7.9 `USB_FS_90R`

Gán cho bốn đoạn:

- `USB_DP_CONN`
- `USB_DM_CONN`
- `USB_DP`
- `USB_DM`

Mỗi cặp ở hai phía linh kiện ESD/điện trở series phải được route ghép cặp và không tạo stub.

### 7.10 `FIELD_BUS_120R`

Gán cho:

- `CAN_H`, `CAN_L`
- `CANH`, `CANL` — chỉ nếu đây là các đoạn riêng hợp lệ
- `RS485_A`, `RS485_B`

`120R` trong tên class nhắc tới môi trường bus/cáp danh định 120 Ω. Nó không có nghĩa mọi đoạn PCB ngắn bắt buộc phải length-match cực chặt. Ưu tiên continuity của return path, ghép cặp hợp lý và không tạo stub.

### 7.11 `EXT_IO`

Gán cho:

- `UART_EXT_TX_CONN`
- `UART_EXT_RX_CONN`
- `SW1_EXT`
- `SW2_EXT`
- `SW1_GATE_CLAMPED`
- `SW2_GATE_CLAMPED`

Có thể đưa các net khác trực tiếp ra connector vào class này nếu chúng không thuộc USB/CAN/RS485 hay đường nguồn.

### 7.12 `DEFAULT_LOGIC`

Gán cho các tín hiệu logic còn lại, ví dụ:

- `MCU_EN`
- `MCU_BOOT`
- `UART0_TX`, `UART0_RX`
- `CAN_TX`, `CAN_RX`
- `RS485_TX`, `RS485_RX`, `RS485_DIR`
- `UART_EXT_TX_MCU`, `UART_EXT_RX_MCU`
- `SW1_SENSE_N`, `SW2_SENSE_N`
- `DO1_CMD`, `DO2_CMD`, `DO3_CMD`
- Các net base transistor cục bộ.

### 7.13 `SHIELD_ESD`

Chỉ dùng khi có net riêng cho connector shield/chassis. Không tự động gán shield USB vào digital GND. Cách nối shield với chassis/GND phụ thuộc enclosure, vị trí đầu nối và kế hoạch ESD toàn hệ thống.

---

## 8. Cách gán Net Class trong schematic/KiCad

Tên menu có thể thay đổi nhẹ giữa KiCad 8, 9 và 10, nhưng quy trình nên như sau.

### 8.1 Tạo danh sách class

1. Mở PCB Editor.
2. Vào **Board Setup → Design Rules → Net Classes**.
3. Tạo các class đúng tên ở mục 6.
4. Nhập toàn bộ giá trị mm.
5. Tắt microvia/blind-buried via nếu nhà sản xuất không dùng HDI.
6. Lưu project trước khi bắt đầu gán net.

Nếu phiên bản KiCad cho phép quản lý Net Class ngay trong Schematic Setup, dùng cùng tên và cùng giá trị; sau đó xác nhận lại effective class trong PCB Editor.

### 8.2 Phương thức gán khuyến nghị

#### Cách 1 — Pattern assignment cho nhóm net

Dùng cho các nhóm có tên nhất quán. Ví dụ:

| Pattern/nhóm | Net Class | Lưu ý |
|---|---|---|
| `VBAT_*` | Không gán tự động toàn bộ | Liệt kê explicit để tránh kéo nhầm net sense/return |
| `VOUT_DIV_HV_*` | `HV60_SENSE_RAW` | Phù hợp nếu tất cả đều là nút cao áp |
| `BUCK_SW` | `BUCK_SW` | Dùng exact name |
| `BUCK_FB`, `BUCK_BOOT`, `BUCK_RT_SYNC`, `BUCK_SS` | `ANALOG_LV` | Liệt kê explicit |
| `USB_DP*`, `USB_DM*` | `USB_FS_90R` | Kiểm tra preview để không bắt nhầm net debug |
| `DO1_SINK`, `DO2_SINK`, `DO3_SINK` | `PWR24_SWITCHED` | Liệt kê explicit |

Sau khi thêm pattern, dùng danh sách/preview của KiCad để kiểm tra các net thực sự được match. Nếu không chắc cú pháp wildcard của phiên bản đang dùng, chuyển sang exact name.

#### Cách 2 — Net Class Directive trên schematic

Dùng lệnh **Place Net Class Directive** và gắn trực tiếp vào dây đối với các net quan trọng, one-off:

- `BUCK_SW`
- `VBAT_PROTECTED_P`
- `VBAT_RELAY_OUT_P`
- `VBAT_OUT_P`
- `VOUT_DIV_HV_IN`
- `VOUT_DIV_HV_MID1`
- `VOUT_DIV_HV_MID2`

Directive phải thực sự bám vào wire. Sau khi update PCB, kiểm tra effective class; không chỉ nhìn biểu tượng trên schematic.

### 8.3 Tránh gán chồng chéo

Không dùng một pattern rộng và một directive trái ngược cho cùng một net nếu không nắm rõ precedence của phiên bản KiCad. Cách an toàn:

- Pattern cho nhóm đơn giản.
- Exact assignment/directive cho net quan trọng.
- Kiểm tra class hiệu lực trong PCB Net Inspector trước routing.

### 8.4 Sau khi Update PCB from Schematic

Mở Net Inspector hoặc danh sách net trong PCB Editor và kiểm tra tối thiểu:

- Tên net.
- Net Class hiệu lực.
- Tổng chiều dài track hiện tại.
- Số via.
- Net có còn tên tự động dạng `Net-(D15...)`, `Net-(R43...)`, `Net-(U9...)`, `Net-(U2...)` hay không.

Các nút chức năng quan trọng không nên còn tên tự động.

---

## 9. Custom Rule và Rule Area bắt buộc

### 9.1 Hành lang dòng 60 V / 20 A

Net Class khởi đầu đặt track 8.00 mm. Khi layout:

- Route trên F.Cu hoặc B.Cu 2 oz; ưu tiên giữ toàn bộ một nhánh dòng trên cùng lớp để tránh cụm via công suất.
- Ưu tiên copper zone/polygon rộng 8–10 mm hoặc lớn hơn nếu có chỗ.
- Không dùng thermal relief cho XT60, contact relay và shunt trên đường 20 A, trừ khi có phân tích nhiệt và khả năng hàn chứng minh cần thiết.
- Tránh via. Nếu buộc phải đổi lớp, dùng mảng via lớn và yêu cầu nhà sản xuất xác nhận copper plating; không dựa vào một via đơn.
- Kiểm tra mọi neck-down tại pad, chân relay, shunt, fuse và connector.
- Đặt đường đi J5 → bảo vệ → relay → shunt → J7 ngắn và thẳng.
- Đường return 20 A phải chạy sát hành lang đi để giảm diện tích vòng dòng.

Ước tính IPC kiểu legacy chỉ nên dùng để sàng lọc: với 2 oz ngoài, 20 A, bề rộng khoảng 6 mm có thể tương ứng mức tăng nhiệt gần 20 °C; 8 mm gần 13 °C; 9.2 mm gần 10 °C trong điều kiện mô hình nhất định. Đây không phải bảo đảm nhiệt vì pad, solder mask, enclosure, airflow và copper spreading thay đổi mạnh kết quả. Prototype phải được tải thật và đo nhiệt.

### 9.2 Kelvin sense của INA240/R41

Hai nhánh Kelvin vẫn mang tên net công suất, nên Net Class sẽ cố route chúng rộng 8 mm. Tạo Rule Area riêng quanh shunt và INA240 để cho phép nhánh sense:

- Bề rộng mục tiêu: khoảng 0.20 mm.
- Lấy tín hiệu trực tiếp từ điểm trong pad shunt, không lấy từ polygon cách pad một đoạn.
- Hai nhánh đi cùng lớp, gần nhau, hình học cân bằng.
- Không via nếu có thể.
- Tránh `BUCK_SW`, cuộn relay, `DOx_SINK` và dòng USB/clock.
- Không để dòng tải chính chia sẻ đoạn copper hẹp với điểm lấy Kelvin.
- Đặt tụ lọc/điện trở input theo khuyến nghị INA240 sát IC nếu schematic có dùng.

Rule Area phải cho phép bề rộng nhỏ riêng cho hai nhánh này nhưng không làm giảm minimum width của toàn bộ net công suất ở nơi khác.

### 9.3 Buck LV14340

Tạo vùng switching compact quanh U9, D8, L2 và các tụ input/output:

- `BUCK_SW`: ngắn nhất, diện tích đồng vừa đủ, không chạy dưới/qua vùng analog.
- Cấm via trên `BUCK_SW` nếu placement cho phép.
- C7 bootstrap đặt sát chân BOOT và SW.
- Tụ input đặt sát vòng VIN–switch–GND.
- `BUCK_FB`, `BUCK_RT_SYNC`, `BUCK_SS` tránh xa SW và L2.
- Lấy feedback tại điểm output sạch sau cuộn cảm/tụ, không lấy tại đường mang xung dòng lớn.
- Thermal pad U9 nối GND plane bằng copper và thermal vias theo datasheet/khả năng hàn.

### 9.4 USB 2.0 Full-Speed

- Route từ connector → ESD → điện trở series (nếu có) → CH340C.
- Cặp D+/D− đi trên cùng lớp, cùng reference plane L2 liên tục.
- Không chạy qua khe plane hoặc đổi reference plane.
- Tránh via; nếu bắt buộc, dùng cấu trúc đối xứng cho cả hai dây.
- Không tạo stub tại ESD.
- Không cố serpentine để match vài phần mười mm; Full-Speed ưu tiên đường ngắn, sạch và cân đối.
- Tính lại DP Width/Gap từ stackup thật để đạt mục tiêu 90 Ω differential.

### 9.5 CAN và RS485

- Route A/B hoặc H/L thành cặp gần nhau, tránh stub dài.
- Đặt TVS/protection sát connector và cho dòng ESD trở về chassis/GND theo đường ngắn.
- Termination 120 Ω chỉ đặt ở hai đầu vật lý của bus; không mặc định bật termination trên mọi node.
- Nếu termination có jumper/switch, silkscreen phải thể hiện rõ trạng thái.
- PCB trace ngắn không cần length matching cực đoan; giữ topology sạch và reference plane liên tục quan trọng hơn.

### 9.6 ESP32 antenna keepout

- Đặt anten module ở mép PCB nếu có thể.
- Tạo keepout copper trên tất cả lớp dưới/vùng trước anten theo footprint/datasheet module.
- Không đặt trace, via, ground pour, connector kim loại hoặc relay trong vùng bức xạ.
- Không chạy đường 20 A, buck SW, coil relay hoặc digital output sát anten.

---

## 10. Thứ tự placement và routing đề xuất

### Bước 1 — khóa cơ khí và connector

- XT60 60 V input/output.
- Connector 24 V, CAN, RS485, UART, switch input, digital output.
- USB-C.
- Lỗ bắt vít, mép bo, enclosure và vùng cách điện.

### Bước 2 — đặt chuỗi 60 V / 20 A

Đặt theo luồng công suất vật lý, giảm loop và neck-down:

```text
60 V IN → bảo vệ → relay → shunt R41 → 60 V OUT
       ↘ return 20 A chạy sát đường đi ↙
```

INA240 đặt sát shunt nhưng ngoài hành lang dòng nóng và tránh relay/buck.

### Bước 3 — đặt nguồn 24 V → 5 V → 3.3 V

- Khóa U9, diode, L2, tụ input/output thành một cụm compact.
- TLV1117-33 và tụ đặt gần tải/rail 3.3 V.
- Giữ `BUCK_SW` xa ADC, anten và connector truyền thông.

### Bước 4 — đặt MCU và USB

- ESP32 anten hướng ra mép bo, giữ keepout.
- CH340C, ESD USB và điện trở CC đặt theo dòng connector → protection → IC.
- Decoupling đặt trước khi route tín hiệu.

### Bước 5 — đặt CAN/RS485 và I/O công nghiệp

- Protection sát connector.
- Transceiver sau protection.
- Đường logic sạch hướng về MCU.
- Driver tải 24 V đặt gần connector/tải, tách khỏi analog.

### Bước 6 — route theo mức ưu tiên

1. `HV60_20A_TRUNK` và return tương ứng.
2. Kelvin sense INA240.
3. Buck hot loop và `BUCK_SW`.
4. Ground/return strategy và stitching.
5. USB differential pair.
6. CAN/RS485 pairs.
7. Analog ADC/feedback.
8. 24 V switched outputs.
9. 5 V, 3.3 V và logic còn lại.

---

## 11. Stackup 2 lớp đã chọn để dùng với các class

| Lớp | Chức năng chính | Ghi chú |
|---|---|---|
| F.Cu — 2 oz finished | Linh kiện; hành lang 20 A; buck hot loop; Kelvin; USB và tín hiệu quan trọng ngắn | Giữ switch node nhỏ; không route dưới anten |
| B.Cu — 2 oz finished | Hành lang return 20 A và GND/PGND reference liên tục tối đa có thể | Không để return công suất cắt qua vùng MCU/ADC; chỉ route tín hiệu chậm khi không phá reference path |

Với bo 2 lớp, khoảng cách F.Cu–B.Cu lớn hơn đáng kể so với signal-to-plane của stack 4 lớp, nên không được tái sử dụng width/gap USB cũ như một kết quả impedance. Yêu cầu nhà sản xuất cung cấp dielectric, Dk, finished copper, solder-mask model và geometry 90 Ω; sau đó cập nhật DP Width/Gap trước khi route hoàn tất.

---

## 12. Checklist trước khi bắt đầu routing

### Schematic/ERC

- [ ] Đã chốt 24 V và 60 V có chung negative hay không.
- [ ] Không còn `60V_GND` và `GND` là hai tên vô tình trên cùng một dây.
- [ ] Đã quyết định `VBAT_RETURN_20A` hoặc một GND duy nhất với Rule Area.
- [ ] U9 thermal pad đã nối GND.
- [ ] CH340C V3 đã thành `CH340_V3` với tụ 100 nF.
- [ ] Đã xác nhận mức logic CH340C → ESP32.
- [ ] `USB_UART_RX_LED` và `USB_UART_TX_LED` đã được kết nối đúng hoặc xóa.
- [ ] Tất cả net ở mục 5 đã được đặt label.
- [ ] Không còn label trùng nghĩa hoặc nhiều label trên cùng wire.
- [ ] ERC không còn lỗi bị che bằng No-Connect/PWR_FLAG sai mục đích.

### Net Class

- [ ] Đã tạo đủ 12 class chính.
- [ ] Đã nhập đúng đơn vị mm.
- [ ] Microvia và blind/buried via đã tắt.
- [ ] Mỗi net quan trọng có đúng một class hiệu lực.
- [ ] `BUCK_SW` chỉ chứa đúng nút switch.
- [ ] Không gán toàn bộ GND vào `HV60_20A_TRUNK`.
- [ ] USB DP Width/Gap được đánh dấu provisional chờ stackup.

### Placement

- [ ] Anten ESP32 ở vị trí hợp lý và có keepout tất cả lớp.
- [ ] Chuỗi 20 A ngắn, thẳng, không có cổ chai.
- [ ] INA240 có thể lấy Kelvin trực tiếp tại pad shunt.
- [ ] Buck hot loop compact.
- [ ] Protection của USB/CAN/RS485/I/O sát connector.
- [ ] Tụ decoupling sát chân nguồn IC.

---

## 13. Checklist sau routing

### DRC và hình học

- [ ] Chạy ERC lại sau mọi thay đổi label.
- [ ] Update PCB from Schematic và xem Net Inspector.
- [ ] Chạy DRC với Custom Rules/Rule Areas đã bật.
- [ ] Không còn net chức năng quan trọng mang tên `Net-(...)`.
- [ ] Không có track 20 A nhỏ hơn giới hạn do neck-down ngoài vùng được duyệt.
- [ ] Không có via đơn mang toàn bộ dòng 20 A.
- [ ] `BUCK_SW` không có via và không chạy gần analog/anten.
- [ ] Nhánh Kelvin không chia sẻ đường dòng tải.
- [ ] USB/CAN/RS485 không chạy qua khe reference plane.
- [ ] Ground plane L2 liên tục dưới MCU và giao tiếp.
- [ ] Creepage quanh 60 V không bị silkscreen, via hoặc copper pour phá vỡ.

### Prototype điện/nhiệt/EMC

- [ ] Tăng tải theo bậc; không cấp ngay 20 A khi lần đầu power-on.
- [ ] Đo sụt áp tại connector, relay contact, shunt và các cổ chai copper.
- [ ] Dùng camera nhiệt/thermocouple đo ở 20 A trong enclosure thực.
- [ ] Kiểm tra relay đóng/cắt khi ESP32 đang chạy Wi-Fi và giao tiếp USB/CAN/RS485.
- [ ] Kiểm tra reset/brownout/ADC spike khi DO1–DO3 đóng cắt tải thực.
- [ ] Dùng oscilloscope với ground spring đo 5 V, 3.3 V, `BUCK_SW`, ADC và rail reset.
- [ ] Thử ESD/EFT/surge theo yêu cầu sản phẩm; TVS presence không đồng nghĩa đã đạt.
- [ ] Lưu log nhiệt độ, dạng sóng và điều kiện test để review trước release.

---

## 14. Các tính toán/simulation cần làm song song

Net Class không thay thế phân tích mạch. Trước khi chốt PCB nên có ít nhất:

- Tổn hao và nhiệt đường đồng 20 A, shunt R41, relay, connector, fuse và MOSFET/diode bảo vệ.
- Buck 24 V → 5 V: Vin min/max, tải min/max, ripple, peak switch current, saturation current của L2, diode current và loop stability theo datasheet.
- Transient/surge trên 24 V và 60 V, bao gồm năng lượng TVS và fuse coordination.
- Coil relay và tải cảm ở DO1–DO3: flyback/clamp energy, thời gian nhả và Vce/Vds stress.
- RC filter ADC: settling time so với source impedance/ADC sampling của ESP32.
- INA240: common-mode range, gain, full-scale, bandwidth, output swing và sai số do shunt/tolerance.

LTspice/ngspice hữu ích cho transient, clamp, buck và filter; nó không mô phỏng chính xác EMI của layout nếu không có parasitic/extracted model.

---

## 15. Tài liệu và thiết kế tham khảo

### Tiêu chuẩn/hướng dẫn chính

- [IPC Design Standards](https://www.electronics.org/ipc-design-standards)
- [IPC Document Revision Table](https://www.electronics.org/ipc-document-revision-table) — kiểm tra revision hiện hành của IPC-2221/2222; IPC-2141 và IPC-2152 được IPC liệt kê là không còn duy trì.
- [IEC 60664-1:2020 + AMD1:2025](https://webstore.iec.ch/en/publication/107319) — nguyên tắc insulation coordination, creepage và clearance.
- [Espressif ESP32 Hardware Design Guidelines](https://documentation.espressif.com/esp-hardware-design-guidelines/en/latest/esp32/index.html)
- [TI LV14340 Datasheet](https://www.ti.com/lit/gpn/LV14340)
- [TI INA240 Datasheet](https://www.ti.com/lit/ds/symlink/ina240.pdf)
- [USB 2.0 Specification](https://www.usb.org/document-library/usb-20-specification)
- [WCH CH340 Datasheet](https://www.wch-ic.com/downloads/CH340DS1_PDF.html)
- [Analog Devices RS-485 Cable Specification Guide](https://www.analog.com/en/resources/technical-articles/rs485-cable-specification-guide--maxim-integrated.html)

### Dự án mở để tham khảo cách tổ chức rule/layout

- [LibreSolar BMS C1 — KiCad project](https://github.com/LibreSolar/bms-c1/blob/0ca09706f49906bdc73f6ccf99635de349d47474/kicad/bms-c1.kicad_pro)
- [VESC BLDC hardware — KiCad PCB](https://github.com/vedderb/bldc-hardware/blob/f1c65014d0caab5d99d888fc3025377861ac6ae2/design/BLDC_4.kicad_pcb)
- [OLIMEX ESP32-EVB — KiCad project](https://github.com/OLIMEX/ESP32-EVB/blob/a3ec2f448109cb8f35ce7cb21a027bb7c837ab61/HARDWARE/REV-L/ESP32-EVB_Rev_L.kicad_pro)
- [OLIMEX ESP32-EVB hardware revision history](https://github.com/OLIMEX/ESP32-EVB/blob/a3ec2f448109cb8f35ce7cb21a027bb7c837ab61/HARDWARE/README.md)

Các project mở chỉ là evidence tham khảo về cách tổ chức, không phải bằng chứng thiết kế này đạt 20 A, EMC hoặc an toàn.

---

## 16. Điều kiện để chốt routing gate

Có thể bắt đầu routing chính thức khi thỏa tất cả điều kiện sau:

1. Schematic/ERC đã xử lý bốn vấn đề ở mục 3.
2. Kiến trúc GND/return 20 A đã được người thiết kế phê duyệt.
3. Tất cả net critical đã có tên và class hiệu lực được kiểm tra trong PCB Editor.
4. Placement của chuỗi 20 A, buck, INA240, ESP32 antenna và connector đã được review.
5. Có stackup sơ bộ của nhà sản xuất; DP Width/Gap USB được cập nhật hoặc đánh dấu rõ là chưa chốt.
6. Rule Area/Custom Rules cho 20 A, Kelvin, `BUCK_SW` và anten đã được tạo.

**Khuyến nghị thiết kế hiện tại:** *conditional pass để chuyển sang placement/routing thử nghiệm*, với điều kiện phải sửa U9 thermal pad, CH340 V3, hai net LED UART và chốt topology GND trước khi phát hành PCB.
