from __future__ import annotations

import csv
import json
import math
import statistics
import zipfile
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
XLSX_PATH = ROOT / "WDIEXCEL.xlsx"
OUTPUT_DIR = ROOT / "data_output"
NOTEBOOK_PATH = ROOT / "notebook" / "Nhom05_KinhTe_LeLamTriDuc.ipynb"

YEARS = [str(y) for y in range(2000, 2024)]
INDICATORS = {
    "NY.GDP.MKTP.CD": {
        "clean_name": "GDP_current_USD",
        "label": "GDP (current US$)",
        "unit": "US$",
    },
    "NY.GDP.PCAP.CD": {
        "clean_name": "GDP_per_capita_current_USD",
        "label": "GDP per capita (current US$)",
        "unit": "US$ per person",
    },
    "NY.GDP.MKTP.KD.ZG": {
        "clean_name": "GDP_growth_annual_pct",
        "label": "GDP growth (annual %)",
        "unit": "%",
    },
    "SI.POV.DDAY": {
        "clean_name": "Poverty_headcount_3usd_2021PPP_pct",
        "label": "Poverty headcount ratio at $3.00 a day (2021 PPP)",
        "unit": "%",
    },
}

NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pkgrel": "http://schemas.openxmlformats.org/package/2006/relationships",
}


def col_index(cell_ref: str) -> int:
    letters = "".join(ch for ch in cell_ref if ch.isalpha())
    value = 0
    for ch in letters:
        value = value * 26 + ord(ch.upper()) - 64
    return value - 1


def load_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    values: list[str] = []
    with zf.open("xl/sharedStrings.xml") as fh:
        for _, elem in ET.iterparse(fh, events=("end",)):
            if elem.tag.endswith("}si"):
                texts = [node.text or "" for node in elem.iter() if node.tag.endswith("}t")]
                values.append("".join(texts))
                elem.clear()
    return values


def get_sheet_paths(zf: zipfile.ZipFile) -> dict[str, str]:
    workbook = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    rel_map = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels.findall("pkgrel:Relationship", NS)
    }
    paths: dict[str, str] = {}
    for sheet in workbook.findall("main:sheets/main:sheet", NS):
        name = sheet.attrib["name"]
        rel_id = sheet.attrib[f"{{{NS['rel']}}}id"]
        target = rel_map[rel_id].replace("\\", "/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        paths[name] = target
    return paths


def cell_value(cell: ET.Element, shared: list[str]):
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.iter() if node.tag.endswith("}t"))
    value = cell.find("main:v", NS)
    if value is None or value.text is None:
        return None
    raw = value.text
    if cell_type == "s":
        return shared[int(raw)]
    if cell_type == "b":
        return raw == "1"
    try:
        return float(raw)
    except ValueError:
        return raw


def iter_rows(zf: zipfile.ZipFile, sheet_path: str, shared: list[str]):
    with zf.open(sheet_path) as fh:
        for _, row in ET.iterparse(fh, events=("end",)):
            if not row.tag.endswith("}row"):
                continue
            values = {}
            current_index = -1
            for cell in row.findall("main:c", NS):
                ref = cell.attrib.get("r", "")
                index = col_index(ref) if ref else current_index + 1
                current_index = index
                values[index] = cell_value(cell, shared)
            if values:
                max_col = max(values)
                yield [values.get(i) for i in range(max_col + 1)]
            row.clear()


def read_small_sheet(zf: zipfile.ZipFile, path: str, shared: list[str]) -> list[dict[str, object]]:
    rows = iter_rows(zf, path, shared)
    header = [str(v) if v is not None else "" for v in next(rows)]
    out = []
    for row in rows:
        out.append({header[i]: row[i] if i < len(row) else None for i in range(len(header))})
    return out


def as_float(value):
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number):
        return None
    return number


