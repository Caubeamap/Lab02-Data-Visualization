# Đặc tả Tableau - Mục tiêu Giáo dục

**Phụ trách:** Hoàng Quốc Việt  
**Nguồn dữ liệu:** `data_output/wdi_education.csv`  
**Phạm vi:** World Development Indicators, quốc gia thật, giai đoạn 2000-2023

Tài liệu này không phải phần báo cáo chính. Đây là đặc tả kỹ thuật để dựng phần giao diện Tableau cho mục tiêu Giáo dục một cách nhất quán và dễ kiểm tra.

## 1. Dữ liệu đầu vào

Các trường chính trong file CSV:

| Trường | Kiểu dữ liệu Tableau | Vai trò |
|---|---|---|
| `Country_Name` | Dimension | Tên quốc gia |
| `Country_Code` | Dimension | Mã quốc gia |
| `Region` | Dimension | Vùng địa lý, dùng filter và màu |
| `Income_Group` | Dimension | Nhóm thu nhập, dùng filter |
| `Year` | Dimension/Date hoặc Number | Trục thời gian |
| `Primary_Net_Enrollment` | Measure | Tỷ lệ nhập học tiểu học đúng độ tuổi |
| `Secondary_Net_Enrollment` | Measure | Tỷ lệ nhập học trung học đúng độ tuổi |
| `Adult_Literacy_Rate` | Measure | Tỷ lệ biết chữ người trưởng thành |
| `Education_Expenditure_GDP` | Measure | Chi tiêu giáo dục của chính phủ theo % GDP |

Các ô trống là `Null` có chủ ý sau tiền xử lý. Khi dựng từng biểu đồ, lọc `Null` theo measure đang dùng.

## 2. Bộ lọc chung

Nên đặt các filter này ở dashboard Giáo dục:

| Filter | Kiểu hiển thị | Ghi chú |
|---|---|---|
| `Year` | Single value slider hoặc range slider | Dùng cho bar/scatter; line chart có thể dùng range |
| `Region` | Multiple values dropdown | Cho phép so sánh vùng |
| `Income_Group` | Multiple values dropdown | So sánh nhóm thu nhập |
| `Country_Name` | Multiple values searchable dropdown | Dùng khi cần xem chi tiết một số quốc gia |

## 3. Worksheet 1 - Xu hướng nhập học theo thời gian

**Tên sheet:** `EDU_01_Enrollment_Trend`

**Loại biểu đồ:** Line chart

**Mục tiêu:** So sánh xu hướng tiếp cận giáo dục tiểu học và trung học theo thời gian.

**Cấu hình Tableau:**

| Thành phần | Trường |
|---|---|
| Columns | `Year` |
| Rows | `AVG(Primary_Net_Enrollment)` và `AVG(Secondary_Net_Enrollment)` |
| Marks | Line |
| Color | Measure Names |
| Detail | Có thể thêm `Region` nếu muốn xem theo vùng |
| Filters | `Region`, `Income_Group`, `Country_Name`, `Year` |
| Tooltip | Year, Region/Country, Primary, Secondary |

**Lý do chọn:** Dữ liệu là time-series, line chart thể hiện xu hướng tăng/giảm rõ nhất. Việc đặt tiểu học và trung học trên cùng biểu đồ giúp thấy khoảng cách tiếp cận giữa hai bậc học.

**Nhận xét cần kiểm tra khi dựng:** Tiểu học thường cao hơn trung học; khoảng cách giữa hai đường phản ánh khó khăn khi học sinh chuyển tiếp lên bậc trung học.

## 4. Worksheet 2 - Chi tiêu giáo dục theo vùng

**Tên sheet:** `EDU_02_Expenditure_By_Region`

**Loại biểu đồ:** Bar chart

**Mục tiêu:** So sánh mức đầu tư giáo dục giữa các vùng hoặc nhóm thu nhập.

**Cấu hình Tableau:**

| Thành phần | Trường |
|---|---|
| Columns | `Region` |
| Rows | `AVG(Education_Expenditure_GDP)` |
| Marks | Bar |
| Color | `Region` |
| Filters | `Year`, `Income_Group`, `Country_Name` |
| Sort | Giảm dần theo `AVG(Education_Expenditure_GDP)` |
| Tooltip | Region, Year, Avg education expenditure, số quốc gia |

**Lý do chọn:** Bar chart phù hợp cho so sánh định lượng giữa các nhóm rời rạc như vùng địa lý.

