
"""Stock reports.

`src/shop/reporting.py` is the second file to repair: it produces the text that
the warehouse reads every morning, so both its numbers and its timestamps matter.
"""

from shop.reporting import build_stock_report, stock_health

STOCK = {"SKU-1": 12, "SKU-2": 3}
PRICES = {"SKU-1": 1_990, "SKU-2": 49_900}


def test_report_contains_a_line_per_sku() -> None:
    report = build_stock_report(STOCK, PRICES)
    assert "SKU-1: 12 x 19.90 = 238.80" in report
    assert "SKU-2: 3 x 499.00 = 1497.00" in report


def test_report_sorts_lines_by_sku() -> None:
    report = build_stock_report({"SKU-2": 3, "SKU-1": 12}, PRICES)
    assert report.index("SKU-1:") < report.index("SKU-2:")


def test_report_contains_total_value() -> None:
    report = build_stock_report(STOCK, PRICES)
    assert "total value: 1735.80" in report


def test_report_lists_low_stock_items() -> None:
    report = build_stock_report(STOCK, PRICES)
    assert "low stock: SKU-2" in report


def test_report_timestamp_is_timezone_aware() -> None:
    report = build_stock_report({},{})
    stamps = [line for line in report.splitlines() if line.startswith("generated_at")]
    assert len(stamps) == 1
    ts = stamps[0].removeprefix("generated_at=")
    assert ts.endswith("+00:00") or ts.endswith("Z")


def test_stock_health_reports_out_of_stock() -> None:
    assert stock_health(0, 0, 0) == "out_of_stock"


def test_stock_health_reports_low_without_incoming() -> None:
    assert stock_health(4, 0, 70) == "low"


def test_stock_health_reports_low_with_incoming() -> None:
    assert stock_health(4, 50, 70) == "incoming_low"


def test_stock_health_reports_unknown_demand() -> None:
    assert stock_health(20, 10, 0) == "unknown_demand"


def test_stock_health_reports_reorder_soon() -> None:
    assert stock_health(25, 0, 70) == "reorder_soon"


def test_stock_health_reports_ok() -> None:
    assert stock_health(100, 10, 70) == "ok"
