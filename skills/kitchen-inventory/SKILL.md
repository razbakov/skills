# Kitchen Inventory

Analyze kitchen photos to produce a detailed inventory, then save to Notion. Use when the user sends kitchen/fridge/pantry photos, asks "what do I have?", "kitchen inventory", "what's in my fridge?", or wants a shopping list based on current stock.

## Inputs
1. **Photos** — kitchen photos (fridge, freezer, counter, cupboard, etc.). Source: Telegram saved messages, local files, or user-provided paths.
2. **Notion parent page** — where to save the inventory (default: ikigai page in Notion).
3. **Standard pantry list** — reference list for gap analysis (default: `sessions/2026-03-22-meal-planning-brainstorm.md` section 2).

## Process

### Step 1: Collect photos
Find or receive kitchen photos. Common sources:
- Telegram saved messages: export via `tdl`, download photos with `tdl dl -u "https://t.me/c/<user_id>/<msg_id>" -d /tmp/telegram-photos/`
- Local files provided by user
- Photos from previous inventory sessions

### Step 2: Analyze each photo
Read each photo with vision. For every item visible, record:

| Field | Description |
|-------|-------------|
| **#** | Photo number + item number (e.g. 1.3, 2.1) |
| **Location** | Where in the photo (shelf, drawer, door, left/right/back/front) |
| **Item** | What it is (generic name) |
| **Brand / Details** | Brand name, product name, size, any text visible on label |
| **Qty** | Count or fill level (~half, mostly full, 4-5 remaining) |
| **Certainty** | High / Medium / Low — how confident the identification is |

Rules:
- Be specific about brands when readable (e.g. "Rauch Happy Day" not "juice")
- Note sizes when visible (200ml, 500g, 1L)
- Include non-food items if stored with food (cables, lighter — note as non-food)
- For grouped items (spice rack), estimate count and note visible types
- For frozen items, note if the package is opened or sealed
- Mark items behind other items or with obscured labels as Low certainty

### Step 3: Create summary table
Group inventory by category:

| Category | Items | Status |
|----------|-------|--------|
| Protein | List items | Low/OK/Well stocked |
| Carbs | ... | ... |
| Vegetables | ... | ... |
| Fruit | ... | ... |
| Dairy | ... | ... |
| Oils/Fats | ... | ... |
| Condiments | ... | ... |
| Spices | ... | ... |
| Drinks | ... | ... |
| Snacks | ... | ... |

Add a one-line verdict (e.g. "Condiment-rich, ingredient-poor. Freezer is the lifeline.")

### Step 4: Save to Notion
Create a page under the Notion parent:
- **Title:** `Kitchen Inventory — YYYY-MM-DD`
- **Icon:** `🧁`
- **Content:** Full inventory tables per photo + summary table + verdict
- **Header:** Date, source (Telegram IDs or file paths), method ("6 photos analyzed by Claude vision")

```
notion-search(query: "ikigai", page_size: 3)
notion-create-pages(parent: {page_id: "<ikigai_page_id>"}, pages: [{properties: {title: "Kitchen Inventory — YYYY-MM-DD"}, icon: "🧁", content: "<inventory>"}])
```

### Step 5 (optional): Generate shopping list
If the user asks for a shopping list, cross-reference against the standard pantry list:
- **Urgent:** Items completely missing that are needed for cooking this week
- **Nice to have:** Items running low or good to stock
- **Already stocked:** Items present, don't order

Estimate total cost if possible (Flink Germany pricing).

## Output
- Notion page URL with full inventory
- Summary verdict
- Shopping list (if requested)
