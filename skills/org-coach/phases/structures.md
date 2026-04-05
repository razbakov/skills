# Building Organizations — Structural Patterns

These patterns define how teams and roles relate to each other structurally. As the organization grows, revisit these patterns to evolve the structure.

## Team Types

### Circle

A self-governing, semi-autonomous team of equivalent people who collaborate to account for a domain:

- Members share authority to govern and operate within their domain constraints
- All members are equivalent in governance decision-making
- The circle maintains its own policies, distributes responsibilities, and shares accountability
- Can delegate or recruit new members as needed

**For AI agent organizations:** A group of agents working in the same domain (e.g., all Festival Experience agents) can be treated as a circle. They share governance of their domain — the Product Lead, Engineer, Designer, and Operations Manager each have a voice in how the domain operates. The delegator sets constraints, but the agents collectively evolve their operational processes.

### Helping Team

A team that executes work without making governance decisions. The delegator defines rules; the team executes and flags governance needs.

- Delegator defines procedures and constraints
- Team executes tasks within those constraints
- Team informs the delegator when governance decisions are needed
- Team members can raise objections and select a representative

**For AI agent organizations:** This is the default structure for AI agent teams. Agents execute within their role boundaries and escalate governance decisions to delegators. The Coordinator can act as the team's representative in governance discussions.

### Open Team

Intentionally attending to a domain by invitation — people contribute when they can, not by formal assignment:

- Delegator creates an invitation with driver, responsibilities, and constraints
- Contributors participate based on availability
- Regular reviews to support effectiveness

**For AI agent organizations:** Use Open Team when you need occasional input from agents outside their primary domain. Example: the Marketing Lead occasionally contributes to the Designer's domain when social media assets are needed, but isn't formally assigned to that domain.

### Service Circle

A structure to provide services required by two or more domains:

- Formed by members from the domains it serves, plus specialists
- Provides shared operational services

**For AI agent organizations:** If multiple domains need the same capability (e.g., data analytics, content writing), create a Service Circle rather than duplicating the capability in each domain. Example: the Analyst agent serves both the Festival Experience domain and a future Discovery domain.

## Linking Patterns

### Linking

Enable the flow of information and influence between two teams:

- One team selects a member to represent their interests in the governance of another team
- The representative participates in the other team's governance decisions

**For AI agent organizations:** When two agent groups need to stay aligned, one agent from each group attends the other's governance discussions (via the Coordinator's synthesis). Example: the Product Lead represents the Engineering team's needs in governance discussions about the Festival Experience domain.

### Double Linking

Two-way flow of information between interdependent teams:

- Each team selects a member to represent their interests in the other team's governance
- Enables equivalence between teams in hierarchical structures

**For AI agent organizations:** When two domains are heavily interdependent, ensure both domains have a representative in each other's governance. The Coordinator facilitates this by including both domains' perspectives in every cross-domain decision.

### Representative

A team member selected to participate in another team's governance:

- Selected for a limited term
- Stands for their team's interests: raises agenda items, forms proposals, raises objections
- Not a leader — a voice for the team

**For AI agent organizations:** The Coordinator naturally acts as representative for the agent team in founder discussions. Additionally, specific agents can be dispatched to represent their domain's perspective in cross-domain decisions.

### Delegate Circle

A governance body formed by representatives from multiple domains:

- Representatives are selected by their respective domains
- The delegate circle makes governance decisions affecting all domains
- External experts can be invited

**For AI agent organizations:** When the organization has 3+ domains, create a delegate circle by having the Coordinator synthesize input from one representative agent per domain. The delegators (founders) make the final consent decisions, informed by the delegate circle's synthesis.

## Organizational Structures (at Scale)

### Peach Organization

Decentralized structure where peripheral teams deliver value directly to customers:

- Teams at the periphery interact directly with the outside world
- The center provides internal services to support peripheral teams
- Domains are linked as needed

**For AI agent organizations:** As the organization grows, the customer-facing agents (e.g., those managing festival relationships, dancer interactions) form the periphery. Support agents (analytics, engineering, operations) form the center. The Coordinator ensures the center serves the periphery, not the other way around.

### Double-Linked Hierarchy

Transitioning a traditional hierarchy toward collective governance:

- Shift governance from individuals to circles at all levels
- Each circle sends a representative upward and receives one downward (double linking)
- Maintains functional hierarchy while adding equivalence to governance

**For AI agent organizations:** When agents have sub-agents (e.g., the Engineer delegates to a Frontend Engineer and Backend Engineer), use double linking: the sub-agents send a representative to the parent agent's governance, and the parent sends context downward.

### Service Organization

Multi-stakeholder collaboration toward a shared driver:

- Central entity aligns efforts across different organizations or departments
- Sometimes called a "backbone organization"

**For AI agent organizations:** If WeDance partners with other organizations (e.g., dance schools, festival networks), the S3 governance structure can extend to include partner representatives. Agents from different organizations collaborate through shared governance.

### Fractal Organization

Multiple constituents with a common driver sharing learning and aligning action:

- Tier 1: Individual constituents (branches, projects)
- Tier 2: Function-specific delegate circles sharing learning across constituents
- Tier 3: Cross-functional delegate circle making policies for the whole body

**For AI agent organizations:** If the S3 governance model is replicated across multiple projects (e.g., WeDance expands to multiple cities, each with their own agent team), use a fractal structure: each city team has its own governance, with delegates forming cross-city circles to share learning and align policies.
