---
name: rewe-order
description: Use when ordering groceries from REWE Lieferservice, adding items to REWE cart, or reordering from a previous Flink shopping list. Requires user logged into rewe.de in Chrome with delivery slot selected.
---

# REWE Order

Batch-add items to REWE Lieferservice cart via their internal API. All items added in ONE JavaScript call — no clicking buttons.

## Prerequisites

- User logged into rewe.de in Chrome (connect via `tabs_context_mcp`)
- Delivery time slot selected (if "Liefertermin wählen" visible, user must select first)

## Process

### Step 1: Get market UUID (once per session)

Navigate to any REWE product page, wait 2s, then:

```javascript
const marketUuid = document.body.innerHTML.match(/\d+-[\w]+-([0-9a-f-]{36})/)?.[1];
```

### Step 2: Batch add all items (single JS call)

```javascript
(async () => {
  const uuid = '<MARKET_UUID>';
  const items = [
    {search: 'Product Name 250g', qty: 1},
    // ... all items — use German names with package size
  ];
  const results = [];
  for (const item of items) {
    try {
      // Search WITH cookies (critical — without credentials, no product data)
      const html = await (await fetch(
        `/shop/productList?search=${encodeURIComponent(item.search)}`,
        {credentials: 'include'}
      )).text();
      // Extract product JSON block
      const blocks = html.match(/\{"articleId":"[^"]+","availability[^}]+\}/g) || [];
      const products = blocks.map(b => JSON.parse(b));
      if (!products.length) { results.push({item: item.search, error: 'NOT_FOUND'}); continue; }
      // Find full listingId
      const artId = products[0].articleId;
      const lid = html.match(new RegExp(`\\d+-${artId}-${uuid}`))?.[0];
      if (!lid) { results.push({item: item.search, error: 'NO_LISTING'}); continue; }
      // Add to cart
      const r = await fetch(`/shop/api/baskets/listings/${lid}`, {
        method: 'POST', credentials: 'include',
        headers: {'content-type':'application/json','x-origin':'AddToBasketV2',
          'x-application-id':'rewe-basket','Accept':'application/vnd.com.rewe.digital.basket-v2+json'},
        body: JSON.stringify({quantity: item.qty, includeTimeslot: false, context: 'product-detail'})
      });
      results.push({item: item.search, price: products[0].price, status: r.status, ok: r.ok});
    } catch(e) { results.push({item: item.search, error: e.message}); }
  }
  return results;
})()
```

### Step 3: Verify cart

Navigate to `https://www.rewe.de/shop/checkout/basket`, wait 3s, then:

```javascript
const text = document.body.innerText;
({
  count: text.match(/Produkte \((\d+)\)/)?.[1],
  total: text.match(/Gesamtsumme\s*([\d,]+)\s*€/)?.[1]
})
```

## Quick Reference

| API | Method | Endpoint |
|-----|--------|----------|
| Search | GET | `/shop/productList?search={query}` (credentials: include) |
| Add to cart | POST | `/shop/api/baskets/listings/{listingId}` |
| Listing ID | — | `{prefix}-{articleId}-{marketUuid}` |

**Cart API headers:** `content-type: application/json`, `x-origin: AddToBasketV2`, `x-application-id: rewe-basket`, `Accept: application/vnd.com.rewe.digital.basket-v2+json`

**Cart API body:** `{"quantity": N, "includeTimeslot": false, "context": "product-detail"}` — quantity is absolute (not additive).

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `fetch()` without `credentials: 'include'` | Server returns template HTML without product data |
| Vague search terms | Use German product name + package size (e.g. "Doritos Sweet Chili 110g") |
| Assuming all Flink products exist | REWE doesn't carry some brands (Iglo frozen meals, some fresh items) |
| Thinking quantity is additive | `qty: 1` called twice = still 1 in cart |

## Integration

Chain with `/flink-order-history` to replicate Flink orders:
1. `/flink-order-history` → get items from Gmail
2. Map Flink names to REWE search terms
3. Run this skill → batch add
4. Report NOT_FOUND items
