# Đặc tả Tableau - Mục tiêu Môi trường & Biến đổi khí hậu

**Phụ trách:** Phạm Quang Vinh  
**Nguồn dữ liệu:** `data_output/wdi_environment.csv`  
**Phạm vi:** World Development Indicators, quốc gia thật, giai đoạn 2000-2023 (riêng năng lượng tái tạo từ 2000-2021)

Tài liệu này không phải phần báo cáo chính. Đây là đặc tả kỹ thuật để dựng phần giao diện Tableau cho mục tiêu Môi trường & Biến đổi khí hậu một cách nhất quán và dễ kiểm tra.

## 1. Dữ liệu đầu vào

Các trường chính trong file CSV:

| Trường | Kiểu dữ liệu Tableau | Vai trò |
|---|---|---|
| `Country_Name` | Dimension | Tên quốc gia |
| `Country_Code` | Dimension | Mã quốc gia |
| `Region` | Dimension | Vùng địa lý, dùng làm bộ lọc và màu sắc |
| `Income_Group` | Dimension | Nhóm thu nhập, dùng làm bộ lọc |
| `Year` | Dimension/Date hoặc Number | Trục thời gian |
| `CO2_Emissions_Total_MtCO2e` | Measure | Tổng lượng phát thải CO2 (Mt CO2e) |
| `CO2_Emissions_Per_Capita` | Measure | Phát thải CO2 bình quân đầu người (t CO2e/capita) |
| `Renewable_Energy_Pct` | Measure | Tỷ lệ năng lượng tái tạo (%) |
| `Forest_Area_Pct` | Measure | Tỷ lệ phủ xanh diện tích rừng (%) |

Các ô trống là `Null` có chủ ý sau tiền xử lý (đặc biệt là năm 2022-2023 của chỉ số năng lượng tái tạo do nguồn WDI gốc chưa cập nhật). Lọc bỏ `Null` tương ứng khi thiết lập từng biểu đồ.

## 2. Bộ lọc chung

Nên đặt các filter này ở dashboard Môi trường:

| Filter | Kiểu hiển thị | Ghi chú |
|---|---|---|
| `Year` | Single value slider hoặc range slider | Dùng cho map và bar chart; line/area chart dùng phạm vi |
| `Region` | Multiple values dropdown | Cho phép so sánh giữa các khu vực |
| `Income_Group` | Multiple values dropdown | So sánh giữa các nhóm thu nhập |
| `Country_Name` | Multiple values searchable dropdown | Dùng khi cần lọc chi tiết một số quốc gia |

## 3. Worksheet 1 - Xu hướng phát thải CO2 theo khu vực

**Tên sheet:** `ENV_01_CO2_Trend`

**Loại biểu đồ:** Stacked Area chart

**Mục tiêu:** Theo dõi xu hướng tổng phát thải CO2 toàn cầu phân rã theo khu vực địa lý.

**Cấu hình Tableau:**

| Thành phần | Trường |
|---|---|
| Columns | `Year` (Continuous) |
| Rows | `SUM(CO2_Emissions_Total_MtCO2e)` |
| Marks | Area |
| Color | `Region` |
| Filters | `Region`, `Income_Group`, `Country_Name`, `Year` |
| Sort | Sắp xếp `Region` giảm dần theo tổng phát thải (vùng nhiều nhất ở dưới cùng) |
| Tooltip | Year, Region, Sum of CO2 Emissions |

**Lý do chọn:** Area chart thể hiện xuất sắc cả xu hướng tổng lượng phát thải toàn cầu (đường biên trên) lẫn sự thay đổi về tỷ trọng đóng góp của từng vùng địa lý theo thời gian.

**Nhận xét cần kiểm tra khi dựng:** Vùng Đông Á & Thái Bình Dương (East Asia & Pacific) có xu hướng tăng phát thải mạnh nhất. Xu hướng toàn cầu có sự sụt giảm nhẹ vào năm 2020 do ảnh hưởng ngưng trệ sản xuất từ đại dịch COVID-19.

