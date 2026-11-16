

get ssh from network
‍‍‍```
python3 -u -c '
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

key = Path.home() / ".ssh/id_rsa.pub"
data = key.read_bytes()

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

HTTPServer(("0.0.0.0", 6200), H).serve_forever()
'

```