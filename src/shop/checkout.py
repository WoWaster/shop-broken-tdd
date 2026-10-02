"""Order checkout.

The rules live in `src/shop/specs/checkout.md` - read it first.
Both functions below are stubs: their signature is final, the bodies are yours.
Do not change the constants: the tests rely on them.
"""

from shop.money import percent_of

PROMO_CODES = {"WELCOME10": 10, "SUMMER15": 15, "VIP35": 35}
SUPPORTED_CITIES = ("msk", "spb")
MAX_DISCOUNT_PERCENT = 30
VAT_PERCENT = 20
SHIPPING_KOPEKS = 49_000
FREE_DELIVERY_FROM_KOPEKS = 500_000
TIER_DISCOUNTS = ((10, 5), (25, 10), (50, 15))
REQUIRED_LINE_KEYS = ("sku", "qty", "unit_price_kopecks")


def _parse_int(value: str | int | None) -> int | None:
    """Convert a warehouse value to int or None when parsing fails."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _validate_line(line: dict[str, str], index: int) -> str | None:
    """Validate a single order line and return the first rejecting reason."""
    for key in REQUIRED_LINE_KEYS:
        if key not in line:
            return f"line {index} is missing {key}"

    sku = line.get("sku", "")
    if not isinstance(sku, str) or not sku.strip():
        return f"line {index} has an empty sku"

    qty = _parse_int(line.get("qty"))
    if qty is None:
        return f"line {index} qty is not an integer"
    if qty <= 0:
        return f"line {index} qty must be greater than zero"

    price = _parse_int(line.get("unit_price_kopecks"))
    if price is None:
        return f"line {index} unit_price_kopecks is not an integer"
    if price < 0:
        return f"line {index} unit_price_kopecks cannot be negative"

    return None


def validate_order(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> str | None:
    """Return a human readable reason why the order is invalid, or None if it is fine."""
    if not lines:
        return "order has no lines"

    seen_skus: set[str] = set()
    for index, line in enumerate(lines, start=1):
        if not isinstance(line, dict):
            return f"line {index} is not a mapping"

        reason = _validate_line(line, index)
        if reason is not None:
            return reason

        sku = str(line["sku"])
        if sku in seen_skus:
            return f"duplicate sku: {sku}"
        seen_skus.add(sku)

    if promo_code and promo_code not in PROMO_CODES:
        return "unknown promo code"

    if shipping_city and shipping_city not in SUPPORTED_CITIES:
        return "unsupported shipping city"

    return None


def calculate_order_total(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> int | None:
    """Return the order total in kopecks, or None if the order is invalid."""
    if validate_order(lines, promo_code, shipping_city) is not None:
        return None

    subtotal = 0
    total_qty = 0
    for line in lines:
        qty = _parse_int(line["qty"])
        price = _parse_int(line["unit_price_kopecks"])
        if qty is None or price is None:
            return None
        subtotal += qty * price
        total_qty += qty

    tier_percent = 0
    for threshold, percent in TIER_DISCOUNTS:
        if total_qty >= threshold:
            tier_percent = percent

    promo_percent = PROMO_CODES.get(promo_code, 0) if promo_code else 0
    discount_percent = max(tier_percent, promo_percent)
    discount_percent = min(discount_percent, MAX_DISCOUNT_PERCENT)

    discount = percent_of(subtotal, discount_percent)
    discounted_subtotal = subtotal - discount

    shipping_cost = 0
    if shipping_city and discounted_subtotal < FREE_DELIVERY_FROM_KOPEKS:
        shipping_cost = SHIPPING_KOPEKS

    base = discounted_subtotal + shipping_cost
    vat = percent_of(base, VAT_PERCENT)
    return base + vat
