---
name: extractKYTransQues
description: Batch chunk, transcribe, and extract questions & topics from Tamil Karma Yoga audio recordings (.m4a/.wav/.mp3) OR direct transcript files (.txt/.docx/.pdf/.md), compiling structured JSON data, plain transcript files, and interactive HTML discussion reports.
---

# Extract Karma Yoga Transcript & Questions Skill (`extractKYTransQues`)

This skill automates the full pipeline for processing Tamil Karma Yoga / Bhagavad Gita lecture recordings or pre-extracted transcripts:

## 🔀 Supported Input Modes

1. **Mode A: Audio File Input (`--audio "/path/to/file.m4a"`)**
   * Segments audio into 3-minute WAV chunks via `ffmpeg`.
   * Runs local `whisper-cli` (`ggml-medium.bin`) parallel speech-to-text.
   * Compiles timestamped plain text and markdown transcript files.
   * Extracts questions, topics, context snippets, and updates `questions_data.json` & `index.html`.

2. **Mode B: Direct Transcript File Input (`--transcript "/path/to/transcript.docx"`)**
   * Accepts pre-extracted text files (`.txt`, `.md`), Word documents (`.docx`), or PDF files (`.pdf`).
   * Extracts the full transcript text directly without needing audio re-transcription.
   * Saves the plain text in the `transcripts/` repository.
   * Extracts discussion questions, categorizes topics, and updates `questions_data.json` & `index.html`.

---

## ⚡ Execution Commands

### Run with Audio File:
```bash
python3 /home/sabrisatharamanathan/.gemini/antigravity-cli/skills/extractKYTransQues/scripts/process_audio.py --audio "/path/to/recording.m4a"
```

### Run with Direct Transcript File (.txt / .docx / .pdf):
```bash
python3 /home/sabrisatharamanathan/.gemini/antigravity-cli/skills/extractKYTransQues/scripts/process_audio.py --transcript "/path/to/meeting_transcript.docx"
```

---

## 📄 Generated & Updated Deliverables

1. **Plain Text Transcript**:
   * `transcripts/<Audio_Or_Transcript_Name>.txt`
   * `<Audio_Or_Transcript_Name>.txt`
2. **JSON Backend Database**:
   * `questions_data.json` (Updated with new transcript entry, questions, and topics)
3. **Interactive Web Application**:
   * `index.html` (Rebuilt with updated JSON & full transcript text viewable in Transcripts Repository tab)
