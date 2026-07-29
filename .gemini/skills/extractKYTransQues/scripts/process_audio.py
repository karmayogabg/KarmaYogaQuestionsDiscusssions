#!/usr/bin/env python3
"""
Karma Yoga Pipeline Processor (extractKYTransQues)
Supports:
  1. Batch Folder Processing (Default or --folder "transcripts to process" / "transcription to process")
     Scans folders for all audio files (.m4a, .wav, .mp3, .mp4, .aac, .flac, .ogg, .wma) AND transcript text files (.txt, .docx, .pdf, .md).
     Transcribes audio via Whisper CLI or extracts text directly, extracts & displays questions in a CLI Table
     (Question Number | Which High level Section Mapped | Question details), generates bilingual Tamil & English entries,
     updates database & index.html, saves transcripts into transcripts/ ONLY, and moves processed files to "processed transcripts".
  2. Single Audio Processing (--audio path/to/recording.m4a)
  3. Single Direct Transcript Processing (--transcript path/to/file.docx / .pdf / .txt / .md)
"""

import os
import sys
import json
import glob
import re
import shutil
import zlib
import textwrap
import argparse
import subprocess
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor

FFMPEG_BIN = "/home/sabrisatharamanathan/my-project/KarmaYoga/tools/ffmpeg-7.0.2-amd64-static/ffmpeg"
WHISPER_BIN = "/home/sabrisatharamanathan/my-project/KarmaYoga/tools/whisper.cpp/build/bin/whisper-cli"
WHISPER_MODEL = "/home/sabrisatharamanathan/my-project/KarmaYoga/tools/whisper.cpp/models/ggml-medium.bin"
WORKSPACE_DIR = "/home/sabrisatharamanathan/my-project/KarmaYoga"
DEFAULT_INPUT_DIRS = [
    os.path.join(WORKSPACE_DIR, "transcripts to process"),
    os.path.join(WORKSPACE_DIR, "transcription to process")
]
DEFAULT_PROCESSED_DIR = os.path.join(WORKSPACE_DIR, "processed transcripts")

TOPIC_TITLES = {
    "definition": "1. கர்மாவின் வரைவிலக்கணம் & எல்லை (Definition & Scope of Karma)",
    "control": "2. செயல் உரிமையும் கட்டுப்பாடும் (Control, Micro & Macro Dynamics)",
    "justice": "3. நீதி, நியாயம் & பூர்வ ஜென்மம் (Divine Justice & Reincarnation)",
    "construct": "4. கர்மக் கோட்பாட்டின் தத்துவார்த்த வடிவம் (Psychological & Societal Construct)",
    "detachment": "5. துன்பம், மன விலகல் & சாதனை (Enduring Suffering & Detachment)",
    "atonement": "6. தானம், பரிகாரம் & கட்டாயச் செயல்கள் (Atonement, Rituals & Coerced Actions)",
    "collective": "7. கூட்டுக் கர்மா & தலைமுறை வழி கர்மப்பலன் (Collective & Generational Karma)"
}

def map_question_to_topic(q_text):
    l_text = q_text.lower()
    if any(k in l_text for k in ['past life', 'previous life', 'remember', 'reincarnation', 'பூர்வ ஜென்மம்', 'மறுபிறவி', 'பிறவி', 'childhood', 'innocent']):
        return "justice"
    elif any(k in l_text for k in ['forced', 'charity', 'unethical', 'gunpoint', 'coercion', 'தானம்', 'பரிகாரம்', 'மிரட்டல்', 'கட்டாய']):
        return "atonement"
    elif any(k in l_text for k in ['death', 'after death', 'war', 'country', 'generations', 'ancestors', 'collective', 'கூட்டு', 'தலைமுறை', 'போர்']):
        return "collective"
    elif any(k in l_text for k in ['suffer', 'suffering', 'detachment', 'prison', 'sadhana', 'free', 'துன்பம்', 'விலகல்', 'சாட்சி']):
        return "detachment"
    elif any(k in l_text for k in ['fate', 'concept', 'construct', 'inequality', 'belief', 'god', 'கடவுள்', 'கோட்பாடு', 'சமுதாயம்']):
        return "construct"
    elif any(k in l_text for k in ['control', 'determined', 'micro', 'macro', 'choice', 'கட்டுப்பாடு', 'இயற்கை']):
        return "control"
    return "definition"

