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
NOTEBOOK_PATH = ROOT / "notebook" / "Nhom15_SucKhoe_NguyenLeTheVinh.ipynb"

YEARS = [str(y) for y in range(2000, 2024)]
INDICATORS = {
    "SP.DYN.LE00.IN": {
        "clean_name": "Life_expectancy",
        "label": "Life expectancy at birth, total (years)",
        "unit": "years",
    },
    "SH.DYN.MORT": {
        "clean_name": "Under5_mortality",
        "label": "Mortality rate, under-5 (per 1,000 live births)",
        "unit": "per 1,000 live births",
    },
    "SH.XPD.CHEX.GD.ZS": {
        "clean_name": "Health_expenditure_pct_GDP",
        "label": "Current health expenditure (% of GDP)",
        "unit": "% of GDP",
    },
    "SP.POP.TOTL": {
        "clean_name": "Population",
        "label": "Population, total",
        "unit": "people",
    },
}

NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pkgrel": "http://schemas.openxmlformats.org/package/2006/relationships",
}


# ---------------------------------------------------------------------------
# XLSX reader (same approach as economy_wdi_builder.py)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Data cleaning utilities
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Main extraction
# ---------------------------------------------------------------------------

def extract_wdi() -> tuple[list[dict], list[dict], list[dict], list[dict]]:
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

    # --- Indicator audit ---
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

    # --- Clean & pivot to long then wide ---
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


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


# ---------------------------------------------------------------------------
# SVG chart helpers (for pre-rendered notebook output)
# ---------------------------------------------------------------------------

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


REGION_COLORS = {
    "East Asia & Pacific": "#2F6B9A",
    "Europe & Central Asia": "#6A8E3F",
    "Latin America & Caribbean": "#C47A2C",
    "Middle East & North Africa": "#8E5A9F",
    "North America": "#4A4A4A",
    "South Asia": "#B24A4A",
    "Sub-Saharan Africa": "#2A8C8C",
}

FOCUS_COUNTRIES = [
    "United States", "China", "India", "Viet Nam",
    "Japan", "Brazil", "Nigeria", "Germany",
]


def svg_multiline(rows, title, metric, countries) -> str:
    """Chart 1: Multi-line chart — Life expectancy trends."""
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
    colors = ["#B24A4A", "#2F6B9A", "#2A8C8C", "#C47A2C", "#6A8E3F", "#8E5A9F", "#4A4A4A", "#D4764E"]
    def x(year): return pad_l + (year - 2000) / 23 * plot_w
    def y(value): return pad_t + (y_max - value) / (y_max - y_min) * plot_h
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="28" text-anchor="middle" font-size="18" font-family="Arial" font-weight="700">{title}</text>',
        f'<line x1="{pad_l}" y1="{pad_t+plot_h}" x2="{pad_l+plot_w}" y2="{pad_t+plot_h}" stroke="#333"/>',
        f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{pad_t+plot_h}" stroke="#333"/>',
    ]
    for yr in [2000, 2005, 2010, 2015, 2020, 2023]:
        parts.append(f'<text x="{x(yr)}" y="{height-28}" text-anchor="middle" font-size="11" font-family="Arial">{yr}</text>')
    for tick in range(5):
        val = y_min + (y_max - y_min) * tick / 4
        yy = y(val)
        parts.append(f'<line x1="{pad_l}" y1="{yy:.1f}" x2="{pad_l+plot_w}" y2="{yy:.1f}" stroke="#eee"/>')
        parts.append(f'<text x="{pad_l-8}" y="{yy+4:.1f}" text-anchor="end" font-size="10" font-family="Arial">{number(val, 1)}</text>')
    for i, (country, pts) in enumerate(series.items()):
        poly = " ".join(f"{x(yr):.1f},{y(val):.1f}" for yr, val in pts)
        color = colors[i % len(colors)]
        parts.append(f'<polyline points="{poly}" fill="none" stroke="{color}" stroke-width="2.4"/>')
        lx, ly = pad_l + plot_w - 165, pad_t + 24 + i * 19
        parts.append(f'<line x1="{lx}" y1="{ly-4}" x2="{lx+20}" y2="{ly-4}" stroke="{color}" stroke-width="3"/>')
        parts.append(f'<text x="{lx+26}" y="{ly}" font-size="12" font-family="Arial">{country}</text>')
    parts.append(f'<text x="{width/2}" y="{height-10}" text-anchor="middle" font-size="12" font-family="Arial">Year</text>')
    parts.append(f'<text x="18" y="{height/2}" transform="rotate(-90 18 {height/2})" text-anchor="middle" font-size="12" font-family="Arial">Life expectancy (years)</text>')
    parts.append("</svg>")
    return "".join(parts)


