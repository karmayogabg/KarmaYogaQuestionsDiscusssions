#!/usr/bin/env python3
"""
extractKYTransQues - Automated Python Pipeline Script
Extracts transcripts and questions from Tamil audio meeting recordings using Whisper CLI and FFmpeg.
Generates structured JSON data, plain transcript files, and interactive HTML discussion manager web applications.
"""

import os
import sys
import glob
import json
import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed

WHISPER_BIN = "/home/sabrisatharamanathan/my-project/KarmaYoga/tools/whisper.cpp/build/bin/whisper-cli"
MODEL_PATH = "/home/sabrisatharamanathan/my-project/KarmaYoga/tools/whisper.cpp/models/ggml-medium.bin"

def run_command(cmd, cwd=None):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if res.returncode != 0:
        print(f"Error running command: {cmd}\nStderr: {res.stderr}")
    return res

def split_audio(audio_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    chunk_pattern = os.path.join(output_dir, "chunk_%02d.wav")
    print(f"[1/5] Splitting audio {audio_path} into 3-minute WAV chunks...")
    cmd = f'"/home/sabrisatharamanathan/my-project/KarmaYoga/tools/ffmpeg-7.0.2-amd64-static/ffmpeg" -y -i "{audio_path}" -f segment -segment_time 180 -c:a pcm_s16le -ar 16000 -ac 1 "{chunk_pattern}"'
    run_command(cmd)
    chunks = sorted(glob.glob(os.path.join(output_dir, "chunk_*.wav")))
    print(f"      Generated {len(chunks)} audio chunks.")
    return chunks

def transcribe_chunk(chunk_path):
    base = os.path.splitext(chunk_path)[0]
    out_txt = base + ".wav.txt"
    if os.path.exists(out_txt) and os.path.getsize(out_txt) > 0:
        return chunk_path
    
    cmd = f'"{WHISPER_BIN}" -m "{MODEL_PATH}" -l ta -t 6 -oj -osrt -otxt "{chunk_path}"'
    run_command(cmd)
    return chunk_path

def transcribe_chunks_parallel(chunks, max_workers=2):
    print(f"[2/5] Transcribing {len(chunks)} chunks in parallel (max_workers={max_workers})...")
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(transcribe_chunk, c) for c in chunks]
        for future in as_completed(futures):
            c_path = future.result()
            print(f"      Completed chunk: {os.path.basename(c_path)}")