## 4. Worksheet 2 - Bản đồ phát thải CO2 bình quân đầu người

**Tên sheet:** `ENV_02_CO2_Per_Capita_Map`

**Loại biểu đồ:** Choropleth Map (Bản đồ phân bố)

**Mục tiêu:** Trực quan hóa mức độ phát thải CO2 bình quân đầu người toàn cầu để thấy sự phân bố địa lý.

**Cấu hình Tableau:**

| Thành phần | Trường |
|---|---|
| Columns | `Longitude (generated)` |
| Rows | `Latitude (generated)` |
| Marks | Map |
| Detail | `Country_Name` (Geographic Role: Country/Region) |
| Color | `AVG(CO2_Emissions_Per_Capita)` |
| Color Palette | Diverging Red-Blue hoặc Orange-Blue (Phát thải cao = Đỏ/Cam, Phát thải thấp = Xanh) |
| Filters | `Year` (Slider chọn năm), `Region`, `Income_Group` |
| Tooltip | Country, Year, Avg CO2 per capita |

**Lý do chọn:** Choropleth Map giúp người xem có cái nhìn trực quan tức thì về địa lý, dễ dàng so sánh dấu chân carbon bình quân đầu người giữa các nước lớn và nước nhỏ.

**Nhận xét cần kiểm tra khi dựng:** Các quốc gia phát triển ở Bắc Mỹ, các nước xuất khẩu dầu mỏ ở Trung Đông và một số nước Châu Âu có màu đỏ đậm (phát thải rất cao), trong khi các quốc gia ở Châu Phi có màu xanh (phát thải cực kỳ thấp).

## 5. Worksheet 3 - Tiêu thụ năng lượng tái tạo theo khu vực

**Tên sheet:** `ENV_03_Renewable_Energy_Bar`

**Loại biểu đồ:** Grouped Bar chart

**Mục tiêu:** So sánh tỷ lệ sử dụng năng lượng tái tạo giữa các khu vực địa lý qua hai mốc thời gian 2000 và 2021.

**Cấu hình Tableau:**

| Thành phần | Trường |
|---|---|
| Columns | `Region`, `Year` (Discrete, filtered to 2000 & 2021) |
| Rows | `AVG(Renewable_Energy_Pct)` |
| Marks | Bar |
| Color | `Year` (màu nhạt cho năm 2000, màu đậm cho năm 2021) |
| Filters | `Year` (chỉ chọn 2000 và 2021), `Income_Group`, `Country_Name` |
| Sort | Sắp xếp `Region` theo giá trị giảm dần của năm 2021 |
| Label | Hiển thị giá trị phần trăm trên đầu các cột |
| Tooltip | Region, Year, Avg Renewable Energy % |

**Lý do chọn:** Grouped Bar chart giúp so sánh trực quan hiệu quả mức tăng trưởng năng lượng sạch của các vùng qua 2 thập kỷ.

**Nhận xét cần kiểm tra khi dựng:** Khu vực Sub-Saharan Africa có tỷ lệ năng lượng tái tạo cao nhất (chủ yếu là sinh khối truyền thống) nhưng có xu hướng giảm nhẹ do tốc độ đô thị hóa nhanh hơn tốc độ chuyển dịch xanh. Các khu vực khác như Châu Âu (Europe) có sự cải thiện rõ rệt.

## 6. Worksheet 4 - Biến động diện tích rừng

**Tên sheet:** `ENV_04_Forest_Area_Heatmap`

**Loại biểu đồ:** Heatmap (Bản đồ nhiệt ma trận)

**Mục tiêu:** Theo dõi xu hướng phủ xanh rừng của các quốc gia theo thời gian.

**Cấu hình Tableau:**

