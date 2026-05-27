# Đặc tả Tableau — Mục tiêu Sức khỏe & Dân số

**Phụ trách:** Nguyễn Lê Thế Vinh  
**Nguồn dữ liệu:** `data_output/wdi_health.csv`  
**Phạm vi:** World Development Indicators, quốc gia thật (217), giai đoạn 2000–2023

Tài liệu này không phải phần báo cáo chính. Đây là đặc tả kỹ thuật để dựng phần giao diện Tableau cho mục tiêu Sức khỏe & Dân số một cách nhất quán và dễ kiểm tra.

## 1. Dữ liệu đầu vào

Các trường chính trong file CSV:

| Trường | Kiểu dữ liệu Tableau | Vai trò |
|---|---|---|
| `Country_Name` | Dimension | Tên quốc gia |
| `Country_Code` | Dimension | Mã quốc gia, dùng cho geographic role |
| `Region` | Dimension | Vùng địa lý (7 vùng), dùng filter và màu |
| `Income_Group` | Dimension | Nhóm thu nhập (4 nhóm), dùng filter |
| `Year` | Dimension (Number hoặc Date) | Trục thời gian |
| `Life_expectancy` | Measure | Tuổi thọ trung bình tính từ lúc sinh (years) |
| `Under5_mortality` | Measure | Tỷ lệ tử vong trẻ em dưới 5 tuổi (per 1,000 live births) |
| `Health_expenditure_pct_GDP` | Measure | Chi tiêu y tế hiện thời (% of GDP) |
| `Population` | Measure | Tổng dân số |

Các ô trống là `Null` có chủ ý sau tiền xử lý. Khi dựng từng biểu đồ, lọc `Null` theo measure đang dùng.

## 2. Bộ lọc chung

Đặt các filter này ở dashboard section Sức khỏe (vị trí: cạnh phải hoặc hàng trên, theo quy ước nhóm):

| Filter | Kiểu hiển thị | Ghi chú |
|---|---|---|
| `Year` | Single value slider hoặc range slider | Line chart dùng range, scatter/bar dùng single value |
| `Region` | Multiple values dropdown | Cho phép chọn nhiều vùng để so sánh |
| `Income_Group` | Multiple values dropdown | So sánh theo nhóm thu nhập |
| `Country_Name` | Multiple values searchable dropdown | Xem chi tiết quốc gia cụ thể |

> ⚠️ **Task 3.7:** Các filter này cần apply cho **tất cả** worksheets trên dashboard, không chỉ riêng section sức khỏe. Sử dụng Dashboard > Actions hoặc "Apply to Worksheets > All Using This Data Source".

## 3. Worksheet 1 — Xu hướng tuổi thọ trung bình (Multi-line chart)

**Tên sheet:** `HEALTH_01_Life_Expectancy_Trend`

**Loại biểu đồ:** Line chart (multi-line)

**Mục tiêu:** Theo dõi sự thay đổi tuổi thọ trung bình của các quốc gia đại diện qua 24 năm, phát hiện xu hướng chung và các sự kiện gây biến động (COVID-19).

**Cấu hình Tableau:**

| Thành phần | Trường |
|---|---|
| Columns | `Year` |
| Rows | `AVG(Life_expectancy)` |
| Marks | Line |
| Color | `Country_Name` (hoặc `Region` nếu muốn nhóm vùng) |
| Detail | `Country_Name` |
| Filters | `Region`, `Income_Group`, `Country_Name`, `Year` (range) |
| Tooltip | Country, Region, Year, Life expectancy |

**Màu sắc:**
- Nếu color = Region: dùng palette vùng địa lý trong `Nhom15_Color_Palette.md`
- Nếu color = Country: chọn 6–8 quốc gia đại diện, dùng palette đỏ trầm `#B24A4A` làm accent

**Quốc gia gợi ý để highlight:**
- Thu nhập cao: United States, Japan, Germany
- Đang phát triển nhanh: China, Viet Nam, India
- Thách thức sức khỏe: Nigeria, Brazil

**Nhận xét cần kiểm tra khi dựng:**
- Xu hướng tăng đều ở hầu hết quốc gia
- Vết lõm rõ ở 2020–2021 do COVID-19 (đặc biệt ở Mỹ Latinh, Nam Á)
- Khoảng cách lớn giữa Sub-Saharan Africa và các khu vực khác
- Nigeria/Chad thường ở dưới cùng, Nhật Bản/Thụy Sĩ ở trên cùng

## 4. Worksheet 2 — Tỷ lệ tử vong trẻ em theo khu vực (Bar chart)

**Tên sheet:** `HEALTH_02_Under5_Mortality_By_Region`