**Nhận xét cần kiểm tra khi dựng:** Vùng có mức chi tiêu cao không nhất thiết có enrollment/literacy cao hơn nếu dữ liệu bị thiếu hoặc có độ trễ chính sách.

## 5. Worksheet 3 - Tương quan biết chữ và nhập học trung học

**Tên sheet:** `EDU_03_Literacy_vs_Secondary`

**Loại biểu đồ:** Scatter plot

**Mục tiêu:** Kiểm tra quan hệ giữa kết quả giáo dục (`Adult_Literacy_Rate`) và khả năng tiếp cận giáo dục trung học (`Secondary_Net_Enrollment`).

**Cấu hình Tableau:**

| Thành phần | Trường |
|---|---|
| Columns | `AVG(Secondary_Net_Enrollment)` |
| Rows | `AVG(Adult_Literacy_Rate)` |
| Marks | Circle |
| Color | `Region` |
| Size | `AVG(Education_Expenditure_GDP)` |
| Detail | `Country_Name` |
| Filters | `Year`, `Region`, `Income_Group` |
| Tooltip | Country, Region, Year, Secondary enrollment, Literacy, Education expenditure |

**Lý do chọn:** Scatter plot phù hợp để xem mối liên hệ giữa hai biến định lượng. Dùng size cho chi tiêu giáo dục giúp thêm lớp thông tin mà không làm biểu đồ quá rối.

**Lưu ý dữ liệu:** `Adult_Literacy_Rate` có nhiều `Null`, nên sheet này cần filter loại null cho cả `Adult_Literacy_Rate` và `Secondary_Net_Enrollment`.

## 6. Worksheet 4 - Bản đồ nhiệt tiếp cận giáo dục trung học

**Tên sheet:** `EDU_04_Secondary_Heatmap`

**Loại biểu đồ:** Heatmap

**Mục tiêu:** Quan sát mô hình thiếu hụt hoặc cải thiện giáo dục theo quốc gia và năm.

**Cấu hình Tableau:**

| Thành phần | Trường |
|---|---|
| Columns | `Year` |
| Rows | `Country_Name` |
| Color | `AVG(Secondary_Net_Enrollment)` |
| Filters | `Region`, `Income_Group`, `Country_Name`, `Year` |
| Sort | Theo `Region`, sau đó theo giá trị trung bình Secondary enrollment |
| Tooltip | Country, Region, Year, Secondary enrollment |

**Lý do chọn:** Heatmap phù hợp để đọc ma trận quốc gia x năm. Chọn `Secondary_Net_Enrollment` thay vì `Adult_Literacy_Rate` làm heatmap chính vì dữ liệu trung học có độ phủ tốt hơn, giúp dashboard ít bị rỗng hơn.

**Gợi ý bổ sung:** Nếu giảng viên yêu cầu đúng heatmap literacy, có thể duplicate sheet và đổi Color sang `Adult_Literacy_Rate`, nhưng cần chấp nhận nhiều ô null.

## 7. Dashboard section đề xuất

**Tên dashboard section:** `Education Overview`

**Bố cục:**

1. Hàng trên: `EDU_01_Enrollment_Trend` chiếm chiều ngang lớn.
2. Hàng giữa: `EDU_02_Expenditure_By_Region` bên trái, `EDU_03_Literacy_vs_Secondary` bên phải.
3. Hàng dưới: `EDU_04_Secondary_Heatmap`.
4. Cột filter bên phải hoặc trên cùng: Year, Region, Income Group, Country.

**Dashboard actions:**

- Filter action: click một vùng trong bar chart để lọc line chart, scatter và heatmap.
- Highlight action: hover một quốc gia trong scatter để highlight quốc gia đó trong heatmap.

## 8. Nhận xét dự kiến để nhóm trưởng đưa vào báo cáo

- Tỷ lệ nhập học tiểu học nhìn chung cao hơn trung học, cho thấy rào cản chuyển tiếp lên bậc học cao hơn vẫn là vấn đề cần quan sát.
- Chi tiêu giáo dục theo % GDP khác biệt rõ giữa các vùng và nhóm thu nhập; cần đọc cùng enrollment/literacy để tránh kết luận chỉ dựa trên ngân sách.
- Các quốc gia có tỷ lệ nhập học trung học cao thường có tỷ lệ biết chữ cao hơn, nhưng quan hệ này có thể bị ảnh hưởng bởi độ thiếu dữ liệu literacy.
- Heatmap giúp phát hiện quốc gia có chuỗi dữ liệu giảm, tăng hoặc thiếu hụt kéo dài, từ đó chọn trường hợp nổi bật để phân tích sâu.
