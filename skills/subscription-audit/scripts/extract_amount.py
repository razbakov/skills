#!/usr/bin/env python3
"""Extract monetary amounts from email text (plain text or HTML).

Usage:
    echo "<email content>" | python3 extract_amount.py
    python3 extract_amount.py < email.txt

Outputs one amount per line in the format: <amount> <currency>
Example: 25.00 EUR
"""

import re
import sys
import html as html_mod


def strip_html(text: str) -> str:
    """Remove HTML tags and decode entities."""
    text = html_mod.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_amounts(text: str) -> list[tuple[str, str]]:
    """Return list of (amount, currency) tuples found in text."""
    # Try plain text first, fall back to stripped HTML
    if "<html" in text.lower() or "<table" in text.lower():
        text = strip_html(text)

    results = []

    # Pattern: currency symbol before amount (e.g. $25.00, €12,50)
    for m in re.finditer(r"([\$\€\£])\s*([\d]+[.,]?\d{0,2})", text):
        symbol, amount = m.group(1), m.group(2).replace(",", ".")
        currency = {"$": "USD", "€": "EUR", "£": "GBP"}.get(symbol, symbol)
        results.append((amount, currency))

    # Pattern: amount before currency code (e.g. 25.00 EUR, 12,50 USD)
    for m in re.finditer(r"([\d]+[.,]\d{2})\s*(EUR|USD|GBP|CHF)", text):
        amount = m.group(1).replace(",", ".")
        results.append((amount, m.group(2)))

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for item in results:
        if item not in seen:
            seen.add(item)
            unique.append(item)

    return unique


if __name__ == "__main__":
    text = sys.stdin.read()
    amounts = extract_amounts(text)
    if amounts:
        for amount, currency in amounts:
            print(f"{amount} {currency}")
    else:
        print("TBD — no amount found")
