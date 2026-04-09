# Julia McCoy Method

Produce AI avatar YouTube videos at scale using the workflow that grew Julia McCoy's "Dr. McCoy" channel to 250K subscribers in 18 months.

## The Pipeline

```
Script (Claude) → Avatar (HeyGen) → Voice (ElevenLabs) → Edit → Publish
```

## Install

```bash
claude install-skill https://github.com/razbakov/skills/tree/main/skills/julia-mccoy-method
```

## Usage

```
/julia-mccoy-method script "How to choose your first dance festival"
/julia-mccoy-method plan
/julia-mccoy-method audit
/julia-mccoy-method optimize [paste script]
```

## Modes

| Mode | What it does |
|------|-------------|
| **script** | Write a full video script with hooks, timing, and B-roll cues |
| **plan** | Design your avatar video pipeline from scratch |
| **audit** | Check if you have everything needed to start |
| **optimize** | Improve an existing script against proven benchmarks |

## Key Benchmarks

- **CTR:** 7-8%+
- **Avg watch time:** 8+ minutes
- **Views improvement:** 3-4x vs non-avatar content
- **Cadence:** 3-7 videos per week

## Tools Required

- **HeyGen** (Business plan) — AI avatar generation
- **ElevenLabs** (Creator plan) — Voice cloning
- **Claude** — Script writing
- **Video editor** — Assembly (CapCut, Premiere, or freelancer)
