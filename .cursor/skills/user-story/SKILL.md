---
name: user-story
description: Transform requirements into structured user stories with acceptance criteria using INVEST principles. Use when the user asks to write a user story, create a ticket, define acceptance criteria, or convert requirements into dev-ready stories.
---
### Custom Instruction for Transforming Requirements into User Story Format

Objective: Transform any given requirements into a user story with detailed acceptance criteria, ensuring clarity and completeness for development and QA teams.

#### Steps:

- Determine who the user is and what they want to achieve and type of the ticket
- Follow the standards below to describe the ticket
- When ticket is too big suggest to split it into multiple stories by asking a question in the end.

#### Standards:
INVEST Framework for writing tickets
When writing tickets, we like to follow the agile INVEST principle. In the ideal world tickets should be:

- Independent - of other tickets
- Negotiable - engineers should be able to provide input
- Valuable - provide user and business value
- Estimable - include enough information to estimate
- Small - manageable enough unit of work
- Testable - a QA or PO/PM can test the end result

Titles should be clear at a glance, concise, easy to find via search, and should portray the where and what. One look at the title should be enough to quickly classify and recognize the ticket later. 

Title format: `# <Topic>: <Action>` (use ":" instead of " - " in ticket title). The title is always an h1 (`#`) with no ticket-type prefix.

Heading levels:
- `#` (h1) — story title
- `##` (h2) — top-level sections (Context, Acceptance Criteria, Out of Scope)
- `###` (h3) — sub-groups within Acceptance Criteria when there are distinct areas

The topic should be the location of the change, for example, Homepage, Thank you page, or Salesforce. The action should concisely summarise what needs to be done, for example, Product mismatch (bug), and Transfer Shopify data to SFDC.

Examples of good ticket titles: "Product Pages: Center Images Automatically", "Browser API: Update Custom Attribute Docs", "Distributed Tracing: Add CAT Relationship Detail".

The ticket type determines what type of ticket it is. Although the ticket types can differ depending on the project, as a rule at least 3 types should always be present

Story: A story contains a user story with testable requirements

Task: A task is a new task that needs to be completed. (Often subordinate to stories) 

Bug: A bug is an error/problem that deviates from the actual target state of the page

Task
A task is a new task that needs to be completed (often subordinate to stories). These tickets should always clearly describe the task.

Bug
A bug is an error/problem that deviates from the actual target state of the page. It should have steps to reproduce, actual result and expected result. Tickets ALWAYS contain a link so that the relevant page can be found and checked quickly. 

Story
At the most basic level, these User stories should contain:

User story summary

When outlining the goal of the issue, use user stories to your advantage. 

According to Atlassian, "A user story is an informal, general explanation of a software feature written from the perspective of the end user. Its purpose is to articulate how a software feature will provide value to the customer."

"User stories are often expressed in a simple sentence, structured as follows: 'As a PERSONA, I want to GOAL_DESCRIPTION, so that CUSTOMER_VALUE_DESCRIPTION.' "

Simply put, user stories are development tasks often expressed as “persona + need + purpose.” 

Acceptance criteria are the requirements that need to be met in order to mark a user story as complete. Best practices are to keep the acceptance criteria number below 8 and to use either of these methods to write them:

- Rules oriented with a verification criteria acceptance checklist
- Scenario-oriented with the given/when/then format

Rules:
- By default use "Rules oriented" criteria, suggest as a question to switch to "Scenario-oriented"
- Break down the requirements into specific, testable criteria.
- Use checklist-like language, avoiding "must be" and instead using "is" or "has".
- Ensure criteria are clear, actionable, and verifiable.
- Specify any default states or conditions mentioned in the requirements.
- Ensure all necessary functionalities and conditions are covered.
- Specify labels, identifiers and default  of input fields, buttons, etc.
- Keep the acceptance criteria number below 8 
- Don't use identifiers in title, only labels
- Write only dev requirements
- Don't write about testing and verification
- Write for PMs, not engineers. Acceptance criteria describe what the user experiences, not how the code works. No file paths, function names, database models, or line numbers in ACs — those belong in dev notes or task comments.
- Use clear, user-facing language for UI labels and actions. If a label would confuse a PM reading the story, rename it. Prefer action-oriented labels (e.g. "Check Quality" over "Re-run").
- Don't include concrete examples that need extra context to understand. If an example raises more questions than it answers, describe the behavior plainly instead.
- Only reference features and data that actually exist in the scope of the story. Don't assume capabilities from other parts of the system (e.g. eval pipeline) carry over to production features.
- See example of user stories below

<examples>
# Search: Find Hotels by City, Name, or Street

As a user, I want to use a search field to type a city, name, or street, so that I can find matching hotel options.

## Acceptance Criteria
- The search field is placed on the top bar.
- Search starts once the user clicks “Search”.
- The field contains a placeholder with grey-colored text: “Where are you going?”
- The placeholder disappears once the user starts typing.
- Search is performed if a user types in a city, hotel name, street, or all combined.
- Search is in English, French, German, and Ukrainian.
- The user can’t type more than 200 symbols.
- The search doesn’t support special symbols (characters). If the user has typed a special symbol, show the warning message: “Search input cannot contain special symbols.”

---

# Sign In: Forgot Password

As a user, I want to be able to recover the password to my account, so that I will be able to access my account in case I forgot the password.

## Scenario: Forgot password
- Given: The user navigates to the login page.
- When: The user selects <forgot password> option.
- And: Enters a valid email to receive a link for password recovery.
- Then: The system sends the link to the entered email.
- Given: The user receives the link via the email.
- When: The user navigates through the link received in the email.
- Then: The system enables the user to set a new password.

---

# Sign In: Login

As a user, I want to enter my user credentials, so that I can access my personal content.

## Acceptance Criteria:
- Acceptance Criteria 1:
  - Given: Login page is shown.
  - When: User entered valid credentials.
  - Then: Grant user access to personal space.
</examples>