def longest_internal_gap(values: list[float | None]) -> int:
    valid = [idx for idx, value in enumerate(values) if value is not None]
    if not valid:
        return len(values)
    start, end = min(valid), max(valid)
    best = current = 0
    for value in values[start : end + 1]:
        if value is None:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def interpolate_short_gaps(values: list[float | None]) -> tuple[list[float | None], int]:
    cleaned = values[:]
    filled = 0
    valid = [idx for idx, value in enumerate(cleaned) if value is not None]
    if len(valid) < 2:
        return cleaned, filled
    for left, right in zip(valid, valid[1:]):
        gap = right - left - 1
        if 0 < gap <= 2:
            start, end = cleaned[left], cleaned[right]
            assert start is not None and end is not None
            step = (end - start) / (right - left)
            for offset in range(1, gap + 1):
                cleaned[left + offset] = start + step * offset
                filled += 1
    return cleaned, filled


def clean_country_indicator(values: list[float | None]) -> tuple[list[float | None] | None, str, int]:
    observed = sum(value is not None for value in values)
    if observed == 0:
        return None, "dropped_no_observation", 0
    if longest_internal_gap(values) > 2:
        return None, "dropped_internal_gap_gt_2_years", 0
    cleaned, filled = interpolate_short_gaps(values)
    return cleaned, "kept", filled


def extract_wdi() -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    if not XLSX_PATH.exists():
        raise FileNotFoundError(f"Missing {XLSX_PATH}")
    with zipfile.ZipFile(XLSX_PATH) as zf:
        shared = load_shared_strings(zf)
        paths = get_sheet_paths(zf)
        series_rows = read_small_sheet(zf, paths["Series"], shared)
        country_rows = read_small_sheet(zf, paths["Country"], shared)

        real_countries = {
            str(row["Country Code"]): {
                "Country_Name": row["Table Name"] or row["Short Name"] or row["Country Code"],
                "Country_Code": row["Country Code"],
                "Region": row.get("Region"),
                "Income_Group": row.get("Income Group"),
            }
            for row in country_rows
            if row.get("Region") not in (None, "")
        }

        series_by_code = {str(row["Series Code"]): row for row in series_rows}

        rows = iter_rows(zf, paths["Data"], shared)
        header = [str(v) if v is not None else "" for v in next(rows)]
        idx = {name: header.index(name) for name in ["Country Name", "Country Code", "Indicator Name", "Indicator Code"]}
        year_idx = {year: header.index(year) for year in YEARS if year in header}

        raw = {}
        for row in rows:
            indicator_code = str(row[idx["Indicator Code"]]) if idx["Indicator Code"] < len(row) and row[idx["Indicator Code"]] is not None else ""
            if indicator_code not in INDICATORS:
                continue
            country_code = str(row[idx["Country Code"]]) if idx["Country Code"] < len(row) and row[idx["Country Code"]] is not None else ""
            if country_code not in real_countries:
                continue
            values = [as_float(row[year_idx[year]]) if year_idx[year] < len(row) else None for year in YEARS]
            raw[(country_code, indicator_code)] = values

    indicator_audit = []
    for code, meta in INDICATORS.items():
        series = series_by_code.get(code, {})
        indicator_audit.append(
            {
                "Indicator_Code": code,
                "Clean_Name": meta["clean_name"],
                "Confirmed_In_WDI": "Yes" if code in series_by_code else "No",
                "Indicator_Name": series.get("Indicator Name", meta["label"]),
                "Topic": series.get("Topic", ""),
                "Unit": meta["unit"],
            }
        )

    cleaning_report = []
    long_rows = []
    for country_code, country in real_countries.items():
        for indicator_code, meta in INDICATORS.items():
            values = raw.get((country_code, indicator_code), [None] * len(YEARS))
            cleaned, status, filled = clean_country_indicator(values)
            cleaning_report.append(
                {
                    "Country_Code": country_code,
                    "Country_Name": country["Country_Name"],
                    "Indicator_Code": indicator_code,
                    "Clean_Name": meta["clean_name"],
                    "Observed_Values": sum(value is not None for value in values),
                    "Internal_Max_Missing_Gap": longest_internal_gap(values),
                    "Interpolated_Values": filled,
                    "Status": status,
                }
            )
            if cleaned is None:
                continue
            for year, value in zip(YEARS, cleaned):
                if value is None:
                    continue
                long_rows.append(
                    {
                        **country,
                        "Year": int(year),
                        "Indicator_Code": indicator_code,
                        "Metric": meta["clean_name"],
                        "Value": value,
                    }
                )

    wide_map = {}
    for row in long_rows:
        key = (row["Country_Code"], row["Year"])
        wide = wide_map.setdefault(
            key,
            {
                "Country_Name": row["Country_Name"],
                "Country_Code": row["Country_Code"],
                "Region": row["Region"],
                "Income_Group": row["Income_Group"],
                "Year": row["Year"],
            },
        )
        wide[row["Metric"]] = row["Value"]

    wide_rows = sorted(wide_map.values(), key=lambda r: (str(r["Country_Name"]), int(r["Year"])))
    return wide_rows, indicator_audit, cleaning_report, long_rows


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def number(value, digits=2) -> str:
    if value is None:
        return ""
    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:.{digits}f}B"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.{digits}f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.{digits}f}K"
    return f"{value:.{digits}f}"


