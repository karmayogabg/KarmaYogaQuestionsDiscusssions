---
name: extractKYTransQues
description: Batch chunk, transcribe, and extract questions & topics from Tamil/English Karma Yoga audio recordings (.m4a/.wav/.mp3/.mp4/.aac/.flac/.ogg/.wma) OR direct transcript files (.txt/.docx/.pdf/.md) from folder "transcripts to process" or "transcription to process", setting default question status to Pending (is_discussed=false), adding bilingual Tamil & English entries, moving processed files to "processed transcripts", saving plain transcripts to "transcripts/" only, and displaying a formatted CLI table (Question Number | Which High level Section Mapped | Question details).
---

# Extract Karma Yoga Transcript & Questions Skill (`extractKYTransQues`)

This skill automates the batch pipeline for processing Tamil/English Karma Yoga lecture recordings or pre-extracted transcripts:

## 📜 Core Business & Formatting Rules

1. **Default Status = Pending (நிலுவையில்)**:
   * EVERY newly extracted or added question MUST have `"is_discussed": false` (Pending) as its default status.
2. **Bilingual Questions & Answers**:
   * EVERY newly added question MUST contain both Tamil (`question_ta`) and English (`question_en`) question text, along with default bilingual answer placeholders (`answer_ta` and `answer_en`).
3. **CLI Table Output**:
   * Displays a formatted terminal table during execution with columns:
     `| Question Number | Which High level Section Mapped | Question details |`
4. **Input Folders & Supported Formats**:
   * Scans both `transcripts to process/` and `transcription to process/` for:
     - Audio files (`.m4a`, `.wav`, `.mp3`, `.mp4`, `.aac`, `.flac`, `.ogg`, `.wma`, `.webm`, `.opus`).
     - Transcript text files (`.txt`, `.docx`, `.pdf`, `.md`).
5. **File Movement & Repository Cleanliness**:
   * Saves compiled transcript `.txt` files in `transcripts/` ONLY (never in the root folder).
   * Moves processed input files into `processed transcripts/`.
6. **Transcript Repository Viewer Isolation**:
   * Embeds all transcript texts into `embeddedTranscriptsMap` and `appData.transcripts`.
   * Selecting a transcript in the Web UI dropdown displays ONLY its own specific text without hardcoded fallback overlaps.

---

## 🔀 Workflow & Input Modes

1. **Batch Mode (Default)**:
   * Scans input folders `transcripts to process/` and `transcription to process/`.
   * For audio files: Segments audio into 3-minute WAV chunks via `ffmpeg` and transcribes using local `whisper-cli` (`ggml-medium.bin`).
   * For transcript text files: Direct text extraction (`.txt`, `.docx`, `.pdf`).
   * Extracts questions, maps them to high-level sections, assigns bilingual Tamil/English entries, and sets status to **Pending (`is_discussed: false`)**.
   * Displays the formatted CLI question table.
   * Updates `questions_data.json` & regenerates `index.html`.
   * Moves processed files into `processed transcripts/`.

2. **Single File Audio Mode (`--audio "/path/to/recording.m4a"`)**:
   * Processes a specific audio file via Whisper CLI, displays CLI table, updates database/UI with pending status, and moves file to `processed transcripts/`.

3. **Single File Direct Transcript Mode (`--transcript "/path/to/transcript.pdf"`)**:
   * Accepts direct text/DOCX/PDF files, displays CLI table, updates database/UI with pending status, and moves file to `processed transcripts/`.

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

---

## 📊 Terminal Output Table Format

```text
+-------------------+------------------------------------------+----------------------------------------------------+
| Question Number   | Which High level Section Mapped          | Question details                                   |
+-------------------+------------------------------------------+----------------------------------------------------+
| Q16 (Pending)     | 3. Divine Justice & Reincarnation        | Why don't we remember our past lives if karma      |
|                   |                                          | depends on them?                                   |
+-------------------+------------------------------------------+----------------------------------------------------+
```
