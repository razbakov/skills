---
name: litellm-proxy
description: Set up LiteLLM AI Gateway proxy with Docker Compose for Claude Code Max subscription. Use when the user wants to route Claude Code through LiteLLM for cost tracking, budget controls, or usage monitoring. Also trigger when user mentions "litellm", "AI gateway", "proxy for Claude Code", "track Claude usage", "Claude Code billing", or wants to set up a local proxy between Claude Code and Anthropic API.
---

# LiteLLM Proxy Setup for Claude Code

Set up a LiteLLM AI Gateway proxy via Docker Compose so Claude Code Max subscription traffic flows through LiteLLM for cost attribution, budget controls, and usage tracking per user or team.

**Reference docs:** https://docs.litellm.ai/docs/tutorials/claude_code_max_subscription

## How it works

Claude Code sends two headers on each request:
- `Authorization: Bearer {oauth_token}` — the Max subscription OAuth token, forwarded to Anthropic
- `x-litellm-api-key: Bearer {virtual_key}` — authenticates with LiteLLM proxy

LiteLLM validates the virtual key, logs the request, then forwards everything (including the OAuth token) to Anthropic.

## Setup steps

### 1. Create project directory

```bash
mkdir -p ~/Projects/litellm && cd ~/Projects/litellm
```

### 2. Create `docker-compose.yml`

```yaml
services:
  litellm:
    image: docker.litellm.ai/berriai/litellm:main-stable
    volumes:
      - ./config.yaml:/app/config.yaml
    command:
      - "--config=/app/config.yaml"
    ports:
      - "4000:4000"
    environment:
      DATABASE_URL: "postgresql://llmproxy:dbpassword9090@db:5432/litellm"
      STORE_MODEL_IN_DB: "True"
    env_file:
      - .env
    depends_on:
      - db
    healthcheck:
      test:
        - CMD-SHELL
        - python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:4000/health/liveliness')"
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  db:
    image: postgres:16
    restart: always
    container_name: litellm_db
    environment:
      POSTGRES_DB: litellm
      POSTGRES_USER: llmproxy
      POSTGRES_PASSWORD: dbpassword9090
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -d litellm -U llmproxy"]
      interval: 1s
      timeout: 5s
      retries: 10

  prometheus:
    image: prom/prometheus
    volumes:
      - prometheus_data:/prometheus
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.path=/prometheus"
      - "--storage.tsdb.retention.time=15d"
    restart: always

volumes:
  prometheus_data:
    driver: local
  postgres_data:
    name: litellm_postgres_data
```

### 3. Create `config.yaml`

Two critical settings in `general_settings`:
- `forward_client_headers_to_llm_api: true` — forwards the OAuth token to Anthropic
- `litellm_key_header_name: "x-litellm-api-key"` — tells LiteLLM to authenticate via this custom header instead of the `Authorization` header (which carries the OAuth token)

```yaml
model_list:
  - model_name: anthropic-claude
    litellm_params:
      model: anthropic/claude-sonnet-4-6
  - model_name: anthropic-opus
    litellm_params:
      model: anthropic/claude-opus-4-6
  - model_name: anthropic-haiku
    litellm_params:
      model: anthropic/claude-haiku-4-5-20251001

general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
  database_url: "postgresql://llmproxy:dbpassword9090@db:5432/litellm"
  forward_client_headers_to_llm_api: true
  litellm_key_header_name: "x-litellm-api-key"
```

Update model IDs to the latest available at time of setup. Check https://docs.anthropic.com/en/docs/about-claude/models for current model IDs.

### 4. Create `.env`

Generate secure random keys for production use. The salt key cannot be changed after adding a model.

```env
LITELLM_MASTER_KEY="sk-change-me-to-a-secure-key"
LITELLM_SALT_KEY="sk-change-me-to-a-secure-salt"
UI_USERNAME="admin"
UI_PASSWORD="admin"
```

### 5. Create `prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "litellm"
    static_configs:
      - targets: ["litellm:4000"]
```

### 6. Start Docker Compose

All config files (`.env`, `config.yaml`, `prometheus.yml`) must exist before starting — Docker will create directories instead of files if they're missing.

```bash
docker compose up -d
```

Wait for health check to pass:

```bash
sleep 15 && curl -s http://localhost:4000/health/liveliness
```

### 7. Generate a virtual key

Use the master key to create a virtual key for Claude Code:

```bash
curl -s -X POST 'http://localhost:4000/key/generate' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer sk-change-me-to-a-secure-key' \
  -d '{"key_name": "claude-code"}' | python3 -m json.tool
```

Save the returned `key` value (starts with `sk-`).

### 8. Configure Claude Code environment

Add to `~/.zshrc` (or `~/.bashrc`):

```bash
# LiteLLM Proxy (Claude Code Max subscription)
export ANTHROPIC_BASE_URL=http://localhost:4000
export ANTHROPIC_MODEL="anthropic-claude"
export ANTHROPIC_CUSTOM_HEADERS="x-litellm-api-key: Bearer <YOUR_VIRTUAL_KEY>"
```

Then `source ~/.zshrc` and restart Claude Code.

### 9. Verify

```bash
# Check proxy auth works
curl -s -H "x-litellm-api-key: Bearer <YOUR_VIRTUAL_KEY>" http://localhost:4000/model/info

# Test from Claude Code
source ~/.zshrc && echo "say hi" | claude --print
```

## Services

| Service | URL |
|---------|-----|
| LiteLLM Proxy | http://localhost:4000 |
| LiteLLM UI | http://localhost:4000/ui |
| Prometheus | http://localhost:9090 |
| Postgres | localhost:5432 |

## Known issues

- The LiteLLM UI (`/ui/`) authenticates via `Authorization` header internally. When `litellm_key_header_name` is set to a custom header, the UI login may not work with API key auth. Use `UI_USERNAME`/`UI_PASSWORD` for UI access instead.

## Management commands

```bash
# Start
cd ~/Projects/litellm && docker compose up -d

# Stop
cd ~/Projects/litellm && docker compose down

# Restart (after config changes)
cd ~/Projects/litellm && docker compose restart litellm

# Logs
cd ~/Projects/litellm && docker compose logs litellm --tail 50

# Health check
curl -s http://localhost:4000/health/liveliness
```
