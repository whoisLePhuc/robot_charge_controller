## 1. Thông số thiết kế

| Thông số | Ký hiệu | Giá trị |
|---|:---:|---:|
| IC đo dòng | — | INA240A2DR |
| Hệ số khuếch đại | $G$ | $50\ V/V$ |
| Điện trở shunt (mỗi điện trở) | $R_{17,i}$ | $2\ m\Omega \times 3$ (song song) |
| Điện trở shunt tương đương | $R_S$ | $0{,}6667\ m\Omega$ |
| Nguồn cấp INA240 | $V_S$ | $3{,}3\ V$ |
| Điện áp tại REF1 | $V_{REF1}$ | $3{,}3\ V$ |
| Điện áp tại REF2 | $V_{REF2}$ | $0\ V$ |
| Độ phân giải ADC giả định | — | 12 bit |
| Giá trị ADC lớn nhất | $ADC_{FS}$ | 4095 |

**Cập nhật so với bản trước:** R17 không còn là một điện trở $1{,}8\ m\Omega$ duy nhất, mà là **3 điện trở $2\ m\Omega$ mắc song song**. Điện trở tương đương:

$$\frac{1}{R_S} = \frac{1}{2\ m\Omega} + \frac{1}{2\ m\Omega} + \frac{1}{2\ m\Omega} = \frac{3}{2\ m\Omega}$$

$$\boxed{R_S = \frac{2\ m\Omega}{3} \approx 0{,}6667\ m\Omega = 0{,}0006667\ \Omega}$$

Toàn bộ phần tính toán bên dưới dùng giá trị $R_S = 0{,}6667\ m\Omega$ này thay cho $1{,}8\ m\Omega$ ở bản tính trước. Như sẽ thấy ở Mục 6 và 9, việc giảm $R_S$ (thay vì giữ nguyên $1{,}8\ m\Omega$) chính là cách khắc phục vấn đề bão hòa đã phát hiện khi dùng INA240A2 (gain 50 V/V) — gần khớp với khuyến nghị "giảm $R_S$ xuống khoảng $0{,}72\ m\Omega$" đã nêu ở bản tính trước.

## 2. Điện áp tham chiếu đầu ra

Điện áp tham chiếu tương đương tại đầu ra được tính bằng:

$$V_{REF} = \frac{V_{REF1} + V_{REF2}}{2}$$

Thay số:

$$V_{REF} = \frac{3{,}3 + 0}{2} = 1{,}65\ V$$

Do đó, khi dòng qua R17 bằng 0 A:

$$\boxed{V_{OUT}(0\ A) = 1{,}65\ V}$$

*(Không đổi so với bản trước — $V_{REF}$ chỉ phụ thuộc REF1/REF2, không liên quan tới giá trị shunt.)*

## 3. Điện áp vi sai trên điện trở shunt

Điện áp trên mạng shunt (3 điện trở song song) được tính theo định luật Ohm với điện trở tương đương:

$$V_{SHUNT} = V_{IN+} - V_{IN-} = I \times R_S$$

Với $R_S = 0{,}6667\ m\Omega = 0{,}0006667\ \Omega$, suy ra:

$$V_{SHUNT} = 0{,}0006667\,I$$

Trong đó $I$ tính bằng ampere và $V_{SHUNT}$ tính bằng volt. Ví dụ tại dòng 20 A:

$$V_{SHUNT} = 20 \times 0{,}0006667 = 0{,}013333\ V \approx 13{,}33\ mV$$

*(So với bản trước — $R_S = 1{,}8\ m\Omega$ cho $V_{SHUNT} = 36\ mV$ tại 20 A — điện áp shunt giờ nhỏ hơn khoảng 2,7 lần vì $R_S$ giảm từ $1{,}8$ xuống $0{,}6667\ m\Omega$.)*

## 4. Công thức điện áp đầu ra INA240A2

Điện áp đầu ra lý tưởng của INA240 được xác định bởi:

$$V_{OUT} = V_{REF} + G(V_{IN+} - V_{IN-})$$

Thay $V_{IN+} - V_{IN-} = I \times R_S$:

$$V_{OUT} = V_{REF} + G \times I \times R_S$$

Thay các giá trị của thiết kế ($G = 50$, $R_S = 0{,}6667\ m\Omega$):