def extract_text_from_docx(file_path):
    """Extract text from docx via zipfile / XML parsing without external dependencies."""
    try:
        import docx
        doc = docx.Document(file_path)
        return '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
    except Exception:
        pass
    try:
        import zipfile
        with zipfile.ZipFile(file_path) as z:
            xml_content = z.read('word/document.xml')
        tree = ET.fromstring(xml_content)
        text = []
        for elem in tree.iter():
            if elem.tag.endswith('t') and elem.text:
                text.append(elem.text)
        return ' '.join(text)
    except Exception:
        pass
    res = subprocess.run(f'pandoc "{file_path}" -t plain', shell=True, capture_output=True, text=True)
    return res.stdout if res.stdout.strip() else ""

def parse_pdf_fallback(file_path):
    """Pure python PDF text parser supporting CMap / Identity-H streams."""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        font_cmaps = {}
        for m in re.finditer(rb'(\d+)\s+0\s+obj(.*?)endobj', content, re.DOTALL):
            obj_id = m.group(1).decode()
            obj_body = m.group(2)
            if b'/Type /Font' in obj_body:
                tu_m = re.search(rb'/ToUnicode\s+(\d+)\s+0\s+R', obj_body)
                if tu_m:
                    tu_id = tu_m.group(1)
                    tu_obj_m = re.search(rb'\b' + tu_id.encode() + rb'\s+0\s+obj(.*?)endobj', content, re.DOTALL)
                    if tu_obj_m:
                        tu_body = tu_obj_m.group(1)
                        if b'stream' in tu_body:
                            s_offset = tu_body.find(b'stream') + 6
                            if tu_body[s_offset:s_offset+1] == b'\r': s_offset += 1
                            if tu_body[s_offset:s_offset+1] == b'\n': s_offset += 1
                            s_end = tu_body.find(b'endstream', s_offset)
                            raw_s = tu_body[s_offset:s_end].rstrip(b'\r\n')
                            try:
                                cmap_text = zlib.decompress(raw_s).decode('utf-8', errors='ignore')
                            except Exception:
                                cmap_text = raw_s.decode('utf-8', errors='ignore')
                            
                            cmap = {}
                            for line in cmap_text.splitlines():
                                m_char = re.search(r'<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>', line)
                                if m_char and 'begin' not in line and 'end' not in line:
                                    src = int(m_char.group(1), 16)
                                    dst_codes = [int(m_char.group(2)[i:i+4], 16) for i in range(0, len(m_char.group(2)), 4)]
                                    cmap[src] = ''.join(chr(c) for c in dst_codes)
                                m_rng1 = re.search(r'<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>', line)
                                if m_rng1 and 'begin' not in line and 'end' not in line:
                                    s_start = int(m_rng1.group(1), 16)
                                    s_end = int(m_rng1.group(2), 16)
                                    d_code = int(m_rng1.group(3), 16)
                                    for k in range(s_start, s_end + 1):
                                        cmap[k] = chr(d_code + (k - s_start))
                                m_rng2 = re.search(r'<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>\s*\[(.*?)\]', line)
                                if m_rng2:
                                    s_start = int(m_rng2.group(1), 16)
                                    s_end = int(m_rng2.group(2), 16)
                                    dst_list = re.findall(r'<([0-9a-fA-F]+)>', m_rng2.group(3))
                                    for idx, d_hex in enumerate(dst_list):
                                        k = s_start + idx
                                        if k <= s_end:
                                            dst_codes = [int(d_hex[i:i+4], 16) for i in range(0, len(d_hex), 4)]
                                            cmap[k] = ''.join(chr(c) for c in dst_codes)
                            font_cmaps[obj_id] = cmap

        text_blocks = []
        for m in re.finditer(rb'stream[\r\n]+(.*?)endstream', content, re.DOTALL):
            stream_bytes = m.group(1).rstrip(b'\r\n')
            try:
                dec = zlib.decompress(stream_bytes)
            except Exception:
                dec = stream_bytes
            if b'BT' in dec:
                lines = []
                for bt_match in re.finditer(rb'BT(.*?)ET', dec, re.DOTALL):
                    bt_code = bt_match.group(1)
                    for tj_m in re.finditer(rb'<([0-9a-fA-F]+)>\s*Tj', bt_code):
                        h_str = tj_m.group(1).decode('ascii')
                        chars = []
                        for i in range(0, len(h_str), 4):
                            code = int(h_str[i:i+4], 16)
                            found = False
                            for cmap in font_cmaps.values():
                                if code in cmap:
                                    chars.append(cmap[code])
                                    found = True
                                    break
                            if not found:
                                chars.append(chr(code) if code >= 32 else '')
                        lines.append(''.join(chars))
                    for txt_m in re.finditer(rb'\((.*?)\)\s*Tj', bt_code):
                        lines.append(txt_m.group(1).decode('utf-8', errors='ignore'))
                if lines:
                    text_blocks.append(' '.join(lines))

        res = '\n'.join(text_blocks)
        if res.strip():
            return res
    except Exception:
        pass
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception:
        return ""

