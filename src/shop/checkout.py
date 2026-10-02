"""Order checkout.

The rules live in `src/shop/specs/checkout.md` - read it first.
Do not change the constants: the tests rely on them.
"""

from re import fullmatch

from shop.money import percent_of

PROMO_CODES = {"WELCOME10": 10, "SUMMER15": 15, "VIP35": 35}
SUPPORTED_CITIES = ("msk", "spb")
MAX_DISCOUNT_PERCENT = 30
VAT_PERCENT = 20
SHIPPING_KOPEKS = 49_000
FREE_DELIVERY_FROM_KOPEKS = 500_000
TIER_DISCOUNTS = ((10, 5), (25, 10), (50, 15))
REQUIRED_LINE_KEYS = ("sku", "qty", "unit_price_kopecks")


def _validate_line(line: dict[str, str], position: int) -> str | None:
    """Validate a line before any key lookup or integer conversion."""
    for key in REQUIRED_LINE_KEYS:
        if key not in line:
            return f"Line {position} is missing required key: {key}."
    if line["sku"] == "":
        return "SKU must not be empty."
    if fullmatch(r"[+-]?\d(?:_?\d)*", line["qty"].strip()) is None:
        return "Quantity must be a whole number."
    if int(line["qty"]) <= 0:
        return "Quantity must be greater than zero."
    if fullmatch(r"[+-]?\d(?:_?\d)*", line["unit_price_kopecks"].strip()) is None:
        return "Price must be a whole number."
    if int(line["unit_price_kopecks"]) < 0:
        return "Price must not be negative."
    return None


def validate_order(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> str | None:
    """Return a human readable reason why the order is invalid, or None if it is fine."""
    if not lines:
        return "Order must contain at least one line."
    seen: dict[str, bool] = {}
    for position, line in enumerate(lines, start=1):
        reason = _validate_line(line, position)
        if reason is not None:
            return reason
        if line["sku"] in seen:
            return "SKU must not be duplicated."
        seen[line["sku"]] = True
    if promo_code and promo_code not in PROMO_CODES:
        return "Unknown promo code."
    if shipping_city and shipping_city not in SUPPORTED_CITIES:
        return "Unsupported shipping city."
    return None


def calculate_order_total(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> int | None:
    """Return the order total in kopecks, or None if the order is invalid."""
    if validate_order(lines, promo_code, shipping_city) is not None:
        return None
    subtotal = sum(int(line["qty"]) * int(line["unit_price_kopecks"]) for line in lines)
    quantity = sum(int(line["qty"]) for line in lines)
    tier_percent = max(
        (percent for threshold, percent in TIER_DISCOUNTS if quantity >= threshold), default=0
    )
    discount_percent = max(tier_percent, PROMO_CODES.get(promo_code, 0))
    discount_percent = min(discount_percent, MAX_DISCOUNT_PERCENT)
    discounted_subtotal = subtotal - percent_of(subtotal, discount_percent)
    shipping = (
        SHIPPING_KOPEKS if shipping_city and discounted_subtotal < FREE_DELIVERY_FROM_KOPEKS else 0
    )
    base = discounted_subtotal + shipping
    vat = percent_of(base, VAT_PERCENT)
    return base + vat