def svg_line(rows, title, metric, countries) -> str:
    width, height = 760, 420
    pad_l, pad_t, pad_r, pad_b = 80, 50, 30, 60
    plot_w, plot_h = width - pad_l - pad_r, height - pad_t - pad_b
    series = {}
    vals = []
    for c in countries:
        pts = [(r["Year"], r.get(metric)) for r in rows if r["Country_Name"] == c and r.get(metric) not in (None, "")]
        pts = [(int(y), float(v)) for y, v in pts]
        if pts:
            series[c] = pts
            vals.extend(v for _, v in pts)
    if not vals:
        return ""
    y_min, y_max = min(vals), max(vals)
    if y_min == y_max:
        y_max += 1
    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#17becf"]
    def x(year): return pad_l + (year - 2000) / 23 * plot_w
    def y(value): return pad_t + (y_max - value) / (y_max - y_min) * plot_h
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             f'<text x="{width/2}" y="28" text-anchor="middle" font-size="18" font-family="Arial" font-weight="700">{title}</text>',
             f'<line x1="{pad_l}" y1="{pad_t+plot_h}" x2="{pad_l+plot_w}" y2="{pad_t+plot_h}" stroke="#333"/>',
             f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{pad_t+plot_h}" stroke="#333"/>']
    for yr in [2000, 2005, 2010, 2015, 2020, 2023]:
        parts.append(f'<text x="{x(yr)}" y="{height-28}" text-anchor="middle" font-size="11" font-family="Arial">{yr}</text>')
    for tick in range(5):
        val = y_min + (y_max - y_min) * tick / 4
        yy = y(val)
        parts.append(f'<line x1="{pad_l}" y1="{yy:.1f}" x2="{pad_l+plot_w}" y2="{yy:.1f}" stroke="#eee"/>')
        parts.append(f'<text x="{pad_l-8}" y="{yy+4:.1f}" text-anchor="end" font-size="10" font-family="Arial">{number(val)}</text>')
    for i, (country, pts) in enumerate(series.items()):
        poly = " ".join(f"{x(yr):.1f},{y(val):.1f}" for yr, val in pts)
        color = colors[i % len(colors)]
        parts.append(f'<polyline points="{poly}" fill="none" stroke="{color}" stroke-width="2.4"/>')
        lx, ly = pad_l + plot_w - 145, pad_t + 24 + i * 19
        parts.append(f'<line x1="{lx}" y1="{ly-4}" x2="{lx+20}" y2="{ly-4}" stroke="{color}" stroke-width="3"/>')
        parts.append(f'<text x="{lx+26}" y="{ly}" font-size="12" font-family="Arial">{country}</text>')
    parts.append("</svg>")
    return "".join(parts)


