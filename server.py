#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEM Studios Invoice Generator — Web Server
Run this script, then open http://localhost:5678 in your browser.
"""

import http.server
import json
import os
import sys
import urllib.parse

# Add the directory so we can import generate_invoice
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from generate_invoice import generate_invoice


class InvoiceHandler(http.server.SimpleHTTPRequestHandler):
    """Handle both static files and the /generate API endpoint."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SCRIPT_DIR, **kwargs)
    
    def do_GET(self):
        if self.path == '/logo':
            self.serve_logo()
        elif self.path in ('/', '/index.html'):
            self.serve_index()
        else:
            self.send_error(404)
    
    def serve_index(self):
        index_path = os.path.join(SCRIPT_DIR, 'index.html')
        with open(index_path, 'rb') as f:
            content = f.read()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(content)
    
    def serve_logo(self):
        # Prefer local logo.png (portable), fallback to desktop reference
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.expanduser("~/Desktop/invoice 参考/Logo NEM_Tranparent.png")
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_error(404, "Logo not found")
    
    def do_POST(self):
        if self.path == '/generate':
            self.handle_generate()
        else:
            self.send_error(404)
    
    def handle_generate(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            # Validate required fields
            required = ['client_name', 'date', 'amount', 'item_description']
            for field in required:
                if not data.get(field).strip():
                    raise ValueError(f"Missing required field: {field}")
            
            out_path, inv_num = generate_invoice(data)
            
            response = {
                'success': True,
                'path': out_path,
                'inv_num': inv_num,
                'filename': os.path.basename(out_path)
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"Error generating invoice: {e}", file=sys.stderr)
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
    
    def log_message(self, format, *args):
        # Clean up console output
        sys.stdout.write(f"\n  [Server] {args[0]}\n")
        sys.stdout.flush()


def main():
    PORT = 5678
    
    # Find an available port if default is taken
    server = None
    for port in range(PORT, PORT + 20):
        try:
            server = http.server.HTTPServer(('127.0.0.1', port), InvoiceHandler)
            actual_port = port
            break
        except OSError:
            continue
    
    if not server:
        print("❌ Could not find an available port.")
        return
    
    url = f"http://localhost:{actual_port}"
    
    print(f"""
╔══════════════════════════════════════════════╗
║     🎵 NEM Studios Invoice Generator         ║
╠══════════════════════════════════════════════╣
║                                              ║
║   Open in browser:                           ║
║   {url:<42} ║
║                                              ║
║   Press Ctrl+C to stop                       ║
╚══════════════════════════════════════════════╝
""")
    
    # Auto-open browser
    import webbrowser
    webbrowser.open(url)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped.")
        server.server_close()


if __name__ == '__main__':
    main()