$$V_{OUT} = 1{,}65 + 50 \times I \times 0{,}0006667$$

Suy ra công thức rút gọn:

$$\boxed{V_{OUT} = 1{,}65 + 0{,}03333\,I}$$

Trong đó:

- $I$ tính bằng ampere.
- $V_{OUT}$ tính bằng volt.
- Độ nhạy của mạch đo là **33,33 mV/A** (đúng bằng $1/30\ V/A$) — gần với độ nhạy $36\ mV/A$ của thiết kế gốc dùng INA241A2, và thấp hơn nhiều so với $90\ mV/A$ khi dùng INA240A2 với $R_S = 1{,}8\ m\Omega$ (bản tính trước).

## 5. Quy ước chiều dòng điện

Nếu kết nối:

- IN+ ở phía nguồn.
- IN− ở phía tải.

Thì:

| Trạng thái | Quan hệ đầu ra |
|---|---:|
| Dòng từ nguồn sang tải | $V_{OUT} > 1{,}65\ V$ |
| Không có dòng | $V_{OUT} \approx 1{,}65\ V$ |
| Dòng từ tải về nguồn | $V_{OUT} < 1{,}65\ V$ |

Nếu đảo IN+ và IN−, dấu của thành phần dòng trong công thức cũng bị đảo.

## 6. Bảng điện áp đầu ra theo dòng điện

Bảng dưới dùng cùng các mốc dòng điện như các bản tính trước (0 A, ±20 A liên tục, ±27,8 A ngưỡng LT4356, ±31,4 A ngưỡng cao nhất).

| Dòng $I$ | $V_{SHUNT}$ | $G \times V_{SHUNT}$ | $V_{OUT}$ | Trạng thái |
|---:|---:|---:|---:|:---|
| $-31{,}4\ A$ | $-20{,}93\ mV$ | $-1{,}0467\ V$ | $0{,}603\ V$ | Hợp lệ |
| $-27{,}8\ A$ | $-18{,}53\ mV$ | $-0{,}9267\ V$ | $0{,}723\ V$ | Hợp lệ |
| $-20\ A$ | $-13{,}33\ mV$ | $-0{,}6667\ V$ | $0{,}983\ V$ | Hợp lệ |
| $-10\ A$ | $-6{,}67\ mV$ | $-0{,}3333\ V$ | $1{,}317\ V$ | Hợp lệ |
| $0\ A$ | $0\ mV$ | $0\ V$ | $1{,}650\ V$ | Hợp lệ |
| $+10\ A$ | $+6{,}67\ mV$ | $+0{,}3333\ V$ | $1{,}983\ V$ | Hợp lệ |
| $+20\ A$ | $+13{,}33\ mV$ | $+0{,}6667\ V$ | $2{,}317\ V$ | Hợp lệ |
| $+27{,}8\ A$ | $+18{,}53\ mV$ | $+0{,}9267\ V$ | $2{,}577\ V$ | Hợp lệ |
| $+31{,}4\ A$ | $+20{,}93\ mV$ | $+1{,}0467\ V$ | $2{,}697\ V$ | Hợp lệ |

**Phát hiện quan trọng — vấn đề bão hòa đã được khắc phục:** với $R_S = 0{,}6667\ m\Omega$ (3×2 mΩ song song), toàn bộ dải dòng $-31{,}4\ A$ đến $+31{,}4\ A$ cho $V_{OUT}$ nằm gọn trong khoảng $0{,}60\ V$ đến $2{,}70\ V$ — **không còn điểm nào bị bão hòa**, khác hẳn với bản tính trước (dùng $R_S = 1{,}8\ m\Omega$ nguyên bản) vốn đã kẹp ngay từ $\pm 20\ A$. Ngoài ra dải này còn khá nhiều margin so với rail $0\ V$/$3{,}3\ V$, xem phân tích định lượng ở Mục 9.

Tại dòng hoạt động liên tục 20 A:

$$\boxed{V_{OUT}(20\ A) = 2{,}317\ V}$$

Tại ngưỡng giới hạn dòng danh định của LT4356, xấp xỉ 27,8 A:

$$\boxed{V_{OUT}(27{,}8\ A) \approx 2{,}577\ V}$$

Tại ngưỡng dòng cao nhất dự kiến, xấp xỉ 31,4 A:

