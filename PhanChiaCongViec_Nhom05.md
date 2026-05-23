# 📋 Phân Chia Công Việc — Nhóm 05

> **Môn học:** Trực Quan Hóa Dữ Liệu (CQ2023/24)  
> **Đồ án:** Lab 02 — Khai thác và trực quan hóa dữ liệu bằng Tableau  
> **Nguồn dữ liệu:** World Development Indicators (WDI) — World Bank  
> **Deadline:** 02/06/2026  

---

## 👥 Thông tin nhóm

| STT | MSSV     | Họ và tên           | Vai trò        |
|-----|----------|---------------------|----------------|
| 1   | 23120237 | Lê Lâm Trí Đức      | **Nhóm trưởng** |
| 2   | 23120189 | Hoàng Quốc Việt     | Thành viên     |
| 3   | 23120190 | Nguyễn Lê Thế Vinh  | Thành viên     |
| 4   | 23120202 | Phạm Quang Vinh     | Thành viên     |

---

## 📅 Lịch trình tổng quan

| Giai đoạn | Công việc chính | Thời gian | Mốc kiểm tra | Trạng thái |
|-----------|-----------------|-----------|---------------|------------|
| **GĐ 1** | Tìm hiểu đề bài, khảo sát dữ liệu WDI, chốt 4 mục tiêu phân tích | 23/05 – 25/05 | Tối 25/05: họp nhóm xác nhận mục tiêu & indicators | ⬜ |
| **GĐ 2** | Tiền xử lý dữ liệu bằng Python / Jupyter Notebook | 25/05 – 27/05 | Tối 27/05: mỗi người gửi file CSV sạch + phần notebook | ⬜ |
| **GĐ 3** | Tạo worksheets & xây dựng Dashboard trên Tableau | 27/05 – 30/05 | Tối 30/05: mỗi người hoàn thành ≥ 3 worksheets | ⬜ |
| **GĐ 4** | Viết báo cáo, chụp ảnh dashboard, quay video | 30/05 – 01/06 | Tối 31/05: nộp bản thảo báo cáo cá nhân | ⬜ |
| **GĐ 5** | **Buffer review** — kiểm tra chéo, chỉnh sửa, export PDF, đóng gói, nộp bài | 01/06 – 02/06 | 01/06: review toàn bộ sản phẩm trước khi nộp | ⬜ |

> ⚠️ **Ngày 01/06 là ngày buffer**: toàn nhóm dành để kiểm tra chéo, phát hiện lỗi và chỉnh sửa lần cuối. Không để công việc mới dồn vào ngày này.

---

## 📐 Quy ước xử lý dữ liệu chung

Toàn nhóm thống nhất các quy ước sau **trước khi bắt đầu tiền xử lý** để đảm bảo dữ liệu đồng nhất khi ghép vào Tableau:

