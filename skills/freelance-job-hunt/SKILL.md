---
name: freelance-job-hunt
description: Search a freelance platform for jobs matching user's skills, verify each listing is live with actual budget, and create a project with verified opportunities and draft proposals.
user_invocable: true
---

# Freelance Job Hunt

Search a freelance platform for matching jobs, verify every listing in the browser, and produce a ready-to-apply project with draft proposals.

## Trigger

Use when the user asks to find freelance work, search for gigs, look for jobs on Upwork/Malt/freelancermap, or wants to start freelancing.

## Inputs

- User's profile (skills, languages, location, portfolio) — read from `profile.md` or ask
- Target platform (default: Upwork)
- Number of jobs to find (default: 10)

## Process

### 1. Build candidate profile

Read the user's `profile.md`, `now.md`, and project registry to extract:
- Technical skills and stack
- Languages spoken
- Location and timezone
- Portfolio projects (live URLs, GitHub repos)
- Unique selling points (combinations of skills that are rare)

### 2. Search for jobs

Use the browser to search the target platform for jobs matching the user's top skills. Run multiple searches across skill combinations:
- Primary stack (e.g., "Vue Nuxt")
- AI/emerging skills (e.g., "Claude API", "LangChain", "MCP")
- Niche combinations (e.g., "Nuxt Firebase", "AI automation n8n")

Collect URLs of promising listings.

### 3. Verify EVERY listing (CRITICAL)

For EACH job URL, open it in the browser and:
1. Confirm the page loads the actual job (not a redirect to a category page = expired)
2. Scroll down to find the budget/rate section
3. Record the **exact posted budget** from the page
4. Note: type (hourly/fixed), duration, hours/week, experience level, location restrictions
5. Check if the job says "no longer available" (closed but still visible)

**Rules:**
- NEVER estimate or guess budgets. Only use the number shown on the page.
- If a listing redirects to a general page, mark it as **Expired** and exclude it.
- If a listing says "US only" or has location restrictions, note that.
- Replace expired jobs with new searches until you have the target number of live, verified jobs.

### 4. Create the project

Create `~/Projects/freelance/README.md` (or update if it exists) with:

```markdown
# Freelance

**Mission:** [User's freelance goal]

## Competitive Edge
- [Unique selling points extracted from profile]

## Market Rates
| Skill Area | Rate Range |
|---|---|
| [skill] | $X–Y/hr |

## Opportunities ([Platform], [Date])

### [Category Name]

#### 1. [Job Title]
- **Type:** [hourly/fixed, hours/week]
- **Duration:** [from listing]
- **Budget:** [EXACT number from listing page]
- **Link:** [clickable URL]
- **Why you:** [1-2 sentences connecting user's experience to this job]

<details><summary>Draft message</summary>

[Personalized proposal referencing user's specific projects and experience relevant to THIS job. Include portfolio link. Keep under 150 words.]
</details>
```

### 5. Write draft proposals

For each job, write a proposal that:
- Opens with relevant experience (not "I'm a developer")
- References a specific project the user built that demonstrates the required skill
- Is concise (under 150 words)
- Ends with portfolio link
- If the job post mentions a keyword to include, include it

## Output

- `~/Projects/freelance/README.md` with only verified, live jobs
- Each job has: verified budget, clickable link, personalized draft message
- Register project in ikigai's PROJECTS.md if not already there

## Lessons

- Upwork listings expire fast. A search result from even 1 week ago may be dead.
- NEVER present estimated budgets as real ones. The actual posted rate is often far lower than market rates.
- Always open each URL in the browser to verify — web search results and API scraping cannot access Upwork budgets reliably.
- Most Upwork AI/dev jobs post $10-30/hr, not the $60-150/hr "market rate" from blog posts.
- Some listings are US-only — check location restrictions before including.