$$\boxed{V_{OUT}(31{,}4\ A) \approx 2{,}697\ V}$$

## 7. Tính dòng điện từ điện áp đầu ra

Từ công thức:

$$V_{OUT} = 1{,}65 + 0{,}03333\,I$$

Suy ra:

$$\boxed{I = \frac{V_{OUT} - 1{,}65}{0{,}03333}}$$

Ví dụ, khi ADC đo được $V_{OUT} = 2{,}317\ V$:

$$I = \frac{2{,}317 - 1{,}65}{0{,}03333} \approx 20\ A$$

Khi ADC đo được $V_{OUT} = 0{,}983\ V$:

$$I = \frac{0{,}983 - 1{,}65}{0{,}03333} \approx -20\ A$$

## 8. Quy đổi sang ADC 12 bit

Với ADC 12 bit và điện áp toàn thang lý tưởng bằng 3,3 V:

$$ADC = \frac{V_{OUT}}{3{,}3} \times 4095 \qquad\Longleftrightarrow\qquad V_{OUT} = \frac{ADC}{4095} \times 3{,}3$$

Thay vào công thức tính dòng:

$$\boxed{I = \frac{\left(\dfrac{ADC}{4095} \times 3{,}3\right) - 1{,}65}{0{,}03333}}$$

Có thể rút gọn thành:

$$\boxed{I \approx 0{,}02418\,(ADC - 2047{,}5)}$$

Theo mô hình lý tưởng, độ phân giải dòng điện trên mỗi LSB là:

$$\Delta I_{LSB} = \frac{3{,}3/4095}{0{,}03333} \approx 0{,}02418\ A$$

$$\boxed{\Delta I_{LSB} \approx 24{,}18\ mA/LSB}$$

*(Thô hơn khoảng 2,7 lần so với phương án dùng $R_S = 1{,}8\ m\Omega$ (8,95 mA/LSB) — nhưng phương án đó bị bão hòa và không dùng được; so với thiết kế gốc INA241A2 (22,4 mA/LSB), độ phân giải ở đây tương đương, hơi thô hơn một chút.)*

### Bảng giá trị ADC lý tưởng theo dòng điện

| Dòng $I$ | $V_{OUT}$ | Giá trị ADC lý tưởng |
|---:|---:|---:|
| $-31{,}4\ A$ | $0{,}603\ V$ | $\approx 749$ |
| $-27{,}8\ A$ | $0{,}723\ V$ | $\approx 898$ |
| $-20\ A$ | $0{,}983\ V$ | $\approx 1220$ |
| $-10\ A$ | $1{,}317\ V$ | $\approx 1634$ |
| $0\ A$ | $1{,}650\ V$ | $\approx 2048$ |
| $+10\ A$ | $1{,}983\ V$ | $\approx 2461$ |
| $+20\ A$ | $2{,}317\ V$ | $\approx 2875$ |
| $+27{,}8\ A$ | $2{,}577\ V$ | $\approx 3197$ |
| $+31{,}4\ A$ | $2{,}697\ V$ | $\approx 3346$ |

Toàn bộ giá trị ADC đều nằm gọn trong dải $0$–$4095$ với nhiều margin ở cả hai đầu — khác hẳn bảng tương ứng ở bản tính trước, nơi các dòng $\geq 20\ A$ hoặc $\leq -20\ A$ cho ra ADC âm hoặc vượt 4095 (vô nghĩa về vật lý).

## 9. Dải dòng tuyến tính gần đúng

Đầu ra INA240 không thể đạt hoàn toàn tới 0 V hoặc $V_S$. Áp dụng cùng giả định bảo thủ như các bản tính trước:

$$0{,}02\ V \lesssim V_{OUT} \lesssim 3{,}10\ V$$

**Giới hạn dòng âm**

$$I_{MIN} = \frac{0{,}02 - 1{,}65}{0{,}03333} \approx -48{,}9\ A$$

**Giới hạn dòng dương**

$$I_{MAX} = \frac{3{,}10 - 1{,}65}{0{,}03333} \approx +43{,}5\ A$$

Suy ra dải dòng tuyến tính ước lượng:

$$\boxed{-48{,}9\ A \lesssim I \lesssim +43{,}5\ A}$$

