"""Order checkout.

The rules live in `src/shop/specs/checkout.md` - read it first.
Do not change the constants: the tests rely on them.
Money is an integer amount of kopecks, percentages are integer only.
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


def _parse_int(value: str) -> int | None:
    """Parse a signed decimal integer, returning None instead of raising."""
    text = value.strip()
    if not text:
        return None
    sign = 1
    if text.startswith("-"):
        sign = -1
        text = text[1:]
    elif text.startswith("+"):
        text = text[1:]
    if not text.isascii() or not text.isdigit():
        return None
    return sign * int(text)


def _validate_line(index: int, line: dict[str, str], seen: set[str]) -> str | None:
    """Return the reason why one line is invalid, or None when it is fine."""
    for key in REQUIRED_LINE_KEYS:
        if key not in line:
            return f"line {index}: missing key {key}"
    sku = line["sku"]
    if not sku:
        return f"line {index}: sku must not be empty"
    if sku in seen:
        return f"line {index}: duplicate sku {sku}"
    seen.add(sku)
    qty = _parse_int(line["qty"])
    if qty is None or qty <= 0:
        return f"line {index}: qty must be a positive integer"
    price = _parse_int(line["unit_price_kopecks"])
    if price is None or price < 0:
        return f"line {index}: price must be a non-negative integer"
    return None


def _validate_lines(lines: list[dict[str, str]]) -> str | None:
    """Return the reason why the lines are invalid, or None when they are fine."""
    seen: set[str] = set()
    for index, line in enumerate(lines, start=1):
        reason = _validate_line(index, line, seen)
        if reason is not None:
            return reason
    return None


def validate_order(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> str | None:
    """Return a human readable reason why the order is invalid, or None if it is fine."""
    if not lines:
        return "order must contain at least one line"
    reason = _validate_lines(lines)
    if reason is not None:
        return reason
    if promo_code and promo_code not in PROMO_CODES:
        return f"unknown promo code: {promo_code}"
    if shipping_city and shipping_city not in SUPPORTED_CITIES:
        return f"unsupported shipping city: {shipping_city}"
    return None


def _order_quantities(lines: list[dict[str, str]]) -> tuple[int, int]:
    """Return the subtotal in kopecks and the total number of units."""
    subtotal = 0
    units = 0
    for line in lines:
        qty = int(line["qty"])
        price = int(line["unit_price_kopecks"])
        subtotal += qty * price
        units += qty
    return subtotal, units


def calculate_order_total(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> int | None:
    """Return the order total in kopecks, or None if the order is invalid."""
    if validate_order(lines, promo_code, shipping_city) is not None:
        return None
    subtotal, units = _order_quantities(lines)

    tier_percent = 0
    for threshold, percent in TIER_DISCOUNTS:
        if units >= threshold:
            tier_percent = percent
    promo_percent = PROMO_CODES.get(promo_code, 0)
    discount_percent = min(max(tier_percent, promo_percent), MAX_DISCOUNT_PERCENT)

    discount = percent_of(subtotal, discount_percent)
    discounted_subtotal = subtotal - discount
    delivery = (
        SHIPPING_KOPEKS if shipping_city and discounted_subtotal < FREE_DELIVERY_FROM_KOPEKS else 0
    )
    base = discounted_subtotal + delivery
    vat = percent_of(base, VAT_PERCENT)
    return base + vat
