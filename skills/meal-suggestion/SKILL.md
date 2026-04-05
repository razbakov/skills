---
description: Suggest meals based on actual kitchen inventory, health goals, and motivation to cook. Always check Notion inventory before suggesting recipes. Use when planning lunch/dinner in daily review or when user asks what to eat.
user_invocable: true
---

# Meal Suggestion

Suggests 3 meal options (cook / fridge raid / order) based on what's actually in the kitchen, health context, and cooking motivation.

## Trigger

- Part of `/daily-review-suggest-plan` when adding lunch/dinner to the schedule
- Independently via `/meal-suggestion`
- When user asks "what should I eat"

## Context

- **Kitchen inventory:** Notion page "Kitchen Inventory" (search: `kitchen inventory`)
- **Health goals:** Memory file `user_health.md`
- **Recipes:** `sessions/2026-03-22-meal-planning-brainstorm.md` (multi-cooker recipes)
- **Flink order history:** `/flink-order-history` skill

## Process

### 1. Check actual inventory

Search Notion for the latest "Kitchen Inventory" page. Read the full inventory with category summary.

**CRITICAL:** Never suggest a recipe without verifying all key ingredients are in the inventory. The brainstorm doc lists aspirational recipes — the inventory shows reality.

### 2. Read health context

Read `user_health.md` for:
- Smoking status (eating regularly kills cravings)
- Weight goals (avoid heavy/empty carbs)
- Meal skipping patterns (is this the first meal today?)
- Exercise plans (protein needs)

### 3. Generate 3 plans

**Plan A — Cook (always first, always motivate)**
- Pick a recipe where ALL main ingredients are confirmed in inventory
- Prefer multi-cooker recipes (lowest friction for Alex)
- State exact items from inventory ("you have eggs (4-5), toast (2 packs), pesto")
- Include cook time and portion count
- Frame it as a win: "15 min, 4 portions = meals for 2 days"

**Plan B — Fridge raid (quick combo from what's there)**
- Combine 2-3 items that are confirmed available
- Must be a real meal, not a snack — especially if it's the first meal of the day
- Examples: scrambled eggs + toast + spinach, pelmeni with soy sauce

**Plan C — Order something new (Bolt Food)**
- Suggest something the user hasn't tried recently
- High protein, lighter options preferred (poke bowl, chicken salad, Thai curry)
- Explicitly say what to skip (pizza, burger — unless earned by a run)

### 4. Add health reminder

Based on context:
- If first meal of the day: "First meal — eat properly"
- If quit smoking recently: "Eating regularly kills cravings"
- If no exercise today: "Go for a run tonight to earn that burger tomorrow"

### 5. Flag missing staples

If inventory shows gaps in basics (no fresh protein, no fresh veg, no fruit), add:
> "Kitchen status: [summary]. Need a Flink order today/this week."

## Output

Include all 3 plans in the calendar event description when syncing to Google Calendar. Format:

```
PLAN A (Cook! X min): [recipe with confirmed ingredients]

PLAN B (Fridge combo): [quick meal from available items]

PLAN C (Order): [specific suggestion]. Skip [unhealthy default].

Kitchen status: [gaps]. [Flink order recommendation].

REMINDER: [health-aware nudge]
```

## Anti-patterns

- Never suggest a recipe without checking inventory first
- Never assume brainstorm doc = reality
- "Omelette sandwich" is not lunch when someone hasn't eaten all day
- Don't default to "just order" — always try to motivate cooking first
- When doing grocery shopping (Flink order), cross-reference desired recipes against what's actually missing
