---
description: Sync a list of people into Google Contacts tagged with a specific label. Creates the label if missing, dedupes by email (adds the label to existing contacts instead of creating duplicates), and creates new contacts with the label attached in a single API call. Uses the Google People API directly via the gog CLI's stored OAuth refresh token. Use this whenever the user wants to add, tag, label, group, or organize contacts in Google Contacts — including phrases like "add these people to my contacts", "tag them as X", "sync this signup list", "put them in a Google Contacts group", "label all of these". Also the right skill when the user has a list (spreadsheet, CRM export, signup data) and wants it represented in Google Contacts with a recognizable label for later bulk actions.
user_invocable: true
---

# Google Contacts — Label Sync

Given a list of people and a label name, make sure every person is in Google Contacts with that label attached. Dedupe by email — existing contacts get the label added, not a duplicate entry created.

## Trigger

Natural user phrasings that should invoke this skill:

- "add these people to my google contacts tagged X"
- "sync this signup list to contacts under label Y"
- "tag all these contacts as Z"
- "put these attendees in a google contacts group"
- "make sure everyone on this list is in my contacts with the X label"

If the user has a list of names + emails and wants them discoverable later by a shared tag, this is the skill.

## Why the People API, not `gog contacts`

`gog contacts create` doesn't support `memberships` (contact group / label assignment) as a flag. Attaching a label requires either:

1. Create the contact with `gog`, then call `people:updateContact` to patch `memberships` (two round trips, two failure points per contact), or
2. Call `people:createContact` directly with `memberships` in the request body (one round trip, atomic).

This skill uses option 2 via `curl` + an access token bootstrapped from `gog`'s stored refresh token. It's still authenticated as the gog-managed user — no new OAuth flow needed.

## Prerequisites

1. `gog` is installed and authorized. Verify with `gog auth status` — `credentials_exists` should be `true`.
2. The authorized account has the `https://www.googleapis.com/auth/contacts` scope. Step 1 of the process verifies this; if missing, the fix is `gog auth manage` (adds scopes interactively).
3. Python 3 is available for JSON parsing.

## Inputs

Always normalize input to a JSON file first — makes the run idempotent and debuggable.

Minimal per-person record:
```json
{"given": "...", "family": "...", "email": "...", "phone": "..."}
```

Optional fields the skill will use if present: `organization`, `title`, `urls`, `note`, `address`.

**Label name**: the human-readable Google Contacts label (e.g., `MysteryGames`, `FestivalAttendees-2026`). If the label doesn't exist, this skill creates it. Labels are per-account and don't conflict with groups from other Google Workspace domains.

**Optional `--bio`**: a short string added to every *created* contact's biography (e.g., `"Source: MysteryGames signup, 2026-04-17"`). Helpful for tracing provenance months later. Not applied to contacts that already exist — you're just adding a label to them, not editing their entry.

## Process

### Step 1 — Get an access token with contacts scope

Discover config paths rather than hardcoding — `gog`'s install location varies by OS. `gog auth status` emits TSV with the relevant paths:

```bash
eval "$(gog auth status 2>/dev/null | awk -F'\t' '
  $1=="account"           {printf "ACC=%s\n",           $2}
  $1=="credentials_path"  {printf "CRED=%s\n",          $2}
')"
```

If `$ACC` or `$CRED` are empty, abort with an instruction to run `gog auth manage` first.

Export the refresh token for that account and exchange it for a short-lived access token:

```bash
RTFILE=$(mktemp -t gog-rt.XXXXXX.json)
ATFILE=$(mktemp -t gog-at.XXXXXX.txt)
chmod 600 "$RTFILE" "$ATFILE"  # owner-only; /tmp is world-readable on multi-user systems

gog auth tokens export "$ACC" --out="$RTFILE" --overwrite >/dev/null

RT=$(python3 -c "import json,sys; print(json.load(open('$RTFILE'))['refresh_token'])")
CID=$(python3 -c "import json,sys; print(json.load(open('$CRED'))['client_id'])")
CSEC=$(python3 -c "import json,sys; print(json.load(open('$CRED'))['client_secret'])")

curl -s -X POST https://oauth2.googleapis.com/token \
  -d "client_id=$CID" -d "client_secret=$CSEC" \
  -d "refresh_token=$RT" -d "grant_type=refresh_token" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])" > "$ATFILE"
AT=$(cat "$ATFILE")
```

