from datetime import datetime

def format_datetime(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def format_currency(amount: float, currency: str = "USD") -> str:
    return f"{amount:,.2f} {currency}"
