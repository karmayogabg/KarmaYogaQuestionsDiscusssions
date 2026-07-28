#!/usr/bin/env python3
"""
Karma Yoga Local Backend Server
Serves static files and provides a POST /api/save endpoint to save questions_data.json directly to disk.
"""

import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8080
WORKSPACE_DIR = "/home/sabrisatharamanathan/my-project/KarmaYoga"

class KarmaYogaRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WORKSPACE_DIR, **kwargs)

    def do_POST(self):
        if self.path == "/api/save":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                target_file = os.path.join(WORKSPACE_DIR, "questions_data.json")
                
                with open(target_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {"status": "success", "message": "Saved directly to questions_data.json on disk!"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                print("Successfully saved questions_data.json to disk.")
            except Exception as e:
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
    print(f"Karma Yoga Local Backend Server running on http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    main()
