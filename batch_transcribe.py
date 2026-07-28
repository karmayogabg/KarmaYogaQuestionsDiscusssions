import subprocess
import os
import glob
import time
from concurrent.futures import ProcessPoolExecutor

CHUNKS_DIR = "/home/sabrisatharamanathan/my-project/KarmaYoga/chunks"
OUTPUT_DIR = "/home/sabrisatharamanathan/my-project/KarmaYoga/transcripts"
MODEL_PATH = "/home/sabrisatharamanathan/my-project/KarmaYoga/tools/whisper.cpp/models/ggml-medium.bin"
WHISPER_CLI = "/home/sabrisatharamanathan/my-project/KarmaYoga/tools/whisper.cpp/build/bin/whisper-cli"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def transcribe_chunk(chunk_path):
    filename = os.path.basename(chunk_path)
    base_name = os.path.splitext(filename)[0]
    out_prefix = os.path.join(OUTPUT_DIR, base_name)
    txt_file = out_prefix + ".txt"
    json_file = out_prefix + ".json"

    # Skip if json already generated and non-empty
    if os.path.exists(json_file) and os.path.getsize(json_file) > 100:
        print(f"[SKIP] {base_name} already completed.")
        return base_name, True

    print(f"[START] Transcribing {base_name}...", flush=True)
    t0 = time.time()
    
    cmd = [
        WHISPER_CLI,
        "-m", MODEL_PATH,
        "-f", chunk_path,
        "-l", "ta",
        "-t", "6",
        "-oj",
        "-osrt",
        "-otxt",
        "-of", out_prefix,
        "--prompt", "பகவத் கீதை கர்மா யோகா உபன்யாசம் கேள்வி பதில்"
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - t0
    
    if res.returncode == 0 and os.path.exists(json_file):
        print(f"[DONE] {base_name} completed in {elapsed:.1f}s", flush=True)
        return base_name, True
    else:
        print(f"[ERROR] {base_name} failed with code {res.returncode}:\n{res.stderr}", flush=True)
        return base_name, False

def main():
    chunks = sorted(glob.glob(os.path.join(CHUNKS_DIR, "chunk_*.wav")))
    print(f"Found {len(chunks)} audio chunks to transcribe.", flush=True)

    # Use 2 process workers, each with 6 threads (total 12 threads out of 16 cores)
    with ProcessPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(transcribe_chunk, chunks))

    successes = sum(1 for _, ok in results if ok)
    print(f"\nCompleted {successes}/{len(chunks)} transcriptions.", flush=True)

if __name__ == "__main__":
    main()
