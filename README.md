# Hoạt hình CS3

Repo CloudStream gồm 5 extension đang được liệt kê: HH3D, YanHH3D, Anime47, AnimeHay và HHTQ.

Thêm URL sau vào CloudStream → Settings → Extensions → Add repository:

`https://raw.githubusercontent.com/taigametaiwan/hoathinh-cs3/main/repo.json`

## Tự cập nhật plugin

Các file `.cs3` vẫn đặt **ngay thư mục gốc** của repo. Khi thêm hoặc cập nhật file `.cs3` trên nhánh `main`, GitHub Actions sẽ đọc `manifest.json` trong gói và cập nhật `plugins.json` (phiên bản, dung lượng, SHA-256, URL tải). Addon mới được thêm vào cuối danh sách với loại `Anime` và ngôn ngữ `vi`. Các mục hiện có giữ nguyên tên hiển thị, mô tả và thông tin khác.

`HHTQProvider.cs3` vốn nằm trong repo nhưng không có trong `plugins.json`, nên được giữ ngoài danh sách qua `catalog-config.json`. Muốn đưa gói đó vào danh sách, xóa tên file khỏi `exclude` rồi commit; workflow sẽ tự thêm.

Kiểm tra metadata trước khi push: `python scripts/generate_catalog.py --check`. Tạo lại: `python scripts/generate_catalog.py`.