**Loại biểu đồ:** Bar chart (horizontal)

**Mục tiêu:** So sánh mức tử vong trẻ em trung bình giữa 7 khu vực địa lý, nhấn mạnh khu vực có thách thức lớn nhất.

**Cấu hình Tableau:**

| Thành phần | Trường |
|---|---|
| Columns | `AVG(Under5_mortality)` |
| Rows | `Region` |
| Marks | Bar |
| Color | `Region` (dùng palette vùng địa lý) |
| Filters | `Year` (single value, mặc định 2022), `Income_Group`, `Country_Name` |
| Sort | Giảm dần theo `AVG(Under5_mortality)` |
| Tooltip | Region, Year, Avg under-5 mortality, số quốc gia |

**Màu sắc:** Dùng palette vùng địa lý cố định. Sub-Saharan Africa (`#2A8C8C`) sẽ là thanh dài nhất.

**Biến thể nâng cao (tùy chọn):**
- Grouped bar: thêm `Year` (chọn 2000, 2010, 2022) vào Color để thấy xu hướng giảm theo thời gian
- Dùng Reference Line ở mức trung bình toàn cầu

**Nhận xét cần kiểm tra khi dựng:**
- Sub-Saharan Africa có tỷ lệ cao nhất (có thể gấp 5–10 lần Europe)
- So sánh 2000 vs 2022 cho thấy mức giảm ấn tượng ở South Asia
- North America và Europe & Central Asia thường thấp nhất

## 5. Worksheet 3 — Chi tiêu y tế vs Tuổi thọ (Bubble scatter plot)

**Tên sheet:** `HEALTH_03_HealthExp_vs_LifeExp_Bubble`

**Loại biểu đồ:** Scatter plot (bubble)

**Mục tiêu:** Kết hợp 3 chiều dữ liệu trong 1 biểu đồ — kiểm tra mối tương quan giữa đầu tư y tế và kết quả sức khỏe, đặt trong ngữ cảnh quy mô dân số.

**Cấu hình Tableau:**

| Thành phần | Trường |
|---|---|
| Columns | `AVG(Health_expenditure_pct_GDP)` |
| Rows | `AVG(Life_expectancy)` |
| Marks | Circle |
| Color | `Region` (palette vùng địa lý) |
| Size | `SUM(Population)` |
| Detail | `Country_Name` |
| Filters | `Year` (single value, mặc định 2022), `Region`, `Income_Group` |
| Tooltip | Country, Region, Year, Health expenditure (% GDP), Life expectancy, Population |

**Lưu ý kỹ thuật:**
- Filter null cho cả `Health_expenditure_pct_GDP` VÀ `Life_expectancy`
- Size range: điều chỉnh sao cho Trung Quốc/Ấn Độ không che khuất quốc gia nhỏ
- Có thể thêm Trend Line (Analytics pane > Trend Line > Linear) để thấy tương quan tổng thể

**Màu sắc:** Palette vùng địa lý. Label cho 5–6 quốc gia lớn hoặc ngoại lai.

**Nhận xét cần kiểm tra khi dựng:**
- Xu hướng dương tổng thể: chi tiêu nhiều hơn → tuổi thọ cao hơn
- Nhưng KHÔNG phải tuyến tính — một số nước chi tiêu rất cao (>10% GDP) nhưng tuổi thọ không tương xứng (ví dụ: US chi tiêu cao nhưng tuổi thọ thấp hơn Nhật/Thụy Sĩ)
- Các nước châu Phi chi tiêu thấp VÀ tuổi thọ thấp — cluster ở góc trái-dưới
- ⚠️ **Chỉ mô tả tương quan, KHÔNG kết luận nhân quả!**

## 6. Worksheet 4 — Phân bố tuổi thọ theo khu vực (Box plot)

**Tên sheet:** `HEALTH_04_LifeExp_Boxplot_By_Region`

**Loại biểu đồ:** Box-and-whisker plot

**Mục tiêu:** Mô tả phân bố (median, Q1, Q3, outliers) tuổi thọ ở mỗi khu vực, cho thấy mức bất bình đẳng sức khỏe giữa các quốc gia trong cùng khu vực.

**Cấu hình Tableau:**

| Thành phần | Trường |
|---|---|
| Columns | `Region` |
| Rows | `AVG(Life_expectancy)` |
| Marks | Circle (Tableau sẽ tự chuyển thành box plot khi thêm Reference Line) |
| Detail | `Country_Name` |
| Filters | `Year` (range hoặc single), `Region`, `Income_Group` |

