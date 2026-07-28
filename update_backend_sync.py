import json, os

with open('questions_data.json', 'r', encoding='utf-8') as f:
    q_data_obj = json.load(f)

with open('Karma Yoga Meeting Recording (Jul 27, 2026).txt', 'r', encoding='utf-8') as f:
    t_text = f.read()

json_q = json.dumps(q_data_obj, ensure_ascii=False, indent=2)
json_t = json.dumps(t_text, ensure_ascii=False)

html_code = f"""<!DOCTYPE html>
<html lang="ta">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Karma Yoga Questions, Answers & Full Transcripts Repository Manager">
    <title>கர்மா யோகா - கேள்வி பதில்கள் & விவாதங்கள் | Karmayoga Questions & Transcripts</title>
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Noto+Sans+Tamil:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- FontAwesome icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <style>
        :root {{
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: rgba(30, 41, 59, 0.85);
            
            --accent-gold: #f59e0b;
            --accent-gold-light: #fbbf24;
            --accent-orange: #ea580c;
            --accent-purple: #8b5cf6;
            --accent-blue: #38bdf8;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            
            --border-color: rgba(255, 255, 255, 0.12);
            --border-highlight: rgba(245, 158, 11, 0.4);
            --glass-bg: rgba(15, 23, 42, 0.85);
            --shadow-glow: 0 10px 30px -10px rgba(245, 158, 11, 0.2);
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: 'Outfit', 'Noto Sans Tamil', sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            background-image: 
                radial-gradient(circle at 15% 15%, rgba(245, 158, 11, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 85% 85%, rgba(139, 92, 246, 0.08) 0%, transparent 40%);
            background-attachment: fixed;
            min-height: 100vh;
            padding-bottom: 80px;
        }}

        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}

        /* Header */
        header {{
            padding: 35px 0 20px;
            text-align: center;
            border-bottom: 1px solid var(--border-color);
            background: linear-gradient(180deg, rgba(30, 41, 59, 0.6) 0%, transparent 100%);
        }}

        .badge-header {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(245, 158, 11, 0.15);
            border: 1px solid rgba(245, 158, 11, 0.3);
            color: var(--accent-gold);
            padding: 6px 16px;
            border-radius: 50px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 15px;
            text-transform: uppercase;
        }}

        h1 {{
            font-size: 2.4rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff 0%, #fbbf24 50%, #ea580c 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}

        .subtitle {{
            font-size: 1.05rem;
            color: var(--text-secondary);
            max-width: 750px;
            margin: 0 auto 20px;
        }}

        /* Top Main View Navigation Tabs */
        .view-tabs-wrapper {{
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 20px 0 10px;
        }}

        .main-tab-btn {{
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            padding: 12px 28px;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: all 0.3s ease;
            font-family: inherit;
        }}

        .main-tab-btn:hover {{
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
        }}

        .main-tab-btn.active {{
            background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-orange) 100%);
            color: #000;
            border-color: transparent;
            box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
        }}

        /* View Section Containers */
        .view-section {{ display: none; }}
        .view-section.active {{ display: block; animation: fadeIn 0.3s ease; }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(5px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Action Toolbar */
        .toolbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid var(--border-color);
            padding: 15px 24px;
            border-radius: 16px;
            margin: 20px 0 25px;
            backdrop-filter: blur(10px);
        }}

        .tool-group {{ display: flex; align-items: center; gap: 12px; }}

        .btn {{
            background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-orange) 100%);
            color: #000;
            font-weight: 600;
            border: none;
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 0.9rem;
            font-family: inherit;
            transition: all 0.2s ease;
            box-shadow: 0 4px 14px rgba(245, 158, 11, 0.2);
        }}

        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(245, 158, 11, 0.35);
        }}

        .btn-secondary {{
            background: rgba(255, 255, 255, 0.08);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            box-shadow: none;
        }}

        .btn-secondary:hover {{
            background: rgba(255, 255, 255, 0.15);
            box-shadow: none;
        }}

        /* Controls: Search & Topic Filter */
        .controls-wrapper {{
            position: sticky;
            top: 20px;
            z-index: 100;
            margin-bottom: 30px;
        }}

        .controls-card {{
            background: var(--glass-bg);
            border: 1px solid var(--border-color);
            backdrop-filter: blur(16px);
            border-radius: 20px;
            padding: 18px 24px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}

        .search-box {{ position: relative; width: 100%; }}
        .search-box i {{ position: absolute; left: 16px; top: 50%; transform: translateY(-50%); color: var(--text-muted); }}
        .search-input {{
            width: 100%;
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid var(--border-color);
            padding: 12px 16px 12px 48px;
            border-radius: 12px;
            color: var(--text-primary);
            font-size: 0.95rem;
            font-family: inherit;
            outline: none;
        }}
        .search-input:focus {{ border-color: var(--accent-gold); }}

        .filter-topics {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .topic-chip {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            padding: 7px 15px;
            border-radius: 50px;
            font-size: 0.85rem;
            cursor: pointer;
            user-select: none;
        }}
        .topic-chip.active {{
            background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-orange) 100%);
            color: #000;
            font-weight: 600;
            border-color: transparent;
        }}

        /* Question Cards & Topic Sections */
        .topic-group {{ margin-bottom: 40px; }}
        .topic-title {{
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 1.35rem;
            font-weight: 600;
            color: var(--accent-gold-light);
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(245, 158, 11, 0.2);
        }}

        .topic-title i {{
            background: rgba(245, 158, 11, 0.15);
            width: 36px;
            height: 36px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .questions-list {{ display: flex; flex-direction: column; gap: 20px; }}

        .question-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 18px;
            overflow: hidden;
            backdrop-filter: blur(10px);
            transition: border-color 0.3s ease;
        }}

        .question-card:hover {{ border-color: var(--border-highlight); }}

        .card-header {{
            padding: 20px 24px;
            display: flex;
            align-items: flex-start;
            gap: 16px;
            cursor: pointer;
        }}

        .q-number {{
            background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-orange) 100%);
            color: #000;
            font-weight: 700;
            min-width: 38px;
            height: 38px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.95rem;
            flex-shrink: 0;
        }}

        .q-title-wrapper {{ flex-grow: 1; }}
        .q-title-ta {{ font-size: 1.15rem; font-weight: 600; color: var(--text-primary); margin-bottom: 6px; }}
        .q-title-en {{ font-size: 0.95rem; color: var(--text-secondary); font-style: italic; }}

        .q-status-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 12px;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .meta-badges {{ display: flex; gap: 10px; font-size: 0.8rem; align-items: center; }}
        .timestamp-badge {{
            background: rgba(56, 189, 248, 0.1);
            color: var(--accent-blue);
            border: 1px solid rgba(56, 189, 248, 0.2);
            padding: 3px 10px;
            border-radius: 6px;
        }}

        /* Discussion Status Toggle Button */
        .status-toggle-btn {{
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: var(--accent-red);
            padding: 6px 16px;
            border-radius: 50px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
        }}

        .status-toggle-btn.discussed {{
            background: rgba(16, 185, 129, 0.15);
            border-color: rgba(16, 185, 129, 0.3);
            color: var(--accent-green);
        }}

        .toggle-icon {{ color: var(--text-muted); font-size: 1.1rem; transition: transform 0.3s ease; }}
        .question-card.open .toggle-icon {{ transform: rotate(180deg); color: var(--accent-gold); }}

        /* Card Body & Answer Editor */
        .card-body {{
            display: none;
            padding: 0 24px 24px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            background: rgba(15, 23, 42, 0.5);
        }}

        .question-card.open .card-body {{ display: block; }}

        .detail-block {{ margin-top: 18px; }}
        .detail-block-title {{
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--accent-gold);
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .context-box {{
            background: rgba(30, 41, 59, 0.6);
            border-left: 3px solid var(--accent-gold);
            padding: 14px 18px;
            border-radius: 0 10px 10px 0;
            font-size: 0.95rem;
            color: var(--text-secondary);
        }}

        .transcript-snippet {{
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 12px 16px;
            font-size: 0.9rem;
            color: #cbd5e1;
            white-space: pre-wrap;
            max-height: 150px;
            overflow-y: auto;
        }}

        /* Prominent Editable Answer Box */
        .answer-editor-box {{
            background: rgba(30, 41, 59, 0.95);
            border: 1.5px solid var(--border-highlight);
            border-radius: 14px;
            padding: 18px;
            margin-top: 18px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        }}

        .form-group {{ margin-bottom: 14px; }}
        .form-group label {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.88rem;
            font-weight: 600;
            color: var(--accent-gold-light);
            margin-bottom: 8px;
        }}

        .answer-textarea {{
            width: 100%;
            min-height: 90px;
            background: rgba(15, 23, 42, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 10px;
            padding: 12px 16px;
            color: var(--text-primary);
            font-size: 0.95rem;
            font-family: inherit;
            outline: none;
            resize: vertical;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }}

        .answer-textarea:focus {{
            border-color: var(--accent-gold);
            box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2);
        }}

        .save-card-btn {{
            background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-orange) 100%);
            color: #000;
            font-weight: 700;
            border: none;
            padding: 8px 18px;
            border-radius: 8px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.85rem;
            margin-top: 5px;
        }}

        /* Transcript Viewer Section */
        .transcript-repository-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 25px;
            backdrop-filter: blur(10px);
        }}

        .transcript-selector-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--border-color);
        }}

        .select-input {{
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 10px 16px;
            border-radius: 10px;
            font-size: 0.95rem;
            font-family: inherit;
            outline: none;
            min-width: 320px;
        }}

        .select-input:focus {{ border-color: var(--accent-gold); }}

        .transcript-content-viewer {{
            background: rgba(15, 23, 42, 0.95);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 24px;
            max-height: 600px;
            overflow-y: auto;
            font-family: 'Outfit', 'Noto Sans Tamil', sans-serif;
            font-size: 0.95rem;
            line-height: 1.8;
            color: #e2e8f0;
            white-space: pre-wrap;
        }}

        .notification {{
            position: fixed;
            bottom: 25px;
            right: 25px;
            background: var(--accent-green);
            color: #000;
            font-weight: 600;
            padding: 12px 24px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            display: none;
            z-index: 1000;
        }}
    </style>
</head>
<body>

    <header>
        <div class="container">
            <div class="badge-header">
                <i class="fa-solid fa-dharmachakra"></i> பகவத் கீதை உபன்யாசம்
            </div>
            <h1>கர்மா யோகா - கேள்வி பதில்கள் & உரைப்பதிவுகள்</h1>
            <p class="subtitle">Bhagavad Gita Karma Yoga - Interactive Questions, Answers, Discussion Tracker & Full Weekly Transcripts</p>

            <!-- Main View Navigation Tabs -->
            <div class="view-tabs-wrapper">
                <button class="main-tab-btn active" id="tabQuestionsBtn" onclick="switchView('questions')">
                    <i class="fa-solid fa-list-check"></i> கேள்வி பதில்கள் (Questions & Answers)
                </button>
                <button class="main-tab-btn" id="tabTranscriptsBtn" onclick="switchView('transcripts')">
                    <i class="fa-solid fa-file-lines"></i> உரைப்பதிவுகள் Repository (Transcripts)
                </button>
            </div>
        </div>
    </header>

    <main class="container">

        <!-- VIEW 1: QUESTIONS & ANSWERS -->
        <div class="view-section active" id="viewQuestions">
            <!-- Action Toolbar -->
            <div class="toolbar">
                <div class="tool-group">
                    <span id="statsSummary" style="font-size: 0.95rem; color: var(--text-secondary);">
                        <i class="fa-solid fa-circle-check" style="color: var(--accent-green);"></i> <strong id="discussedCount" style="color: var(--text-primary);">15</strong>/15 கேள்விகள் விவாதிக்கப்பட்டன
                    </span>
                </div>
                <div class="tool-group">
                    <button class="btn" onclick="saveData()"><i class="fa-solid fa-floppy-disk"></i> Save to Backend JSON & GitHub</button>
                    <button class="btn btn-secondary" onclick="resetData()"><i class="fa-solid fa-rotate-left"></i> Reset Defaults</button>
                </div>
            </div>

            <!-- Sticky Controls: Search & Topic Filter -->
            <div class="controls-wrapper">
                <div class="controls-card">
                    <div class="search-box">
                        <i class="fa-solid fa-magnifying-glass"></i>
                        <input type="text" id="searchInput" class="search-input" placeholder="தேடுக (e.g. தண்டனை, Reincarnation, Tilak, பாவம்)...">
                    </div>

                    <div class="filter-topics" id="topicFilters">
                        <!-- Dynamic Topic Chips -->
                    </div>
                </div>
            </div>

            <!-- Questions List Container -->
            <div id="questionsContainer"></div>
        </div>

        <!-- VIEW 2: FULL TRANSCRIPTS REPOSITORY -->
        <div class="view-section" id="viewTranscripts">
            <div class="transcript-repository-card">
                <div class="transcript-selector-row">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <i class="fa-solid fa-folder-open" style="font-size: 1.5rem; color: var(--accent-gold);"></i>
                        <div>
                            <h3 style="font-size: 1.2rem; color: var(--text-primary);">வாராந்திர உரைப்பதிவுகள் (Weekly Audio Transcripts)</h3>
                            <p style="font-size: 0.85rem; color: var(--text-secondary);">Select and view the full audio transcription text</p>
                        </div>
                    </div>

                    <div style="display: flex; align-items: center; gap: 10px;">
                        <select id="transcriptSelect" class="select-input" onchange="loadSelectedTranscript()">
                            <!-- Dynamic Transcript Options -->
                        </select>
                        <button class="btn btn-secondary" onclick="copyTranscriptText()"><i class="fa-solid fa-copy"></i> Copy Text</button>
                    </div>
                </div>

                <div class="search-box" style="margin-bottom: 20px;">
                    <i class="fa-solid fa-magnifying-glass"></i>
                    <input type="text" id="transcriptSearchInput" class="search-input" placeholder="உரைப்பதிவில் தேடுக (Search inside full transcript)..." oninput="filterTranscriptText()">
                </div>

                <div class="transcript-content-viewer" id="transcriptViewer">
                    உரைப்பதிவு ஏற்றப்படுகிறது... (Loading transcript text...)
                </div>
            </div>
        </div>

    </main>

    <div class="notification" id="notification">
        <i class="fa-solid fa-circle-check"></i> JSON Data Saved Successfully!
    </div>

    <!-- Application Script -->
    <script>
        // Embedded Offline Fallbacks
        const embeddedDefaultJSON = {json_q};
        const embeddedDefaultTranscript = {json_t};

        let appData = null;
        let currentTopic = 'all';
        let currentSearchTerm = '';
        let fullTranscriptText = '';

        async function initApp() {{
            const savedState = localStorage.getItem('karma_yoga_questions_state');
            if (savedState) {{
                try {{
                    const parsed = JSON.parse(savedState);
                    if (parsed && parsed.questions && parsed.questions.length > 0) {{
                        appData = parsed;
                    }}
                }} catch (e) {{
                    console.error('LocalStorage parse error:', e);
                }}
            }}

            if (!appData || !appData.questions || appData.questions.length === 0) {{
                try {{
                    const response = await fetch('questions_data.json');
                    if (response.ok) {{
                        const fetched = await response.json();
                        if (fetched && fetched.questions && fetched.questions.length > 0) {{
                            appData = fetched;
                        }}
                    }}
                }} catch (e) {{
                    console.warn('Fetch failed, using embedded JSON fallback:', e);
                }}
            }}

            if (!appData || !appData.questions || appData.questions.length === 0) {{
                appData = embeddedDefaultJSON;
            }}

            renderFilters();
            renderQuestions();
            updateStats();
            renderTranscriptDropdown();
        }}

        function switchView(viewName) {{
            document.querySelectorAll('.main-tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active'));

            if (viewName === 'questions') {{
                document.getElementById('tabQuestionsBtn').classList.add('active');
                document.getElementById('viewQuestions').classList.add('active');
            }} else if (viewName === 'transcripts') {{
                document.getElementById('tabTranscriptsBtn').classList.add('active');
                document.getElementById('viewTranscripts').classList.add('active');
                loadSelectedTranscript();
            }}
        }}

        function renderFilters() {{
            const filterContainer = document.getElementById('topicFilters');
            let html = `<span class="topic-chip active" data-topic="all" onclick="filterByTopic('all', this)">அனைத்தும் (All Topics)</span>`;
            if (appData && appData.topics) {{
                appData.topics.forEach(t => {{
                    html += `<span class="topic-chip" data-topic="${{t.id}}" onclick="filterByTopic('${{t.id}}', this)">${{t.title_ta}}</span>`;
                }});
            }}
            filterContainer.innerHTML = html;
        }}

        function filterByTopic(topicId, element) {{
            document.querySelectorAll('.topic-chip').forEach(c => c.classList.remove('active'));
            element.classList.add('active');
            currentTopic = topicId;
            renderQuestions();
        }}

        function renderQuestions() {{
            const container = document.getElementById('questionsContainer');
            let html = '';

            if (!appData || !appData.topics || !appData.questions) {{
                container.innerHTML = `<div style="text-align:center; padding:50px; color:var(--text-muted);"><h3>வினாக்கள் கிடைக்கவில்லை</h3></div>`;
                return;
            }}

            appData.topics.forEach(topic => {{
                if (currentTopic !== 'all' && currentTopic !== topic.id) return;
                const topicQuestions = appData.questions.filter(q => q.topic_id === topic.id);
                const visibleQuestions = topicQuestions.filter(q => {{
                    if (!currentSearchTerm) return true;
                    const text = (q.question_ta + ' ' + q.question_en + ' ' + (q.answer_ta||'') + ' ' + (q.answer_en||'') + ' ' + (q.keywords||'')).toLowerCase();
                    return text.includes(currentSearchTerm);
                }});

                if (visibleQuestions.length === 0) return;

                html += `
                <section class="topic-group" data-topic="${{topic.id}}">
                    <div class="topic-title">
                        <i class="fa-solid ${{topic.icon}}"></i>
                        <span>${{topic.title_ta}} (${{topic.title_en}})</span>
                    </div>
                    <div class="questions-list">
                `;

                visibleQuestions.forEach(q => {{
                    const isDiscussed = q.is_discussed;
                    const statusClass = isDiscussed ? 'discussed' : 'pending';
                    const statusText = isDiscussed ? '<i class="fa-solid fa-circle-check"></i> விவாதிக்கப்பட்டது (Discussed)' : '<i class="fa-solid fa-hourglass-half"></i> நிலுவையில் (Pending)';

                    html += `
                        <div class="question-card" id="card-${{q.id}}">
                            <div class="card-header" onclick="toggleCard('${{q.id}}')">
                                <div class="q-number">${{q.id}}</div>
                                <div class="q-title-wrapper">
                                    <div class="q-title-ta">${{q.question_ta}}</div>
                                    <div class="q-title-en">${{q.question_en}}</div>
                                    <div class="q-status-row">
                                        <div class="meta-badges">
                                            <span class="timestamp-badge"><i class="fa-solid fa-stopwatch"></i> ${{q.timestamp}}</span>
                                            <span class="category-tag">${{q.category}}</span>
                                        </div>
                                        <button class="status-toggle-btn ${{statusClass}}" onclick="toggleStatus(event, '${{q.id}}')">
                                            ${{statusText}}
                                        </button>
                                    </div>
                                </div>
                                <div class="toggle-icon"><i class="fa-solid fa-chevron-down"></i></div>
                            </div>
                            <div class="card-body">
                                <div class="detail-block">
                                    <div class="detail-block-title"><i class="fa-solid fa-circle-info"></i> பின்னணி (Context)</div>
                                    <div class="context-box">${{q.context_ta}}</div>
                                </div>
                                <div class="detail-block">
                                    <div class="detail-block-title"><i class="fa-solid fa-quote-left"></i> உரைப்பதிவுப் பகுதி (Transcript Snippet)</div>
                                    <div class="transcript-snippet">${{q.transcript_snippet}}</div>
                                </div>
                                <div class="answer-editor-box">
                                    <div class="detail-block-title"><i class="fa-solid fa-pen-to-square"></i> விவாதிக்கப்பட்ட பதில் / குறிப்புகள் (Type Answer & Notes)</div>
                                    <div class="form-group">
                                        <label><i class="fa-solid fa-language"></i> தமிழ் பதில் (Tamil Answer):</label>
                                        <textarea class="answer-textarea" oninput="updateAnswer('${{q.id}}', 'ta', this.value)" placeholder="இங்கே விவாதிக்கப்பட்ட பதிலைத் தட்டச்சு செய்க (Type Tamil answer here)...">${{q.answer_ta || ''}}</textarea>
                                    </div>
                                    <div class="form-group">
                                        <label><i class="fa-solid fa-globe"></i> English Summary Answer:</label>
                                        <textarea class="answer-textarea" oninput="updateAnswer('${{q.id}}', 'en', this.value)" placeholder="Type English summary answer here...">${{q.answer_en || ''}}</textarea>
                                    </div>
                                    <button class="save-card-btn" onclick="saveData()"><i class="fa-solid fa-floppy-disk"></i> Save to Backend JSON & GitHub</button>
                                </div>
                            </div>
                        </div>
                    `;
                }});
                html += `</div></section>`;
            }});

            container.innerHTML = html || `<div style="text-align:center; padding:50px; color:var(--text-muted);"><h3>வினாக்கள் கிடைக்கவில்லை</h3></div>`;
        }}

        function toggleCard(id) {{
            const card = document.getElementById(`card-${{id}}`);
            if (card) card.classList.toggle('open');
        }}

        function toggleStatus(event, qId) {{
            event.stopPropagation();
            const question = appData.questions.find(q => q.id === qId);
            if (question) {{
                question.is_discussed = !question.is_discussed;
                renderQuestions();
                updateStats();
                autoSaveState();
            }}
        }}

        function updateAnswer(qId, lang, value) {{
            const question = appData.questions.find(q => q.id === qId);
            if (question) {{
                if (lang === 'ta') question.answer_ta = value;
                if (lang === 'en') question.answer_en = value;
                autoSaveState();
            }}
        }}

        function updateStats() {{
            if (!appData || !appData.questions) return;
            const total = appData.questions.length;
            const discussed = appData.questions.filter(q => q.is_discussed).length;
            document.getElementById('discussedCount').innerText = discussed;
            document.getElementById('statsSummary').innerHTML = `<i class="fa-solid fa-circle-check" style="color: var(--accent-green);"></i> <strong style="color: var(--text-primary);">${{discussed}}</strong>/${{total}} கேள்விகள் விவாதிக்கப்பட்டன (Discussed)`;
        }}

        function autoSaveState() {{
            localStorage.setItem('karma_yoga_questions_state', JSON.stringify(appData));
        }}

        async function saveData() {{
            autoSaveState();
            
            // Post directly to local backend server (/api/save), which saves questions_data.json to disk AND git pushes to GitHub automatically!
            try {{
                const res = await fetch('/api/save', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(appData, null, 2)
                }});
                if (res.ok) {{
                    const result = await res.json();
                    showNotification('✓ ' + (result.message || 'Saved to questions_data.json and pushed to GitHub!'));
                    return;
                }}
            }} catch (e) {{
                console.warn('Backend API save endpoint unavailable:', e);
            }}

            showNotification('Saved to LocalStorage!');
        }}

        function resetData() {{
            if (confirm('Reset all typed answers & statuses to original defaults?')) {{
                localStorage.removeItem('karma_yoga_questions_state');
                location.reload();
            }}
        }}

        /* Transcript Viewer Logic */
        function renderTranscriptDropdown() {{
            const select = document.getElementById('transcriptSelect');
            let html = '';
            if (appData && appData.transcripts && appData.transcripts.length > 0) {{
                appData.transcripts.forEach(t => {{
                    html += `<option value="${{t.file}}">${{t.title}} (${{t.date}})</option>`;
                }});
            }} else {{
                html = `<option value="Karma Yoga Meeting Recording (Jul 27, 2026).txt">Karma Yoga Meeting Recording (Jul 27, 2026)</option>`;
            }}
            select.innerHTML = html;
        }}

        async function loadSelectedTranscript() {{
            const select = document.getElementById('transcriptSelect');
            const file = select.value || 'Karma Yoga Meeting Recording (Jul 27, 2026).txt';
            const viewer = document.getElementById('transcriptViewer');

            viewer.innerHTML = 'உரைப்பதிவு ஏற்றப்படுகிறது... (Loading transcript text...)';

            try {{
                const res = await fetch(file);
                if (res.ok) {{
                    fullTranscriptText = await res.text();
                    viewer.innerText = fullTranscriptText;
                    return;
                }}
            }} catch (e) {{
                console.warn('Fetch failed, using embedded fallback transcript:', e);
            }}

            fullTranscriptText = embeddedDefaultTranscript;
            viewer.innerText = fullTranscriptText;
        }}

        function filterTranscriptText() {{
            const term = document.getElementById('transcriptSearchInput').value.toLowerCase().trim();
            const viewer = document.getElementById('transcriptViewer');
            if (!term) {{
                viewer.innerText = fullTranscriptText;
                return;
            }}
            const lines = fullTranscriptText.split('\\n');
            const matchingLines = lines.filter(line => line.toLowerCase().includes(term));
            if (matchingLines.length > 0) {{
                viewer.innerText = `--- Matches Found (${{matchingLines.length}} lines) ---\\n\\n` + matchingLines.join('\\n');
            }} else {{
                viewer.innerText = 'தேடிய வார்த்தை உரைப்பதிவில் இல்லை.';
            }}
        }}

        function copyTranscriptText() {{
            navigator.clipboard.writeText(fullTranscriptText).then(() => {{
                showNotification('Transcript copied to clipboard!');
            }});
        }}

        function showNotification(msg) {{
            const notif = document.getElementById('notification');
            notif.innerText = msg;
            notif.style.display = 'block';
            setTimeout(() => {{ notif.style.display = 'none'; }}, 3500);
        }}

        document.getElementById('searchInput').addEventListener('input', (e) => {{
            currentSearchTerm = e.target.value.toLowerCase().trim();
            renderQuestions();
        }});

        window.addEventListener('DOMContentLoaded', initApp);
    </script>
</body>
</html>"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_code)

with open('Karmayoga-Questions-Discussion.html', 'w', encoding='utf-8') as f:
    f.write(html_code)

artifact_path = '/home/sabrisatharamanathan/.gemini/antigravity-cli/brain/f1e6c23f-d0aa-47df-8f98-22cad29b7277/Karmayoga-Questions-Discussion.html'
with open(artifact_path, 'w', encoding='utf-8') as f:
    f.write(html_code)

print('Updated index.html, Karmayoga-Questions-Discussion.html, and artifact for seamless backend save!')
