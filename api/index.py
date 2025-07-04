from http.server import BaseHTTPRequestHandler
from sabor_con_flow.wsgi import application
import io
import sys
import traceback
from urllib.parse import urlparse, parse_qs

class VercelHandler(BaseHTTPRequestHandler):
    def handle_request(self):
        try:
            # Parse URL to get path and query string
            parsed_url = urlparse(self.path)
            path_info = parsed_url.path
            query_string = parsed_url.query or ''
            
            # Get content length for POST requests
            content_length = int(self.headers.get('Content-Length', 0))
            
            # Create a WSGI environment
            environ = {
                'REQUEST_METHOD': self.command,
                'SCRIPT_NAME': '',
                'PATH_INFO': path_info,
                'QUERY_STRING': query_string,
                'SERVER_NAME': self.server.server_name,
                'SERVER_PORT': str(self.server.server_port),
                'SERVER_PROTOCOL': self.protocol_version,
                'CONTENT_LENGTH': str(content_length),
                'wsgi.version': (1, 0),
                'wsgi.url_scheme': 'https' if self.headers.get('X-Forwarded-Proto') == 'https' else 'http',
                'wsgi.input': io.BytesIO(self.rfile.read(content_length) if content_length > 0 else b''),
                'wsgi.errors': sys.stderr,
                'wsgi.multithread': False,
                'wsgi.multiprocess': False,
                'wsgi.run_once': False,
            }

            # Add headers to environ
            for key, value in self.headers.items():
                key = key.upper().replace('-', '_')
                if key == 'CONTENT_TYPE':
                    environ['CONTENT_TYPE'] = value
                elif key == 'CONTENT_LENGTH':
                    environ['CONTENT_LENGTH'] = value
                else:
                    environ['HTTP_' + key] = value

            # Create a response buffer
            response_buffer = io.BytesIO()
            
            def start_response(status, headers, exc_info=None):
                self.send_response(int(status.split()[0]))
                for header, value in headers:
                    self.send_header(header, value)
                self.end_headers()
                return response_buffer.write

            # Call the WSGI application
            response = application(environ, start_response)
            
            # Write the response
            for chunk in response:
                self.wfile.write(chunk)
            
            # Close the response
            if hasattr(response, 'close'):
                response.close()

        except Exception as e:
            # Log the error
            error_msg = f"Error handling request: {str(e)}\n{traceback.format_exc()}"
            print(error_msg, file=sys.stderr)
            
            # Send error response
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Internal Server Error")
    
    def do_GET(self):
        self.handle_request()
    
    def do_POST(self):
        self.handle_request()
    
    def do_PUT(self):
        self.handle_request()
    
    def do_DELETE(self):
        self.handle_request()
    
    def do_HEAD(self):
        self.handle_request()
    
    def do_OPTIONS(self):
        self.handle_request()

# Vercel requires this exact variable name
handler = VercelHandler 