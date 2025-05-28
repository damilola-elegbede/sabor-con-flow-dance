from http.server import BaseHTTPRequestHandler
from sabor_con_flow.wsgi import application
from asgiref.wsgi import WsgiToAsgi

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Convert WSGI app to ASGI
        asgi_app = WsgiToAsgi(application)
        
        # Handle the request
        response = asgi_app(self.environ, self.start_response)
        self.wfile.write(response)

handler = Handler 