**Đối chiếu với yêu cầu thiết kế:** dải dòng cần đo của hệ thống là $-20\ A$ đến khoảng $+31{,}4\ A$. Dải khả dụng $-48{,}9\ A \lesssim I \lesssim +43{,}5\ A$ **phủ kín toàn bộ dải yêu cầu với margin rộng** ở cả hai đầu — margin âm $\approx 28{,}9\ A$, margin dương $\approx 12{,}1\ A$. Đây thậm chí còn rộng hơn dải của thiết kế gốc dùng INA241A2 ($-45{,}3\ A$ đến $+40{,}3\ A$).

$$\boxed{\text{Cấu hình INA240A2DR} + 3\times2\ m\Omega \text{ song song phủ đủ dải dòng yêu cầu, có margin.}}$$

## 10. Sai số và lưu ý bố trí phần cứng

Kết quả tính toán phía trên là giá trị lý tưởng. Sai số đo thực tế còn phụ thuộc vào:

- Sai số và TCR của từng điện trở shunt, và **sai số dung sai giữa 3 điện trở** (xem lưu ý bố trí bên dưới).
- Điện áp offset đầu vào của INA240A2: tối đa $\pm 25\ \mu V$ theo datasheet (trôi $2{,}5\ ppm/^\circ C$ gain, $250\ nV/^\circ C$ offset).
- Sai số hệ số khuếch đại của INA240A2: tối đa $\pm 0{,}2\%$.
- Sai số điện áp tạo bởi REF1 và REF2.
- Nhiễu trên nguồn 3,3 V.
- Sai số, độ phi tuyến và suy hao do mạch RC ở ADC ESP32.
- Điện trở đường mạch và chất lượng kết nối Kelvin — **với mạng 3 điện trở song song, điểm đặt Kelvin sense càng quan trọng hơn** (xem bên dưới).
- Nhiệt độ của shunt, INA240 và PCB.
- Dòng phân cực đầu vào (input bias current) của INA240, khoảng $90\ \mu A$ theo datasheet, do kiến trúc current-output đặc trưng của họ INA24x. Nếu sau này thêm điện trở lọc nối tiếp trên IN+/IN−, bắt buộc dùng giá trị đối xứng ở hai chân.

**Lưu ý riêng cho mạng 3 điện trở song song:**

- **Đặt hai điểm Kelvin sense (IN+/IN−) tại hai node chung** nơi cả 3 điện trở đấu vào, không đặt tại chân riêng của một điện trở cụ thể. Khi đó điện áp đo được luôn đúng bằng $I_{total} \times R_S$ bất kể dòng có chia đều tuyệt đối giữa 3 nhánh hay không — sai lệch dung sai giữa 3 điện trở **không** làm sai kết quả đo dòng tổng, miễn là Kelvin sense đặt đúng vị trí.
- Tuy nhiên, sai lệch dung sai (và chênh lệch nhiệt độ) giữa 3 điện trở **có** ảnh hưởng tới cách dòng phân bố giữa chúng: điện trở nào có giá trị thấp hơn sẽ gánh dòng lớn hơn tương ứng, nóng hơn các điện trở còn lại. Nên chọn linh kiện cùng lô/cùng dung sai (ví dụ ±1%) và cùng hệ số nhiệt.
- **Bố trí PCB đối xứng**: chiều dài, độ rộng và độ dày đồng dẫn từ node chung tới từng điện trở nên bằng nhau, để trở kháng đường mạch không làm lệch thêm sự phân bố dòng ngoài sai số bản thân điện trở. Nên đặt 3 điện trở đối xứng nhau về mặt nhiệt (khoảng cách đều, không có điện trở nào ở vị trí tản nhiệt kém hơn hẳn hai cái kia).
- **Công suất tiêu tán** — với dòng phân bố đều (giả định lý tưởng), mỗi điện trở chỉ chịu khoảng 1/3 tổng công suất, và tổng công suất bản thân đã giảm do $R_S$ nhỏ hơn:

