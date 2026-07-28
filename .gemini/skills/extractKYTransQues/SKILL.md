---
name: extractKYTransQues
description: Batch chunk, transcribe, and extract questions & topics from Tamil Karma Yoga audio recordings (.m4a/.wav/.mp3), compiling structured JSON data, plain transcript files, and interactive HTML discussion reports.
---

# Extract Karma Yoga Transcript & Questions Skill (`extractKYTransQues`)

This skill automates the full pipeline for processing Tamil audio meeting recordings (such as Bhagavad Gita / Karma Yoga Q&A lectures):
1. **Audio Chunking**: Segmenting large audio files into 3-minute WAV chunks via `ffmpeg` (16kHz mono).
2. **Parallel Speech Transcription**: Running local `whisper-cli` with `ggml-medium.bin` (`-l ta -t 6 -oj -osrt -otxt`) across CPU worker processes.
3. **Transcript Assembly**: Compiling timestamped chunk transcripts into plain text files (`transcripts/` directory and standalone `.txt` files) and Markdown transcripts (`_Transcript.md`).
4. **Question & Topic Extraction**: Extracting core discussion questions, categorizing into topics, generating Tamil & English translations, context summaries, and audio timestamps into `_Questions.md` and `questions_data.json`.
5. **Interactive Web App Generation**: Building/updating `Karmayoga-Questions-Discussion.html` and `index.html` with dual-tab support (Questions & Answers Manager + Full Transcripts Repository Viewer).

---

## Tooling Dependencies & Paths

* **Whisper CLI Binary**: `/home/sabrisatharamanathan/my-project/KarmaYoga/tools/whisper.cpp/build/bin/whisper-cli`
* **Whisper Model**: `/home/sabrisatharamanathan/my-project/KarmaYoga/tools/whisper.cpp/models/ggml-medium.bin`
* **FFmpeg**: System `ffmpeg` for 16kHz audio conversion and 3-minute chunk segmentation.

---

## Execution Workflow

When the user asks to process an audio recording or run `extractKYTransQues`:

### Step 1: Execute Python Pipeline Script
Run the automated skill script specifying the input audio file:

```bash
python3 /home/sabrisatharamanathan/.gemini/antigravity-cli/skills/extractKYTransQues/scripts/process_audio.py --audio "/path/to/meeting_recording.m4a"
```

### Step 2: Generated Deliverables

The script produces the following outputs in the workspace:

1. **Plain Text Transcript**:
   * `transcripts/<Audio_Base_Name>.txt`
   * `<Audio_Base_Name>.txt`
2. **Markdown Transcript**:
   * `<Audio_Base_Name>_Transcript.md`
3. **Markdown Questions Summary**:
   * `<Audio_Base_Name>_Questions.md`
4. **JSON Backend Database**:
   * `questions_data.json`
5. **Interactive Web Application**:
   * `Karmayoga-Questions-Discussion.html`
   * `index.html`

---

## Verification & Output Checklist

After running the skill script:
- Confirm that `questions_data.json` contains all extracted questions with `is_discussed`, `answer_ta`, and `answer_en`.
- Verify that `Karmayoga-Questions-Discussion.html` opens cleanly and displays both the **Questions & Answers Tab** and the **Transcripts Repository Tab**.