| Thành phần | Trường |
|---|---|
| Columns | `Year` (Discrete) |
| Rows | `Country_Name` |
| Marks | Square |
| Color | `AVG(Forest_Area_Pct)` |
| Color Palette | Sequential Green (Diện tích rừng cao = Xanh lá đậm, thấp = Xanh rất nhạt/trắng) |
| Filters | `Region`, `Income_Group`, `Country_Name` (Lọc khoảng 20 quốc gia có biến động lớn nhất) |
| Sort | Theo `Region` và `AVG(Forest_Area_Pct)` giảm dần |
| Tooltip | Country, Region, Year, Forest Area % |

**Lý do chọn:** Heatmap giúp biểu diễn ma trận Quốc gia × Năm một cách trực quan, giúp người xem nhận diện ngay lập tức các mô hình mất rừng (màu xanh nhạt dần) hoặc phục hồi rừng (màu xanh đậm dần) qua các năm.

**Nhận xét cần kiểm tra khi dựng:** Phát hiện các quốc gia có sự sụt giảm độ che phủ rừng nghiêm trọng (như ở một số khu vực Đông Nam Á hoặc Nam Mỹ) và những quốc gia thành công phục hồi rừng.

## 7. Bố cục Dashboard đề xuất

**Tên dashboard section:** `Environment & Climate Change`

**Bố cục giao diện:**
1. **Hàng trên cùng:** Bộ lọc chung nằm ngang (Year Slider, Region Dropdown, Income Group Dropdown).
2. **Khu vực chính:**
   * Bên trái: `ENV_01_CO2_Trend` (Stacked Area) chiếm diện tích lớn để người dùng bắt đầu đọc từ bức tranh tổng quan.
   * Bên phải: `ENV_02_CO2_Per_Capita_Map` để định vị địa lý.
3. **Khu vực dưới:**
   * Bên trái: `ENV_03_Renewable_Energy_Bar` (Grouped Bar chart) so sánh cơ cấu năng lượng.
   * Bên phải: `ENV_04_Forest_Area_Heatmap` (Ma trận diện tích rừng).

**Dashboard Actions:**
* **Filter Action:** Click chọn một quốc gia trên Choropleth Map hoặc click chọn một vùng trên Area Chart sẽ lọc toàn bộ dữ liệu của quốc gia/khu vực đó trên tất cả các biểu đồ còn lại.
* **Highlight Action:** Rê chuột (hover) vào một vùng địa lý (`Region`) trên bất kỳ biểu đồ nào sẽ làm sáng vùng đó trên tất cả các biểu đồ đang hiển thị.

## 8. Nhận xét dự kiến đưa vào báo cáo
* Tổng phát thải khí nhà kính toàn cầu liên tục gia tăng trong giai đoạn 2000-2019, dẫn đầu bởi sự gia tăng mạnh mẽ tại khu vực Đông Á & Thái Bình Dương (do quá trình công nghiệp hóa nhanh). Đại dịch COVID-19 năm 2020 đã tạo ra sự sụt giảm phát thải tạm thời nhưng nhanh chóng phục hồi ngay sau đó.
* Bản đồ phát thải bình quân đầu người phơi bày bất bình đẳng lớn: các nền kinh tế phát triển hoặc giàu tài nguyên có phát thải bình quân trên đầu người gấp hàng chục đến hàng trăm lần so với các quốc gia nghèo ở Châu Phi hoặc Nam Á.
* Năng lượng tái tạo đang có xu hướng tăng dần tại các quốc gia thu nhập cao nhờ chính sách chuyển dịch xanh, tuy nhiên tốc độ tăng vẫn chưa đủ nhanh để thay thế hoàn toàn năng lượng hóa thạch trong bối cảnh nhu cầu tiêu dùng gia tăng.
* Diện tích rừng toàn cầu đang chịu áp lực lớn; một số quốc gia ghi nhận mức suy giảm độ che phủ nghiêm trọng do khai thác đất nông nghiệp và công nghiệp, trong khi một số nước khác bắt đầu có dấu hiệu phục hồi nhờ các chương trình phủ xanh quốc gia.
