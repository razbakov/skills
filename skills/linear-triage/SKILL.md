---
name: linear-triage
description: 'Turn one source with many asks (a video review or screen recording, a call or demo, a feedback sheet, a document) into one Linear project: the requester''s jobs, how each is done in the product today, the friction in each, and the issue that removes each friction. For a video, the transcript is read together with the frames shown at the moments someone says "look here", "this button", "вот тут" or "hier", so the issues describe what was on screen, not just what was said. Issues are filed with linear-issue, estimated when the team estimates, and prioritised here. Use for "triage this video", "process this review recording", "turn this call / sheet / feedback into issues", or "linear-triage <link or file>". Not for a single bug or task (use linear-issue), and not for a strategy conversation with no product feedback in it (use linear-project).'
---

# Linear Triage

One source in, one **Linear project** out. The project says what the requester's team is trying to get done in the product: their jobs, how each is done today, and where the product gets in the way. Every friction line starts with the issue that removes it, so the project brief is also the map from the source to the issues. The issues belong to the project, are written with the **linear-issue** skill, and get their priority here.

Linear work goes through the Linear MCP tools (`list_teams`, `list_projects`, `list_issues`, `save_project`, `save_issue`, `get_issue`, `prepare_file_upload`). If they aren't connected, produce the project brief and the issue drafts as text and say what to set when filing.

## Input

A link, a file path, or pasted text, to one of:

| Source | How to read it |
|---|---|
| **Video** (screen recording, review walkthrough, recorded demo, Loom / YouTube link, `.mp4` / `.mov` / `.webm`) | Get a timestamped transcript, then pull the frames the speakers point at: see **Reading a video** below. |
| Meeting (call, demo, brainstorm, feedback round) | The meeting tool the team uses (Wispr Flow, Jamie, Granola, Teams, Zoom): read the **full transcript with timestamps and speakers**, not the auto-summary. If the meeting was recorded on video, treat it as a video. |
| Spreadsheet or document (Google Sheets / Docs, Excel / Word, Notion, Confluence) | The matching connector or CLI; for a spreadsheet read the named sheet, for a page include its comments. |
| Anything else | Read it in full; if it can't be reached, ask for it to be pasted. |

Read the whole source before extracting anything. If part of it can't be read (a broken link, an unreadable stretch of audio, a frame too blurry to read), say which part and don't guess its content.

## Reading a video

In a recording people point instead of describing: "look here", "this doesn't work", "and that column is empty". The transcript alone loses what they meant. Read the words and the picture together.

1. **Get the video locally.** A file path is used as is. A link: download it to a new, empty folder (`yt-dlp -o "video.%(ext)s" <url>` for YouTube, Loom and most players). A video behind a login the tools can't reach: ask for the file.
2. **Get a timestamped transcript.**
   - If the meeting tool already made one with timestamps and speakers, use it (export as SRT / VTT / JSON, or write the segments to a JSON file).
   - Otherwise transcribe locally with word timestamps, in the recording's language:
     ```bash
     whisper video.mp4 --model small --language <xx> --word_timestamps True --output_format json --output_dir out/
     ```
     (or the **transcribe-via-faster-whisper** skill, whose `verbose_json` output works the same way). Leave `--language` out only if you don't know it.
   - Check where the transcript's zero is. A transcript from a meeting tool may start earlier or later than the video file; find one moment you can see and hear in both, and pass the difference as `--offset`.
3. **Pull the frames.** Run the helper that ships with this skill:
   ```bash
   python3 <this skill>/scripts/video_context.py video.mp4 out/video.json --out out/context --scenes 0.3
   ```
   It finds the moments someone points at the screen (pointing phrases in English, German, Russian, Ukrainian and Spanish; add others with `--pattern`), saves the frame shown just after each one, and with `--scenes` also a frame at each screen change (page switch, dialog opening). For a talking-head call with a shared screen, `--every 20` adds a frame every 20 seconds instead. It writes `out/context/context.md`: one entry per moment with its timecode, the words said and the frame.
