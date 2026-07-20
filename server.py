import http.server
import socketserver
import json
import os

PORT = 8123

class AdminHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/save':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                payload = json.loads(post_data.decode('utf-8'))
                
                # Simple validation of payload structure
                if not isinstance(payload, dict):
                    raise ValueError("Payload must be a dictionary")
                
                # Write to content.json (using DATA_DIR if configured for persistent environments)
                data_dir = os.environ.get('DATA_DIR', os.getcwd())
                content_file_path = os.path.join(data_dir, 'content.json')
                with open(content_file_path, 'w', encoding='utf-8') as f:
                    json.dump(payload, f, indent=2, ensure_ascii=False)
                
                # Respond with success
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                response = {"status": "success", "message": "Content updated successfully"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                print("[Server] content.json updated successfully.")
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {"status": "error", "message": str(e)}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                print(f"[Server] Error saving content: {e}")
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/content.json':
            data_dir = os.environ.get('DATA_DIR', os.getcwd())
            content_file_path = os.path.join(data_dir, 'content.json')
            if os.path.exists(content_file_path):
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                with open(content_file_path, 'rb') as f:
                    self.wfile.write(f.read())
                return
        super().do_GET()

    def end_headers(self):
        # Add CORS headers for local dev convenience
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == '__main__':
    # Ensure port is reusable
    socketserver.TCPServer.allow_reuse_address = True
    
    # Run the server
    with socketserver.TCPServer(("", PORT), AdminHandler) as httpd:
        print(f"[Server] Ryan Waymire website serving at http://localhost:{PORT}")
        print(f"[Server] Admin dashboard available at http://localhost:{PORT}/admin.html")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Server] Shutting down.")
