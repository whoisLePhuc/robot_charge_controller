# hardware/

Thiết kế phần cứng — schematic, PCB và thư viện linh kiện cho Robot Charge Controller.

## Cấu trúc

| Thư mục | Chức năng |
|---|---|
| `libraries/` | Thư viện symbol, footprint và mô hình 3D của dự án |
| `templates/` | Template KiCad dùng chung |

> [!NOTE]
> Các thiết kế board cụ thể được phát triển trên các nhánh riêng và sẽ được
> đặt trực tiếp trong `hardware/`:
> - `design/one-board`   → `hardware/One_Board_Design/`
> - `design/split-board` → `hardware/Split_Board_Design/`
>
> Thư viện dùng chung (`libraries/`) được duy trì trên nhánh `develop`.