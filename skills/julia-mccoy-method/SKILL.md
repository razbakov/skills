---
name: julia-mccoy-method
description: "Produce AI avatar YouTube videos using the Julia McCoy method: write scripts with Claude, generate avatar with HeyGen, clone voice with ElevenLabs. Use when the user wants to create YouTube content at scale using AI avatars, plan an avatar video pipeline, write video scripts, or audit readiness for AI-powered video production. Triggers: 'create avatar video', 'julia mccoy method', 'AI YouTube pipeline', 'avatar content plan', 'write video script for avatar', 'scale YouTube with AI'."
---

# Julia McCoy Method

Produce YouTube videos at scale using AI avatars. Based on Julia McCoy's workflow that grew her "Dr. McCoy" channel to 250K subscribers and 2M monthly views in 18 months.

## The Pipeline

```
Script (Claude) → Avatar (HeyGen) → Voice (ElevenLabs) → Edit → Publish
```

### 1. Script Writing

Use Claude to write video scripts. The script is the foundation — everything else depends on it.

**Process:**
- Collect the creator's top 5-10 performing videos (or closest reference content)
- Analyze patterns: hooks, pacing, tone, recurring phrases, CTA style
- Write scripts in the creator's voice, not generic YouTube style
- Structure every script as: **Hook (0-30s) → Value (2-8 min) → CTA (30s)**
- Target 8-12 min total length (her avatar videos averaged 8 min retention)
- Include visual directions: `[B-ROLL: ...]`, `[TEXT ON SCREEN: ...]`, `[CUT TO: ...]`

**Script template:**

```markdown
# [Video Title]

## Hook (0:00-0:30)
[Opening line that creates curiosity or stakes]
[B-ROLL: relevant visual]

## Main Content

### Point 1 (0:30-3:00)
[Key insight]
[TEXT ON SCREEN: key takeaway]

### Point 2 (3:00-6:00)
[Key insight]

### Point 3 (6:00-8:00)
[Key insight]

## CTA (8:00-8:30)
[Specific call to action]
[END SCREEN: subscribe + related video]
```

### 2. Avatar Generation (HeyGen)

Build a custom digital twin of the creator.

**Training data requirements:**
- 2-5 minutes of high-quality source video (minimum)
- Consistent lighting, same camera angle throughout
- No jump cuts in the training footage
- Same outfit and background for brand consistency
- Natural gestures — don't stay still, don't overact

**Production tips:**
- Generate clips in segments (1-2 min each), not as one long take
- Review each clip for lip-sync accuracy before assembly
- Use the same avatar preset across all videos for consistency

### 3. Voice Cloning (ElevenLabs)

Clone the creator's voice for natural-sounding narration.

**Training data requirements:**
- ~2 hours of clean audio (audiobook recordings, podcast episodes, or dedicated sessions)
- Same microphone throughout all training samples
- No background noise, no music
- Natural speaking pace — not reading-voice, but talking-voice
- Include varied emotions: excited, calm, explanatory, storytelling

**Quality checks:**
- Test with sentences the model hasn't seen
- Listen for unnatural pauses or emphasis
- Compare A/B with real voice — if people can't tell, it's ready

### 4. Assembly & Publishing

**Video assembly:**
- Combine avatar footage + voice + B-roll + text overlays
- Add captions/subtitles (boosts retention for silent viewers)
- Keep transitions simple — hard cuts or subtle fades

**Thumbnails:**
- Use real photos of the creator (not the avatar) for authenticity
- High contrast, readable text at mobile size
- Face showing emotion + 3-5 words max

**Metadata:**
- SEO-optimized title (front-load the keyword)
- Description: first 2 lines are the hook (visible before "Show more")
- Tags: 10-15 relevant keywords
- End screen: subscribe button + next video

## Benchmarks

| Metric | Target | Julia's Results |
|--------|--------|-----------------|
| CTR | 7%+ | 7.8% |
| Avg view duration | 8+ min | 8 min |
| Views vs manual | 3x+ | 3.8x |
| Publishing cadence | 3-7x/week | Daily |

## Modes

### Mode: Script

When asked to write a script:
1. Ask for the topic and target audience
2. Ask for reference content (links to creator's best videos, or describe their style)
3. Write a full script using the template above
4. Include timing estimates per section
5. Add visual/B-roll directions

### Mode: Plan

When asked to plan a video pipeline:
1. Assess current assets (existing footage, audio, accounts)
2. Identify gaps (what needs to be recorded/purchased)
3. Create a step-by-step setup checklist
4. Estimate time to first published video
5. Propose a content calendar (topics for first 10 videos)

### Mode: Audit

When asked to audit readiness:
1. Check: Does the creator have 2-5 min clean source video?
2. Check: Does the creator have 2+ hours clean audio?
3. Check: HeyGen account (Pro plan needed for custom avatars)?
4. Check: ElevenLabs account (Creator plan for voice cloning)?
5. Check: Video editor available (human or tool)?
6. Report gaps and next steps

### Mode: Optimize

When asked to improve existing content:
1. Review the script or video plan
2. Score against Julia's benchmarks
3. Suggest specific improvements (hook strength, pacing, CTA clarity)
4. Rewrite weak sections

## Cost Estimate

| Tool | Plan | ~Cost/month |
|------|------|-------------|
| HeyGen | Business | $89-$199 |
| ElevenLabs | Creator | $22-$99 |
| Claude | Pro | $20 |
| Video editor | Freelance or CapCut | $0-500 |

## References

- [Julia McCoy AI Clone Story](https://firstmovers.ai/julia-mccoy-ai-clone/)
- [HeyGen Customer Story](https://www.heygen.com/customer-stories/first-movers)
- [YouTube AI Clone Guide](https://firstmovers.ai/youtube-ai-clone/)
