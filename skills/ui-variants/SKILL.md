---
name: ui-variants
description: "Build several clickable UI alternatives side by side on one page inside the real app, recommend one, let the user pick, then implement the winner. Use this whenever the user wants to compare UI directions before building: 'make 4 prototypes', 'show me options', 'give me variants of the nav/header/page/flow', and also complaints with no solution attached, like 'the main navigation is not good', 'this page is confusing', 'redesign the header', 'the mobile menu sucks'. Not for idea-level ideation (use design-sprint) or static mockup images."
---

# UI Variants

Turn "this UI is not good" into a decision: a single clickable page in the user's own app that shows N real alternatives in the app's real design system, with a recommendation, followed by implementing the chosen one.

## Why this shape

- **In the app, not in Figma or an image.** Variants built with the project's own components and tokens show the real fonts, spacing and constraints; the user judges the thing they will actually get.
- **One page, a switcher.** Side-by-side comparison beats N separate links. The user flips A/B/C/D in place.
- **Each variant states its cost.** Options without trade-offs read as decoration. A variant earns its place only if it optimises for something different.
- **A recommendation, not a menu.** The user is the decider, but you have opinions. Recommending a hybrid is often the right answer; offer it as an extra variant they can click.

Built for web apps with a dev server. For native apps, do the same with a debug-only screen or preview harness the platform offers (e.g. SwiftUI previews), and the same switcher idea.

## Step 1 — Audit what exists (before designing anything)

Read the component(s) that render the UI in question and every place they're used. Write down **concrete, checkable problems**, not taste:

- What is hidden at which breakpoint? (e.g. "signed-in links all `hidden sm:inline` → a phone user can't reach My plan")
- Which important pages/actions are unreachable from it?
- What competes visually (five inline text links of equal weight)?
- Duplicated or divergent implementations (a second header in another layout)?
- What fixed/floating elements live near it (bottom bars, FABs, report buttons) — a new design may collide with them.

List the real destinations it must offer (from the routes/pages folder), grouped by audience (visitor, signed-in user, business user, admin).

## Step 2 — Isolate the work

Follow the repo's branching conventions (worktree/branch naming from the project or user instructions). Never work on the main checkout if the user's rules forbid it. Start a dev server for the branch so the user can review live. If the default env points at production data, prefer a local database for anything that will write data, and say which one the preview uses.

## Step 3 — Build one sketch page with all variants

Put it where the project keeps prototypes (e.g. `pages/sketches/<topic>`), using the app's layout system so it renders without the normal chrome. Requirements:

**Control bar** (sticky, clearly not part of any variant):
- Variant switcher (A, B, C, D…).
- **Device toggle: desktop / mobile.** Render mobile inside a ~390px phone frame. Its height must fit the viewport (`min(760px, 100vh - controls)`), or bottom bars fall off-screen.
- State toggles that change the UI: signed in / out, role, empty / full.
- A one-line **Idea · Good · Cost** for the selected variant.

**Important:** inside a frame narrower than the window, CSS media queries / breakpoint utilities (e.g. Tailwind's `sm:`, `md:`) still read the *window* width. Branch on an `isMobile` prop/computed in the template instead of relying on breakpoint classes.

**Each variant:**
- Uses real components (brand mark, buttons, tokens) and mock data. No navigation, no API calls, no DB.
- Is fully clickable: menus open, sheets slide, tabs switch, search filters.
- Resets its local state when the variant/device/state toggle changes.
- Has a mock page body under it, so the UI is judged in context.

**Choosing the N directions** — make them differ in *strategy*, not styling. Typical axes for navigation: classic top bar + account menu · app-style bottom tab bar · audience/mode split · search-first. For a page: list-first · map-first · feed · wizard. Default N = 4 unless the user names a number.

## Step 4 — Verify every variant yourself

For each variant × device × state: load it, click its interactive parts, screenshot. Common breakages:
- The page renders but clicks do nothing → the client bundle hasn't hydrated yet (first dev load can take 10–20 s). Wait and retry; don't debug phantom bugs.
- Logo/brand collapses next to a `flex-1` element → add `shrink-0`.
- Brand mark invisible on a dark variant → give it a light backing.
- Overlays/sheets under other fixed elements → check z-index against existing floating UI.

Never ask the user to check. Show them working variants.

## Step 5 — Present and recommend

Short message:
1. The URL of the sketch page and how to use the toggles.
2. **What's wrong today** — the concrete problems from Step 1.
3. One line per variant: what it does.
4. **Recommendation** with the reason, which often combines two (e.g. "A on desktop + B's tab bar on phones").
5. Ask which one, or which parts to combine.

If the user asks for the recommendation as its own option, add it as the next variant (E) on the same page, make it the default, and verify it like the others.

## Step 6 — Implement the chosen variant

- **Extract shared pieces** when the same UI appears in more than one layout (e.g. an account menu used on both the consumer and business side). One component, a `mode` prop for the differences.
- **Symmetry:** if users enter a mode/section through a control, they must leave it through the same control in the same place (the menu row that says "Business" on one side says "Dancing" on the other). Remove one-off exits that break this.
- **Fixed bottom bars:** reserve their height with a CSS variable on the root (e.g. `--tabbar-h` set under the mobile breakpoint, plus `padding-bottom` on body), and move existing fixed/floating elements up by it (`bottom: calc(1.25rem + var(--tabbar-h, 0px))`).
- **Tests:** grep e2e steps for selectors on controls you moved (e.g. a "Sign out" button now inside a menu) and update them. Add accessible names (`aria-label="Account menu"`) that tests can target.
- **Verify signed-in states with a test account** on a local/dev database, per the project's rules for test credentials. Never use real credentials or production data for this.
- Run unit tests and any design/architecture guardrail tests the project has.
- Keep the sketch page and commit it separately (`sketch(...)`) as the record of what was compared and why.

## Outputs

- `pages/sketches/<topic>` — clickable comparison page (committed).
- The implemented UI on the branch, verified in the browser at desktop and phone sizes, signed in and out.
- A short message with the problems found, variants, recommendation and what was built.

## Integration points

- `design-sprint` — use it first when the problem itself is still unclear; use this skill once the question is "which UI".
- Project-level live-coding / local-preview rules decide where the dev server runs and which database it uses.
- After the user picks, follow the project's normal PR and deploy flow.
