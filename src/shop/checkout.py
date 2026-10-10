"""Order checkout.

The rules live in `src/shop/specs/checkout.md` - read it first.
Both functions below are stubs: their signature is final, the bodies are yours.
Do not change the constants: the tests rely on them.
"""

PROMO_CODES = {"WELCOME10": 10, "SUMMER15": 15, "VIP35": 35}
SUPPORTED_CITIES = ("msk", "spb")
MAX_DISCOUNT_PERCENT = 30
VAT_PERCENT = 20
SHIPPING_KOPECKS = 49_000
FREE_DELIVERY_FROM_KOPECKS = 500_000
TIER_DISCOUNTS = ((10, 5), (25, 10), (50, 15))
REQUIRED_LINE_KEYS = ("sku", "qty", "unit_price_kopecks")


def validate_order(order):
    REQUIRED_KEYS = {"sku", "qty", "price"}
    if not order:
        return False

    if "lines" not in order:
        return False

    for line in order["lines"]:
        if not line.get("sku"):
            return False
        for key in REQUIRED_KEYS:
            if key not in line:
                return False
    return True


def validate_order(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> str | None:
    """Return a human readable reason why the order is invalid, or None if it is fine."""
    if not lines:
        return "No items in order"

    for line in lines:
        for key in REQUIRED_LINE_KEYS:
            if key not in line:
                return f"Missing line key: {key}"

            try:
                qty = int(line["qty"])
                if qty <= 0:
                    return "quantity must be a positive"
            except (ValueError, TypeError):
                return "Quantity must be a number"

            try:
                price = int(line["unit_price_kopecks"])
                if price < 0:
                   return "Price cannot be negative"
            except (ValueError, TypeError):
                return "Price must be a number"
    if promo_code and promo_code not in PROMO_CODES:
        return "Invalid promo code"
    if shipping_city and shipping_city not in SUPPORTED_CITIES:
        return "Shipping not available to this city"

    return None

def calculate_discount(order):
    """Apply discount, capped at maximum 30%."""
    total = order.get("total", 0)
    discount_percent = order.get("discount_percent", 0)
    max_discount = 30
    actual_discount = min(discount_percent, max_discount)
    discount_amount = total * actual_discount / 100
    return discount_amount


def calculate_order_total(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> int | None:
    """Return the order total in kopecks, or None if the order is invalid."""
    error = validate_order(lines,promo_code, shipping_city)
    if error is not None:
        return None

    total = 0
    for line in lines:
        qty = int(line["qty"])
        unit_price = int(line["unit_price_kopecks"])
        total += qty * unit_price

    tier_discount = 0
    for threshold, percent in TIER_DISCOUNTS:
        if total > threshold * 1000:
            tier_discount = max(tier_discount, percent)

    promo_discount = PROMO_CODES.get(promo_code, 0)
    discount_percent = max(tier_discount, promo_discount)
    discount_percent = min(discount_percent, MAX_DISCOUNT_PERCENT)

    total = total * (100 - discount_percent) // 100
    if shipping_city and shipping_city not in SUPPORTED_CITIES:
        return None

    if shipping_city and total < FREE_DELIVERY_FROM_KOPECKS:
        total += SHIPPING_KOPECKS
    total = total * (100 + VAT_PERCENT) // 100

    return total
