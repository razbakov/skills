---
description: "Grocery Run — full pipeline from kitchen photos to Flink checkout. Chains kitchen-inventory, shopping-list, and flink-order skills."
---

# Grocery Run (Meta-Skill)

End-to-end grocery ordering pipeline: photograph kitchen → analyze inventory → generate shopping list → fill Flink cart → checkout.

## Trigger

- "grocery run"
- "restock kitchen"
- "order groceries"
- "time to shop"

## Process

### Step 1: Kitchen Inventory

Invoke `/kitchen-inventory` to analyze what's currently in the kitchen.

```
Skill: kitchen-inventory
```

**Input:** Kitchen photos (from Telegram saved messages, direct upload, or Notion)
**Output:** Structured inventory — items by location (fridge, freezer, cupboard, counter) with brand, quantity, certainty level

**If no recent photos:** Ask user to take 4-6 photos (fridge, freezer top, freezer bottom, counter, cupboard, spice area) and save to Telegram.

### Step 2: Shopping List

Invoke `/shopping-list` to generate what to buy.

```
Skill: shopping-list
```

**Input:**
- Kitchen inventory (from Step 1)
- Flink order history (invoke `/flink-order-history` to get patterns)
- Notion standard pantry list (if exists)
- User's cooking preferences (multicooker meals, ready meals)

**Output:** Categorized shopping list with:
- Every-order staples (fruits, snacks, drinks, water)
- Ready meals (frozen meals user regularly orders)
- Dairy/deli (milk, cheese, ham, sour cream)
- Cooking ingredients (if multicooker meals requested: rice, chicken, passata, onions, garlic, butter)
- Household (deo, toothpaste, trash bags, cleaning supplies)
- Skip list (items already in inventory)

### Step 3: User Review

Present the shopping list to the user. Ask:
- "Add or remove anything?"
- "Want cooking ingredients for multicooker meals?"
- "Any household items needed?"

Wait for approval before proceeding.

### Step 4: Flink Order

Invoke `/flink-order` to fill the cart.

```
Skill: flink-order
```

**Input:** Approved shopping list
**Output:** Filled Flink cart with item count and total price

### Step 5: Cart Review & Checkout

Present full cart summary:
- All items with prices
- Total price
- Delivery fee (free above ~€50)
- Estimated delivery time
- Any deals/discounts applied

**REQUIRE explicit user confirmation** before clicking Checkout.

## Integration Points

| Skill | Role |
|-------|------|
| `/kitchen-inventory` | Analyze photos → structured inventory |
| `/flink-order-history` | Past orders → frequently bought items |
| `/shopping-list` | Inventory + history → what to buy |
| `/flink-order` | Shopping list → Flink cart |
| `/notion-add-to-db` | Save inventory/list to Notion |

## Typical Flow

```
User: "grocery run"
→ Check for recent kitchen photos (Telegram saved messages, last 24h)
→ If photos found: /kitchen-inventory
→ If no photos: ask user to photograph kitchen
→ /flink-order-history (get buying patterns)
→ /shopping-list (cross-reference inventory + history)
→ Present list, get approval
→ /flink-order (add items to cart)
→ Present cart total, get checkout confirmation
```

## Shortcuts

Each child skill works standalone:
- `/kitchen-inventory` — just analyze photos, no ordering
- `/shopping-list` — generate list from any input, no ordering
- `/flink-order` — fill cart from a manual list
- `/flink-order-history` — just review past orders

## Notes

- Flink delivers to user's address (from CLAUDE.md Personal Info)
- Store hours: 7:30 AM – 11:00 PM
- Free delivery above ~€50
- Average order: ~€80-100
- Use German product names for Flink search
- Session may timeout — re-navigate if blank page appears