def extract_text_from_file(file_path):
    """Extract plain text from .txt, .md, .docx, or .pdf files."""
    ext = file_path.lower().split('.')[-1]
    if ext in ['txt', 'md']:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    elif ext == 'docx':
        return extract_text_from_docx(file_path)
    elif ext == 'pdf':
        res = subprocess.run(f'pdftotext "{file_path}" -', shell=True, capture_output=True, text=True)
        if res.stdout.strip():
            return res.stdout
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            txt = '\n'.join([page.extract_text() for page in reader.pages])
            if txt.strip():
                return txt
        except Exception:
            pass
        return parse_pdf_fallback(file_path)
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

def rebuild_index_html():
    """Triggers update_backend_sync.py to rebuild index.html."""
    fix_script = os.path.join(WORKSPACE_DIR, "update_backend_sync.py")
    if os.path.exists(fix_script):
        subprocess.run(f"python3 \"{fix_script}\"", shell=True, cwd=WORKSPACE_DIR)

def print_questions_table(questions_list, title):
    """Prints a formatted CLI table with Question Number | Which High level Section Mapped | Question details"""
    if not questions_list:
        return
        
    print("\n" + "="*112)
    print(f"📊 {title}")
    print("="*112)
    
    col1_w = 17 # Question Number
    col2_w = 40 # Which High level Section Mapped
    col3_w = 50 # Question details
    
    header = f"| {'Question Number':<{col1_w}} | {'Which High level Section Mapped':<{col2_w}} | {'Question details':<{col3_w}} |"
    sep = "+" + "-"*(col1_w+2) + "+" + "-"*(col2_w+2) + "+" + "-"*(col3_w+2) + "+"
    
    print(sep)
    print(header)
    print(sep)
    
    for q in questions_list:
        q_num = q.get('id', '')
        topic_id = q.get('topic_id', 'definition')
        section_name = TOPIC_TITLES.get(topic_id, TOPIC_TITLES['definition'])
        
        q_ta = q.get('question_ta', '')
        q_en = q.get('question_en', '')
        if q_ta and q_en and q_ta != q_en:
            q_text = f"{q_ta} / {q_en}"
        else:
            q_text = q_ta or q_en or ''
        
        q_lines = textwrap.wrap(q_text, width=col3_w) if q_text else ['']
        
        print(f"| {q_num:<{col1_w}} | {section_name:<{col2_w}} | {q_lines[0]:<{col3_w}} |")
        for extra_line in q_lines[1:]:
            print(f"| {'':<{col1_w}} | {'':<{col2_w}} | {extra_line:<{col3_w}} |")
            
        print(sep)
    print("\n")

