CURRENCIES = {
    "MAD": "MAD",
    "EUR": "€",
    "USD": "$",
    "GBP": "£",
}


def get_currency_symbol(page):
    code = page.session.store.get("currency") or "MAD"
    return CURRENCIES.get(code, code)