| Dòng $I$ | $P_{total} = I^2 R_S$ | $P$ mỗi điện trở (chia đều) | So với 1 điện trở $1{,}8\ m\Omega$ duy nhất |
|---:|---:|---:|---:|
| $20\ A$ | $0{,}267\ W$ | $\approx 0{,}089\ W$ | $0{,}720\ W$ |
| $27{,}8\ A$ | $0{,}515\ W$ | $\approx 0{,}172\ W$ | $1{,}391\ W$ |
| $31{,}4\ A$ | $0{,}657\ W$ | $\approx 0{,}219\ W$ | $1{,}775\ W$ |

Nhờ vậy, ứng suất nhiệt trên mỗi điện trở giảm đáng kể (khoảng 8 lần tại 31,4 A) so với phương án dùng một điện trở $1{,}8\ m\Omega$ duy nhất — có lợi cho độ trôi nhiệt và tuổi thọ linh kiện, nhưng chỉ đúng nếu dòng thực sự chia đều; nên vẫn kiểm tra bằng đo nhiệt thực tế (camera nhiệt hoặc đo $V$ rơi trên từng điện trở) sau khi lắp.

Để giảm sai số nói chung:

- Đặt tụ bypass 100 nF sát chân nguồn INA240.
- Đặt bộ lọc RC giữa OUT và ADC, ví dụ 1 kΩ nối tiếp và 10 nF xuống GND (tần số cắt $\approx 15{,}9\ kHz$, thấp hơn nhiều so với băng thông 400 kHz của INA240).
- Lấy nhiều mẫu ADC và lọc trung bình trong firmware.
- Hiệu chuẩn zero-current sau khi hệ thống ổn định nhiệt.
- Nếu có thể, dùng điện áp tham chiếu ADC đã hiệu chuẩn thay vì mặc định chính xác 3,3 V.

## 11. So sánh với INA241A2IDDFR (thiết kế gốc)

| Thông số | INA241A2IDDFR ($R_S=1{,}8\ m\Omega$, gốc) | INA240A2DR ($R_S=0{,}6667\ m\Omega$, tài liệu này) |
|---|---:|---:|
| Gain | $20\ V/V$ | $50\ V/V$ |
| Độ nhạy | $36\ mV/A$ | $33{,}33\ mV/A$ |
| Dải dòng tuyến tính ước lượng | $-45{,}3\ A$ đến $+40{,}3\ A$ | $-48{,}9\ A$ đến $+43{,}5\ A$ |
| Độ phân giải ADC | $22{,}4\ mA/LSB$ | $24{,}18\ mA/LSB$ |
| Dải nguồn cấp | $2{,}7\text{–}20\ V$ | $2{,}7\text{–}5{,}5\ V$ |
| Common-mode input | $-5\ V$ đến $110\ V$ (hoạt động) | $-4\ V$ đến $80\ V$ |
| Băng thông ($-3\ dB$) | $1{,}1\ MHz$ | $400\ kHz$ |
| Đóng gói | DDF — SOT-23-THN, 8 chân | D — SOIC-8 |

Với $R_S = 0{,}6667\ m\Omega$ (3×2 mΩ song song), INA240A2DR cho **độ nhạy và dải đo gần tương đương thiết kế gốc**, khắc phục hoàn toàn vấn đề bão hòa nêu ở bản tính trước (dùng nguyên $R_S = 1{,}8\ m\Omega$). Hai điểm vẫn cần xác nhận trước khi chốt thiết kế, không liên quan tới giá trị shunt:

1. **Common-mode input:** INA240 chịu $-4\ V$ đến $+80\ V$, hẹp hơn INA241 ($-5\ V$ đến $110\ V$). Cần xác nhận điện áp common-mode thực tế tại hai điểm Kelvin của R17 trong ứng dụng — đặc biệt nếu shunt này nằm trên cùng đường bus HV đã được xét trong các tài liệu review bảo vệ đầu vào (LT4356, TVS clamp) của dự án — có nằm trong $\pm 80\ V$ ở mọi điều kiện kể cả transient hay không.
2. **Đóng gói khác nhau:** SOIC-8 (D) so với SOT-23-THN (DDF) — không lắp thay thế trực tiếp (drop-in), cần cập nhật footprint PCB nếu chuyển từ INA241A2IDDFR sang INA240A2DR.

## 12. Tài liệu tham khảo

- Texas Instruments — INA240 datasheet
- Texas Instruments — INA240 product page
- Texas Instruments — INA241A product page (dùng để đối chiếu so sánh ở Mục 11)