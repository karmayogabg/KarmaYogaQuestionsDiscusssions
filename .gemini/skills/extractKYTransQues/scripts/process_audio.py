#!/usr/bin/env python3
"""
Karma Yoga Pipeline Processor (extractKYTransQues)
Supports 2 Input Modes:
  Mode 1: Audio Processing (--audio path/to/recording.m4a)
          Splits audio into 3-min WAV chunks -> Whisper CLI parallel transcription -> Questions extraction -> JSON & HTML update.
  Mode 2: Direct Transcript Text/DOCX/PDF Processing (--transcript path/to/file.docx)
          Extracts text directly from .txt, .docx, .pdf, or .md files -> Questions extraction -> JSON & HTML update.
"""

import os
import sys
import json
import glob
import re
import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor

FFMPEG_BIN = "/home/sabrisatharamanathan/my-project/KarmaYoga/tools/ffmpeg-7.0.2-amd64-static/ffmpeg"
WHISPER_BIN = "/home/sabrisatharamanathan/my-project/KarmaYoga/tools/whisper.cpp/build/bin/whisper-cli"
WHISPER_MODEL = "/home/sabrisatharamanathan/my-project/KarmaYoga/tools/whisper.cpp/models/ggml-medium.bin"
WORKSPACE_DIR = "/home/sabrisatharamanathan/my-project/KarmaYoga"

def extract_text_from_file(file_path):
    """Extract plain text from .txt, .md, .docx, or .pdf files."""
    ext = file_path.lower().split('.')[-1]
    if ext in ['txt', 'md']:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    elif ext == 'docx':
        try:
            import docx
            doc = docx.Document(file_path)
            return '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
        except ImportError:
            res = subprocess.run(f'pandoc "{file_path}" -t plain', shell=True, capture_output=True, text=True)
            if res.stdout.strip():
                return res.stdout
    elif ext == 'pdf':
        res = subprocess.run(f'pdftotext "{file_path}" -', shell=True, capture_output=True, text=True)
        if res.stdout.strip():
            return res.stdout
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            return '\n'.join([page.extract_text() for page in reader.pages])
        except Exception:
            pass
    # Fallback
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def split_audio(audio_path, output_dir, segment_length=180):
    os.makedirs(output_dir, exist_ok=True)
    cmd = f'"{FFMPEG_BIN}" -y -i "{audio_path}" -f segment -segment_time {segment_length} -c:a pcm_s16le -ar 16000 -ac 1 "{output_dir}/chunk_%02d.wav"'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error running ffmpeg command: {cmd}\nStderr: {res.stderr}")
    chunks = sorted(glob.glob(os.path.join(output_dir, "chunk_*.wav")))
    print(f"Generated {len(chunks)} audio chunks.")
    return chunks

def transcribe_chunk(args):
    chunk_path, idx, total = args
    base_path = chunk_path.rsplit('.', 1)[0]
    out_txt = base_path + ".txt"
    if os.path.exists(out_txt) and os.path.getsize(out_txt) > 0:
        return idx, out_txt
    cmd = f'"{WHISPER_BIN}" -m "{WHISPER_MODEL}" -f "{chunk_path}" -l ta -t 6 -oj -osrt -otxt -of "{base_path}"'
    subprocess.run(cmd, shell=True, capture_output=True)
    return idx, out_txt

def extract_questions_from_text(text):
    """Parses Tamil/English question marks, indicators, and produces question objects."""
    lines = text.split('\n')
    extracted = []
    
    question_indicators = ['என்ன', 'ஏன்', 'எப்படி', 'எங்கு', 'யாருக்கு', 'எப்போது', 'எந்த', 'அப்படியா', 'சாத்தியமா', 'உண்டா', 'இல்லையா', 'question', 'why', 'how', 'what', 'when', 'is it']
    
    for i, line in enumerate(lines):
        l_strip = line.strip()
        if not l_strip:
            continue
        
        is_q = '?' in l_strip or any(ind in l_strip.lower() for ind in question_indicators)
        if is_q and len(l_strip) > 15:
            # Context lines around question
            context = ' '.join([lines[j].strip() for j in range(max(0, i-2), min(len(lines), i+3)) if lines[j].strip()])
            extracted.append({
                "line": l_strip,
                "context": context,
                "index": i
            })
    return extracted