def compile_transcript(chunks, base_name, workspace_dir):
    print("[3/5] Compiling transcripts...")
    transcript_lines = []
    
    for i, c in enumerate(chunks):
        txt_file = c + ".txt"
        start_min = i * 3
        end_min = (i + 1) * 3
        timestamp_header = f"\n--- [{start_min:02d}:00 - {end_min:02d}:00] ---\n"
        
        if os.path.exists(txt_file):
            with open(txt_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    transcript_lines.append(timestamp_header + content)

    full_transcript = "\n".join(transcript_lines)
    
    # Write to transcripts/ directory and root
    transcripts_dir = os.path.join(workspace_dir, "transcripts")
    os.makedirs(transcripts_dir, exist_ok=True)
    
    plain_txt_path = os.path.join(transcripts_dir, f"{base_name}.txt")
    root_txt_path = os.path.join(workspace_dir, f"{base_name}.txt")
    md_transcript_path = os.path.join(workspace_dir, f"{base_name}_Transcript.md")
    
    with open(plain_txt_path, "w", encoding="utf-8") as f:
        f.write(full_transcript)
        
    with open(root_txt_path, "w", encoding="utf-8") as f:
        f.write(full_transcript)

    with open(md_transcript_path, "w", encoding="utf-8") as f:
        f.write(f"# Transcript: {base_name}\n\n" + full_transcript)

    print(f"      Saved plain transcript: {plain_txt_path}")
    return full_transcript, plain_txt_path

def update_questions_data_and_html(workspace_dir, base_name, full_transcript):
    print("[4/5 & 5/5] Updating questions_data.json and generating HTML application...")
    
    q_json_path = os.path.join(workspace_dir, "questions_data.json")
    if os.path.exists(q_json_path):
        with open(q_json_path, "r", encoding="utf-8") as f:
            q_data = json.load(f)
    else:
        q_data = {"topics": [], "questions": [], "transcripts": []}

    # Ensure transcript is in transcripts array
    if "transcripts" not in q_data:
        q_data["transcripts"] = []

    file_rel = f"transcripts/{base_name}.txt"
    exists_in_json = any(t.get("file") == file_rel for t in q_data["transcripts"])
    if not exists_in_json:
        q_data["transcripts"].append({
            "id": base_name.lower().replace(" ", "_"),
            "title": base_name,
            "date": "2026-07-28",
            "file": file_rel
        })

    with open(q_json_path, "w", encoding="utf-8") as f:
        json.dump(q_data, f, ensure_ascii=False, indent=2)

    # Rebuild HTML template
    q_json_str = json.dumps(q_data, ensure_ascii=False)
    t_json_str = json.dumps(full_transcript, ensure_ascii=False)

    html_template = f'''<!DOCTYPE html>
<html lang="ta">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>கர்மா யோகா - கேள்வி பதில்கள் & உரைப்பதிவுகள்</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Noto+Sans+Tamil:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --bg-primary: #0f172a; --bg-secondary: #1e293b; --bg-card: rgba(30, 41, 59, 0.75);
            --accent-gold: #f59e0b; --accent-gold-light: #fbbf24; --accent-orange: #ea580c;
            --accent-purple: #8b5cf6; --accent-blue: #38bdf8; --accent-green: #10b981; --accent-red: #ef4444;
            --text-primary: #f8fafc; --text-secondary: #94a3b8; --text-muted: #64748b;
            --border-color: rgba(255, 255, 255, 0.1); --border-highlight: rgba(245, 158, 11, 0.3);
            --glass-bg: rgba(15, 23, 42, 0.85);
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Outfit', 'Noto Sans Tamil', sans-serif;
            background-color: var(--bg-primary); color: var(--text-primary); line-height: 1.6;
            background-image: radial-gradient(circle at 15% 15%, rgba(245, 158, 11, 0.08) 0%, transparent 40%),
                              radial-gradient(circle at 85% 85%, rgba(139, 92, 246, 0.08) 0%, transparent 40%);
            background-attachment: fixed; min-height: 100vh; padding-bottom: 80px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        header {{
            padding: 35px 0 20px; text-align: center; border-bottom: 1px solid var(--border-color);
            background: linear-gradient(180deg, rgba(30, 41, 59, 0.6) 0%, transparent 100%);
        }}
        .badge-header {{
            display: inline-flex; align-items: center; gap: 8px; background: rgba(245, 158, 11, 0.15);
            border: 1px solid rgba(245, 158, 11, 0.3); color: var(--accent-gold);
            padding: 6px 16px; border-radius: 50px; font-size: 0.85rem; font-weight: 600; margin-bottom: 15px;
        }}
        h1 {{
            font-size: 2.4rem; font-weight: 700;
            background: linear-gradient(135deg, #ffffff 0%, #fbbf24 50%, #ea580c 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;
        }}
        .subtitle {{ font-size: 1.05rem; color: var(--text-secondary); max-width: 750px; margin: 0 auto 20px; }}
        .view-tabs-wrapper {{ display: flex; justify-content: center; gap: 15px; margin: 20px 0 10px; }}
        .main-tab-btn {{
            background: rgba(30, 41, 59, 0.8); border: 1px solid var(--border-color); color: var(--text-secondary);
            padding: 12px 28px; border-radius: 12px; font-size: 1rem; font-weight: 600; cursor: pointer;
            display: flex; align-items: center; gap: 10px; transition: all 0.3s ease; font-family: inherit;
        }}
        .main-tab-btn:hover {{ background: rgba(255, 255, 255, 0.1); color: var(--text-primary); }}
        .main-tab-btn.active {{
            background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-orange) 100%);
            color: #000; border-color: transparent; box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
        }}
        .view-section {{ display: none; }}
        .view-section.active {{ display: block; animation: fadeIn 0.3s ease; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(5px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .toolbar {{
            display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;
            background: rgba(30, 41, 59, 0.7); border: 1px solid var(--border-color); padding: 15px 24px;
            border-radius: 16px; margin: 20px 0 25px; backdrop-filter: blur(10px);
        }}
        .tool-group {{ display: flex; align-items: center; gap: 12px; }}
        .btn {{
            background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-orange) 100%);
            color: #000; font-weight: 600; border: none; padding: 10px 20px; border-radius: 10px;
            cursor: pointer; display: inline-flex; align-items: center; gap: 8px; font-size: 0.9rem; font-family: inherit;
        }}
        .btn-secondary {{ background: rgba(255, 255, 255, 0.08); color: var(--text-primary); border: 1px solid var(--border-color); }}
        .controls-wrapper {{ position: sticky; top: 20px; z-index: 100; margin-bottom: 30px; }}
        .controls-card {{
            background: var(--glass-bg); border: 1px solid var(--border-color); backdrop-filter: blur(16px);
            border-radius: 20px; padding: 18px 24px; display: flex; flex-direction: column; gap: 15px;
        }}
        .search-box {{ position: relative; width: 100%; }}
        .search-box i {{ position: absolute; left: 16px; top: 50%; transform: translateY(-50%); color: var(--text-muted); }}
        .search-input {{
            width: 100%; background: rgba(15, 23, 42, 0.9); border: 1px solid var(--border-color);
            padding: 12px 16px 12px 48px; border-radius: 12px; color: var(--text-primary); font-size: 0.95rem; font-family: inherit; outline: none;
        }}
        .filter-topics {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .topic-chip {{
            background: rgba(255, 255, 255, 0.05); border: 1px solid var(--border-color); color: var(--text-secondary);
            padding: 7px 15px; border-radius: 50px; font-size: 0.85rem; cursor: pointer; user-select: none;
        }}
        .topic-chip.active {{ background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-orange) 100%); color: #000; font-weight: 600; border-color: transparent; }}
        .topic-group {{ margin-bottom: 40px; }}
        .topic-title {{
            display: flex; align-items: center; gap: 12px; font-size: 1.35rem; font-weight: 600; color: var(--accent-gold-light);
            margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid rgba(245, 158, 11, 0.2);
        }}
        .topic-title i {{ background: rgba(245, 158, 11, 0.15); width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; }}
        .questions-list {{ display: flex; flex-direction: column; gap: 20px; }}
        .question-card {{ background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 18px; overflow: hidden; backdrop-filter: blur(10px); }}
        .card-header {{ padding: 20px 24px; display: flex; align-items: flex-start; gap: 16px; cursor: pointer; }}
        .q-number {{
            background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-orange) 100%);
            color: #000; font-weight: 700; min-width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center;
        }}
        .q-title-wrapper {{ flex-grow: 1; }}
        .q-title-ta {{ font-size: 1.15rem; font-weight: 600; color: var(--text-primary); margin-bottom: 6px; }}
        .q-title-en {{ font-size: 0.95rem; color: var(--text-secondary); font-style: italic; }}
        .q-status-row {{ display: flex; align-items: center; justify-content: space-between; margin-top: 12px; flex-wrap: wrap; gap: 10px; }}
        .timestamp-badge {{ background: rgba(56, 189, 248, 0.1); color: var(--accent-blue); border: 1px solid rgba(56, 189, 248, 0.2); padding: 3px 10px; border-radius: 6px; font-size: 0.8rem; }}
        .status-toggle-btn {{
            background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); color: var(--accent-red);
            padding: 5px 14px; border-radius: 50px; font-size: 0.82rem; font-weight: 600; cursor: pointer;
        }}
        .status-toggle-btn.discussed {{ background: rgba(16, 185, 129, 0.15); border-color: rgba(16, 185, 129, 0.3); color: var(--accent-green); }}
        .toggle-icon {{ color: var(--text-muted); font-size: 1.1rem; transition: transform 0.3s ease; }}
        .question-card.open .toggle-icon {{ transform: rotate(180deg); color: var(--accent-gold); }}
        .card-body {{ display: none; padding: 0 24px 24px; border-top: 1px solid rgba(255, 255, 255, 0.05); background: rgba(15, 23, 42, 0.5); }}
        .question-card.open .card-body {{ display: block; }}
        .detail-block {{ margin-top: 18px; }}
        .detail-block-title {{ font-size: 0.85rem; font-weight: 600; text-transform: uppercase; color: var(--accent-gold); margin-bottom: 8px; }}
        .context-box {{ background: rgba(30, 41, 59, 0.6); border-left: 3px solid var(--accent-gold); padding: 14px 18px; border-radius: 0 10px 10px 0; font-size: 0.95rem; color: var(--text-secondary); }}
        .transcript-snippet {{ background: rgba(15, 23, 42, 0.9); border: 1px solid var(--border-color); border-radius: 10px; padding: 12px 16px; font-size: 0.9rem; color: #cbd5e1; white-space: pre-wrap; max-height: 150px; overflow-y: auto; }}
        .answer-editor-box {{ background: rgba(30, 41, 59, 0.9); border: 1px solid var(--border-highlight); border-radius: 14px; padding: 16px; margin-top: 15px; }}
        .answer-textarea {{ width: 100%; min-height: 80px; background: rgba(15, 23, 42, 0.9); border: 1px solid var(--border-color); border-radius: 10px; padding: 10px 14px; color: var(--text-primary); font-size: 0.95rem; font-family: inherit; outline: none; resize: vertical; }}
        .transcript-repository-card {{ background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 20px; padding: 25px; backdrop-filter: blur(10px); }}
        .select-input {{ background: rgba(15, 23, 42, 0.9); border: 1px solid var(--border-color); color: var(--text-primary); padding: 10px 16px; border-radius: 10px; font-size: 0.95rem; font-family: inherit; outline: none; min-width: 320px; }}
        .transcript-content-viewer {{ background: rgba(15, 23, 42, 0.95); border: 1px solid var(--border-color); border-radius: 14px; padding: 24px; max-height: 600px; overflow-y: auto; font-size: 0.95rem; line-height: 1.8; color: #e2e8f0; white-space: pre-wrap; }}
        .notification {{ position: fixed; bottom: 25px; right: 25px; background: var(--accent-green); color: #000; font-weight: 600; padding: 12px 24px; border-radius: 12px; display: none; z-index: 1000; }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="badge-header"><i class="fa-solid fa-dharmachakra"></i> பகவத் கீதை உபன்யாசம்</div>
            <h1>கர்மா யோகா - கேள்வி பதில்கள் & உரைப்பதிவுகள்</h1>
            <p class="subtitle">Bhagavad Gita Karma Yoga - Interactive Questions, Answers, Discussion Tracker & Full Weekly Transcripts</p>
            <div class="view-tabs-wrapper">
                <button class="main-tab-btn active" id="tabQuestionsBtn" onclick="switchView('questions')"><i class="fa-solid fa-list-check"></i> கேள்வி பதில்கள் (Questions & Answers)</button>
                <button class="main-tab-btn" id="tabTranscriptsBtn" onclick="switchView('transcripts')"><i class="fa-solid fa-file-lines"></i> உரைப்பதிவுகள் Repository (Transcripts)</button>
            </div>
        </div>
    </header>
    <main class="container">
        <div class="view-section active" id="viewQuestions">
            <div class="toolbar">
                <div class="tool-group">
                    <span id="statsSummary" style="font-size: 0.95rem; color: var(--text-secondary);">
                        <i class="fa-solid fa-circle-check" style="color: var(--accent-green);"></i> <strong id="discussedCount" style="color: var(--text-primary);">0</strong> கேள்விகள் விவாதிக்கப்பட்டன
                    </span>
                </div>
                <div class="tool-group">
                    <button class="btn" onclick="saveData()"><i class="fa-solid fa-floppy-disk"></i> Save & Export JSON</button>
                    <button class="btn btn-secondary" onclick="resetData()"><i class="fa-solid fa-rotate-left"></i> Reset to Default</button>
                </div>
            </div>
            <div class="controls-wrapper">
                <div class="controls-card">
                    <div class="search-box">
                        <i class="fa-solid fa-magnifying-glass"></i>
                        <input type="text" id="searchInput" class="search-input" placeholder="தேடுக (e.g. தண்டனை, Reincarnation, Tilak, பாவம்)...">
                    </div>
                    <div class="filter-topics" id="topicFilters"></div>
                </div>
            </div>
            <div id="questionsContainer"></div>
        </div>
        <div class="view-section" id="viewTranscripts">
            <div class="transcript-repository-card">
                <div class="transcript-selector-row" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                    <div>
                        <h3 style="font-size: 1.2rem; color: var(--text-primary);">வாராந்திர உரைப்பதிவுகள் (Weekly Audio Transcripts)</h3>
                        <p style="font-size: 0.85rem; color: var(--text-secondary);">Select and view full audio transcription text</p>
                    </div>
                    <div style="display:flex; gap:10px;">
                        <select id="transcriptSelect" class="select-input" onchange="loadSelectedTranscript()"></select>
                        <button class="btn btn-secondary" onclick="copyTranscriptText()"><i class="fa-solid fa-copy"></i> Copy Text</button>
                    </div>
                </div>
                <div class="search-box" style="margin-bottom: 20px;">
                    <i class="fa-solid fa-magnifying-glass"></i>
                    <input type="text" id="transcriptSearchInput" class="search-input" placeholder="உரைப்பதிவில் தேடுக (Search inside full transcript)..." oninput="filterTranscriptText()">
                </div>
                <div class="transcript-content-viewer" id="transcriptViewer">உரைப்பதிவு ஏற்றப்படுகிறது...</div>
            </div>
        </div>
    </main>
    <div class="notification" id="notification"><i class="fa-solid fa-circle-check"></i> JSON Saved!</div>
    <script>
        const embeddedDefaultJSON = {q_json_str};
        const embeddedDefaultTranscript = {t_json_str};
        let appData = null; let currentTopic = 'all'; let currentSearchTerm = ''; let fullTranscriptText = '';

        async function initApp() {{
            const savedState = localStorage.getItem('karma_yoga_questions_state');
            if (savedState) {{ try {{ appData = JSON.parse(savedState); }} catch (e) {{ console.error(e); }} }}
            if (!appData || !appData.questions || appData.questions.length === 0) {{
                try {{
                    const response = await fetch('questions_data.json');
                    if (response.ok) appData = await response.json();
                    else throw new Error('HTTP ' + response.status);
                }} catch (e) {{ appData = embeddedDefaultJSON; }}
            }}
            renderFilters(); renderQuestions(); updateStats(); renderTranscriptDropdown();
        }}
        function switchView(viewName) {{
            document.querySelectorAll('.main-tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active'));
            if (viewName === 'questions') {{
                document.getElementById('tabQuestionsBtn').classList.add('active');
                document.getElementById('viewQuestions').classList.add('active');
            }} else {{
                document.getElementById('tabTranscriptsBtn').classList.add('active');
                document.getElementById('viewTranscripts').classList.add('active');
                loadSelectedTranscript();
            }}
        }}
        function renderFilters() {{
            const filterContainer = document.getElementById('topicFilters');
            let html = `<span class="topic-chip active" data-topic="all" onclick="filterByTopic('all', this)">அனைத்தும் (All Topics)</span>`;
            if (appData && appData.topics) {{ appData.topics.forEach(t => html += `<span class="topic-chip" data-topic="${{t.id}}" onclick="filterByTopic('${{t.id}}', this)">${{t.title_ta}}</span>`); }}
            filterContainer.innerHTML = html;
        }}
        function filterByTopic(topicId, element) {{
            document.querySelectorAll('.topic-chip').forEach(c => c.classList.remove('active'));
            element.classList.add('active'); currentTopic = topicId; renderQuestions();
        }}
        function renderQuestions() {{
            const container = document.getElementById('questionsContainer'); let html = '';
            if (!appData || !appData.topics || !appData.questions) return;
            appData.topics.forEach(topic => {{
                if (currentTopic !== 'all' && currentTopic !== topic.id) return;
                const topicQuestions = appData.questions.filter(q => q.topic_id === topic.id);
                const visibleQuestions = topicQuestions.filter(q => {{
                    if (!currentSearchTerm) return true;
                    return (q.question_ta + ' ' + q.question_en + ' ' + (q.answer_ta||'') + ' ' + (q.keywords||'')).toLowerCase().includes(currentSearchTerm);
                }});
                if (visibleQuestions.length === 0) return;
                html += `<section class="topic-group"><div class="topic-title"><i class="fa-solid ${{topic.icon}}"></i><span>${{topic.title_ta}} (${{topic.title_en}})</span></div><div class="questions-list">`;
                visibleQuestions.forEach(q => {{
                    const statusClass = q.is_discussed ? 'discussed' : 'pending';
                    const statusText = q.is_discussed ? '<i class="fa-solid fa-circle-check"></i> விவாதிக்கப்பட்டது' : '<i class="fa-solid fa-hourglass-half"></i> நிலுவையில்';
                    html += `<div class="question-card" id="card-${{q.id}}">
                        <div class="card-header" onclick="toggleCard('${{q.id}}')">
                            <div class="q-number">${{q.id}}</div>
                            <div class="q-title-wrapper">
                                <div class="q-title-ta">${{q.question_ta}}</div>
                                <div class="q-title-en">${{q.question_en}}</div>
                                <div class="q-status-row">
                                    <div class="meta-badges"><span class="timestamp-badge"><i class="fa-solid fa-stopwatch"></i> ${{q.timestamp}}</span><span class="category-tag">${{q.category}}</span></div>
                                    <button class="status-toggle-btn ${{statusClass}}" onclick="toggleStatus(event, '${{q.id}}')">${{statusText}}</button>
                                </div>
                            </div>
                            <div class="toggle-icon"><i class="fa-solid fa-chevron-down"></i></div>
                        </div>
                        <div class="card-body">
                            <div class="detail-block"><div class="detail-block-title">பின்னணி (Context)</div><div class="context-box">${{q.context_ta}}</div></div>
                            <div class="detail-block"><div class="detail-block-title">உரைப்பதிவுப் பகுதி (Transcript Snippet)</div><div class="transcript-snippet">${{q.transcript_snippet}}</div></div>
                            <div class="answer-editor-box">
                                <div class="detail-block-title">பதில் / விளக்கம் (Edit Answer)</div>
                                <div style="margin-bottom:10px;"><label style="display:block; font-size:0.85rem; margin-bottom:4px; color:var(--accent-gold-light);">தமிழ் பதில்:</label><textarea class="answer-textarea" onchange="updateAnswer('${{q.id}}', 'ta', this.value)">${{q.answer_ta||''}}</textarea></div>
                                <div><label style="display:block; font-size:0.85rem; margin-bottom:4px; color:var(--accent-gold-light);">English Answer:</label><textarea class="answer-textarea" onchange="updateAnswer('${{q.id}}', 'en', this.value)">${{q.answer_en||''}}</textarea></div>
                            </div>
                        </div>
                    </div>`;
                }});
                html += `</div></section>`;
            }});
            container.innerHTML = html || `<div style="text-align:center; padding:50px; color:var(--text-muted);"><h3>வினாக்கள் கிடைக்கவில்லை</h3></div>`;
        }}
        function toggleCard(id) {{ const c = document.getElementById(`card-${{id}}`); if (c) c.classList.toggle('open'); }}
        function toggleStatus(e, qId) {{ e.stopPropagation(); const q = appData.questions.find(x => x.id === qId); if (q) {{ q.is_discussed = !q.is_discussed; renderQuestions(); updateStats(); autoSaveState(); }} }}
        function updateAnswer(qId, lang, val) {{ const q = appData.questions.find(x => x.id === qId); if (q) {{ if (lang === 'ta') q.answer_ta = val; else q.answer_en = val; autoSaveState(); }} }}
        function updateStats() {{ if (!appData || !appData.questions) return; const discussed = appData.questions.filter(q => q.is_discussed).length; document.getElementById('discussedCount').innerText = discussed; }}
        function autoSaveState() {{ localStorage.setItem('karma_yoga_questions_state', JSON.stringify(appData)); }}
        function saveData() {{ autoSaveState(); const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(appData, null, 2)); const a = document.createElement('a'); a.href = dataStr; a.download = "questions_data.json"; a.click(); showNotification('JSON Saved!'); }}
        function resetData() {{ if (confirm('Reset to default?')) {{ localStorage.removeItem('karma_yoga_questions_state'); location.reload(); }} }}
        function renderTranscriptDropdown() {{ const sel = document.getElementById('transcriptSelect'); let h = ''; if (appData && appData.transcripts) appData.transcripts.forEach(t => h += `<option value="${{t.file}}">${{t.title}} (${{t.date}})</option>`); sel.innerHTML = h || `<option value="Karma Yoga Meeting Recording (Jul 27, 2026).txt">Karma Yoga Meeting Recording (Jul 27, 2026)</option>`; }}
        async function loadSelectedTranscript() {{
            const file = document.getElementById('transcriptSelect').value || 'Karma Yoga Meeting Recording (Jul 27, 2026).txt';
            const viewer = document.getElementById('transcriptViewer');
            try {{ const res = await fetch(file); if (res.ok) {{ fullTranscriptText = await res.text(); viewer.innerText = fullTranscriptText; return; }} }} catch (e) {{}}
            fullTranscriptText = embeddedDefaultTranscript; viewer.innerText = fullTranscriptText;
        }}
        function filterTranscriptText() {{
            const term = document.getElementById('transcriptSearchInput').value.toLowerCase().trim();
            const viewer = document.getElementById('transcriptViewer');
            if (!term) {{ viewer.innerText = fullTranscriptText; return; }}
            const lines = fullTranscriptText.split('\\n').filter(l => l.toLowerCase().includes(term));
            viewer.innerText = lines.length ? `--- Matches Found (${{lines.length}} lines) ---\\n\\n` + lines.join('\\n') : 'No matches found.';
        }}
        function copyTranscriptText() {{ navigator.clipboard.writeText(fullTranscriptText).then(() => showNotification('Copied!')); }}
        function showNotification(msg) {{ const n = document.getElementById('notification'); n.innerText = msg; n.style.display = 'block'; setTimeout(() => n.style.display = 'none', 3000); }}
        document.getElementById('searchInput').addEventListener('input', e => {{ currentSearchTerm = e.target.value.toLowerCase().trim(); renderQuestions(); }});
        window.addEventListener('DOMContentLoaded', initApp);
    </script>
</body>
</html>'''

    html_file = os.path.join(workspace_dir, "index.html")
    index_file = os.path.join(workspace_dir, "index.html")
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_template)
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(html_template)

    print(f"      Saved HTML application: {html_file}")

def main():
    parser = argparse.ArgumentParser(description="Extract Transcript and Questions from Audio (extractKYTransQues Skill)")
    parser.add_argument("--audio", required=True, help="Path to input audio file (.m4a, .wav, .mp3)")
    parser.add_argument("--workspace", default="/home/sabrisatharamanathan/my-project/KarmaYoga", help="Workspace output folder")
    args = parser.parse_args()

    audio_path = os.path.abspath(args.audio)
    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found at {audio_path}")
        sys.exit(1)

    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    chunks_dir = os.path.join(args.workspace, "chunks")

    print(f"=== Starting extractKYTransQues Pipeline for: {base_name} ===")
    chunks = split_audio(audio_path, chunks_dir)
    transcribe_chunks_parallel(chunks, max_workers=2)
    full_transcript, plain_txt_path = compile_transcript(chunks, base_name, args.workspace)
    update_questions_data_and_html(args.workspace, base_name, full_transcript)
    print(f"=== extractKYTransQues Pipeline Completed Successfully! ===")

if __name__ == "__main__":
    main()
