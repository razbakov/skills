# X (Twitter) Post — Post tweets and threads via API

Post a single tweet or a thread to X/Twitter using OAuth 1.0a API.

## Trigger

When the user asks to post on X, tweet something, create a thread, or share content on Twitter.

## Prerequisites

- API keys at `~/.config/x/.env` with these variables:
  - `X_CONSUMER_KEY`
  - `X_CONSUMER_SECRET`
  - `X_ACCESS_TOKEN`
  - `X_ACCESS_TOKEN_SECRET`
- Account: From CLAUDE.md Personal Info (X/Twitter handle)
- Permissions: Read and Write
- Plan: Pay Per Use

## Process

### 1. Load credentials

```bash
source ~/.config/x/.env
```

### 2. Post a single tweet

```python
python3 << 'PYEOF'
import urllib.request, urllib.parse, hmac, hashlib, base64, time, uuid, json, os

def oauth_sign(method, url, params, ck, cs, tk, ts):
    op = {
        'oauth_consumer_key': ck,
        'oauth_nonce': uuid.uuid4().hex,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_token': tk,
        'oauth_version': '1.0'
    }
    all_p = {**op, **params}
    sp = '&'.join(f'{urllib.parse.quote(k,"")}'f'={urllib.parse.quote(str(v),"")}' for k,v in sorted(all_p.items()))
    bs = f'{method}&{urllib.parse.quote(url,"")}&{urllib.parse.quote(sp,"")}'
    sk = f'{urllib.parse.quote(cs,"")}&{urllib.parse.quote(ts,"")}'
    sig = base64.b64encode(hmac.new(sk.encode(), bs.encode(), hashlib.sha1).digest()).decode()
    op['oauth_signature'] = sig
    return 'OAuth ' + ', '.join(f'{urllib.parse.quote(k,"")}="{urllib.parse.quote(v,"")}"' for k,v in sorted(op.items()))

def post_tweet(text, reply_to=None):
    url = 'https://api.x.com/2/tweets'
    body = {'text': text}
    if reply_to:
        body['reply'] = {'in_reply_to_tweet_id': reply_to}
    data = json.dumps(body).encode()
    auth = oauth_sign('POST', url, {},
        os.environ['X_CONSUMER_KEY'], os.environ['X_CONSUMER_SECRET'],
        os.environ['X_ACCESS_TOKEN'], os.environ['X_ACCESS_TOKEN_SECRET'])
    req = urllib.request.Request(url, data=data, headers={
        'Authorization': auth,
        'Content-Type': 'application/json'
    })
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

# Single tweet
result = post_tweet("YOUR_TWEET_TEXT_HERE")
print(json.dumps(result, indent=2))
PYEOF
```

### 3. Post a thread

Post tweets sequentially, each replying to the previous one:

```python
python3 << 'PYEOF'
import urllib.request, urllib.parse, hmac, hashlib, base64, time, uuid, json, os

def oauth_sign(method, url, params, ck, cs, tk, ts):
    op = {
        'oauth_consumer_key': ck,
        'oauth_nonce': uuid.uuid4().hex,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_token': tk,
        'oauth_version': '1.0'
    }
    all_p = {**op, **params}
    sp = '&'.join(f'{urllib.parse.quote(k,"")}'f'={urllib.parse.quote(str(v),"")}' for k,v in sorted(all_p.items()))
    bs = f'{method}&{urllib.parse.quote(url,"")}&{urllib.parse.quote(sp,"")}'
    sk = f'{urllib.parse.quote(cs,"")}&{urllib.parse.quote(ts,"")}'
    sig = base64.b64encode(hmac.new(sk.encode(), bs.encode(), hashlib.sha1).digest()).decode()
    op['oauth_signature'] = sig
    return 'OAuth ' + ', '.join(f'{urllib.parse.quote(k,"")}="{urllib.parse.quote(v,"")}"' for k,v in sorted(op.items()))

def post_tweet(text, reply_to=None):
    url = 'https://api.x.com/2/tweets'
    body = {'text': text}
    if reply_to:
        body['reply'] = {'in_reply_to_tweet_id': reply_to}
    data = json.dumps(body).encode()
    auth = oauth_sign('POST', url, {},
        os.environ['X_CONSUMER_KEY'], os.environ['X_CONSUMER_SECRET'],
        os.environ['X_ACCESS_TOKEN'], os.environ['X_ACCESS_TOKEN_SECRET'])
    req = urllib.request.Request(url, data=data, headers={
        'Authorization': auth,
        'Content-Type': 'application/json'
    })
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

tweets = [
    "Tweet 1 — the hook",
    "Tweet 2 — details",
    "Tweet 3 — CTA + link",
]

prev_id = None
for i, text in enumerate(tweets):
    result = post_tweet(text, reply_to=prev_id)
    tweet_id = result['data']['id']
    prev_id = tweet_id
    print(f"Tweet {i+1} posted: https://x.com/status/{tweet_id}")
    time.sleep(1)  # Rate limit buffer
PYEOF
```

### 4. Delete a tweet

```python
python3 -c "
import urllib.request, urllib.parse, hmac, hashlib, base64, time, uuid, json, os
# ... same oauth_sign function ...
tweet_id = 'TWEET_ID_HERE'
url = f'https://api.x.com/2/tweets/{tweet_id}'
auth = oauth_sign('DELETE', url, {},
    os.environ['X_CONSUMER_KEY'], os.environ['X_CONSUMER_SECRET'],
    os.environ['X_ACCESS_TOKEN'], os.environ['X_ACCESS_TOKEN_SECRET'])
req = urllib.request.Request(url, method='DELETE', headers={'Authorization': auth})
resp = urllib.request.urlopen(req)
print(json.loads(resp.read()))
"
```

## Guidelines

- **Character limit:** 280 per tweet (check before posting)
- **Thread max:** No hard limit, but 5-8 tweets is ideal for engagement
- **Rate limits:** X API v2 pay-per-use — 100 tweets/15min, $0.01/tweet
- **Images:** Not yet supported via this skill — use browser for media uploads
- **Links:** YouTube/website URLs count as 23 chars (t.co wrapping)

## API Reference

- Base URL: `https://api.x.com/2/`
- Auth: OAuth 1.0a (HMAC-SHA1)
- Docs: https://docs.x.com/x-api

## Setup (if keys don't exist)

1. Go to https://console.x.com → Apps → select app
2. Set App permissions to "Read and write" (under User authentication settings)
3. Generate/regenerate Consumer Key + Access Token
4. Save all 4 values to `~/.config/x/.env`
5. Use Claude in Chrome (`tabs_context_mcp`) for the browser steps — the user is already signed in
