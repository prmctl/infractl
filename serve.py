from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path

site = Path(__file__).resolve().parent / "site"
handler = partial(SimpleHTTPRequestHandler, directory=str(site))
server = ThreadingHTTPServer(("0.0.0.0", 8000), handler)

print("infractl: http://localhost:8000")
print("serving:", site)

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nbye")
