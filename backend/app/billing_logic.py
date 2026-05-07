def calculate_invoice_total(items: list[dict]) -> float:
    return sum(float(item.get("quantity", 1)) * float(item.get("unit_price", 0)) for item in items)
