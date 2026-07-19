import http.server
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5173

class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        '.js': 'application/javascript',
        '.css': 'text/css',
    }

with http.server.ThreadingHTTPServer(("", PORT), Handler) as httpd:
    httpd.allow_reuse_address = True
    print(f"Dev server: http://localhost:{PORT}")
    print(f"Serving from: {os.getcwd()}")
    httpd.serve_forever()