def svg_bar_mortality(rows, title, metric, year=2022) -> str:
    """Chart 2: Bar chart — Under-5 mortality by region."""
    width, height = 760, 420
    data = defaultdict(list)
    for r in rows:
        if r["Year"] == year and r.get(metric) not in (None, ""):
            data[r["Region"]].append(float(r[metric]))
    values = [(region, statistics.mean(vals)) for region, vals in data.items() if vals]
    values.sort(key=lambda item: item[1], reverse=True)
    values = values[:8]
    max_v = max(v for _, v in values) if values else 1
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="28" text-anchor="middle" font-size="18" font-family="Arial" font-weight="700">{title}</text>',
    ]
    x0, y0, bar_h, gap = 280, 58, 35, 12
    for i, (region, value) in enumerate(values):
        y = y0 + i * (bar_h + gap)
        w = (width - x0 - 80) * value / max_v
        color = REGION_COLORS.get(region, "#B24A4A")
        parts.append(f'<text x="{x0-12}" y="{y+22}" text-anchor="end" font-size="12" font-family="Arial">{region}</text>')
        parts.append(f'<rect x="{x0}" y="{y}" width="{w:.1f}" height="{bar_h}" fill="{color}" rx="3"/>')
        parts.append(f'<text x="{x0+w+6:.1f}" y="{y+22}" font-size="12" font-family="Arial" font-weight="600">{number(value, 1)}</text>')
    parts.append(f'<text x="{width/2}" y="{height-15}" text-anchor="middle" font-size="12" font-family="Arial">Under-5 mortality rate (per 1,000 live births)</text>')
    parts.append("</svg>")
    return "".join(parts)


def svg_bubble(rows, title, x_metric, y_metric, size_metric, year=2022) -> str:
    """Chart 3: Bubble scatter — Health expenditure vs life expectancy, size=population."""
    width, height = 760, 480
    pts = []
    for r in rows:
        if r["Year"] == year and r.get(x_metric) not in (None, "") and r.get(y_metric) not in (None, "") and r.get(size_metric) not in (None, ""):
            pts.append((float(r[x_metric]), float(r[y_metric]), float(r[size_metric]), r["Country_Name"], r["Region"]))
    pts = pts[:220]
    if not pts:
        return ""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    pops = [p[2] for p in pts]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    pop_max = max(pops) if pops else 1
    pad_l, pad_t, pad_r, pad_b = 85, 52, 40, 72
    plot_w, plot_h = width - pad_l - pad_r, height - pad_t - pad_b

    def x(v): return pad_l + (v - x_min) / (x_max - x_min) * plot_w if x_max != x_min else pad_l + plot_w / 2
    def y(v): return pad_t + (y_max - v) / (y_max - y_min) * plot_h if y_max != y_min else pad_t + plot_h / 2
    def radius(pop): return max(3, min(28, 3 + 25 * math.sqrt(pop / pop_max)))

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="28" text-anchor="middle" font-size="18" font-family="Arial" font-weight="700">{title}</text>',
        f'<line x1="{pad_l}" y1="{pad_t+plot_h}" x2="{pad_l+plot_w}" y2="{pad_t+plot_h}" stroke="#333"/>',
        f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{pad_t+plot_h}" stroke="#333"/>',
    ]
    # Grid lines
    for tick in range(5):
        yv = y_min + (y_max - y_min) * tick / 4
        yy = y(yv)
        parts.append(f'<line x1="{pad_l}" y1="{yy:.1f}" x2="{pad_l+plot_w}" y2="{yy:.1f}" stroke="#eee"/>')
        parts.append(f'<text x="{pad_l-8}" y="{yy+4:.1f}" text-anchor="end" font-size="10" font-family="Arial">{yv:.1f}</text>')
    for tick in range(5):
        xv = x_min + (x_max - x_min) * tick / 4
        xx = x(xv)
        parts.append(f'<text x="{xx:.1f}" y="{pad_t+plot_h+18}" text-anchor="middle" font-size="10" font-family="Arial">{xv:.1f}%</text>')
    # Bubbles
    for xv, yv, pop, country, region in pts:
        r = radius(pop)
        color = REGION_COLORS.get(region, "#777")
        parts.append(f'<circle cx="{x(xv):.1f}" cy="{y(yv):.1f}" r="{r:.1f}" fill="{color}" opacity="0.6"><title>{country}: exp={xv:.1f}% GDP, LE={yv:.1f}y, pop={number(pop)}</title></circle>')
    # Axis labels
    parts.append(f'<text x="{width/2}" y="{height-18}" text-anchor="middle" font-size="12" font-family="Arial">Health expenditure (% of GDP)</text>')
    parts.append(f'<text x="18" y="{height/2}" transform="rotate(-90 18 {height/2})" text-anchor="middle" font-size="12" font-family="Arial">Life expectancy (years)</text>')
    # Legend
    lx, ly = pad_l + plot_w - 180, pad_t + 10
    for i, (region, color) in enumerate(REGION_COLORS.items()):
        parts.append(f'<circle cx="{lx}" cy="{ly + i * 17}" r="5" fill="{color}"/>')
        parts.append(f'<text x="{lx+10}" y="{ly + i * 17 + 4}" font-size="10" font-family="Arial">{region}</text>')
    parts.append("</svg>")
    return "".join(parts)


