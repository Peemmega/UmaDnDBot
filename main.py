import http.server

class Maintenance(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(503)
        self.end_headers()
        self.wfile.write(b"Test service maintenance")
    def do_POST(self):
        self.do_GET()
    def do_PUT(self):
        self.do_GET()
    def do_DELETE(self):
        self.do_GET()

print("PROFILE_MIGRATION_MAINTENANCE", flush=True)
http.server.ThreadingHTTPServer(("0.0.0.0", 8000), Maintenance).serve_forever()
