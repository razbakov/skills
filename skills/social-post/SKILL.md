# Social Post — Cross-Platform Content Distribution

Post content across multiple social media platforms: X (Twitter), LinkedIn, Threads, Hacker News, Reddit, Instagram, and DEV.to.

## Trigger

When the user asks to post content across social media, distribute a post, share on multiple platforms, or says "social post", "cross-post", "share everywhere".

## Prerequisites

### API-based (automated)
- **X/Twitter:** OAuth 1.0a keys at `~/.config/x/.env` — use `/x-post` skill
- **LinkedIn:** OAuth 2.0 token at `~/.config/linkedin/.env` (CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN, PERSON_ID)
- **Telegram:** Telethon via `~/.config/telegram/session` (credentials in `$TELEGRAM_API_ID` / `$TELEGRAM_API_HASH` env vars). Channels from CLAUDE.md Personal Info.

### Browser-based (requires user's authenticated session)
- **Threads:** Use Claude in Chrome (`tabs_context_mcp`) — user's Threads handle is in CLAUDE.md Personal Info
- **Hacker News:** Use Claude in Chrome (`tabs_context_mcp`) — user is signed in
- **Reddit:** Use Claude in Chrome — user is signed in
- **DEV.to:** Use Claude in Chrome (`tabs_context_mcp`) — user is signed in
- **Instagram:** Mobile-only for Reels; copy caption to clipboard for manual paste

## Process

### 1. Prepare content variants

Each platform needs different formatting. From the user's raw content, generate:

| Platform | Format | Char Limit | Notes |
|----------|--------|-----------|-------|
| X/Twitter | Thread (5-8 tweets) | 280/tweet | Hook in tweet 1, CTA + link in last tweet |
| LinkedIn | Single post | 3,000 | Professional tone, emoji bullets, hashtags at end, YouTube link inline |
| Threads | Single post | 500 | Conversational tone, link auto-generates preview card, no hashtags needed |
| Hacker News | Title + URL (Show HN) | 80 title | No hashtags, technical audience, add first comment separately |
| Reddit | Title + body (markdown) | 300 title / 40K body | Subreddit-specific tone, markdown tables work |
| Instagram | Caption for Reel/Post | 2,200 | Casual tone, hashtags at end, "link in bio" |
| DEV.to | Full blog article (markdown) | No limit | Jekyll frontmatter, embed YouTube with `{% embed URL %}`, technical depth |
| Telegram EN | Channel post | 4,096 | EN channel from CLAUDE.md — concise, emoji bullets, links at end |
| Telegram RU | Channel post (Russian) | 4,096 | RU channel from CLAUDE.md — same content translated to Russian |

### 2. Post via API (X + LinkedIn)

#### X/Twitter Thread
Use the `/x-post` skill with thread format.

#### LinkedIn Post
```bash
source ~/.config/linkedin/.env

curl -s -X POST "https://api.linkedin.com/v2/ugcPosts" \
  -H "Authorization: Bearer ${LINKEDIN_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-Restli-Protocol-Version: 2.0.0" \
  -d '{
    "author": "urn:li:person:'"${LINKEDIN_PERSON_ID}"'",
    "lifecycleState": "PUBLISHED",
    "specificContent": {
      "com.linkedin.ugc.ShareContent": {
        "shareCommentary": {
          "text": "POST_TEXT_HERE"
        },
        "shareMediaCategory": "NONE"
      }
    },
    "visibility": {
      "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
  }'
```

**Note:** LinkedIn API cannot edit or read existing posts. Only create and delete. If a post is cut off or wrong, delete and re-post.

### 3. Post via browser (Threads + HN + Reddit)

#### Threads
Use Claude in Chrome for authenticated posting. Account handle from CLAUDE.md Personal Info.

1. `tabs_context_mcp(createIfEmpty: true)` → get tabId
2. Navigate to `https://www.threads.com`
3. Click "What's new?" or the compose button (+)
4. Use JavaScript to insert text reliably (the `type` action loses line breaks):
   ```javascript
   const editor = document.querySelector('[contenteditable="true"][role="textbox"]');
   editor.focus();
   document.execCommand('selectAll', false, null);
   document.execCommand('delete', false, null);
   document.execCommand('insertText', false, postText);
   ```
5. Click "Post"
6. Get the post URL from the profile page or "View" toast link

