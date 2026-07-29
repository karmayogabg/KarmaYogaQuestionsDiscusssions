---
name: extractKYTransQues
description: Batch chunk, transcribe, and extract questions & topics from Tamil Karma Yoga audio recordings (.m4a/.wav/.mp3/.mp4/.aac/.flac/.ogg/.wma) OR direct transcript files (.txt/.docx/.pdf/.md) from folder "transcripts to process" or "transcription to process", moving processed files to "processed transcripts" and displaying a formatted CLI table (Question Number | Which High level Section Mapped | Question details).
---

# Extract Karma Yoga Transcript & Questions Skill (`extractKYTransQues`)

This skill automates the batch pipeline for processing Tamil/English Karma Yoga lecture recordings or pre-extracted transcripts:

## 🔀 Workflow & Input Modes

1. **Batch Mode (Default)**:
   * Scans input folders `transcripts to process/` and `transcription to process/` for all **audio files** (`.m4a`, `.wav`, `.mp3`, `.mp4`, `.aac`, `.flac`, `.ogg`, `.wma`) and **transcript text files** (`.txt`, `.docx`, `.pdf`, `.md`).
   * For **audio files**:
     - Segments audio into 3-minute WAV chunks via `ffmpeg`.
     - Runs local `whisper-cli` (`ggml-medium.bin`) parallel speech-to-text.
     - Saves combined transcript text into `transcripts/<base_name>.txt`.
   * For **transcript files**:
     - Direct text extraction (`.txt`, `.docx`, `.pdf`).
   * Extracts questions, generates bilingual Tamil & English entries (`question_ta`, `question_en`), and maps them to high-level sections.
   * **Terminal Table Output**: Displays a CLI Table for every processed file with:
     `| Question Number | Which High level Section Mapped | Question details |`
   * **Database & UI Update**: Updates `questions_data.json` & regenerates `index.html`.
   * **Auto-Move**: Automatically moves processed audio and transcript files into `processed transcripts/`.

2. **Single File Audio Mode (`--audio "/path/to/recording.m4a"`)**:
   * Processes a specific audio file, transcribes via Whisper CLI, displays CLI table, and moves the audio file to `processed transcripts/`.

3. **Single File Direct Transcript Mode (`--transcript "/path/to/transcript.pdf"`)**:
   * Accepts text files (`.txt`, `.md`), Word documents (`.docx`), or PDF files (`.pdf`), displays CLI table, updates `questions_data.json` & `index.html`, and moves the file to `processed transcripts/`.

---

## ⚡ Execution Commands

### Batch Process All Files in Folder:
```bash
python3 /home/sabrisatharamanathan/.gemini/antigravity-cli/skills/extractKYTransQues/scripts/process_audio.py
```

### Specify Custom Folders:
```bash
python3 /home/sabrisatharamanathan/.gemini/antigravity-cli/skills/extractKYTransQues/scripts/process_audio.py --folder "/path/to/transcription to process" --processed-dir "/path/to/processed transcripts"
```

### Run for Single Audio File:
```bash
python3 /home/sabrisatharamanathan/.gemini/antigravity-cli/skills/extractKYTransQues/scripts/process_audio.py --audio "/path/to/recording.m4a"
```

### Run for Single Transcript File (.txt / .docx / .pdf):
```bash
python3 /home/sabrisatharamanathan/.gemini/antigravity-cli/skills/extractKYTransQues/scripts/process_audio.py --transcript "/path/to/meeting_transcript.pdf"
```

---

## 📊 Terminal Output Table Format

During execution, the skill displays a clean table in the terminal:

```text
+-------------------+------------------------------------------+----------------------------------------------------+
| Question Number   | Which High level Section Mapped          | Question details                                   |
+-------------------+------------------------------------------+----------------------------------------------------+
| Q16               | 3. Divine Justice & Reincarnation        | Why don't we remember our past lives if karma      |
|                   |                                          | depends on them?                                   |
+-------------------+------------------------------------------+----------------------------------------------------+
| Q17               | 3. Divine Justice & Reincarnation        | Is it fair to hold someone accountable for actions |
|                   |                                          | from a previous life that they cannot remember?    |
+-------------------+------------------------------------------+----------------------------------------------------+
```
