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


def dostovka(city: str, price: int) -> int:
    if len(city) != 0 and price < FREE_DELIVERY_FROM_KOPEKS:
        return SHIPPING_KOPEKS
    return 0


# {'sku': 'SKU-1', 'qty': '1', 'unit_price_kopecks': '10000'}
def isinteger(text: str) -> bool:
    return all(i.isdigit() for i in text)


def isrep(commande: list[dict[str, str]]) -> bool:

    tous_les_skus = [article["sku"] for article in commande]

    # Si la longueur du set est plus petite, c'est qu'il y avait des doublons
    return len(tous_les_skus) != len(set(tous_les_skus))


def skidka(commande: dict[str, str]) -> float:
    quantity = int(commande["qty"])
    if quantity < 10:
        return 1.0
    if quantity < 25:
        return 0.95
    if quantity < 50:
        return 0.9

    return 0.85


def applypromo(code: str, montant: int) -> float:
    if code == "WELCOME10":
        return 0.9
    if code == "SUMMER15":
        return 0.85
    if code == "VIP35":
        if montant * 0.35 >= 300000:
            return 0.7
        return 0.65
    return 1.0


def validate_order(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> str | None:
    if lines == []:
        return "lines пустой"
    if isrep(lines):
        return "артикул не может повторяться"
    return None


def calculate_order_total(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> int | None:
    summ = 0
    summ2 = 0
    for i in lines:
        subtotal = int(i["qty"]) * int(i["unit_price_kopecks"])
        summ += int(subtotal * skidka(i))
        summ2 += subtotal
    summ = int(min(summ, summ2 * applypromo(promo_code, summ2)))
    summ += dostovka(shipping_city, summ)
    vat = percent_of(summ, VAT_PERCENT)
    return vat + summ