def extract_and_display_questions(full_transcript_text, base_name, q_db):
    """Extracts questions, generates bilingual Tamil/English entries, appends new ones to q_db, and prints table."""
    lines = [l.strip() for l in full_transcript_text.split('\n') if l.strip()]
    
    question_keywords = [
        'என்ன', 'ஏன்', 'எப்படி', 'எங்கு', 'யாருக்கு', 'எப்போது', 'எந்த', 'அப்படியா', 'சாத்தியமா', 'உண்டா', 'இல்லையா', 'தானா', 'நியாயமா',
        'what', 'why', 'how', 'when', 'where', 'who', 'is it', 'can ', 'does ', 'should ', 'is karma'
    ]
    
    extracted = []
    seen_texts = set()
    for i, l_strip in enumerate(lines):
        if len(l_strip) < 15 or l_strip.startswith('#') or l_strip.startswith('---'):
            continue
        if any(k in l_strip for k in ['/URI', '/Type', 'http://', 'https://', 'endobj', 'stream', 'endstream', 'wkhtmltopdf', 'TurboScribe']):
            continue
            
        has_q_mark = '?' in l_strip
        l_lower = ' ' + l_strip.lower()
        has_kw = any(kw in l_lower for kw in question_keywords)
        
        if has_q_mark or has_kw:
            clean_q = re.sub(r'^[0-9#\-\*\.\s:]+', '', l_strip).strip()
            if clean_q not in seen_texts and len(clean_q) > 12:
                seen_texts.add(clean_q)
                snippet = ' '.join([lines[j] for j in range(max(0, i-1), min(len(lines), i+2))])
                extracted.append({
                    "question_text": clean_q,
                    "line_no": i + 1,
                    "snippet": snippet
                })

    existing_questions = q_db.get("questions", [])
    existing_texts = set()
    for q in existing_questions:
        if q.get("question_ta"): existing_texts.add(q["question_ta"].lower().strip())
        if q.get("question_en"): existing_texts.add(q["question_en"].lower().strip())

    newly_added = []
    matched_existing = []

    for item in extracted:
        q_text = item["question_text"]
        q_text_clean = q_text.lower().strip()
        
        match_q = None
        for eq in existing_questions:
            eq_ta = eq.get("question_ta", "").lower().strip()
            eq_en = eq.get("question_en", "").lower().strip()
            if q_text_clean in eq_ta or eq_ta in q_text_clean or (eq_en and q_text_clean in eq_en):
                match_q = eq
                break

        if match_q:
            matched_existing.append(match_q)
        elif q_text_clean not in existing_texts:
            new_id = f"Q{len(existing_questions) + len(newly_added) + 1}"
            is_ta = any('\u0b80' <= c <= '\u0bff' for c in q_text)
            topic_id = map_question_to_topic(q_text)
            
            q_ta = q_text if is_ta else q_text
            q_en = q_text if not is_ta else q_text
            
            new_q_obj = {
                "id": new_id,
                "topic_id": topic_id,
                "question_ta": q_ta,
                "question_en": q_en,
                "timestamp": f"Line {item['line_no']}",
                "category": "extracted",
                "context_ta": item["snippet"],
                "transcript_snippet": item["snippet"],
                "is_discussed": False,
                "answer_ta": "விவாதிக்கப்படும் பதில் விரைவில் சேர்க்கப்படும்.",
                "answer_en": "Discussion answer to be updated.",
                "keywords": (q_ta + " " + q_en).lower()
            }
            newly_added.append(new_q_obj)
            existing_texts.add(q_text_clean)

    # DISPLAY TABLE IN TERMINAL
    if newly_added:
        print_questions_table(newly_added, f"NEW BILINGUAL QUESTIONS EXTRACTED & MAPPED ({base_name})")
        q_db["questions"].extend(newly_added)
    else:
        print(f"\nℹ️  No new question IDs added for '{base_name}' (matched existing database questions Q1-Q25).")

    if matched_existing:
        unique_matches = []
        seen_m = set()
        for mq in matched_existing:
            if mq['id'] not in seen_m:
                seen_m.add(mq['id'])
                unique_matches.append(mq)
        print_questions_table(unique_matches[:10], f"MATCHED EXISTING DATABASE QUESTIONS ({base_name})")

    return q_db

