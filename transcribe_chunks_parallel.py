import subprocess
import os
import glob
from concurrent.futures import ProcessPoolExecutor

CHUNKS_DIR = "/home/sabrisatharamanathan/my-project/KarmaYoga/chunks"
OUTPUT_DIR = "/home/sabrisatharamanathan/my-project/KarmaYoga/transcripts"
MODEL_PATH = "/home/sabrisatharamanathan/my-project/KarmaYoga/tools/whisper.cpp/models/ggml-small.bin"
WHISPER_CLI = "/home/sabrisatharamanathan/my-project/KarmaYoga/tools/whisper.cpp/build/bin/whisper-cli"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def transcribe_one(chunk_info):
    idx, chunk_file = chunk_info
    chunk_name = os.path.basename(chunk_file).replace(".wav", "")
    out_prefix = os.path.join(OUTPUT_DIR, chunk_name)
    txt_file = out_prefix + ".txt"

    if os.path.exists(txt_file) and os.path.getsize(txt_file) > 0:
        print(f"Skipping already completed {chunk_name}")
        return idx, txt_file

    print(f"[{idx+1}/18] Processing {chunk_name}...", flush=True)
    
    cmd = [
        WHISPER_CLI,
        "-m", MODEL_PATH,
        "-f", chunk_file,
        "-l", "ta",
        "-t", "6",
        "-bs", "1",
        "-bo", "1",
        "-otxt",
        "-of", out_prefix,
        "--prompt", "கர்மா யோகா உபன்யாசம் பகவத் கீதை"
    ]

    subprocess.run(cmd, capture_output=True, text=True)
    print(f"[{idx+1}/18] Finished {chunk_name}", flush=True)
    return idx, txt_file

if __name__ == "__main__":
    chunk_files = sorted(glob.glob(os.path.join(CHUNKS_DIR, "chunk_*.wav")))
    tasks = list(enumerate(chunk_files))
    
    print(f"Transcribing {len(tasks)} chunks with 2 parallel workers (6 threads each)...", flush=True)
    with ProcessPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(transcribe_one, tasks))
        
    print("\nAll chunks transcribed! Combining results...", flush=True)
    
    combined = []
    for idx, txt_file in sorted(results, key=lambda x: x[0]):
        start_min = idx * 3
        end_min = (idx + 1) * 3
        header = f"\n### [{start_min:02d}:00 - {end_min:02d}:00]\n"
        
        if os.path.exists(txt_file):
            with open(txt_file, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
            chunk_text = "\n".join(lines)
            combined.append(f"{header}{chunk_text}")
        else:
            combined.append(f"{header}(No audio text detected)")

    final_md = "/home/sabrisatharamanathan/my-project/KarmaYoga/KarmaYoga_Jul27_2026_Transcript.md"
    with open(final_md, "w", encoding="utf-8") as f:
        f.write("# கர்மா யோகா (Karma Yoga) - Tamil Audio Transcript\n\n")
        f.write("- **Audio File**: `KarmaYoga_Jul27_2026.m4a`\n")
        f.write("- **Date**: July 27, 2026\n")
        f.write("- **Duration**: 51 minutes 43 seconds\n")
        f.write("- **Language**: Tamil (தமிழ்)\n\n")
        f.write("---\n")
        f.write("\n".join(combined))

    print(f"Successfully generated {final_md}", flush=True)
