# Color Palette & Formatting Cho Tableau

**Phụ trách:** Hoàng Quốc Việt  
**Phạm vi:** áp dụng nhất quán cho toàn bộ dashboard nhóm 05.

## 1. Palette theo chủ đề

| Chủ đề | Màu chính | Hex | Ghi chú |
|---|---:|---|---|
| Kinh tế | Xanh dương | `#2F6B9A` | Tăng trưởng, GDP, thu nhập |
| Giáo dục | Xanh lá | `#2E7D59` | Enrollment, literacy, education expenditure |
| Sức khỏe & dân số | Đỏ trầm | `#B24A4A` | Mortality, health expenditure, population |
| Môi trường | Xanh teal | `#2A8C8C` | CO2, renewable energy, forest |
| Trung tính | Xám đậm | `#4A4A4A` | Text, gridline, label |
| Nền phụ | Xám rất nhạt | `#F4F6F7` | Dashboard background hoặc band nhẹ |

## 2. Palette theo vùng địa lý

Khi cần tô màu theo `Region`, dùng palette cố định:

| Region | Hex |
|---|---|
| East Asia & Pacific | `#2F6B9A` |
| Europe & Central Asia | `#6A8E3F` |
| Latin America & Caribbean | `#C47A2C` |
| Middle East & North Africa | `#8E5A9F` |
| North America | `#4A4A4A` |
| South Asia | `#B24A4A` |
| Sub-Saharan Africa | `#2A8C8C` |

## 3. Quy ước trình bày

- Font: dùng font mặc định của Tableau hoặc Arial, tránh nhiều font trong cùng dashboard.
- Tiêu đề worksheet: ngắn, mô tả trực tiếp nội dung biểu đồ.
- Axis title: phải ghi rõ đơn vị, ví dụ `%`, `% of GDP`, `years`.
- Tooltip: luôn gồm Country/Region, Year và giá trị measure chính.
- Null values: lọc null theo từng worksheet; không thay null bằng 0 nếu không có lý do dữ liệu.
- Gridlines: giảm độ đậm để biểu đồ dễ đọc; ưu tiên label và tooltip thay vì quá nhiều text trên chart.
- Dashboard: đặt biểu đồ tổng quan trước, chi tiết sau; filter dùng chung đặt ở cạnh phải hoặc hàng trên.