**Verify scope** before any People API call:

```bash
HAS_SCOPE=$(curl -s "https://oauth2.googleapis.com/tokeninfo?access_token=$AT" \
  | python3 -c "import json,sys; s=json.load(sys.stdin).get('scope',''); print('yes' if 'auth/contacts' in s else 'no')")
```

If `no`, abort and tell the user: *"The gog-authorized account is missing the Contacts scope. Run `gog auth manage` and re-authorize with the Contacts scope enabled, then re-run."*

**Trap cleanup so secrets get removed even on error:**

```bash
trap 'rm -f "$RTFILE" "$ATFILE"' EXIT
```

This pattern applies for the rest of the skill — treat the access token file as write-once/read-many and the refresh token file as sensitive.

### Step 2 — Find or create the contact group (label)

List user-defined groups:

```bash
GROUP=$(curl -s "https://people.googleapis.com/v1/contactGroups?pageSize=200" \
  -H "Authorization: Bearer $AT" \
  | python3 -c "
import json,sys
target = sys.argv[1]
for g in json.load(sys.stdin).get('contactGroups', []):
    if g.get('groupType') == 'USER_CONTACT_GROUP' and g.get('name') == target:
        print(g['resourceName'])
        break
" "$LABEL_NAME")
```

If `$GROUP` is empty, create it:

```bash
GROUP=$(curl -s -X POST "https://people.googleapis.com/v1/contactGroups" \
  -H "Authorization: Bearer $AT" -H "Content-Type: application/json" \
  -d "{\"contactGroup\":{\"name\":\"$LABEL_NAME\"}}" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['resourceName'])")
```

`$GROUP` will have the form `contactGroups/<id>`. Keep the whole string — the membership endpoint needs it.

### Step 3 — Dedupe against existing contacts by email

The `people:searchContacts` endpoint is eventually consistent — it relies on an index that lags direct writes. Warm the cache with one empty query, pause briefly, then run the real lookups:

```python
import subprocess, urllib.parse, time, json

AT = open(ATFILE).read().strip()

# Warm the searchContacts cache — the index is eventually consistent
subprocess.run(['curl','-s',
  'https://people.googleapis.com/v1/people:searchContacts?query=&readMask=names',
  '-H', f'Authorization: Bearer {AT}'], capture_output=True)
time.sleep(2)

def lookup(email):
    url = (f"https://people.googleapis.com/v1/people:searchContacts"
           f"?query={urllib.parse.quote(email)}"
           f"&readMask=names,emailAddresses,memberships&pageSize=30")
    r = subprocess.run(['curl','-s',url,'-H',f'Authorization: Bearer {AT}'],
                       capture_output=True, text=True)
    matches = []
    for item in json.loads(r.stdout).get('results', []):
        person = item.get('person', {})
        for ea in person.get('emailAddresses', []):
            if ea.get('value','').lower() == email.lower():
                matches.append(person)
                break
    return matches
```