def svg_boxplot(rows, title, metric) -> str:
    """Chart 4: Box plot — Life expectancy distribution by region."""
    width, height = 760, 420
    pad_l, pad_t, pad_r, pad_b = 280, 50, 40, 50
    plot_w, plot_h = width - pad_l - pad_r, height - pad_t - pad_b

    grouped = defaultdict(list)
    for r in rows:
        if r.get(metric) not in (None, ""):
            grouped[r["Region"]].append(float(r[metric]))
    if not grouped:
        return ""

    all_vals = [v for vals in grouped.values() for v in vals]
    v_min, v_max = min(all_vals), max(all_vals)
    margin = (v_max - v_min) * 0.05
    v_min -= margin
    v_max += margin

    regions = sorted(grouped.keys())
    n = len(regions)
    box_h = max(12, min(30, (plot_h - 20) // n))
    gap = max(4, (plot_h - n * box_h) // (n + 1))

    def x(v): return pad_l + (v - v_min) / (v_max - v_min) * plot_w

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="28" text-anchor="middle" font-size="18" font-family="Arial" font-weight="700">{title}</text>',
    ]
    # X axis ticks
    for tick in range(6):
        val = v_min + (v_max - v_min) * tick / 5
        xx = x(val)
        parts.append(f'<line x1="{xx:.1f}" y1="{pad_t}" x2="{xx:.1f}" y2="{pad_t+plot_h}" stroke="#eee"/>')
        parts.append(f'<text x="{xx:.1f}" y="{height-20}" text-anchor="middle" font-size="10" font-family="Arial">{val:.1f}</text>')

    for i, region in enumerate(regions):
        vals = sorted(grouped[region])
        q1 = vals[len(vals) // 4]
        median = vals[len(vals) // 2]
        q3 = vals[3 * len(vals) // 4]
        lo = vals[0]
        hi = vals[-1]
        cy = pad_t + gap + i * (box_h + gap) + box_h / 2
        color = REGION_COLORS.get(region, "#B24A4A")

        # Whiskers
        parts.append(f'<line x1="{x(lo):.1f}" y1="{cy:.1f}" x2="{x(q1):.1f}" y2="{cy:.1f}" stroke="{color}" stroke-width="1.5"/>')
        parts.append(f'<line x1="{x(q3):.1f}" y1="{cy:.1f}" x2="{x(hi):.1f}" y2="{cy:.1f}" stroke="{color}" stroke-width="1.5"/>')
        # Whisker caps
        parts.append(f'<line x1="{x(lo):.1f}" y1="{cy-box_h/4:.1f}" x2="{x(lo):.1f}" y2="{cy+box_h/4:.1f}" stroke="{color}" stroke-width="1.5"/>')
        parts.append(f'<line x1="{x(hi):.1f}" y1="{cy-box_h/4:.1f}" x2="{x(hi):.1f}" y2="{cy+box_h/4:.1f}" stroke="{color}" stroke-width="1.5"/>')
        # Box
        parts.append(f'<rect x="{x(q1):.1f}" y="{cy-box_h/2:.1f}" width="{x(q3)-x(q1):.1f}" height="{box_h}" fill="{color}" opacity="0.3" stroke="{color}" stroke-width="1.5" rx="2"/>')
        # Median line
        parts.append(f'<line x1="{x(median):.1f}" y1="{cy-box_h/2:.1f}" x2="{x(median):.1f}" y2="{cy+box_h/2:.1f}" stroke="{color}" stroke-width="2.5"/>')
        # Label
        parts.append(f'<text x="{pad_l-12}" y="{cy+4:.1f}" text-anchor="end" font-size="11" font-family="Arial">{region}</text>')

    parts.append(f'<text x="{width/2}" y="{height-4}" text-anchor="middle" font-size="12" font-family="Arial">Life expectancy (years)</text>')
    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# Notebook builder
# ---------------------------------------------------------------------------

def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(True)}


def code_cell(source: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": source.strip("\n").splitlines(True)}


def svg_cell(svg: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": 1,
        "metadata": {},
        "outputs": [{"data": {"image/svg+xml": svg}, "metadata": {}, "output_type": "display_data"}],
        "source": ["# Pre-rendered SVG chart generated from data_output/wdi_health.csv\n"],
    }


def build_notebook(summary: dict, svgs: dict) -> None:
    code = r'''
from pathlib import Path
import numpy as np
import pandas as pd

# Optional visualization dependencies for local rerun.
import matplotlib.pyplot as plt

ROOT = Path.cwd()
if not (ROOT / "WDIEXCEL.xlsx").exists() and (ROOT.parent / "WDIEXCEL.xlsx").exists():
    ROOT = ROOT.parent

DATA_PATH = ROOT / "data_output" / "wdi_health.csv"
df = pd.read_csv(DATA_PATH)
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"Countries: {df['Country_Code'].nunique()}")
print(f"Year range: {df['Year'].min()} - {df['Year'].max()}")
df.head(10)
'''
    stats_code = r'''
# Thong ke mo ta cho cac chi so suc khoe
health_cols = ["Life_expectancy", "Under5_mortality", "Health_expenditure_pct_GDP", "Population"]
desc = df[health_cols].describe().round(2)
print(desc.to_string())
'''
    chart_code = r'''
import matplotlib.pyplot as plt

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

# --- Chart 1: Life expectancy trends ---
focus_countries = ["United States", "China", "India", "Viet Nam", "Japan", "Brazil", "Nigeria", "Germany"]
fig, ax = plt.subplots(figsize=(11, 5))
for country in focus_countries:
    sub = df[df["Country_Name"].eq(country)]
    ax.plot(sub["Year"], sub["Life_expectancy"], marker="o", markersize=3, linewidth=2, label=country)
ax.set_title("Life expectancy at birth, selected countries (2000-2023)")
ax.set_xlabel("Year")
ax.set_ylabel("Life expectancy (years)")
ax.legend(bbox_to_anchor=(1.03, 1), loc="upper left")
plt.tight_layout()
plt.show()

# --- Chart 2: Under-5 mortality by region ---
latest = df[df["Year"].eq(2022)].dropna(subset=["Under5_mortality"])
region_mort = latest.groupby("Region", as_index=False)["Under5_mortality"].mean().sort_values("Under5_mortality", ascending=False)
fig, ax = plt.subplots(figsize=(10, 5))
colors_map = {
    "East Asia & Pacific": "#2F6B9A", "Europe & Central Asia": "#6A8E3F",
    "Latin America & Caribbean": "#C47A2C", "Middle East & North Africa": "#8E5A9F",
    "North America": "#4A4A4A", "South Asia": "#B24A4A", "Sub-Saharan Africa": "#2A8C8C",
}
bar_colors = [colors_map.get(r, "#B24A4A") for r in region_mort["Region"]]
ax.barh(region_mort["Region"], region_mort["Under5_mortality"], color=bar_colors)
ax.invert_yaxis()
ax.set_title("Average under-5 mortality rate by region, 2022")
ax.set_xlabel("Per 1,000 live births")
plt.tight_layout()
plt.show()

# --- Chart 3: Health expenditure vs life expectancy (bubble) ---
scatter = df[df["Year"].eq(2022)].dropna(subset=["Health_expenditure_pct_GDP", "Life_expectancy", "Population"])
fig, ax = plt.subplots(figsize=(10, 7))
for region, sub in scatter.groupby("Region"):
    sizes = sub["Population"] / sub["Population"].max() * 500
    ax.scatter(sub["Health_expenditure_pct_GDP"], sub["Life_expectancy"],
               s=sizes, alpha=0.6, label=region, color=colors_map.get(region, "#777"))
ax.set_title("Health expenditure vs life expectancy, 2022 (bubble size = population)")
ax.set_xlabel("Health expenditure (% of GDP)")
ax.set_ylabel("Life expectancy (years)")
ax.legend(bbox_to_anchor=(1.03, 1), loc="upper left")
plt.tight_layout()
plt.show()

# --- Chart 4: Box plot - life expectancy by region ---
import pandas as pd
regions = sorted(df["Region"].dropna().unique())
fig, ax = plt.subplots(figsize=(10, 6))
box_data = [df[df["Region"].eq(r)]["Life_expectancy"].dropna().values for r in regions]
bp = ax.boxplot(box_data, vert=False, labels=regions, patch_artist=True)
for patch, region in zip(bp["boxes"], regions):
    patch.set_facecolor(colors_map.get(region, "#B24A4A"))
    patch.set_alpha(0.4)
ax.set_title("Life expectancy distribution by region (2000-2023)")
ax.set_xlabel("Life expectancy (years)")
plt.tight_layout()
plt.show()
'''
    cells = [
        md("# Lab 02 — Phan tich suc khoe va dan so (WDI)\n\n"
           "**Phu trach:** Nguyen Le The Vinh — 23120190\n\n"
           "Notebook nay loc va lam sach nhom chi so suc khoe tu World Development Indicators (WDI),\n"
           "xuat `data_output/wdi_health.csv`, va tao cac bieu do phan tich de dua vao Tableau/bao cao."),
        md("## Cau hoi phan tich\n\n"
           "- Tuoi tho trung binh va ty le tu vong tre em thay doi ra sao trong giai doan 2000-2023?\n"
           "- Chi tieu y te co anh huong den ket qua suc khoe khong?\n"
           "- Dai dich COVID-19 (2020-2021) tac dong the nao len tuoi tho trung binh?\n"
           "- Khu vuc nao con co ty le tu vong tre em cao bat thuong?"),
        md("## Indicators su dung\n\n"
           "| Indicator code | Cot output | Y nghia | Don vi |\n"
           "|---|---|---|---|\n"
           "| `SP.DYN.LE00.IN` | `Life_expectancy` | Tuoi tho trung binh tinh tu luc sinh. Phan anh chat luong y te va dieu kien song tong the cua quoc gia. | years |\n"
           "| `SH.DYN.MORT` | `Under5_mortality` | Ty le tu vong tre em duoi 5 tuoi. Chi bao quan trong ve y te co ban, dinh duong va ve sinh. | per 1,000 live births |\n"
           "| `SH.XPD.CHEX.GD.ZS` | `Health_expenditure_pct_GDP` | Chi tieu y te hien thoi tinh theo phan tram GDP. Do muc dau tu cua quoc gia cho y te. | % of GDP |\n"
           "| `SP.POP.TOTL` | `Population` | Tong dan so. Dung lam size trong bubble chart va dat ngu canh dan so. | people |"),
        md("## Ly do chon cac chi so\n\n"
           "1. **Life expectancy** la chi so tong hop phan anh ket qua cua he thong y te, dieu kien kinh te va moi truong song. No la thang do 'outcome' quan trong nhat.\n"
           "2. **Under-5 mortality** tap trung vao nhom dan so de bi ton thuong nhat — tre em. Giam tu vong tre em la muc tieu phat trien ben vung (SDG 3.2).\n"
           "3. **Health expenditure (% GDP)** do muc dau tu 'input', giup phan tich moi lien he giua dau tu y te va ket qua suc khoe.\n"
           "4. **Population** dung lam bien kich thuoc (bubble chart) de dat cac chi so vao boi canh quy mo quoc gia.\n\n"
           "> **Luu y:** Khi nhan xet, can phan biet ro *tuong quan* (correlation) voi *nhan qua* (causation). Chi tieu y te cao khong nhat thiet gay ra tuoi tho cao — co nhieu yeu to gay nhieu (confounders) nhu thu nhap, giao duc, moi truong."),
        code_cell(code),
        md(f"## Ket qua tien xu ly\n\n"
           f"- So dong trong `wdi_health.csv`: **{summary['rows']}**\n"
           f"- So quoc gia/vung lanh tho co it nhat mot chi so suc khoe: **{summary['countries']}**\n"
           f"- Giai doan: **2000-2023**\n"
           f"- Quy uoc missing data: noi suy tuyen tinh neu khoang trong noi bo <= 2 nam; loai cap country-indicator neu khoang trong noi bo > 2 nam; khong extrapolate dau/cuoi chuoi.\n\n"
           f"### Thong ke so luong theo indicator:\n"
           f"| Indicator | Quoc gia co data | Observations |\n"
           f"|---|---|---|\n"
           f"| Life_expectancy | {summary.get('le_countries', '—')} | {summary.get('le_obs', '—')} |\n"
           f"| Under5_mortality | {summary.get('mort_countries', '—')} | {summary.get('mort_obs', '—')} |\n"
           f"| Health_expenditure_pct_GDP | {summary.get('hexp_countries', '—')} | {summary.get('hexp_obs', '—')} |\n"
           f"| Population | {summary.get('pop_countries', '—')} | {summary.get('pop_obs', '—')} |"),
        md("## Thong ke mo ta (Descriptive Statistics)"),
        code_cell(stats_code),
        md("## Bieu do 1 — Xu huong tuoi tho trung binh (Multi-line chart)\n\n"
           "Bieu do duong nhieu nhom the hien su thay doi tuoi tho trung binh cua cac quoc gia dai dien qua thoi gian.\n"
           "Chu y quan sat:\n"
           "- Xu huong tang chung o hau het cac quoc gia\n"
           "- Vet lom nam 2020-2021 do anh huong cua COVID-19\n"
           "- Khoang cach lon giua cac quoc gia chau Phi va cac nuoc phat trien"),
        svg_cell(svgs.get("multiline", "")),
        md("## Bieu do 2 — Ty le tu vong tre em theo khu vuc (Bar chart)\n\n"
           "Bieu do thanh so sanh ty le tu vong tre em duoi 5 tuoi trung binh giua cac khu vuc.\n"
           "Sub-Saharan Africa co ty le cao nhat, cho thay thach thuc lon ve y te co ban."),
        svg_cell(svgs.get("bar_mortality", "")),
        md("## Bieu do 3 — Chi tieu y te vs Tuoi tho (Bubble scatter plot)\n\n"
           "Bubble scatter plot ket hop 3 chieu du lieu:\n"
           "- Truc X: chi tieu y te (% GDP)\n"
           "- Truc Y: tuoi tho trung binh (years)\n"
           "- Kich thuoc bong: dan so\n"
           "- Mau: khu vuc dia ly\n\n"
           "> Luu y: Mot so quoc gia chi nhieu cho y te nhung tuoi tho khong tuong xung cao — do cau truc chi tieu (curative vs preventive), bat binh dang trong tiep can y te."),
        svg_cell(svgs.get("bubble", "")),
        md("## Bieu do 4 — Phan bo tuoi tho theo khu vuc (Box plot)\n\n"
           "Box plot cho thay phan bo tuoi tho o moi khu vuc qua toan bo giai doan 2000-2023.\n"
           "Giup nhan ra khu vuc co phan bo rong (bat binh dang lon giua cac quoc gia) va cac outliers."),
        svg_cell(svgs.get("boxplot", "")),
        md("## Code ve lai bieu do bang matplotlib\n\n"
           "Cell nay dung khi mo notebook trong moi truong Jupyter co `matplotlib`. Cac bieu do SVG o tren da duoc tao san tu file CSV hien tai."),
        code_cell(chart_code),
        md("## Goi y worksheet Tableau\n\n"
           "1. **Multi-line chart:** `Year` tren Columns, `Life_expectancy` tren Rows, `Country_Name` tren Color, filter `Region`/`Year`.\n"
           "2. **Bar chart:** `Region` tren Rows, AVG(`Under5_mortality`) tren Columns, filter `Year`. Color theo Region.\n"
           "3. **Bubble scatter:** `Health_expenditure_pct_GDP` tren Columns, `Life_expectancy` tren Rows, `Population` tren Size, `Region` tren Color, `Country_Name` tren Detail.\n"
           "4. **Box plot:** `Region` tren Columns (hoac Rows), `Life_expectancy` tren kia. Dung Reference Line > Box Plot.\n\n"
           "**Mau chu de suc khoe:** `#B24A4A` (do tram). Palette vung dia ly theo Nhom15_Color_Palette.md."),
        md("## Nhan xet so bo\n\n"
           "- Tuoi tho trung binh tang deu o hau het cac khu vuc trong giai doan 2000-2023, nhung van con khoang cach lon giua Sub-Saharan Africa va cac khu vuc khac.\n"
           "- Tu vong tre em giam manh toan cau, dac biet o Nam A va Dong Nam A, nhung Sub-Saharan Africa van cao nhat.\n"
           "- Bubble chart cho thay moi quan he duong giua chi tieu y te va tuoi tho, nhung ban chat khong hoan toan tuyen tinh — nhieu yeu to khac (GDP, giao duc, co so ha tang) cung dong vai tro.\n"
           "- COVID-19 (2020-2021) gay ra su sut giam tuoi tho o nhieu quoc gia, ro nhat o My Latinh va Nam A.\n"
           "- Box plot cho thay Sub-Saharan Africa co phan bo rong nhat, phan anh bat binh dang lon ve ket qua suc khoe giua cac quoc gia trong khu vuc."),
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


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    wide, audit, cleaning, _ = extract_wdi()

    fieldnames = [
        "Country_Name",
        "Country_Code",
        "Region",
        "Income_Group",
        "Year",
        "Life_expectancy",
        "Under5_mortality",
        "Health_expenditure_pct_GDP",
        "Population",
    ]
    write_csv(OUTPUT_DIR / "wdi_health.csv", wide, fieldnames)
    write_csv(
        OUTPUT_DIR / "wdi_health_indicator_audit.csv",
        audit,
        ["Indicator_Code", "Clean_Name", "Confirmed_In_WDI", "Indicator_Name", "Topic", "Unit"],
    )
    write_csv(
        OUTPUT_DIR / "wdi_health_cleaning_report.csv",
        cleaning,
        ["Country_Code", "Country_Name", "Indicator_Code", "Clean_Name", "Observed_Values", "Internal_Max_Missing_Gap", "Interpolated_Values", "Status"],
    )

    # Compute summary stats for notebook
    summary = {
        "rows": len(wide),
        "countries": len({r["Country_Code"] for r in wide}),
    }
    for metric_key, prefix in [("Life_expectancy", "le"), ("Under5_mortality", "mort"),
                                ("Health_expenditure_pct_GDP", "hexp"), ("Population", "pop")]:
        metric_rows = [r for r in wide if r.get(metric_key) not in (None, "")]
        summary[f"{prefix}_countries"] = len({r["Country_Code"] for r in metric_rows})
        summary[f"{prefix}_obs"] = len(metric_rows)

    # Generate SVG charts
    svgs = {
        "multiline": svg_multiline(wide, "Life expectancy at birth, selected countries (2000-2023)",
                                   "Life_expectancy", FOCUS_COUNTRIES),
        "bar_mortality": svg_bar_mortality(wide, "Average under-5 mortality rate by region, 2022",
                                          "Under5_mortality", 2022),
        "bubble": svg_bubble(wide, "Health expenditure vs life expectancy, 2022 (bubble size = population)",
                             "Health_expenditure_pct_GDP", "Life_expectancy", "Population", 2022),
        "boxplot": svg_boxplot(wide, "Life expectancy distribution by region (all years)",
                               "Life_expectancy"),
    }

    build_notebook(summary, svgs)
    print(f"Wrote {OUTPUT_DIR / 'wdi_health.csv'} ({len(wide)} rows, {summary['countries']} countries)")
    print(f"Wrote {OUTPUT_DIR / 'wdi_health_indicator_audit.csv'}")
    print(f"Wrote {OUTPUT_DIR / 'wdi_health_cleaning_report.csv'}")
    print(f"Wrote {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()