def svg_bar(rows, title, metric, year=2023) -> str:
    width, height = 760, 420
    data = defaultdict(list)
    for r in rows:
        if r["Year"] == year and r.get(metric) not in (None, ""):
            data[r["Region"]].append(float(r[metric]))
    values = [(region, statistics.mean(vals)) for region, vals in data.items() if vals]
    values.sort(key=lambda item: item[1], reverse=True)
    values = values[:8]
    max_v = max(v for _, v in values) if values else 1
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             f'<text x="{width/2}" y="28" text-anchor="middle" font-size="18" font-family="Arial" font-weight="700">{title}</text>']
    x0, y0, bar_h, gap = 260, 58, 30, 15
    for i, (region, value) in enumerate(values):
        y = y0 + i * (bar_h + gap)
        w = (width - x0 - 80) * value / max_v
        parts.append(f'<text x="{x0-12}" y="{y+20}" text-anchor="end" font-size="12" font-family="Arial">{region}</text>')
        parts.append(f'<rect x="{x0}" y="{y}" width="{w:.1f}" height="{bar_h}" fill="#3a7ca5"/>')
        parts.append(f'<text x="{x0+w+6:.1f}" y="{y+20}" font-size="12" font-family="Arial">{number(value)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def svg_scatter(rows, title, x_metric, y_metric, year=2022) -> str:
    width, height = 760, 440
    pts = []
    for r in rows:
        if r["Year"] == year and r.get(x_metric) not in (None, "") and r.get(y_metric) not in (None, ""):
            pts.append((float(r[x_metric]), float(r[y_metric]), r["Country_Name"], r["Region"]))
    pts = pts[:220]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    if not xs or not ys:
        return ""
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    pad_l, pad_t, pad_r, pad_b = 85, 52, 40, 62
    plot_w, plot_h = width - pad_l - pad_r, height - pad_t - pad_b
    colors = {
        "East Asia & Pacific": "#1f77b4",
        "Europe & Central Asia": "#2ca02c",
        "Latin America & Caribbean": "#ff7f0e",
        "Middle East & North Africa": "#9467bd",
        "North America": "#8c564b",
        "South Asia": "#d62728",
        "Sub-Saharan Africa": "#17becf",
    }
    def x(v): return pad_l + (math.log10(v + 1) - math.log10(x_min + 1)) / (math.log10(x_max + 1) - math.log10(x_min + 1)) * plot_w
    def y(v): return pad_t + (y_max - v) / (y_max - y_min) * plot_h
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             f'<text x="{width/2}" y="28" text-anchor="middle" font-size="18" font-family="Arial" font-weight="700">{title}</text>',
             f'<line x1="{pad_l}" y1="{pad_t+plot_h}" x2="{pad_l+plot_w}" y2="{pad_t+plot_h}" stroke="#333"/>',
             f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{pad_t+plot_h}" stroke="#333"/>']
    for xv, yv, country, region in pts:
        parts.append(f'<circle cx="{x(xv):.1f}" cy="{y(yv):.1f}" r="4" fill="{colors.get(region, "#777")}" opacity="0.72"><title>{country}: {number(xv)}, {number(yv)}</title></circle>')
    parts.append(f'<text x="{width/2}" y="{height-18}" text-anchor="middle" font-size="12" font-family="Arial">GDP per capita, log scale</text>')
    parts.append(f'<text x="18" y="{height/2}" transform="rotate(-90 18 {height/2})" text-anchor="middle" font-size="12" font-family="Arial">Poverty headcount (%)</text>')
    parts.append("</svg>")
    return "".join(parts)


def svg_region_choropleth(rows, title, metric, year=2023) -> str:
    width, height = 760, 420
    grouped = defaultdict(list)
    for row in rows:
        if row["Year"] == year and row.get(metric) not in (None, ""):
            grouped[row["Region"]].append(float(row[metric]))
    values = {region: statistics.mean(vals) for region, vals in grouped.items() if vals}
    if not values:
        return ""
    v_min, v_max = min(values.values()), max(values.values())
    layout = {
        "North America": (0, 1),
        "Latin America & Caribbean": (0, 2),
        "Europe & Central Asia": (2, 0),
        "Middle East & North Africa": (2, 1),
        "Sub-Saharan Africa": (2, 2),
        "South Asia": (4, 1),
        "East Asia & Pacific": (5, 1),
    }
    def color(value):
        ratio = 0 if v_max == v_min else (value - v_min) / (v_max - v_min)
        lo, hi = (224, 238, 245), (23, 92, 128)
        rgb = tuple(int(lo[i] + (hi[i] - lo[i]) * ratio) for i in range(3))
        return f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             f'<text x="{width/2}" y="28" text-anchor="middle" font-size="18" font-family="Arial" font-weight="700">{title}</text>',
             '<text x="380" y="55" text-anchor="middle" font-size="11" font-family="Arial" fill="#555">Regional choropleth tile map; use Tableau geographic map for final dashboard</text>']
    tile_w, tile_h = 120, 72
    x0, y0 = 70, 80
    for region, (col, row) in layout.items():
        value = values.get(region)
        fill = color(value) if value is not None else "#eee"
        x, y = x0 + col * 105, y0 + row * 82
        label = region.replace(" & ", " &\n").replace("Middle East", "Middle\nEast")
        parts.append(f'<rect x="{x}" y="{y}" width="{tile_w}" height="{tile_h}" rx="6" fill="{fill}" stroke="#fff" stroke-width="2"/>')
        for j, line in enumerate(label.split("\\n")):
            parts.append(f'<text x="{x+tile_w/2}" y="{y+24+j*14}" text-anchor="middle" font-size="11" font-family="Arial" fill="#111">{line}</text>')
        if value is not None:
            parts.append(f'<text x="{x+tile_w/2}" y="{y+tile_h-12}" text-anchor="middle" font-size="12" font-family="Arial" font-weight="700" fill="#111">{number(value)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def build_notebook(summary: dict[str, object], svgs: dict[str, str]) -> None:
    code = r'''
from pathlib import Path
import numpy as np
import pandas as pd

# Optional visualization dependencies for local rerun.
import matplotlib.pyplot as plt

ROOT = Path.cwd()
if not (ROOT / "WDIEXCEL.xlsx").exists() and (ROOT.parent / "WDIEXCEL.xlsx").exists():
    ROOT = ROOT.parent

DATA_PATH = ROOT / "data_output" / "wdi_economy.csv"
df = pd.read_csv(DATA_PATH)
df.head()
'''
    chart_code = r'''
import matplotlib.pyplot as plt

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

focus_countries = ["United States", "China", "India", "Viet Nam", "Germany", "Brazil"]
fig, ax = plt.subplots(figsize=(10, 5))
for country in focus_countries:
    sub = df[df["Country_Name"].eq(country)]
    ax.plot(sub["Year"], sub["GDP_per_capita_current_USD"], marker="o", linewidth=2, label=country)
ax.set_title("GDP per capita trend, selected countries")
ax.set_xlabel("Year")
ax.set_ylabel("Current US$")
ax.legend()
plt.show()

latest = df[df["Year"].eq(2023)]
region_growth = latest.groupby("Region", as_index=False)["GDP_growth_annual_pct"].mean().sort_values("GDP_growth_annual_pct", ascending=False)
fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(region_growth["Region"], region_growth["GDP_growth_annual_pct"], color="#3a7ca5")
ax.invert_yaxis()
ax.set_title("Average GDP growth by region, 2023")
ax.set_xlabel("Annual growth (%)")
plt.show()

scatter = df[df["Year"].eq(2022)].dropna(subset=["GDP_per_capita_current_USD", "Poverty_headcount_3usd_2021PPP_pct"])
fig, ax = plt.subplots(figsize=(9, 6))
for region, sub in scatter.groupby("Region"):
    ax.scatter(sub["GDP_per_capita_current_USD"], sub["Poverty_headcount_3usd_2021PPP_pct"], s=35, alpha=0.75, label=region)
ax.set_xscale("log")
ax.set_title("GDP per capita vs poverty headcount, 2022")
ax.set_xlabel("GDP per capita, current US$ (log scale)")
ax.set_ylabel("Poverty headcount at $3.00/day (%)")
ax.legend(bbox_to_anchor=(1.03, 1), loc="upper left")
plt.show()
'''
    cells = [
        md("# Lab 02 - Phan tich kinh te WDI\n\n**Phu trach:** Le Lam Tri Duc - 23120237\n\nNotebook nay loc va lam sach nhom chi so kinh te tu World Development Indicators, xuat `data_output/wdi_economy.csv`, va chuan bi cac bieu do phan tich de dua vao Tableau/bao cao."),
        md("## Cau hoi phan tich\n\n- Xu huong tang truong kinh te cua cac quoc gia/khu vuc giai doan 2000-2023 nhu the nao?\n- GDP binh quan dau nguoi co moi quan he gi voi ty le ngheo?\n- Cac cu soc nam 2008 va giai doan COVID-19 co the hien tren GDP growth hay khong?"),
        md("## Indicators su dung\n\n| Indicator code | Cot output | Y nghia |\n|---|---|---|\n| `NY.GDP.MKTP.CD` | `GDP_current_USD` | Quy mo GDP theo USD hien hanh |\n| `NY.GDP.PCAP.CD` | `GDP_per_capita_current_USD` | Muc thu nhap/qui mo kinh te binh quan dau nguoi |\n| `NY.GDP.MKTP.KD.ZG` | `GDP_growth_annual_pct` | Toc do tang truong GDP hang nam |\n| `SI.POV.DDAY` | `Poverty_headcount_3usd_2021PPP_pct` | Ty le dan so song duoi nguong 3 USD/ngay theo PPP 2021 |"),
        code_cell(code),
        md(f"## Ket qua tien xu ly\n\n- So dong trong `wdi_economy.csv`: **{summary['rows']}**\n- So quoc gia/vung lanh tho that co it nhat mot chi so kinh te: **{summary['countries']}**\n- Giai doan: **2000-2023**\n- Quy uoc missing data: noi suy tuyen tinh neu khoang trong noi bo <= 2 nam; loai cap country-indicator neu khoang trong noi bo > 2 nam; khong extrapolate dau/cuoi chuoi."),
        md("## Bieu do 1 - Xu huong GDP per capita\n\nBieu do dung de so sanh muc GDP binh quan dau nguoi cua mot so quoc gia dai dien. Khi dua sang Tableau, dung line chart voi filter Country/Region."),
        svg_cell(svgs.get("line", "")),
        md("## Bieu do 2 - Tang truong GDP theo khu vuc\n\nBieu do thanh cho thay khac biet ve tang truong trung binh giua cac khu vuc trong nam gan nhat co du lieu."),
        svg_cell(svgs.get("bar", "")),
        md("## Bieu do 3 - GDP per capita va ty le ngheo\n\nScatter plot kiem tra moi quan he giua GDP per capita va poverty headcount. Truc X nen dung log scale de tranh cac nuoc thu nhap cao lam nen bieu do."),
        svg_cell(svgs.get("scatter", "")),
        md("## Bieu do 4 - Phan bo GDP per capita theo khu vuc\n\nNotebook tao tile choropleth theo khu vuc de xem nhanh phan bo GDP per capita. Khi lam san pham cuoi cung tren Tableau, thay bang choropleth map theo `Country_Name` hoac `Country_Code`."),
        svg_cell(svgs.get("choropleth", "")),
        md("## Code ve lai bieu do bang matplotlib\n\nCell nay dung khi mo notebook trong moi truong Jupyter co `matplotlib`. Cac bieu do SVG o tren da duoc tao san tu file CSV hien tai."),
        code_cell(chart_code),
        md("## Goi y worksheet Tableau\n\n1. **Line chart:** `Year` tren Columns, `GDP_per_capita_current_USD` tren Rows, `Country_Name` tren Color, filter `Region`/`Income_Group`.\n2. **Bar chart:** `Region` tren Rows, AVG(`GDP_growth_annual_pct`) tren Columns, filter `Year`.\n3. **Scatter plot:** `GDP_per_capita_current_USD` tren Columns, `Poverty_headcount_3usd_2021PPP_pct` tren Rows, `Region` tren Color, `Country_Name` tren Detail.\n4. **Map:** `Country_Name`/`Country_Code` lam geographic role, color theo `GDP_per_capita_current_USD`, filter `Year`."),
        md("## Nhan xet so bo\n\n- GDP per capita tang manh o nhieu quoc gia chau A trong giai doan 2000-2023, nhung muc tuyet doi van chen lech lon so voi nhom thu nhap cao.\n- GDP growth co bien dong ro quanh cac nam khung hoang tai chinh 2008-2009 va COVID-19 2020.\n- Scatter plot ky vong the hien quan he nghich: GDP per capita cang cao thi poverty headcount cang thap, du van co ngoai lai do bat binh dang va khac biet co cau kinh te."),
    ]
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.x"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    NOTEBOOK_PATH.write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding="utf-8")


def md(source: str) -> dict[str, object]:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(True)}