**Cách tạo Box Plot trong Tableau:**
1. Kéo `Region` vào Columns, `Life_expectancy` vào Rows
2. Kéo `Country_Name` vào Detail
3. Vào Analytics pane > kéo "Box Plot" vào view
4. Hoặc: Click vào trục Y > Add Reference Line > Box Plot

**Tùy chỉnh hiển thị:**
- Whiskers: extend to 1.5 × IQR
- Show outliers: Yes
- Fill box: dùng màu `#B24A4A` với opacity 30–40%
- Median line: đậm hơn (stroke-width 2.5)

**Nhận xét cần kiểm tra khi dựng:**
- Sub-Saharan Africa có phân bố rộng nhất (spread lớn) → bất bình đẳng sức khỏe cao
- Europe & Central Asia có median cao nhất và spread hẹp
- South Asia có median trung bình nhưng spread hẹp (ít quốc gia)
- Outliers thú vị: các quốc đảo nhỏ, các nước xung đột

## 7. Dashboard section đề xuất

**Tên dashboard section:** `Health & Population Overview`

**Bố cục:**

```
┌──────────────────────────────────────────┐
│  HEALTH_01_Life_Expectancy_Trend         │  ← Line chart chiếm hàng trên, toàn chiều ngang
│  (multi-line, full width)                │
├─────────────────────┬────────────────────┤
│ HEALTH_02           │ HEALTH_03          │  ← Hàng giữa chia đôi
│ Under5_Mortality    │ HealthExp_vs       │
│ Bar chart           │ LifeExp Bubble     │
├─────────────────────┴────────────────────┤
│  HEALTH_04_LifeExp_Boxplot_By_Region     │  ← Box plot hàng dưới
│  (box plot, full width)                  │
└──────────────────────────────────────────┘
                          Filters ──→ [ Year ] [ Region ] [ Country ]
```

**Dashboard actions (Task 3.7 + 4.7):**

| Action | Loại | Source | Target | Chi tiết |
|---|---|---|---|---|
| Filter by Region | Filter | `HEALTH_02` | All health sheets | Click một thanh region → lọc tất cả |
| Highlight Country | Highlight | `HEALTH_03` | `HEALTH_01`, `HEALTH_04` | Hover một quốc gia trong bubble → highlight trong line và box |
| Filter by Country | Filter | `HEALTH_01` | `HEALTH_03`, `HEALTH_04` | Click một đường quốc gia → lọc scatter và box |

## 8. Nhận xét dự kiến để đưa vào báo cáo

### Biểu đồ 1 (Line chart — Life expectancy):
- Tuổi thọ trung bình toàn cầu tăng đều từ 2000 đến 2019, phản ánh cải thiện y tế và điều kiện sống.
- COVID-19 (2020–2021) gây sụt giảm rõ ở nhiều quốc gia, đặc biệt Mỹ Latinh và Nam Á. Sau 2021, phần lớn đã phục hồi.
- Khoảng cách tuổi thọ giữa Sub-Saharan Africa (~55–60 năm) và châu Âu/Đông Á (~75–85 năm) vẫn rất lớn.

### Biểu đồ 2 (Bar chart — Under-5 mortality):
- Sub-Saharan Africa có tỷ lệ tử vong trẻ em cao nhất, phản ánh thách thức lớn về y tế cơ bản, dinh dưỡng và vệ sinh.
- So sánh 2000 vs 2022 cho thấy mức giảm ấn tượng ở South Asia (từ ~90 xuống ~30 per 1,000).
- Europe & Central Asia và North America đã đạt mức rất thấp (<10 per 1,000).

### Biểu đồ 3 (Bubble scatter — Health expenditure vs Life expectancy):
- Xu hướng dương tổng thể: chi tiêu y tế cao thường đi kèm tuổi thọ cao hơn.
- Tuy nhiên, quan hệ không tuyến tính — ví dụ: Mỹ chi tiêu ~17% GDP cho y tế nhưng tuổi thọ thấp hơn Nhật Bản (chi ~11%). Nguyên nhân có thể liên quan đến cấu trúc hệ thống y tế, bất bình đẳng tiếp cận, và lối sống.
- Các nước châu Phi tập trung ở góc trái-dưới (chi tiêu thấp, tuổi thọ thấp).
- ⚠️ Chỉ mô tả tương quan, không kết luận nhân quả.

### Biểu đồ 4 (Box plot — Life expectancy distribution):
- Sub-Saharan Africa có phân bố rộng nhất, cho thấy bất bình đẳng sức khỏe lớn giữa các quốc gia trong khu vực.
- Europe có median cao nhất và phân bố hẹp — các quốc gia khá đồng đều.
- Outliers thú vị: một số quốc đảo nhỏ hoặc quốc gia xung đột có tuổi thọ thấp bất thường so với khu vực.
