#!/usr/bin/env python3
"""
Karma Yoga Local Backend Server with Automatic Git Commit & Push
Serves static files and provides a POST /api/save endpoint that:
1. Writes questions_data.json directly to disk.
2. Automatically commits and pushes questions_data.json to GitHub!
"""

import os
import json
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8080
WORKSPACE_DIR = "/home/sabrisatharamanathan/my-project/KarmaYoga"

from master_data import ensure_valid_data

class KarmaYogaRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WORKSPACE_DIR, **kwargs)

    def do_POST(self):
        if self.path == "/api/save":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                raw_data = json.loads(post_data.decode('utf-8'))
                data = ensure_valid_data(raw_data)
                target_file = os.path.join(WORKSPACE_DIR, "questions_data.json")
                
                # 1. Save to local disk
                with open(target_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # 2. Rebuild index.html to keep embedded fallbacks updated
                subprocess.run("python3 update_backend_sync.py", shell=True, cwd=WORKSPACE_DIR)

                # 3. Auto Git Commit & Push to GitHub
                git_cmd = "git add questions_data.json index.html && git commit -m 'Auto-update questions_data.json answers & status' && git push origin main"
                git_res = subprocess.run(git_cmd, shell=True, capture_output=True, text=True, cwd=WORKSPACE_DIR)
                
                push_status = "and pushed to GitHub!" if git_res.returncode == 0 else "(local disk saved)"
                if git_res.returncode != 0:
                    print("Git push output:", git_res.stdout, git_res.stderr)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {
                    "status": "success",
                    "message": f"Saved to questions_data.json {push_status}"
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                print(f"Successfully saved questions_data.json {push_status}")
            except Exception as e:
                print("Save error:", e)
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {"status": "error", "message": str(e)}
                self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_error(404, "Endpoint not found")

def main():
    os.chdir(WORKSPACE_DIR)
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, KarmaYogaRequestHandler)
    print(f"Karma Yoga Local Backend Server with Auto Git Push running on http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    main()
