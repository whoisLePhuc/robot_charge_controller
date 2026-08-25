# Quy trình phát triển

Tài liệu này quy định cách tổ chức repository và luồng thay đổi cho Robot Charge Controller. Hai phương án phần cứng cùng tồn tại trong cây thư mục; nhánh Git chỉ dùng để cô lập thay đổi trong thời gian ngắn.

## 1. Mô hình repository

~~~text
main                         baseline có thể tái tạo
└── develop                  nhánh tích hợp tùy chọn
    ├── feature/<name>       tính năng hoặc artifact mới
    ├── fix/<name>           sửa lỗi
    └── docs/<name>          thay đổi tài liệu

hardware/
├── One_Board_Design/        thiết kế tích hợp một PCB
├── Split_Board_Design/      thiết kế Control Board + Relay Board
├── libraries/               thư viện KiCad dùng chung
└── templates/               template dùng chung
~~~

`design/one-board` và `design/split-board` cũ được giữ nguyên trong giai đoạn chuyển đổi để đối chiếu lịch sử. Sau khi integration baseline được review và merge, mọi phát triển mới dùng nhánh ngắn hạn từ baseline phù hợp.

## 2. Vai trò của nhánh

### `main`

- Chứa toàn bộ artifact cần thiết để tái tạo baseline đã chọn, bao gồm các phương án phần cứng được hỗ trợ và thư viện dùng chung.
- Không đồng nghĩa với chứng nhận an toàn hoặc cho phép sản xuất; trạng thái release phải dựa trên hồ sơ kiểm chứng và quyết định của người có thẩm quyền.
- Chỉ nhận thay đổi qua pull request đã review.

### `develop` — tùy chọn

- Dùng làm nhánh tích hợp khi nhiều thay đổi đang phát triển song song.
- Phải được đồng bộ thường xuyên với `main` và không được trở thành nơi duy nhất chứa thư viện hoặc artifact cần cho việc tái tạo thiết kế.
- Có thể bỏ qua đối với thay đổi nhỏ bằng cách tạo nhánh ngắn hạn trực tiếp từ `main`.

### Nhánh thay đổi ngắn hạn

- `feature/<name>` cho chức năng hoặc artifact mới.
- `fix/<name>` cho sửa lỗi.
- `docs/<name>` cho tài liệu.
- Nhánh phải được xóa sau khi merge và không được dùng làm nơi lưu duy nhất của một phương án sản phẩm.

## 3. Luồng thay đổi

1. Chọn baseline phù hợp (`main` hoặc `develop`) và cập nhật từ remote.
2. Tạo nhánh ngắn hạn với tên mô tả đúng phạm vi.
3. Chỉ sửa các artifact thuộc phạm vi thay đổi; file KiCad phải được chỉnh qua Konnect.
4. Chạy kiểm tra repository:

   ~~~sh
   python tools/check_repository.py
   ~~~

5. Với thay đổi KiCad, chạy ERC/DRC trên từng project bị ảnh hưởng và lưu bằng chứng theo revision.
6. Review diff, mở pull request và ghi rõ kiểm tra đã chạy cùng các rủi ro còn mở.
7. Merge sau khi review; xóa nhánh thay đổi khi không còn cần thiết.

## 4. Quản lý hai phương án phần cứng

- `hardware/One_Board_Design/` và `hardware/Split_Board_Design/` cùng tồn tại trên baseline.
- Mỗi project KiCad phải tự mở được từ thư mục của nó và dùng thư viện chung tại `hardware/libraries/` qua đường dẫn portable.
- Thay đổi thư viện dùng chung phải được kiểm tra với mọi project sử dụng thư viện đó.
- Split-Board phải có interface contract được quản lý revision trước khi Control Board hoặc Relay Board phụ thuộc vào pinout hay mức điện áp cụ thể.
- Tài liệu trạng thái phải phân biệt rõ “artifact tồn tại”, “tool đã chạy”, “vi phạm đã được xử lý” và “yêu cầu đã được kiểm chứng”.

## 5. Quality gates

| Gate | Công cụ hoặc bằng chứng | Điều kiện tối thiểu trước merge |
|---|---|---|
| Repository | `python tools/check_repository.py` | PASS |
| Markdown | Link nội bộ và encoding | Không có link hỏng hoặc mojibake |
| KiCad source integrity | Konnect workflow | Không chỉnh tay file KiCad |
| ERC | KiCad 10 `kicad-cli sch erc` | Không có error chưa được xử lý; warning đã review |
| DRC | KiCad 10 `kicad-cli pcb drc` | Không có short, unconnected hoặc error chưa được xử lý |
| Shared libraries | Mở project và render/export liên quan | Không thiếu symbol, footprint hoặc 3D model cần thiết |
| Engineering review | Findings và verification records | Phạm vi và rủi ro còn mở được ghi rõ |

Tool chạy thành công không đồng nghĩa với yêu cầu đã được kiểm chứng hoặc thiết kế được phép phát hành.

## 6. Quy ước commit

Sử dụng thông điệp ngữ nghĩa, ví dụ:

- `feat(hardware): add control-board interface scaffold`
- `fix(hardware): resolve relay-board clearance violation`
- `docs: update repository workflow`
- `chore(repo): normalize documentation paths`

Không gộp thay đổi tài liệu, thư viện và schematic không liên quan vào cùng một commit.

## 7. Baseline và release

Một baseline phần cứng phải xác định rõ:

- Commit hoặc tag chính xác.
- Biến thể board áp dụng.
- Phiên bản KiCad và stack-up chế tạo.
- BOM, schematic, PCB, calculation và verification records tương ứng.
- ERC/DRC cùng disposition của từng finding.
- Người có thẩm quyền quyết định release.

Chỉ tạo release tag sau khi các artifact trên đồng bộ và review hoàn tất.
