These phases sit between research (understanding the problem) and commitment (full backlog, architecture, etc.). The goal is to test the hypothesis cheaply before investing in detailed planning.

All three phases are skippable — but strongly recommended. In autopilot, the AI runs through them fast. In guided, the user participates at each step.

# Phase 5: Sketch

Explore multiple approaches before committing to one. Design sprints teach that individual ideation beats groupthink — and with AI, you can explore more options faster than any workshop.

**Autopilot mode:**
The AI generates 3 distinct approaches based on the JTBD analysis and user journey. Each approach is a one-page summary: key idea, how it solves the top job, what's different about this approach, and a rough wireframe.

**Guided mode — the user participates:**

1. **Lightning demos** (optional): Ask the user to find 2–3 products they admire — competitors, adjacent tools, or anything that inspired them. "Spend 10 minutes browsing. Screenshot anything that made you think 'I wish we had that.' Don't filter — just collect." The user shares screenshots or links; the AI extracts patterns.

2. **Sketching** (optional): Invite the user to sketch their vision on paper. "Grab a pen and paper. Draw the most important screen — the one where the user gets value. Don't worry about polish. Take a photo and share it." The AI uses the sketch as input alongside the JTBD analysis to generate refined approaches.

3. **AI generates 3 approaches**: Even in guided mode, the AI produces 3 distinct options — but now informed by the user's demos and sketches. Each approach includes a name, the core idea, a wireframe, and the trade-offs.

**Output:** 3 one-page approach summaries. Present them side by side and ask the user to pick one (or combine elements).

# Phase 6: Prototype

Build a testable version of the chosen approach. Not production code — a realistic enough facade that someone can react to it.

**What "prototype" means depends on the product:**
- **Website / landing page** → a single HTML page with real copy, real layout, clickable but not functional
- **Web app** → key screens in HTML/CSS or a Figma-style mockup showing the critical flow
- **API / backend** → a mock API with hardcoded responses that demonstrates the data model

**Rules:**
- Build the prototype from the approach chosen in Phase 5
- Focus on the "aha moment" from the user journey — that's the screen/flow to prototype
- Use real copy, not lorem ipsum — the words matter as much as the layout
- Keep it to 1–3 screens maximum. Prototype the critical path, not the whole app.
- In autopilot, build all 3 approaches as quick prototypes so the user can compare by interacting, not just reading

**Output:** A working prototype the user (or their test subjects) can click through.

# Phase 7: Test

Put the prototype in front of real people and learn. This is the cheapest learning you'll ever get — before a single story is written or a line of production code exists.

**Autopilot mode:**
Ask the user: "Can you show this to 3–5 people who match your target audience? Ask them to complete [the key task from the user journey] and observe where they get stuck." Provide a simple test script:

1. "What do you think this is for?" (first impression)
2. "Try to [key task]." (observe, don't help)
3. "What was confusing?" (debrief)
4. "Would you use this? Why / why not?" (gut check)

**Guided mode:**
Coach the user through recruiting testers, running sessions, and synthesizing findings. Offer to help write a test script tailored to their JTBD.

**Skipping this phase:**
If the user says "I already know my audience well" or "I've validated this before," respect that. Ask: "What gives you confidence the hypothesis is right?" If the answer is solid, move on. If it's vague, gently push for at least one test.

**After testing — the decision gate:**
Based on test results, one of three things happens:
- **Proceed** → the prototype validated the hypothesis. Move to Phase 8 (Story Map) and commit to full planning.
- **Pivot** → the tests revealed a different problem or approach. Loop back to Phase 5 (Sketch) with new insights.
- **Kill** → the hypothesis was wrong and no pivot makes sense. Document what was learned and stop.

This is the most important moment in the process. Everything before this was cheap. Everything after this is expensive. Test before you commit.