| Hạng mục | Quy ước |
|----------|---------|
| **Nguồn dữ liệu** | Chỉ sử dụng World Development Indicators (WDI) — tải từ [databank.worldbank.org](https://databank.worldbank.org/source/world-development-indicators) hoặc file CSV chính thức của World Bank. |
| **Giai đoạn thời gian** | Thống nhất phân tích giai đoạn **2000–2023** (hoặc 2000–2022 nếu 2023 thiếu nhiều). Nếu indicator cụ thể thiếu dữ liệu trước 2005, ghi rõ trong báo cáo. |
| **Danh sách quốc gia** | Ưu tiên phân tích **≥ 20 quốc gia đại diện** cho các khu vực (Đông Á, Đông Nam Á, Châu Âu, Bắc Mỹ, Châu Phi, Nam Mỹ). Loại bỏ các aggregate rows (World, regions) trừ khi cần so sánh khu vực. |
| **Xử lý missing values** | (1) Nếu thiếu ≤ 2 năm liên tiếp → nội suy tuyến tính. (2) Nếu thiếu > 2 năm liên tiếp → loại quốc gia/indicator đó khỏi phân tích. Ghi rõ cách xử lý trong notebook. |
| **Chuẩn hóa tên cột** | Sau tiền xử lý, các file CSV phải có cột: `Country_Name`, `Country_Code`, `Year`, và các cột chỉ số đặt tên bằng tiếng Anh viết tắt (ví dụ: `GDP_per_capita`, `CO2_emissions_mt`). |
| **Định dạng file output** | Mỗi thành viên xuất 1 file CSV sạch đặt tên: `wdi_<chủ_đề>.csv` (ví dụ: `wdi_economy.csv`). Encoding UTF-8, dấu phân cách comma. |
| **Thư viện Python** | Chỉ dùng NumPy, pandas, (tùy chọn: scipy cho nội suy). Nếu dùng thư viện khác, ghi rõ lý do trong notebook. |

---

## 🎯 4 Mục tiêu phân tích chi tiết

> Yêu cầu đề bài: **số mục tiêu = số thành viên = 4**. Mỗi thành viên chịu trách nhiệm chính 1 mục tiêu.

---

### Mục tiêu 1 — Phát triển kinh tế *(Phụ trách: Lê Lâm Trí Đức)*

| Hạng mục | Nội dung |
|----------|---------|
| **Câu hỏi phân tích** | Xu hướng tăng trưởng kinh tế của các quốc gia/khu vực trong giai đoạn 2000–2023 như thế nào? GDP bình quân đầu người có mối quan hệ gì với tỷ lệ nghèo? |
| **Metrics chính (WDI)** | `NY.GDP.MKTP.CD` (GDP), `NY.GDP.PCAP.CD` (GDP per capita), `NY.GDP.MKTP.KD.ZG` (GDP growth %), `SI.POV.DDAY` (Poverty headcount ratio) |
| **Loại biểu đồ dự kiến** | ① **Line chart**: xu hướng GDP per capita theo thời gian. ② **Bar chart (grouped)**: so sánh GDP growth giữa các khu vực. ③ **Scatter plot**: tương quan GDP per capita vs tỷ lệ nghèo. ④ **Choropleth map**: phân bố GDP per capita toàn cầu. |
| **Kết luận mong muốn** | Xác định quốc gia/khu vực tăng trưởng nhanh nhất, chậm nhất; mối tương quan nghịch giữa GDP per capita và tỷ lệ nghèo; tác động của các sự kiện kinh tế lớn (2008, COVID-19). |

---

### Mục tiêu 2 — Giáo dục *(Phụ trách: Hoàng Quốc Việt)*

| Hạng mục | Nội dung |
|----------|---------|
| **Câu hỏi phân tích** | Mức độ tiếp cận giáo dục và đầu tư cho giáo dục thay đổi thế nào theo thời gian? Có sự chênh lệch giới tính trong tỷ lệ nhập học không? |
| **Metrics chính (WDI)** | `SE.PRM.NENR` (Net enrollment rate, primary), `SE.SEC.NENR` (Net enrollment rate, secondary), `SE.ADT.LITR.ZS` (Literacy rate, adult), `SE.XPD.TOTL.GD.ZS` (Government expenditure on education, % of GDP) |
| **Loại biểu đồ dự kiến** | ① **Line chart**: xu hướng enrollment rate theo thời gian cho nhiều quốc gia. ② **Bar chart (stacked)**: so sánh chi tiêu giáo dục giữa các khu vực. ③ **Scatter plot**: tương quan literacy rate vs enrollment rate. ④ **Heatmap**: literacy rate theo quốc gia × năm. |
| **Kết luận mong muốn** | Đánh giá tiến bộ giáo dục toàn cầu, xác định khu vực còn tụt hậu, mối liên hệ giữa đầu tư giáo dục và kết quả giáo dục. |

> ⚠️ HDI không phải chỉ số WDI (thuộc UNDP). Đã thay bằng các indicators WDI xác minh được.

---

### Mục tiêu 3 — Sức khỏe & dân số *(Phụ trách: Nguyễn Lê Thế Vinh)*

| Hạng mục | Nội dung |
|----------|---------|
| **Câu hỏi phân tích** | Tuổi thọ trung bình và tỷ lệ tử vong trẻ em thay đổi ra sao? Chi tiêu y tế có ảnh hưởng đến kết quả sức khỏe không? |
| **Metrics chính (WDI)** | `SP.DYN.LE00.IN` (Life expectancy at birth), `SH.DYN.MORT` (Under-5 mortality rate), `SH.XPD.CHEX.GD.ZS` (Current health expenditure, % of GDP), `SP.POP.TOTL` (Total population) |
| **Loại biểu đồ dự kiến** | ① **Line chart (multi-line)**: xu hướng life expectancy theo thời gian. ② **Bar chart**: so sánh tỷ lệ tử vong trẻ em giữa các khu vực. ③ **Scatter plot (bubble)**: tương quan health expenditure vs life expectancy (size = population). ④ **Box plot**: phân bố life expectancy theo khu vực. |
| **Kết luận mong muốn** | Xu hướng cải thiện sức khỏe toàn cầu, mối liên hệ chi tiêu y tế — tuổi thọ, khu vực có tỷ lệ tử vong trẻ em cao bất thường, ảnh hưởng COVID-19 lên tuổi thọ. |

---

### Mục tiêu 4 — Môi trường & biến đổi khí hậu *(Phụ trách: Phạm Quang Vinh)*

| Hạng mục | Nội dung |
|----------|---------|
| **Câu hỏi phân tích** | Xu hướng phát thải CO₂ toàn cầu như thế nào? Năng lượng tái tạo có đang tăng không? Diện tích rừng thay đổi ra sao? |
| **Metrics chính (WDI)** | `EN.GHG.CO2.MT.CE.AR5` (CO₂ emissions total excl. LULUCF, Mt CO₂e), `EN.GHG.CO2.PC.CE.AR5` (CO₂ emissions per capita, t CO₂e/capita), `EG.FEC.RNEW.ZS` (Renewable energy consumption, %), `AG.LND.FRST.ZS` (Forest area, % of land) |
| **Loại biểu đồ dự kiến** | ① **Line chart (area)**: xu hướng CO₂ emissions (Mt CO₂e) theo thời gian. ② **Choropleth map**: CO₂ per capita toàn cầu. ③ **Bar chart (grouped)**: so sánh renewable energy % giữa các khu vực. ④ **Heatmap**: forest area % theo quốc gia × năm. |
| **Kết luận mong muốn** | Xác định top quốc gia phát thải, xu hướng chuyển đổi năng lượng tái tạo, mối liên hệ giữa phát triển kinh tế và phát thải, tình trạng mất rừng toàn cầu. |

> ⚠️ Hạn chế dùng pie/donut chart cho dữ liệu WDI vì phần lớn chỉ số là time-series hoặc numerical, không phải tỷ trọng rõ ràng. Ưu tiên line, bar, scatter, map, heatmap, box plot.

> ⚠️ **Lưu ý về mã CO₂:** Dataset này **không có** mã cũ `EN.ATM.CO2E.KT` / `EN.ATM.CO2E.PC`. Thay vào đó sử dụng mã mới từ bộ GHG: `EN.GHG.CO2.MT.CE.AR5` (tổng CO₂, Mt CO₂e) và `EN.GHG.CO2.PC.CE.AR5` (CO₂ per capita, t CO₂e/capita). Đã xác minh có trong file `WDIEXCEL.xlsx`.

---

## 📝 Phân chia công việc chi tiết

---

### 🔷 Lê Lâm Trí Đức (23120237) — Nhóm trưởng

**Mục tiêu phân tích:** Phát triển kinh tế

#### A. Nhiệm vụ theo mục tiêu cá nhân:

| # | Công việc | Deadline | Trạng thái |
|---|-----------|----------|------------|
| 1.1 | Khảo sát indicators kinh tế trong WDI, xác nhận mã chỉ số khả dụng | 25/05 | ⬜ |
| 1.2 | Tiền xử lý dữ liệu kinh tế trong Jupyter Notebook: lọc indicators, xử lý missing data, chuẩn hóa tên cột, xuất file `wdi_economy.csv` | 27/05 | ⬜ |
| 1.3 | Giải thích ý nghĩa từng metric kinh tế & lý do chọn (viết trong notebook + báo cáo) | 27/05 | ⬜ |
| 1.4 | Tạo **≥ 3 worksheets Tableau** cho mục tiêu kinh tế: line chart (xu hướng GDP), bar chart (so sánh khu vực), scatter plot (GDP vs nghèo), choropleth map | 29/05 | ⬜ |
| 1.5 | Viết nhận xét bám sát biểu đồ: chỉ ra xu hướng, ngoại lai, khác biệt đáng chú ý, kết luận | 30/05 | ⬜ |
| 1.6 | Viết phần báo cáo cho mục tiêu kinh tế (mô tả bài toán, ảnh chụp biểu đồ Tableau, nhận xét, kết luận) | 31/05 | ⬜ |

#### B. Nhiệm vụ chung / điều phối:

| # | Công việc | Deadline | Trạng thái |
|---|-----------|----------|------------|
| 1.7 | Thiết lập thư mục làm việc chung (Google Drive / GitHub), chia sẻ dữ liệu WDI gốc | 23/05 | ⬜ |
| 1.8 | Điều phối họp nhóm chốt 4 mục tiêu phân tích & quy ước chung | 25/05 | ⬜ |
| 1.9 | Viết phần **giới thiệu tổng quan dataset** trong Jupyter Notebook (cấu trúc dữ liệu, số bản ghi, số trường, ý nghĩa) | 26/05 | ⬜ |
| 1.10 | Thiết kế **bố cục Dashboard tổng** trên Tableau (layout, vị trí biểu đồ từng thành viên, thứ tự đọc tổng quan → chi tiết) | 29/05 | ⬜ |

> 💡 Các việc tổng hợp notebook, export PDF, đóng gói nộp bài đã được **chia đều** cho các thành viên khác — xem bên dưới.

---

### 🔷 Hoàng Quốc Việt (23120189)

**Mục tiêu phân tích:** Giáo dục

#### A. Nhiệm vụ theo mục tiêu cá nhân:

| # | Công việc | Deadline | Trạng thái |
|---|-----------|----------|------------|
| 2.1 | Khảo sát indicators giáo dục trong WDI, xác nhận mã chỉ số khả dụng | 25/05 | ⬜ |
| 2.2 | Tiền xử lý dữ liệu giáo dục trong Jupyter Notebook: lọc indicators, xử lý missing data, chuẩn hóa tên cột, xuất file `wdi_education.csv` | 27/05 | ⬜ |
| 2.3 | Giải thích ý nghĩa từng metric giáo dục & lý do chọn (viết trong notebook + báo cáo) | 27/05 | ⬜ |
| 2.4 | Tạo **≥ 3 worksheets Tableau** cho mục tiêu giáo dục: line chart (enrollment trend), stacked bar chart (chi tiêu giáo dục), scatter plot (literacy vs enrollment), heatmap | 29/05 | ⬜ |
| 2.5 | Viết nhận xét bám sát biểu đồ: chỉ ra xu hướng, ngoại lai, khác biệt đáng chú ý, kết luận | 30/05 | ⬜ |
| 2.6 | Viết phần báo cáo cho mục tiêu giáo dục (mô tả bài toán, ảnh chụp biểu đồ Tableau, nhận xét, kết luận) | 31/05 | ⬜ |

#### B. Nhiệm vụ chung:

| # | Công việc | Deadline | Trạng thái |
|---|-----------|----------|------------|
| 2.7 | Viết phần **thống kê mô tả cơ bản** (descriptive statistics) trong Jupyter Notebook: mean, median, std, min, max cho các indicators chính | 27/05 | ⬜ |
| 2.8 | **Tổng hợp file Jupyter Notebook** (.ipynb): ghép phần tiền xử lý của 4 thành viên thành 1 notebook hoàn chỉnh, chạy lại toàn bộ cell, giữ output | 28/05 | ⬜ |
| 2.9 | Thiết kế **color palette & formatting** nhất quán cho toàn bộ biểu đồ Tableau (thống nhất bảng màu, font, kích thước chữ) | 29/05 | ⬜ |

---

### 🔷 Nguyễn Lê Thế Vinh (23120190)

**Mục tiêu phân tích:** Sức khỏe & dân số

#### A. Nhiệm vụ theo mục tiêu cá nhân:

| # | Công việc | Deadline | Trạng thái |
|---|-----------|----------|------------|
| 3.1 | Khảo sát indicators sức khỏe & dân số trong WDI, xác nhận mã chỉ số khả dụng | 25/05 | ⬜ |
| 3.2 | Tiền xử lý dữ liệu sức khỏe trong Jupyter Notebook: lọc indicators, xử lý missing data, chuẩn hóa tên cột, xuất file `wdi_health.csv` | 27/05 | ⬜ |
| 3.3 | Giải thích ý nghĩa từng metric sức khỏe & lý do chọn (viết trong notebook + báo cáo) | 27/05 | ⬜ |
| 3.4 | Tạo **≥ 3 worksheets Tableau** cho mục tiêu sức khỏe: multi-line chart (life expectancy), bar chart (tử vong trẻ em), bubble chart (health exp vs life exp), box plot (phân bố) | 29/05 | ⬜ |
| 3.5 | Viết nhận xét bám sát biểu đồ: chỉ ra xu hướng, ngoại lai, khác biệt đáng chú ý, kết luận | 30/05 | ⬜ |
| 3.6 | Viết phần báo cáo cho mục tiêu sức khỏe (mô tả bài toán, ảnh chụp biểu đồ Tableau, nhận xét, kết luận) | 31/05 | ⬜ |

#### B. Nhiệm vụ chung:

| # | Công việc | Deadline | Trạng thái |
|---|-----------|----------|------------|
| 3.7 | Cài đặt **filter & selector/dropdown** tương tác trên Dashboard Tableau (bộ lọc quốc gia, năm, khu vực) | 30/05 | ⬜ |
| 3.8 | Quay & chỉnh sửa **Video 1** — Giới thiệu công cụ Tableau: tổng quan Tableau, các tính năng chính nhóm đã sử dụng (chart types, dashboard, filter, actions) | 01/06 | ⬜ |
| 3.9 | **Export Tableau Dashboard ra PDF** (File → Print to PDF), kiểm tra trùng khớp với file .twbx | 01/06 | ⬜ |

---

### 🔷 Phạm Quang Vinh (23120202)

**Mục tiêu phân tích:** Môi trường & biến đổi khí hậu

#### A. Nhiệm vụ theo mục tiêu cá nhân:

| # | Công việc | Deadline | Trạng thái |
|---|-----------|----------|------------|
| 4.1 | Khảo sát indicators môi trường & khí hậu trong WDI, xác nhận mã chỉ số khả dụng | 25/05 | ⬜ |
| 4.2 | Tiền xử lý dữ liệu môi trường trong Jupyter Notebook: lọc indicators, xử lý missing data, chuẩn hóa tên cột, xuất file `wdi_environment.csv` | 27/05 | ⬜ |
| 4.3 | Giải thích ý nghĩa từng metric môi trường & lý do chọn (viết trong notebook + báo cáo) | 27/05 | ⬜ |
| 4.4 | Tạo **≥ 3 worksheets Tableau** cho mục tiêu môi trường: area chart (CO₂ trend), choropleth map (CO₂ per capita), grouped bar chart (renewable energy), heatmap (forest area) | 29/05 | ⬜ |
| 4.5 | Viết nhận xét bám sát biểu đồ: chỉ ra xu hướng, ngoại lai, khác biệt đáng chú ý, kết luận | 30/05 | ⬜ |
| 4.6 | Viết phần báo cáo cho mục tiêu môi trường (mô tả bài toán, ảnh chụp biểu đồ Tableau, nhận xét, kết luận) | 31/05 | ⬜ |

#### B. Nhiệm vụ chung:

| # | Công việc | Deadline | Trạng thái |
|---|-----------|----------|------------|
| 4.7 | Cài đặt **Dashboard Actions** (filter action & highlight action giữa các biểu đồ) trên Tableau | 30/05 | ⬜ |
| 4.8 | Quay & chỉnh sửa **Video 2** — Trình bày phân tích: kết quả phân tích dữ liệu, diễn giải các biểu đồ và dashboard, nhận xét, kết luận | 01/06 | ⬜ |
| 4.9 | **Đóng gói file nén** `Nhom05.zip` theo đúng cấu trúc, kiểm tra đầy đủ, nộp bài trên Moodle | 02/06 | ⬜ |

---

## 📦 Sản phẩm cụ thể của từng thành viên

| Sản phẩm | Trí Đức | Quốc Việt | Thế Vinh | Quang Vinh |
|----------|---------|-----------|----------|------------|
| **File CSV sạch** | `wdi_economy.csv` | `wdi_education.csv` | `wdi_health.csv` | `wdi_environment.csv` |
| **Worksheets Tableau** (≥ 3) | Line, bar, scatter, map (kinh tế) | Line, stacked bar, scatter, heatmap (giáo dục) | Multi-line, bar, bubble, box plot (sức khỏe) | Area, map, grouped bar, heatmap (môi trường) |
| **Section trong Dashboard** | Khu vực kinh tế + layout tổng | Khu vực giáo dục + color palette | Khu vực sức khỏe + filter/selector | Khu vực môi trường + dashboard actions |
| **Phần báo cáo** | Giới thiệu dataset + Phân tích kinh tế | Thống kê mô tả + Phân tích giáo dục | Phân tích sức khỏe | Phân tích môi trường |
| **Nhận xét / kết luận** | Xu hướng GDP, tương quan GDP-nghèo | Tiến bộ giáo dục, chênh lệch khu vực | Cải thiện sức khỏe, tác động COVID | Phát thải CO₂, chuyển đổi năng lượng |
| **Việc chung** | Tổng quan dataset + Layout dashboard | Tổng hợp notebook + Color palette | Filter + Video 1 + Export PDF | Dashboard actions + Video 2 + Đóng gói nộp |

---

## 📊 Bảng tổng hợp phân chia theo tiêu chí đánh giá

| Tiêu chí (Tỉ lệ) | Trí Đức | Quốc Việt | Thế Vinh | Quang Vinh |
|---------------------|---------|-----------|----------|------------|
| **1. Xác định bài toán & mục tiêu (20%)** | Bài toán chung + Mục tiêu Kinh tế | Mục tiêu Giáo dục | Mục tiêu Sức khỏe | Mục tiêu Môi trường |
| **2. Tiền xử lý dữ liệu (20%)** | Giới thiệu dataset + Tiền xử lý Kinh tế | Thống kê mô tả + Tổng hợp notebook + Tiền xử lý Giáo dục | Tiền xử lý Sức khỏe | Tiền xử lý Môi trường |
| **3. Trực quan hóa & Dashboard (40%)** | ≥3 worksheets Kinh tế + Layout dashboard | ≥3 worksheets Giáo dục + Color palette | ≥3 worksheets Sức khỏe + Filter/Selector | ≥3 worksheets Môi trường + Dashboard Actions |
| **4. Báo cáo & trình bày (20%)** | Báo cáo Kinh tế | Báo cáo Giáo dục | Báo cáo Sức khỏe + Video 1 + Export PDF | Báo cáo Môi trường + Video 2 + Đóng gói nộp |

---

## 🎬 Phân công Video

| Video | Nội dung yêu cầu | Phụ trách chính | Hỗ trợ nội dung | Thời lượng |
|-------|-------------------|-----------------|-----------------|------------|
| **Video 1** | Giới thiệu công cụ Tableau: tổng quan, các tính năng chính nhóm đã sử dụng (chart types, dashboard, filter, actions) | Nguyễn Lê Thế Vinh | Lê Lâm Trí Đức | ≤ 10 phút |
| **Video 2** | Trình bày phân tích: kết quả phân tích dữ liệu, diễn giải các biểu đồ và dashboard, nhận xét và kết luận | Phạm Quang Vinh | Hoàng Quốc Việt | ≤ 10 phút |

**Yêu cầu video:**
- Định dạng: **MP4**
- Thời lượng: **không quá 10 phút/video**
- Nếu file quá nặng: upload lên **Google Drive** (chế độ Anyone with the link) hoặc **YouTube** (chế độ unlisted), đính kèm link trong báo cáo
- Link phải còn truy cập được **ít nhất 2 năm**

---

## 📂 Cấu trúc thư mục nộp bài

```
Nhom05.zip
├── data/                              # Thư mục dữ liệu
│   ├── WDI_raw.csv                   # Dữ liệu gốc (hoặc link công khai)
│   ├── wdi_economy.csv               # Dữ liệu sạch - Kinh tế
│   ├── wdi_education.csv             # Dữ liệu sạch - Giáo dục
│   ├── wdi_health.csv                # Dữ liệu sạch - Sức khỏe
│   └── wdi_environment.csv           # Dữ liệu sạch - Môi trường
├── code/
│   └── Nhom05_TienXuLy.ipynb         # Jupyter Notebook (đã chạy, giữ output)
├── Nhom05_Dashboard.twbx              # File Tableau đóng gói (kèm dữ liệu)
├── Nhom05_Dashboard_Export.pdf         # PDF export từ Tableau (File → Print to PDF)
├── Nhom05.pdf                         # File báo cáo chính
├── Video1_GioiThieuTableau.mp4        # Video 1 (hoặc link trong báo cáo)
└── Video2_TrinhBayPhanTich.mp4        # Video 2 (hoặc link trong báo cáo)
```

> Nếu file video hoặc dữ liệu quá nặng, thay bằng file `links.txt` chứa link Google Drive / YouTube. File code và báo cáo vẫn nộp trực tiếp trên Moodle.

---

## ✅ Checklist trước khi nộp (01/06 — Ngày buffer review)

**Phụ trách kiểm tra:** mỗi người tự kiểm tra phần mình + kiểm tra chéo 1 phần của người khác.

| # | Hạng mục kiểm tra | Người kiểm tra chéo | Trạng thái |
|---|-------------------|---------------------|------------|
| 1 | Jupyter Notebook đã **chạy lại toàn bộ cell** và **không xóa output** | Quốc Việt (người tổng hợp) | ⬜ |
| 2 | File Tableau (.twbx) đã **đóng gói kèm dữ liệu** (Save As → Packaged Workbook) | Trí Đức | ⬜ |
| 3 | Dashboard có **filter** hiển thị trên dashboard | Thế Vinh (người cài filter) | ⬜ |
| 4 | Dashboard có **dashboard actions** (filter/highlight) hoạt động đúng | Quang Vinh (người cài actions) | ⬜ |
| 5 | PDF export từ Tableau **hiển thị đầy đủ** các trang/dashboard, trùng khớp với file .twbx | Thế Vinh (người export) | ⬜ |
| 6 | Sử dụng **đa dạng loại biểu đồ** đã học: line, bar, scatter, map, heatmap, box plot, area,... | Cả nhóm | ⬜ |
| 7 | Color palette **hài hòa, nhất quán** xuyên suốt các biểu đồ | Quốc Việt (người thiết kế palette) | ⬜ |
| 8 | Mọi biểu đồ có **tiêu đề rõ ràng, nhãn trục đầy đủ, chú thích (legend) dễ đọc** | Cả nhóm tự kiểm tra | ⬜ |
| 9 | Báo cáo đầy đủ: mô tả bài toán, giải thích dữ liệu, quy trình tiền xử lý, ảnh chụp biểu đồ Tableau, nhận xét, kết luận | Trí Đức (review tổng) | ⬜ |
| 10 | Video 1 & Video 2: ≤ 10 phút/video, định dạng MP4, nội dung đúng yêu cầu | Trí Đức kiểm Video 1, Quốc Việt kiểm Video 2 | ⬜ |
| 11 | Tài liệu tham khảo ghi đầy đủ trong báo cáo | Cả nhóm | ⬜ |
| 12 | File nén đặt tên đúng `Nhom05.zip`, cấu trúc thư mục đúng quy định | Quang Vinh (người đóng gói) | ⬜ |
| 13 | Đại diện **1 người nộp bài** trên Moodle | Quang Vinh | ⬜ |

---

## 📌 Ghi chú quan trọng

1. **Chỉ sử dụng dữ liệu WDI** — không dùng nguồn dữ liệu khác (UNDP, WHO riêng,...).
2. **Trực quan hóa bằng Tableau** — không dùng matplotlib, seaborn, plotly,... cho kết quả cuối cùng. Mọi biểu đồ trong báo cáo phải được xuất trực tiếp từ file Tableau.
3. **Python chỉ dùng cho tiền xử lý** — tổ chức trong 1 file Jupyter Notebook (.ipynb) kèm theo bài nộp.
4. **Tránh biểu diễn gây hiểu nhầm** — đảm bảo dữ liệu chính xác, trục bắt đầu từ 0 khi cần, không cắt xén gây lệch cảm nhận.
5. **AI (ChatGPT, Copilot,...)** chỉ là công cụ tham khảo — nội dung phải được kiểm tra và chỉnh sửa phù hợp. Nếu phát hiện sử dụng AI sinh nội dung quá nhiều hoặc nội dung sai lệch, **trừ tối đa 50% điểm**.
6. **Bài giống nhau** sẽ nhận **0 điểm môn học**.
7. Link video/dữ liệu trên Drive/YouTube phải **truy cập được ít nhất 2 năm**.
8. **Ưu tiên loại biểu đồ phù hợp WDI**: line chart (xu hướng), bar chart (so sánh), scatter plot (tương quan), map/choropleth (phân bố địa lý), heatmap (ma trận), box plot (phân bố). Hạn chế pie/donut khi dữ liệu không có tỷ trọng rõ ràng.

---

## 🔍 Kết quả kiểm tra dữ liệu (23/05/2026)

**File dữ liệu:** `WDIEXCEL.xlsx` (~80 MB) + `WDIEXCEL.csv` (metadata quốc gia)

| Thông số | Giá trị |
|----------|--------|
| **Tổng số indicators** | 1.486 |
| **Tổng số quốc gia/khu vực** | 265 (217 quốc gia thực, 48 nhóm aggregate) |
| **Khoảng thời gian** | 1960 – 2025 (66 cột năm) |
| **7 vùng địa lý** | Latin America & Caribbean, Middle East & North Africa, Sub-Saharan Africa, Europe & Central Asia, East Asia & Pacific, South Asia, North America |
| **4 nhóm thu nhập** | High income, Upper middle income, Lower middle income, Low income |
| **Sheets trong file** | Data, Country, Series, country-series, series-time, footnote |

### Kết quả kiểm tra 16 indicators theo kế hoạch:

| # | Indicator Code | Tên chỉ số | Trạng thái |
|---|---------------|-----------|------------|
| 1 | `NY.GDP.MKTP.CD` | GDP (current US$) | ✅ Có |
| 2 | `NY.GDP.PCAP.CD` | GDP per capita (current US$) | ✅ Có |
| 3 | `NY.GDP.MKTP.KD.ZG` | GDP (annual % growth) | ✅ Có |
| 4 | `SI.POV.DDAY` | Poverty headcount ratio at $3.00 a day (2021 PPP) | ✅ Có |
| 5 | `SE.PRM.NENR` | School enrollment, primary (% net) | ✅ Có |
| 6 | `SE.SEC.NENR` | School enrollment, secondary (% net) | ✅ Có |
| 7 | `SE.ADT.LITR.ZS` | Literacy rate, adult total (% of people ages 15+) | ✅ Có |
| 8 | `SE.XPD.TOTL.GD.ZS` | Government expenditure on education, total (% of GDP) | ✅ Có |
| 9 | `SP.DYN.LE00.IN` | Life expectancy at birth, total (years) | ✅ Có |
| 10 | `SH.DYN.MORT` | Mortality rate, under-5 (per 1,000 live births) | ✅ Có |
| 11 | `SH.XPD.CHEX.GD.ZS` | Current health expenditure (% of GDP) | ✅ Có |
| 12 | `SP.POP.TOTL` | Population, total | ✅ Có |
| 13 | `EN.GHG.CO2.MT.CE.AR5` | CO₂ emissions (total) excl. LULUCF (Mt CO₂e) | ✅ Có |
| 14 | `EN.GHG.CO2.PC.CE.AR5` | CO₂ emissions per capita (t CO₂e/capita) | ✅ Có |
| 15 | `EG.FEC.RNEW.ZS` | Renewable energy consumption (% of total) | ✅ Có |
| 16 | `AG.LND.FRST.ZS` | Forest area (% of land area) | ✅ Có |

> ✅ **Kết luận: Dữ liệu hoàn toàn phù hợp.** Tất cả 16/16 indicators đều có trong dataset sau khi thay thế 2 mã CO₂ cũ (`EN.ATM.CO2E.*`) bằng mã mới (`EN.GHG.CO2.*`). Nhóm có thể bắt tay vào tiền xử lý ngay.

---

*Cập nhật lần cuối: 23/05/2026*