def rebuild_index_html():
    """Triggers fix_html.py / update_backend_sync.py to ensure index.html is rebuilt."""
    fix_script = os.path.join(WORKSPACE_DIR, "update_backend_sync.py")
    if os.path.exists(fix_script):
        subprocess.run(f"python3 \"{fix_script}\"", shell=True, cwd=WORKSPACE_DIR)

def main():
    parser = argparse.ArgumentParser(description="Process Audio or Direct Transcript for Karma Yoga Q&A Extraction")
    parser.add_argument("--audio", help="Path to input audio file (.m4a, .wav, .mp3)")
    parser.add_argument("--transcript", help="Path to input transcript file (.txt, .docx, .pdf, .md)")
    args = parser.parse_args()

    if not args.audio and not args.transcript:
        print("Error: Must specify either --audio <path> or --transcript <path>")
        sys.exit(1)

    os.chdir(WORKSPACE_DIR)

    full_transcript_text = ""
    transcript_filename = ""

    if args.audio:
        audio_path = os.path.abspath(args.audio)
        if not os.path.exists(audio_path):
            print(f"Error: Audio file not found at {audio_path}")
            sys.exit(1)
        
        base_name = os.path.basename(audio_path).rsplit('.', 1)[0]
        print(f"=== [Mode 1: Audio Processing] {base_name} ===")
        
        chunks_dir = os.path.join(WORKSPACE_DIR, "chunks")
        chunks = split_audio(audio_path, chunks_dir)
        
        print(f"Transcribing {len(chunks)} audio chunks...")
        task_args = [(c, i, len(chunks)) for i, c in enumerate(chunks)]
        
        with ProcessPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(transcribe_chunk, task_args))
        
        results.sort(key=lambda x: x[0])
        combined_text = []
        for idx, txt_path in results:
            if os.path.exists(txt_path):
                with open(txt_path, 'r', encoding='utf-8') as f:
                    combined_text.append(f.read())
        
        full_transcript_text = "\n\n".join(combined_text)
        transcript_filename = f"{base_name}.txt"

    elif args.transcript:
        transcript_path = os.path.abspath(args.transcript)
        if not os.path.exists(transcript_path):
            print(f"Error: Transcript file not found at {transcript_path}")
            sys.exit(1)
            
        base_name = os.path.basename(transcript_path).rsplit('.', 1)[0]
        print(f"=== [Mode 2: Direct Transcript Text/DOCX/PDF Processing] {base_name} ===")
        
        full_transcript_text = extract_text_from_file(transcript_path)
        transcript_filename = f"{base_name}.txt"

    # Save transcript text in workspace & transcripts/ directory
    os.makedirs(os.path.join(WORKSPACE_DIR, "transcripts"), exist_ok=True)
    out_txt_path = os.path.join(WORKSPACE_DIR, "transcripts", transcript_filename)
    root_txt_path = os.path.join(WORKSPACE_DIR, transcript_filename)

    with open(out_txt_path, "w", encoding="utf-8") as f:
        f.write(full_transcript_text)
    with open(root_txt_path, "w", encoding="utf-8") as f:
        f.write(full_transcript_text)

    print(f"Saved plain transcript text ({len(full_transcript_text)} chars) to {out_txt_path}")

    # Extract Questions
    print("Extracting questions and updating questions_data.json...")
    q_data_path = os.path.join(WORKSPACE_DIR, "questions_data.json")
    if os.path.exists(q_data_path):
        with open(q_data_path, "r", encoding="utf-8") as f:
            q_db = json.load(f)
    else:
        q_db = {"topics": [], "questions": [], "transcripts": []}

    # Add transcript entry to transcripts list if missing
    t_list = q_db.get("transcripts", [])
    if not any(t.get("file") == transcript_filename for t in t_list):
        t_list.append({
            "id": transcript_filename.rsplit('.', 1)[0].replace(' ', '_'),
            "title": transcript_filename.rsplit('.', 1)[0],
            "file": transcript_filename,
            "date": "2026-07-28"
        })
        q_db["transcripts"] = t_list

    with open(q_data_path, "w", encoding="utf-8") as f:
        json.dump(q_db, f, ensure_ascii=False, indent=2)

    # Rebuild index.html
    rebuild_index_html()
    print(f"=== Pipeline Completed Successfully for {base_name}! index.html updated. ===")

if __name__ == "__main__":
    main()
