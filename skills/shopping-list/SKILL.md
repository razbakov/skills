# Shopping List

Generate a grocery shopping list by cross-referencing kitchen inventory, Flink order history, and the standard pantry list. Save to Notion. Use when the user asks for a shopping list, "what should I order", "what do I need from Flink", or "grocery list".

## Inputs
1. **Kitchen inventory** — latest inventory from Notion (Kitchen Inventory page under ikigai) or fresh photos
2. **Flink order history** — Notion page (Flink Orders page under ikigai) or run /flink-order-history
3. **Standard pantry** — from `sessions/2026-03-22-meal-planning-brainstorm.md` section 2
4. **User corrections** — ask the user to verify uncertain items from inventory

## Process

### Step 1: Load data sources
1. Fetch the latest Kitchen Inventory page from Notion (search "Kitchen Inventory" under ikigai)
2. Fetch the Flink Orders page from Notion (search "Flink Orders" under ikigai)
3. If either is missing or outdated, run the corresponding skill first (/kitchen-inventory or /flink-order-history)

### Step 2: Cross-reference
For each item in Flink order history "Most Ordered" list:
- Check if it's in the current kitchen inventory
- If **not present** → add to shopping list
- If **present but low** → add with note "check qty"
- If **present and sufficient** → add to "Skip" section

### Step 3: Categorize the list
Group items by shopping pattern:

| Section | Rule |
|---------|------|
| **Urgent** | Items completely missing that are basic necessities (eggs, milk, butter) |
| **Every-Order Staples** | Items ordered 5+ times in history — the core basket |
| **Ready Meals** | Frozen/prepared meals from order history |
| **Dairy/Deli** | Fresh dairy and deli items |
| **Drinks** | Juices, sodas, water |
| **Nice to Have** | Items ordered 2-3 times — not essential |
| **Skip** | Items already in stock with explanation |
| **If Starting to Cook** | Raw ingredients from standard pantry not in order history (onions, garlic, etc.) |

### Step 4: User review
Present the list to the user. Common corrections:
- Misidentified items from photos (e.g. apple carton mistaken for eggs)
- Quantity adjustments (e.g. "Mango x2 not x1")
- Items they don't want this time

### Step 5: Save to Notion
Create page under ikigai:
- **Title:** `Shopping List — YYYY-MM-DD`
- **Icon:** `📝`
- **Content:** Categorized checklist with checkboxes, skip section, estimated total
- **Footer:** "Est. total: ~XX EUR (avg Flink order is 82 EUR)"

## Key Data Points
- Alex orders from Flink ~weekly, avg 82 EUR/order
- Store: Near user's address from CLAUDE.md (pickup)
- Top items: Happy Day Mango (15x), Maryland nuts (8x), Doritos (7x), YouCook Caesar (7x), Iglo meatballs (7x)
- Almost never orders raw cooking ingredients — basket is 80% ready meals, snacks, fruit, drinks
- Has a multi-cooker but rarely uses it

## Output
- Notion page URL with checklist
- Estimated total
