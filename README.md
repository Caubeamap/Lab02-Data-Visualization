# Dự án Trực quan hóa Dữ liệu - Lab 02
## Phân tích Dữ liệu World Development Indicators (WDI)

Chào mừng bạn đến với kho lưu trữ (repository) dự án Lab 02 của **Nhóm 05** - Môn học **Trực quan hóa Dữ liệu**.

### 👥 Thành viên nhóm
* **23120237 - Lê Lâm Trí Đức** (Nhóm trưởng)
* **23120189 - Hoàng Quốc Việt**
* **23120190 - Nguyễn Lê Thế Vinh**
* **23120202 - Phạm Quang Vinh**

---

### 📂 Cấu trúc thư mục dự án đề xuất
Dự án được tổ chức theo cấu trúc chuẩn dưới đây:
```text
Lab2_TQH/
├── code/                      # Thư mục chứa mã nguồn tiền xử lý dữ liệu
│   └── Nhom05_TienXuLy.ipynb  # Jupyter Notebook xử lý và làm sạch dữ liệu
├── dashboard/                 # Thư mục chứa file thiết kế Tableau
│   └── Nhom05_Dashboard.twbx  # File đóng gói Tableau Dashboard (Tableau Packaged Workbook)
├── report/                    # Báo cáo và tài liệu đi kèm
│   ├── Nhom05_BaoCao.pdf      # Báo cáo chi tiết (PDF)
│   └── Nhom05_Slide.pdf       # Slide thuyết trình (nếu có)
├── README.md                  # Hướng dẫn chung về dự án
├── .gitignore                 # Cấu hình bỏ qua các file dung lượng lớn hoặc file tạm
├── Lab 02.pdf                 # Đề bài chi tiết của bài tập Lab 2
└── PhanChiaCongViec_Nhom05.md # Kế hoạch & Phân chia công việc chi tiết của Nhóm 05
```

---

### 📊 Dữ liệu sử dụng (World Development Indicators - WDI)
Dự án sử dụng bộ dữ liệu **World Development Indicators (WDI)** được cung cấp bởi Ngân hàng Thế giới (World Bank).
* **Lưu ý quan trọng**: Do file dữ liệu gốc `WDIEXCEL.xlsx` có dung lượng rất lớn (~80MB), file này đã được thêm vào `.gitignore` và **KHÔNG** được đẩy lên GitHub để tránh làm nặng repository.
* **Hướng dẫn cài đặt dữ liệu**:
  1. Nhóm trưởng hoặc các thành viên chia sẻ file dữ liệu gốc `WDIEXCEL.xlsx` cho nhau thông qua kênh riêng (Google Drive, USB, v.v.).
  2. Tải và copy file `WDIEXCEL.xlsx` vào trực tiếp thư mục gốc `Lab2_TQH/` trên máy cá nhân của bạn để các mã nguồn tiền xử lý dữ liệu có thể hoạt động bình thường.

---

### 🛠️ Quy trình triển khai dự án

1. **Bước 1: Tiền xử lý dữ liệu (Python)**
   * Xem kế hoạch xử lý dữ liệu chi tiết tại [PhanChiaCongViec_Nhom05.md](file:///d:/Lab2_TQH/PhanChiaCongViec_Nhom05.md#quy-ước-xử-lý-dữ-liệu-chung).
   * Mã nguồn tiền xử lý nằm tại thư mục `code/`. Các chỉ số cần được lọc, xử lý giá trị khuyết (Imputation/Forward fill/Backward fill), và chuẩn hóa tên quốc gia trước khi đưa vào Tableau.

2. **Bước 2: Thiết kế Dashboard (Tableau)**
   * Import dữ liệu đã sạch (từ file `.csv` kết quả sau khi chạy notebook tiền xử lý) vào Tableau.
   * Thiết kế các biểu đồ trực quan động, sử dụng Storytelling, thiết lập các bộ lọc (Filters) và các Action tương tác giữa các biểu đồ.
   * File sản phẩm cuối cùng phải được lưu dưới dạng `.twbx` (Tableau Packaged Workbook) đặt trong thư mục `dashboard/`.

3. **Bước 3: Viết Báo cáo & Quay Video thuyết trình**
   * Hoàn thiện báo cáo PDF theo đúng cấu trúc yêu cầu của đề bài tại thư mục `report/`.
   * Thực hiện quay 2 video thuyết trình (Video 1 giới thiệu Dashboard, Video 2 phân tích chuyên sâu các phát hiện) và upload lên nền tảng chia sẻ (Google Drive/YouTube) theo phân công.

---

### 📅 Kế hoạch & Tiến độ chi tiết
Chi tiết về phân công nhiệm vụ, thời hạn (Deadline: **02/06/2026**) và tiêu chuẩn nghiệm thu của từng thành viên, vui lòng tham khảo file:
👉 **[Bảng phân chia công việc Nhóm 05](file:///d:/Lab2_TQH/PhanChiaCongViec_Nhom05.md)**
