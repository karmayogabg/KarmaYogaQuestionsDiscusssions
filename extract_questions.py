import json
import glob
import os
import re

TRANSCRIPTS_DIR = "/home/sabrisatharamanathan/my-project/KarmaYoga/transcripts"
OUTPUT_MD = "/home/sabrisatharamanathan/my-project/KarmaYoga/KarmaYoga_Jul27_2026_Transcript.md"
QUESTIONS_MD = "/home/sabrisatharamanathan/my-project/KarmaYoga/KarmaYoga_Jul27_2026_Questions.md"

def ms_to_time(ms):
    total_sec = int(ms // 1000)
    mins = total_sec // 60
    secs = total_sec % 60
    return f"{mins:02d}:{secs:02d}"

def extract_all():
    chunk_txts = sorted(glob.glob(os.path.join(TRANSCRIPTS_DIR, "chunk_*.txt")))
    full_transcript_lines = []
    all_segments = []

    for idx, txt_file in enumerate(chunk_txts):
        chunk_name = os.path.basename(txt_file).replace(".txt", "")
        start_min = idx * 3
        end_min = (idx + 1) * 3
        header = f"\n### [{start_min:02d}:00 - {end_min:02d}:00]\n"

        if os.path.exists(txt_file):
            with open(txt_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if content:
                full_transcript_lines.append(f"{header}{content}")
            else:
                full_transcript_lines.append(f"{header}(No audio text detected)")
        
        # Check json for timestamped segments
        json_file = txt_file.replace(".txt", ".json")
        if os.path.exists(json_file):
            try:
                with open(json_file, "r", encoding="utf-8") as jf:
                    data = json.load(jf)
                    transcription = data.get("transcription", [])
                    for seg in transcription:
                        t_from = seg.get("offsets", {}).get("from", 0) + (idx * 3 * 60 * 1000)
                        t_to = seg.get("offsets", {}).get("to", 0) + (idx * 3 * 60 * 1000)
                        text = seg.get("text", "").strip()
                        if text:
                            all_segments.append({
                                "start_ms": t_from,
                                "end_ms": t_to,
                                "timestamp": f"{ms_to_time(t_from)} - {ms_to_time(t_to)}",
                                "text": text
                            })
            except Exception as e:
                print(f"Error parsing {json_file}: {e}")

    # Write combined transcript
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("# கர்மா யோகா (Karma Yoga) - Tamil Audio Transcript\n\n")
        f.write("- **Audio File**: `KarmaYoga_Jul27_2026.m4a`\n")
        f.write("- **Date**: July 27, 2026\n")
        f.write("- **Duration**: 51 minutes 43 seconds\n")
        f.write("- **Language**: Tamil (தமிழ்)\n\n")
        f.write("---\n")
        f.write("\n".join(full_transcript_lines))

    print(f"Updated full transcript at {OUTPUT_MD}")
    return all_segments

if __name__ == "__main__":
    segments = extract_all()
    print(f"Total segments extracted: {len(segments)}")
