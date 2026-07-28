import subprocess
import os
import glob
import re

CHUNKS_DIR = "/home/sabrisatharamanathan/my-project/KarmaYoga/chunks"
OUTPUT_DIR = "/home/sabrisatharamanathan/my-project/KarmaYoga/transcripts"
MODEL_PATH = "/home/sabrisatharamanathan/my-project/KarmaYoga/tools/whisper.cpp/models/ggml-large-v3-turbo.bin"
WHISPER_CLI = "/home/sabrisatharamanathan/my-project/KarmaYoga/tools/whisper.cpp/build/bin/whisper-cli"

os.makedirs(OUTPUT_DIR, exist_ok=True)

chunk_files = sorted(glob.glob(os.path.join(CHUNKS_DIR, "chunk_*.wav")))
print(f"Found {len(chunk_files)} audio chunks.")

combined_transcript = []

for idx, chunk_file in enumerate(chunk_files):
    chunk_name = os.path.basename(chunk_file).replace(".wav", "")
    out_prefix = os.path.join(OUTPUT_DIR, chunk_name)
    txt_file = out_prefix + ".txt"

    start_min = idx * 3
    end_min = (idx + 1) * 3
    header = f"\n### [{start_min:02d}:00 - {end_min:02d}:00]\n"

    print(f"[{idx+1}/{len(chunk_files)}] Transcribing {chunk_name}...")
    
    cmd = [
        WHISPER_CLI,
        "-m", MODEL_PATH,
        "-f", chunk_file,
        "-l", "ta",
        "-t", "14",
        "-mc", "64",
        "-nth", "0.65",
        "-et", "2.8",
        "-sow",
        "-otxt",
        "-of", out_prefix,
        "--prompt", "கர்மா யோகா உபன்யாசம் பகவத் கீதை தமிழ் சொற்பொழிவு"
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    
    if os.path.exists(txt_file):
        with open(txt_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        clean_lines = []
        for l in lines:
            line_str = l.strip()
            if not line_str:
                continue
            clean_lines.append(line_str)
            
        chunk_text = "\n".join(clean_lines)
        combined_transcript.append(f"{header}{chunk_text}")
        print(f"Chunk {chunk_name} finished ({len(clean_lines)} lines).")
    else:
        print(f"Warning: {txt_file} not found.")

final_md = "/home/sabrisatharamanathan/my-project/KarmaYoga/KarmaYoga_Jul27_2026_Transcript.md"
with open(final_md, "w", encoding="utf-8") as f:
    f.write("# கர்மா யோகா (Karma Yoga) - Tamil Audio Transcript\n")
    f.write("**Audio File**: KarmaYoga_Jul27_2026.m4a\n")
    f.write("**Date**: July 27, 2026\n")
    f.write("**Duration**: 51 minutes 43 seconds\n\n")
    f.write("---\n")
    f.write("\n".join(combined_transcript))

print(f"\nSaved combined transcript to {final_md}")
