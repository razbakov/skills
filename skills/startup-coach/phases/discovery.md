# Phase 0: Discovery

Before creating any files, coach the user through design thinking to frame the real problem.

**The conversation (4 questions max in autopilot, deeper in guided):**

1. **Mission** — "Why does this exist? Not what it does — why does it need to exist at all?"
2. **Vision** — "What does the world look like if this succeeds? Paint the picture."
3. **First Obstacle** — "What's the biggest thing standing between you and that vision right now?"
4. **Hypothesis** — "So if we [solution], then [target users] will [desired outcome]. Is that the bet we're making?"

**Rules:**
- Start from the end, work backwards — this is design sprint thinking
- Don't accept the first answer as the real problem. "I want a website" is a solution, not a problem. Dig one level deeper.
- Keep it to 4 questions max in autopilot — don't interrogate. If the user just wants to build, respect that and infer the rest.
- Mission and vision are each one sentence. Mission is the "why" (rarely changes). Vision is the "where" (aspirational future state).
- Capture mission, vision, obstacle, and hypothesis — mission and vision go into the README, hypothesis goes into strategy.
- If the user already has a clear, well-framed mission and vision, acknowledge it and move to Phase 1 quickly.

# Phase 1: Foundation

Create `README.md` using → `templates/README.md`

Then copy `link-readmes.sh` from this skill into `.bin/link-readmes.sh`, make it executable, and run it to create CLAUDE.md and AGENTS.md symlinks.

**Workspace structure selection:**

The workspace structure defines where all documents live. It's recorded in README.md so the coach and other agents know where to find and create files.

Available structure templates are in `templates/structures/`. In autopilot, pick the best fit and move on. In guided, present the options.

- **startup** — full lifecycle: product, design, marketing, engineering. Use for new products, startups, side projects with branding needs.
- **custom** — the user defines their own. Ask what directories they want, then record the tree in README.md.

**Rules:**
- Open with **Mission** (one sentence — why this exists) and **Vision** (one sentence — what the world looks like if it works)
- Include **Status** — what's live, what's being built right now
- Include **Next Steps** — what's coming next, with ✅ / 🔲 checkboxes
- Include **OKRs** when the project is mature enough — 2–3 objectives with 3 key results each, updated quarterly. OKRs bridge the vision to the backlog and answer "why are we working on these stories now?"
- Include **Workspace** section with the structure tree and links to each area
- Products section lists each product with audience in parentheses
- CLAUDE.md and AGENTS.md are always symlinks to README.md — never edit them directly
- One page max — if longer, move details to linked docs
- Run `.bin/link-readmes.sh` after creating any new README.md in a subdirectory
