# hardware/libraries/

Thư viện dùng chung của dự án — symbol, footprint và mô hình 3D, là nguồn duy nhất (single source of truth) cho mọi thiết kế board.

## Cấu trúc

| Thư mục | Chức năng |
|---|---|
| `symbols/` | Symbol schematic (`.kicad_sym`) |
| `footprints/` | Footprint PCB (`.pretty/`) |
| `3d-models/` | Mô hình 3D (`.step`/`.stp`) |

> [!NOTE]
> Thư mục này được duy trì trên nhánh `develop`. Các nhánh thiết kế merge `develop` để nhận bản cập nhật thư viện mới nhất.