def code_cell(source: str) -> dict[str, object]:
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": source.strip("\n").splitlines(True)}


def svg_cell(svg: str) -> dict[str, object]:
    return {
        "cell_type": "code",
        "execution_count": 1,
        "metadata": {},
        "outputs": [{"data": {"image/svg+xml": svg}, "metadata": {}, "output_type": "display_data"}],
        "source": ["# Pre-rendered SVG chart generated from data_output/wdi_economy.csv\n"],
    }


def main() -> None:
    wide, audit, cleaning, _ = extract_wdi()
    fieldnames = [
        "Country_Name",
        "Country_Code",
        "Region",
        "Income_Group",
        "Year",
        "GDP_current_USD",
        "GDP_per_capita_current_USD",
        "GDP_growth_annual_pct",
        "Poverty_headcount_3usd_2021PPP_pct",
    ]
    write_csv(OUTPUT_DIR / "wdi_economy.csv", wide, fieldnames)
    write_csv(
        OUTPUT_DIR / "wdi_economy_indicator_audit.csv",
        audit,
        ["Indicator_Code", "Clean_Name", "Confirmed_In_WDI", "Indicator_Name", "Topic", "Unit"],
    )
    write_csv(
        OUTPUT_DIR / "wdi_economy_cleaning_report.csv",
        cleaning,
        ["Country_Code", "Country_Name", "Indicator_Code", "Clean_Name", "Observed_Values", "Internal_Max_Missing_Gap", "Interpolated_Values", "Status"],
    )
    summary = {"rows": len(wide), "countries": len({r["Country_Code"] for r in wide})}
    countries = ["United States", "China", "India", "Viet Nam", "Germany", "Brazil"]
    svgs = {
        "line": svg_line(wide, "GDP per capita trend, selected countries", "GDP_per_capita_current_USD", countries),
        "bar": svg_bar(wide, "Average GDP growth by region, 2023", "GDP_growth_annual_pct", 2023),
        "scatter": svg_scatter(wide, "GDP per capita vs poverty headcount, 2022", "GDP_per_capita_current_USD", "Poverty_headcount_3usd_2021PPP_pct", 2022),
        "choropleth": svg_region_choropleth(wide, "GDP per capita by region, 2023", "GDP_per_capita_current_USD", 2023),
    }
    build_notebook(summary, svgs)
    print(f"Wrote {OUTPUT_DIR / 'wdi_economy.csv'} ({len(wide)} rows)")
    print(f"Wrote {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()
