import http.server
import socketserver

PORT = 8080  # Port for the HLS stream
DIRECTORY = "hls_output"  # Directory containing HLS files

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving HLS on http://localhost:{PORT}")
    httpd.serve_forever()