def process_single_file(file_path, target_processed_dir):
    """Processes a single audio or transcript file and moves it to target_processed_dir."""
    file_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return False
    
    filename = os.path.basename(file_path)
    if filename.endswith(':Zone.Identifier') or filename.startswith('.'):
        return False
        
    ext = filename.lower().rsplit('.', 1)[-1]
    base_name = filename.rsplit('.', 1)[0]
    
    audio_extensions = ['m4a', 'wav', 'mp3', 'mp4', 'aac', 'flac', 'ogg', 'wma', 'opus', 'webm', 'm4v']
    transcript_extensions = ['txt', 'md', 'docx', 'pdf']

    print(f"\n==================================================")
    print(f"Processing File: {filename}")
    print(f"==================================================")

    full_transcript_text = ""
    transcript_filename = f"{base_name}.txt"

    if ext in audio_extensions:
        print(f"=== [Mode 1: Audio Processing] {base_name} ===")
        chunks_dir = os.path.join(WORKSPACE_DIR, "chunks")
        chunks = split_audio(file_path, chunks_dir)
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
    elif ext in transcript_extensions:
        print(f"=== [Mode 2: Direct Transcript Text/DOCX/PDF Processing] {base_name} ===")
        full_transcript_text = extract_text_from_file(file_path)
    else:
        print(f"Skipping unsupported file extension: .{ext}")
        return False

    if not full_transcript_text.strip():
        print(f"Warning: Extracted empty text for {filename}.")

    # Save plain transcript text in workspace transcripts/ ONLY (NOT in root folder)
    os.makedirs(os.path.join(WORKSPACE_DIR, "transcripts"), exist_ok=True)
    out_txt_path = os.path.join(WORKSPACE_DIR, "transcripts", transcript_filename)

    with open(out_txt_path, "w", encoding="utf-8") as f:
        f.write(full_transcript_text)

    # Remove duplicate copy from root folder if present to keep root clean
    root_txt_path = os.path.join(WORKSPACE_DIR, transcript_filename)
    if os.path.exists(root_txt_path) and os.path.abspath(root_txt_path) != os.path.abspath(out_txt_path):
        try:
            os.remove(root_txt_path)
        except Exception:
            pass

    print(f"Saved plain transcript text ({len(full_transcript_text)} chars) to {out_txt_path}")

    # Extract questions and update database
    sys.path.append(WORKSPACE_DIR)
    from master_data import ensure_valid_data

    q_data_path = os.path.join(WORKSPACE_DIR, "questions_data.json")
    if os.path.exists(q_data_path):
        try:
            with open(q_data_path, "r", encoding="utf-8") as f:
                q_db = json.load(f)
        except Exception:
            q_db = {}
    else:
        q_db = {}

    q_db = ensure_valid_data(q_db)

    # Extract, display table & add bilingual questions to database
    q_db = extract_and_display_questions(full_transcript_text, base_name, q_db)

    # Add transcript entry to transcripts list if missing
    t_list = q_db.get("transcripts", [])
    if not any(t.get("file") == f"transcripts/{transcript_filename}" or t.get("file") == transcript_filename for t in t_list):
        t_list.append({
            "id": base_name.replace(' ', '_').lower(),
            "title": base_name,
            "file": f"transcripts/{transcript_filename}",
            "date": "2026-07-29"
        })
        q_db["transcripts"] = t_list

    with open(q_data_path, "w", encoding="utf-8") as f:
        json.dump(q_db, f, ensure_ascii=False, indent=2)

    # Rebuild index.html
    rebuild_index_html()

    # Move processed file to target_processed_dir
    os.makedirs(target_processed_dir, exist_ok=True)
    dest_path = os.path.join(target_processed_dir, filename)
    if os.path.exists(dest_path):
        os.remove(dest_path)
    shutil.move(file_path, dest_path)
    print(f"Moved processed file '{filename}' -> '{target_processed_dir}/'")

    # Move companion Zone.Identifier if present
    zone_id_file = file_path + ":Zone.Identifier"
    if os.path.exists(zone_id_file):
        try:
            dest_zone_file = dest_path + ":Zone.Identifier"
            if os.path.exists(dest_zone_file):
                os.remove(dest_zone_file)
            shutil.move(zone_id_file, dest_zone_file)
        except Exception:
            try:
                os.remove(zone_id_file)
            except Exception:
                pass

    print(f"=== Successfully Processed & Moved {filename}! ===")
    return True

def main():
    parser = argparse.ArgumentParser(description="Batch Process Transcripts/Audio for Karma Yoga Repository")
    parser.add_argument("--audio", help="Path to single input audio file")
    parser.add_argument("--transcript", help="Path to single input transcript file")
    parser.add_argument("--folder", help="Input directory containing files to process")
    parser.add_argument("--processed-dir", help="Directory where processed files will be moved", default=DEFAULT_PROCESSED_DIR)
    args = parser.parse_args()

    os.chdir(WORKSPACE_DIR)

    # Handle single file explicit arguments
    if args.audio:
        process_single_file(args.audio, args.processed_dir)
        return
    elif args.transcript:
        process_single_file(args.transcript, args.processed_dir)
        return

    # Determine input folders to scan
    if args.folder:
        input_folders = [os.path.abspath(args.folder)]
    else:
        input_folders = DEFAULT_INPUT_DIRS

    all_files = []
    for folder in input_folders:
        if os.path.exists(folder):
            files = sorted([
                os.path.join(folder, f) for f in os.listdir(folder)
                if os.path.isfile(os.path.join(folder, f))
                and not f.startswith('.')
                and not f.endswith(':Zone.Identifier')
            ])
            all_files.extend(files)

    if not all_files:
        print(f"No files found in input folder(s) to process.")
        for folder in input_folders:
            os.makedirs(folder, exist_ok=True)
        return

    print(f"Found {len(all_files)} file(s) (audio & transcripts) to process...")
    processed_count = 0
    for f_path in all_files:
        success = process_single_file(f_path, args.processed_dir)
        if success:
            processed_count += 1

    print(f"\n==================================================")
    print(f"Batch Processing Completed! ({processed_count}/{len(all_files)} files processed and moved to '{args.processed_dir}')")
    print(f"==================================================")

if __name__ == "__main__":
    main()
