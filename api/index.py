import os
import sys
from http.server import BaseHTTPRequestHandler

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Django and configure it
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sabor_con_flow.settings')

import django
django.setup()

from django.core.handlers.wsgi import WSGIHandler
from io import BytesIO

# Create the WSGI application
application = WSGIHandler()


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle_request()
    
    def do_POST(self):
        self._handle_request()
    
    def do_PUT(self):
        self._handle_request()
    
    def do_DELETE(self):
        self._handle_request()
    
    def do_HEAD(self):
        self._handle_request()
    
    def do_OPTIONS(self):
        self._handle_request()
    
    def _handle_request(self):
        # Parse the URL
        from urllib.parse import urlparse
        parsed_path = urlparse(self.path)
        
        # Get content length for POST requests
        content_length = int(self.headers.get('Content-Length', 0))
        
        # Create WSGI environ
        environ = {
            'REQUEST_METHOD': self.command,
            'SCRIPT_NAME': '',
            'PATH_INFO': parsed_path.path,
            'QUERY_STRING': parsed_path.query or '',
            'CONTENT_TYPE': self.headers.get('Content-Type', ''),
            'CONTENT_LENGTH': str(content_length),
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '80',
            'SERVER_PROTOCOL': self.request_version,
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https' if self.headers.get('X-Forwarded-Proto') == 'https' else 'http',
            'wsgi.input': BytesIO(self.rfile.read(content_length) if content_length > 0 else b''),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False,
        }
        
        # Add HTTP headers to environ
        for key, value in self.headers.items():
            key = key.replace('-', '_').upper()
            if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                environ[f'HTTP_{key}'] = value
        
        # Call the Django application
        response_started = False
        response_headers = []
        
        def start_response(status, headers, exc_info=None):
            nonlocal response_started, response_headers
            if exc_info:
                try:
                    if response_started:
                        raise exc_info[1].with_traceback(exc_info[2])
                finally:
                    exc_info = None
            elif response_headers:
                raise RuntimeError("Response has already started")
            
            response_started = True
            response_headers = (status, headers)
            return BytesIO().write
        
        # Get the response from Django
        response = application(environ, start_response)
        
        # Send the response
        try:
            status, headers = response_headers
            self.send_response(int(status.split()[0]))
            for header, value in headers:
                self.send_header(header, value)
            self.end_headers()
            
            # Write the response body
            for data in response:
                self.wfile.write(data)
        finally:
            if hasattr(response, 'close'):
                response.close()