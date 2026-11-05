from http.server import BaseHTTPRequestHandler
import json
import sys

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        data = {
            "status": "ok",
            "message": "Python on Vercel is ALIVE!",
            "python_version": sys.version
        }
        self.wfile.write(json.dumps(data).encode('utf-8'))
