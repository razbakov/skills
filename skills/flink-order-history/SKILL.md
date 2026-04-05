# Flink Order History

Extract Flink grocery order history from Gmail, parse items/totals, analyze purchasing patterns, and save to Notion. Use when the user asks about Flink orders, grocery spending, shopping patterns, "what do I usually order", or wants a shopping list based on past orders.

## Inputs
1. **Date range** — period to analyze (default: current year, `after:YYYY/01/01`)
2. **Notion parent page** — where to save (default: ikigai page in Notion)

## Process

### Step 1: Search Gmail for Flink order emails
```bash
gog gmail search "from:goflink.com subject:Bestelldetails after:YYYY/01/01" -j
```
Flink sends order confirmations from `status.orders@goflink.com` with subject "Bestelldetails". Also check for `"Sorry, some items weren't available"` emails for substitution data.

### Step 2: Save each email to a file
```bash
for tid in <thread_ids>; do
  gog gmail read "$tid" -j > "/tmp/flink-orders/${tid}.json"
done
```

### Step 3: Parse order details from HTML
Each email is HTML with items in a table. Extract:
- **Date** — from "Bestellung vom DD Month YYYY"
- **Order number** — from "Bestellnummer: de-muc-XXXX-XXXX"
- **Items** — from the table between "Anzahl MwSt. Gesamt" header and "Artikel XX,XX €" subtotal
- **Item format:** `Name Price € Qty Tax% MwSt Total €`
- **Totals** — Artikel (subtotal), Pfand (deposit), Liefergebühr (delivery), Rabatt (discount), Gesamt (total)

Key parsing steps:
1. Extract HTML part from email payload (base64-decode `text/html` MIME part)
2. Strip HTML tags: `re.sub(r'<[^>]+>', ' ', html)`
3. Decode entities: `&amp;` → `&`, `&apos;` → `'`
4. Find items section between table header and subtotal row
5. Match items with regex: `(.+?)\s+(\d+,\d{2})\s*€\s+(\d+)\s+\d+%\s+MwSt\s+\d+,\d{2}\s*€`

### Step 4: Generate frequency analysis
Count how many times each item was ordered across all orders. Calculate:
- Total orders, total spent, average per order
- Items sorted by purchase frequency
- Category breakdown (ready meals, snacks, fruit, drinks, dairy, household)

### Step 5: Save to Notion
Create a page under the Notion parent with:
- **Title:** `Flink Orders YYYY`
- **Icon:** `🛒`
- **Content:** Summary stats, top 20 items table, pattern analysis, each order in a collapsible toggle

## Notes
- Flink has no web order history — Gmail is the only data source
- Flink website (goflink.com) returns 404 for /orders — app-only
- Store address: Near user's address from CLAUDE.md Personal Info
- Orders are pickup ("Abholung") not delivery in Alex's case
- The first item in each HTML email sometimes includes header noise — filter items that contain "Flink" or "Bestellung" or "Artikel Preis"

## Output
- Notion page URL with full order history + analysis
- Pattern insights (what's ordered every time vs. one-offs)
