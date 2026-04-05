---
description: Book a cleaning lady via Putzperle.de. Use when the user asks to book cleaning, hire a cleaner, schedule house cleaning, or says "clean the house". Uses the authenticated browser to search, select, and message a cleaner.
---

# Book Cleaning

Book a cleaning service through Putzperle.de using the user's authenticated browser session.

## Inputs

- **Address:** From user's global CLAUDE.md Personal Info section
- **Date:** User-specified or default to today/tomorrow
- **Tasks:** User-specified or default checklist:
  - Take out trash
  - Return Pfand (bottles/cans)
  - Clean bathroom
  - Clean windows
  - Vacuum floors
  - Wipe/mop floors

## Process

1. **Connect to browser**
   - `tabs_context_mcp(createIfEmpty: true)` to get tabId

2. **Navigate to Putzperle**
   - Navigate to `https://putzperle.de/de`
   - Decline cookies (click "Ablehnen")
   - Ensure "Ich suche eine Reinigungskraft" is selected

3. **Search by location**
   - Enter PLZ `80799` in "Stadt oder PLZ" field
   - Select `80799 München` from dropdown
   - Click "Jetzt suchen"

4. **Select a cleaner**
   - Scroll through results, prioritize:
     - Nearby (< 5 km)
     - High ratings (4.5+ stars)
     - Recent activity ("Zuletzt online: Heute/Gestern")
     - Services include: Allg. Wohnungsreinigung, Fenster putzen
     - Reasonable price (15-25 EUR/Stunde)
   - Click on the best match to view profile

5. **Verify profile**
   - Check reviews, experience, languages
   - Confirm services match needs
   - Note the hourly rate

6. **Send booking message**
   - Click "Konversation öffnen"
   - Compose message (adapt based on date/tasks):

   ```
   Hallo [Name],

   ich suche eine Reinigungskraft für [heute/morgen], [Datum].

   Aufgaben:
   - Allgemeine Wohnungsreinigung
   - Badezimmer putzen
   - Fenster putzen
   - Staubsaugen und Wischen

   Adresse: <ADDRESS_FROM_CLAUDE_MD>
   Klingel: <NAME_FROM_CLAUDE_MD>

   Wann hätten Sie Zeit? Geschätzt ca. 2-3 Stunden.

   Vielen Dank!
   Alex
   ```

   - **ASK USER for confirmation before sending** (this is a message on their behalf)

7. **If no account exists**
   - Navigate to registration page
   - **STOP** — user must create the account themselves (prohibited action)
   - Resume after user confirms account is created

## Output

- Confirmation that message was sent
- Cleaner's name, rating, price, and profile link
- Remind user to check Putzperle inbox for response

## Notes

- User already has a Putzperle account (created 2026-03-24)
- Always ask permission before sending messages
- Cannot create accounts — user must do this themselves
- Cannot enter payment information — user must do this themselves