4. **Look at every frame**, in order, with its quote. For each, write down in one line what the frame shows that the words point at: the page (in the product's own page names), the element ("the Save button in the profile form", "the empty Hours column for March"), and anything visibly wrong (an error message, a wrong number, a broken layout). Read text on screen exactly as shown. If a frame doesn't show what the speaker meant (the cursor is elsewhere, the page had already changed), pull one a little earlier or later with `ffmpeg -ss <seconds> -i video.mp4 -frames:v 1 out.jpg` rather than guessing.
5. **Use the result as the source.** From here on, an ask from a video carries its timecode, the words exactly as said, and what the frame shows. Keep the frames: the ones that show a friction are attached to its issue in step 5.

## Steps

### 1. Name the source

Record: title, link or file, type (video, call, sheet, document), date, and who it came from (team or role; for a call or video, who took part). If a project for the same team and goal already exists (`list_projects`, including archived ones), add to it instead of making a second one.

### 2. Extract every ask

Go through the source item by item: each sheet row, each request, complaint, question, idea or decision in the call, video or document. For each, keep:

- a **reference back**: sheet row number; for a call or video, speaker and timecode; for a document, the heading,
- the words **exactly as written or said**: no paraphrase, no translation, no tidying,
- for a video, **what the frame shows** at that moment (from *Reading a video*, step 4),
- the page or area of the product it's about, in the product's own names.

A call or video is not a list of asks. Sort what was said first: a demo of what's new, the requester's jobs, how they do them today and where it hurts, solution ideas (who proposed each, and whether it was agreed, rejected or replaced later in the same recording), and open questions. Only friction and agreed solutions become work.

### 3. Check each ask against the product

Update the code (`git fetch`, read on a fresh default branch) and read the docs and code behind each ask, as **linear-issue** step 2 describes. For each ask, find out:

- **Already there**: it's shipped. Name what exists and where, and the issue it shipped with.
- **Open**: the product doesn't do it yet, or the requester needs an answer or a decision.

Search Linear for an existing issue on the same thing (`list_issues` with a query, including done and canceled). An open match is reused, with new information added as a comment; a closed one that came back gets a new issue that links to it.

### 4. Group the asks into jobs

A job is what the requester's team is trying to get done, in their words, not a page of the product: "Run the weekly planning call", "Know who is free next month", "Send the invoice to the client". Several asks usually belong to one job; one ask belongs to one job.

For each job write:

- **The job**, as a short title, and one italic line on what it really involves.
- **Today**: how it is done in the product now, in the product's own page names and labels. For a call or video, how the requester showed or described it (the frames help here); for a sheet, what the product offers today.
- **Friction**: one line per problem, in plain words, close to how the requester put it. An ask that's already in the product stays as a line, with the issue it shipped with.

For a call or video, present the jobs and their friction to the person who asked, one job at a time, and file issues only for what they agree to. For a sheet, go on.

### 5. File the issues

File each new issue with the **linear-issue** skill, in the project, in the team that owns the work. One friction can need one issue; one issue can remove several frictions. An ask that holds two separate things becomes two issues, both naming the same reference.

On top of what linear-issue asks for:

- **The quote comes from the source** with its reference: "(row 6)", or the speaker and timecode for a call or video.
- **For a video, add the frame.** Upload the frame that shows the friction (`prepare_file_upload`, then the markdown it returns) right under the quote, with its timecode, and say in one line what it shows. If the video has a shareable link, link the timecode (`?t=754` on YouTube and Loom).
- **Kind**, through the team's labels if it uses them: a **bug** (the product does something wrong today), a **change** (new or changed behaviour a user would notice), or a **question / decision** (an answer someone needs, or a decision the work waits on). A question or decision is an issue assigned to whoever can answer it.

### 6. Estimate

If the team estimates (its settings show an estimate scale), check every new bug and change has an estimate on that scale, using the **estimation** skill to size it; a reused issue without one is estimated here too. Questions and decisions are not estimated. If the team doesn't estimate, skip this step and weigh size in your own words in step 7.

### 7. Prioritise

Set Linear's priority on each issue:

| Priority | When |
|---|---|
| Urgent | someone can't do their job in the product, or the product shows wrong figures |
| High | blocks other issues in this project, asked for by many, or marked important by the requester |
| Medium | clear value for the requester's team at a reasonable size |
| Low | nice to have, or small value for its size |

Weigh value against size: a small issue that saves a team time every week goes above a large one for an occasional case. Answer questions early: they're cheap and often remove an issue. A job that gates the others raises its issues, and the gating issue `blocks` the ones that wait on it. The priority the requester gave counts as input, not as the answer.

### 8. Write the project

A Linear project named for the team and its goal in a few words ("Agency onboarding", "Checkout review March"), in the team that owns the work, under an initiative only if one already fits. Description:

```markdown
**Source:** [<source title>](<link>), <type> on <date>, from <team / participants>. <anything that could not be read>

<One or two sentences: what the team wants to do in the product.> Below are the jobs where the product gets in the way today: what the job is, how it is done today, and the friction.

### J1. <Job>

_<What the job really involves, in one line.>_

* **Today:** <how it is done in the product now>
* **Friction:**
    * ABC-123 <the friction this issue removes> (12:34)
    * ABC-124, ABC-125 <a friction two issues remove together>
    * <a friction with no issue, left unmarked on purpose>

### J2. …
```

How to fill it well:

- **Issue first.** Each friction line starts with its issue ID. Linear turns an ID into a live link that shows the issue's status, so a shipped issue reads as done; don't add status words.
- **Keep the reference.** End the friction line with the row ("row 6") or the timecode ("12:34"), so every ask can be found again from the project.
- **Nothing silently dropped.** A friction with no issue stays as an unmarked line; say why in the report. An ask that is neither friction nor a job (praise, an empty row, small talk) goes in one line under the Source.
- **No tables, no checklist, no "Done when".** The project's issue list shows what's open; a copy goes stale.
- **No solutions in the project.** What to build lives in each issue.
- **No frames in the project.** They belong to the issues they explain.

Create the project before the issues if they need it to exist, then fill its description once the issue IDs are known.

### 9. Link back to the source

- A sheet with an issue column: write each row's issue as `=HYPERLINK("<issue URL>","<issue ID>")`. If the sheet can't be written from here, put the paste-ready formulas in a comment on the project and say so.
- A document someone else owns: don't edit it. Offer the person who asked a short list of issue links to add.
- A call or video: nothing to write back; the project is the record. If the video lives somewhere that takes comments at a timecode (Loom, Frame.io, YouTube), offer the issue links per timecode instead of posting them.

### 10. Report

Read the project back from Linear and check that every issue is in it and every ID in the brief resolves. Report to whoever asked: the project link, its jobs, how many asks became new issues, reused issues and asks already in the product, the top priorities with their reasons, older issues the new ones replace, and anything that couldn't be read, heard or seen.

The next step for the project is building its issues and answering its questions, with whatever the team uses to work through Linear issues.