For each input person:
- 0 matches → bucket as `missing`
- 1 match → bucket as `exists` with that `resourceName`
- 2+ matches → bucket as `ambiguous`, report to user, ask which one (don't silently pick the first — duplicates in contacts usually signal a real distinction the user knows about, like personal vs. work)

Pace requests (`time.sleep(0.2)` between lookups). Save the dedup map to `/tmp/<slug>-dedup.json` for debugging and retry.

### Step 4 — Create missing contacts WITH the label attached

One API call per missing contact:

```python
body = {
    "names": [{"givenName": p['given'], "familyName": p.get('family','')}],
    "emailAddresses": [{"value": p['email']}],
    "phoneNumbers": [{"value": p['phone']}] if p.get('phone') else [],
    "memberships": [{"contactGroupMembership": {"contactGroupResourceName": GROUP}}],
}
if BIO_TEXT:
    body["biographies"] = [{"value": BIO_TEXT, "contentType": "TEXT_PLAIN"}]

# Retry on empty response — occasional transient network blips
for attempt in range(3):
    r = subprocess.run(['curl','-s','--max-time','20','-X','POST',
      'https://people.googleapis.com/v1/people:createContact',
      '-H', f'Authorization: Bearer {AT}',
      '-H', 'Content-Type: application/json',
      '-d', json.dumps(body)], capture_output=True, text=True)
    if r.stdout.strip():
        break
    time.sleep(1 + attempt)  # 1s, 2s, 3s backoff
```

Parse the response and collect the returned `resourceName` into a `created` list. Pace with `time.sleep(0.25)` between creates.

### Step 5 — Attach label to existing contacts (batch)

For people bucketed as `exists`, add them to the group in one batch call. `members:modify` accepts up to 1000 resourceNames:

```bash
curl -s -X POST "https://people.googleapis.com/v1/${GROUP}/members:modify" \
  -H "Authorization: Bearer $AT" -H "Content-Type: application/json" \
  -d "{\"resourceNamesToAdd\":[\"people/c...\", \"people/c...\"]}"
```

Empty `{}` response on success. Adding someone already in the group is a no-op — idempotent.

### Step 6 — Verify and report

Fetch the group to confirm the final member count:

```bash
curl -s "https://people.googleapis.com/v1/$GROUP?maxMembers=1000" \
  -H "Authorization: Bearer $AT" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(f\"{d['name']}: {d.get('memberCount',0)} members\")"
```

Report to the user:
- **Label**: name + `https://contacts.google.com/label/<id>` (extract `<id>` from the `contactGroups/<id>` resource name)
- **Created**: N — bullet list with names
- **Updated** (existing, label attached): N — bullet list
- **Ambiguous / needs user decision**: N (with which emails had multiple matches)
- **Failed**: N (with emails + error reason)
- **Total in label now**: N

### Step 7 — Cleanup

The `trap` in Step 1 handles this, but state it explicitly for readers who copy-paste fragments:

```bash
rm -f "$RTFILE" "$ATFILE"
```

These files contain a refresh token (long-lived) and an access token (1h). Leaving them behind is a real risk on shared machines — they grant access to the user's entire Google account scope bundle, not just Contacts.

## Error handling

| Symptom | Cause | Fix |
|---|---|---|
| `gog auth tokens export` fails | Refresh token missing or expired | `gog auth manage` to re-auth |
| Token exchange returns `invalid_grant` | Refresh token revoked | `gog auth manage` |
| `tokeninfo` response missing `auth/contacts` scope | gog authorized without Contacts scope | `gog auth manage`, re-authorize with Contacts |
| `409` on group create | Race — label created between list and create | Re-list, use found resourceName |
| `429` rate limit | Too-tight loop | Increase sleep to 0.5s between calls |
| Empty response body on createContact | Transient network | Skill retries 3x with backoff; surface persistent failures |
| 2+ matches for same email | Existing duplicate contacts | Ask user which one to label; don't silently pick |

## When NOT to use this skill

- **Single-contact creation** with no label needed — `gog contacts create` is simpler and doesn't need OAuth juggling.
- **Bulk creation with no labeling** — `gog contacts create` in a loop.
- **Contact merging or deduplication of existing entries** — this skill creates and labels; it doesn't merge. Google Contacts has a built-in merge UI for that.
- **Deleting or removing labels** — out of scope. Same `members:modify` endpoint supports `resourceNamesToRemove` if needed later.

## Idempotency

Re-running with the same input list is safe:
- Existing contacts stay put; label-add is a no-op if already attached.
- Missing ones get created.
- Dedup map at `/tmp/<slug>-dedup.json` shows which bucket each person landed in.

This makes incremental syncs trivial: when the source list grows (e.g., 3 new signups since last run), just re-run — only the new ones will hit `createContact`.

## One thing to double-check before running

Phone number format: People API stores whatever string you pass — no validation, no normalization. If a downstream consumer needs a specific format (E.164 for WhatsApp, for instance), normalize in a wrapper skill before calling this one. This skill deliberately doesn't touch phone format because "what's the right format" depends on where the phone is going next.