**Important Threads notes:**
- 500 char limit per post. For longer content, post a single condensed version (not a multi-part thread — browser automation of Threads threads is unreliable)
- Links auto-generate a rich preview card with image and title
- No hashtags needed (Threads doesn't use them for discovery like Instagram)
- Line breaks via `\n` in `insertText` may collapse — the content still reads fine as a block

Use Claude in Chrome for authenticated pages:

```
tabs_context_mcp(createIfEmpty: true) → get tabId → navigate → interact
```

#### Hacker News
1. Navigate to `https://news.ycombinator.com/submit`
2. Fill title field: `Show HN: <title>` (keep under 80 chars)
3. Fill URL field with the link
4. Leave text blank (comment separately after posting)
5. Click submit
6. Copy first comment to clipboard — HN doesn't show comment box on own new posts immediately

#### Reddit
1. Navigate to `https://www.reddit.com/r/{subreddit}/submit`
2. Fill title and body
3. Click submit
4. Good subreddits for AI/dev content: r/ClaudeAI, r/artificial, r/SideProject, r/programming

### 4. Telegram (API-based)

Post to both channels using Telethon:

```bash
cd ~/.config/telegram && uvx --python python3 --from telethon python3 -c "
import asyncio, os
from telethon import TelegramClient

API_ID = int(os.environ['TELEGRAM_API_ID'])
API_HASH = os.environ['TELEGRAM_API_HASH']

async def main():
    client = TelegramClient('\$HOME/.config/telegram/session', API_ID, API_HASH)
    await client.start()
    # EN channel — use channel name from CLAUDE.md
    await client.send_message(EN_CHANNEL, EN_TEXT)
    # RU channel — use Russian translation, link to Russian blog post
    await client.send_message(RU_CHANNEL, RU_TEXT)
    await client.disconnect()

asyncio.run(main())
"
```

**Important:**
- The Russian channel must link to the Russian blog post URL (e.g. `razbakov.com/blog/2026-03-24-slug-ru`), not the English one.
- After posting, capture the message IDs and add `telegram:` links back to the blog post frontmatter using the channel handles from CLAUDE.md.

### 5. DEV.to (browser-based)

Use Claude in Chrome for authenticated posting:

1. Navigate to `https://dev.to/new`
2. Select all existing content (Cmd+A) and replace with full article
3. Use Jekyll frontmatter format:

```markdown
---
title: Article Title Here
published: false
description: Short description for SEO and social cards
tags: tag1, tag2, tag3, tag4
cover_image: https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg
canonical_url: https://razbakov.com/blog/YYYY-MM-DD-slug
---
```

**IMPORTANT:** Always include `canonical_url` pointing to the original blog post. This prevents duplicate content SEO issues and credits the source.

4. Embed YouTube videos with: `{% embed https://www.youtube.com/watch?v=VIDEO_ID %}`
5. Use full markdown: headers, tables, bold, code blocks, lists
6. Set `published: false` as draft for review, or `true` to publish immediately
7. Article should be longer and more technical than other platforms — include implementation details, code snippets, lessons learned

**Content guidelines for DEV.to:**
- Technical depth — this is a developer audience
- Include code snippets and architecture details
- Use markdown tables for structured data
- End with a discussion question
- 4 tags max (lowercase, no spaces)
- Cover image uses YouTube thumbnail by default

### 5. Instagram (manual assist)

Instagram doesn't support API posting for personal accounts. Copy the caption to clipboard:

```bash
echo 'CAPTION_HERE' | pbcopy
```

Tell the user: "Instagram caption is in your clipboard. Open Instagram → create post/reel → paste."

### 6. Report results

After posting, output a summary:

```
Posted:
- X: https://x.com/<handle>/status/...
- LinkedIn: https://www.linkedin.com/feed/update/urn:li:activity:.../
- Threads: https://www.threads.com/@<handle>/post/...
- HN: https://news.ycombinator.com/item?id=...
- Reddit: https://www.reddit.com/r/.../comments/...
- DEV.to: https://dev.to/<handle>/... (draft or published)
- Instagram: caption copied to clipboard (manual)
```

## LinkedIn API Setup (if token doesn't exist)

1. Go to https://www.linkedin.com/developers/apps → Create app
2. App name: "Social Poster", Company page: any
3. Under Products tab → request "Share on LinkedIn" and "Sign In with LinkedIn using OpenID Connect"
4. Under Auth tab → add redirect URL: `http://localhost:8888/callback`
5. Save Client ID and Client Secret to `~/.config/linkedin/.env`
6. Run `python3 ~/.config/linkedin/get-token.py` to complete OAuth flow
7. Token is saved automatically. Expires in 60 days — re-run get-token.py to refresh.

## Content Guidelines

- **X:** Hook first tweet hard. End thread with CTA. No hashtags in tweets (they don't help on X).
- **LinkedIn:** Professional but personal. Use emoji bullets. End with a question to drive engagement. Hashtags at the very end (6 max).
- **Threads:** Conversational, casual. Condense to 500 chars. Include a link for auto-preview card. No hashtags.
- **HN:** Technical, humble, no marketing language. "Show HN" for things you built. First comment should be substantive context.
- **Reddit:** Match subreddit tone. Include AMA offer. Markdown tables work well.
- **DEV.to:** Full technical blog post. Include code snippets, architecture details, lessons learned. Embed YouTube with `{% embed URL %}`. 4 tags max. End with discussion question. Longer and deeper than other platforms.
- **Instagram:** Visual-first. Short punchy lines. Heavy hashtags (10-15). "Link in bio" instead of URLs.

## Rate Limits

- X: 100 tweets/15min ($0.01/tweet on pay-per-use)
- LinkedIn: 100 posts/day
- HN: 1 submission every ~10 minutes
- Reddit: varies by karma and subreddit
