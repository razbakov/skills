---
name: flink-order
description: Use when ordering groceries from Flink, adding items to Flink cart, or reordering from a previous shopping list. Requires user logged into goflink.com in Chrome.
---

# Flink Order

Batch-add items to Flink cart via their Nuxt store API. All items added in ONE JavaScript call — no clicking buttons.

## Prerequisites

- User logged into goflink.com in Chrome (connect via `tabs_context_mcp`)
- Delivery address set in Flink account
- If page shows token refresh, re-navigate to `https://www.goflink.com/shop/en/`

## Process

### Step 1: Open Flink shop

Navigate to `https://www.goflink.com/shop/en/`, wait 3s. If redirected to `refresh-token`, navigate again.

### Step 2: Batch add all items (single JS call)

```javascript
(async () => {
  const cartStore = window.$nuxt.$pinia._s.get('cart');
  const router = window.$nuxt.$router;
  const catalog = () => Object.values(window.$nuxt.$pinia.state.value.catalog.products);

  // Reset cart for clean order
  await cartStore.resetCart();
  await cartStore.createCart();

  const items = [
    {search: 'Product Name 250g', qty: 1},
    // ... all items — use German names with package size
  ];

  const results = [];
  for (const item of items) {
    await router.push(`/en/search/?q=${encodeURIComponent(item.search)}`);
    await new Promise(r => setTimeout(r, 1500));

    // Score products by word match count
    const words = item.search.toLowerCase().split(/\s+/);
    const scored = catalog().map(p => {
      const name = p.name.toLowerCase();
      return {...p, score: words.filter(w => name.includes(w)).length};
    }).filter(p => p.score >= 2).sort((a, b) => b.score - a.score);

    const found = scored[0];
    if (!found) { results.push({item: item.search, error: 'NOT_FOUND'}); continue; }

    await cartStore.addToCart({sku: found.sku, quantity: item.qty});
    results.push({name: found.name, sku: found.sku, price: found.price?.amount, qty: item.qty});
  }
  return results;
})()
```

### Step 3: Verify cart and present summary

```javascript
const lines = window.$nuxt.$pinia._s.get('cart').remoteCart?.lines || [];
const total = window.$nuxt.$pinia._s.get('cart').remoteCart?.total_price;
({items: lines.map(l => ({sku: l.product_sku, qty: l.quantity})), total})
```

Present cart summary to user. **MANDATORY:** Get explicit confirmation before checkout — this is a financial transaction.

## Quick Reference

| What | How |
|------|-----|
| Router | `window.$nuxt.$router.push(path)` |
| Catalog | `window.$nuxt.$pinia.state.value.catalog.products` (object keyed by SKU) |
| Cart store | `window.$nuxt.$pinia._s.get('cart')` |
| Add item | `cartStore.addToCart({sku, quantity})` |
| Add multiple | `cartStore.addMultipleToCart(items)` |
| Remove item | `cartStore.removeFromCart({sku})` |
| Reset cart | `cartStore.resetCart()` then `cartStore.createCart()` |
| Cart lines | `cartStore.remoteCart?.lines` |

## Product Matching

Search returns all catalog products. Match using word scoring:
- Split search query into words
- Count how many words appear in each product name
- Require score >= 2 to avoid false matches
- Take highest-scoring product

Use German product names with package size for best results (e.g. "Doritos Sweet Chili Pepper 110g" scores 5/5).

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Token refresh redirect | Navigate to `/shop/en/` again — sessions expire |
| Wrong product matched | Use more specific search terms with brand + size |
| `match: 'hot'` matching wrong products | Use full search string for scoring, not partial keywords |
| Cart API 409 conflict | Use `cartStore.addToCart()` — it handles slot/version internally |
| Calling cart REST API directly | Use pinia store methods instead — they handle auth + slot + versioning |

## Safety

- **Never auto-checkout** — always show full cart summary and get explicit user confirmation
- **Show total price** including delivery fee and discounts before confirming
- If user says "just order it", still show summary first

## Integration

Chain with `/flink-order-history` to reorder:
1. `/flink-order-history` → get items from Gmail
2. Feed items into this skill
3. Report NOT_FOUND items

Chain with `/shopping-list` for new orders:
`/kitchen-inventory` → `/shopping-list` → `/flink-order`
