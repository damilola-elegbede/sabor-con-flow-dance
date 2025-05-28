from http.server import BaseHTTPRequestHandler
from sabor_con_flow.wsgi import application
import io
import sys
import traceback

class VercelHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Create a WSGI environment
            environ = {
                'REQUEST_METHOD': self.command,
                'SCRIPT_NAME': '',
                'PATH_INFO': self.path,
                'QUERY_STRING': '',
                'SERVER_NAME': self.server.server_name,
                'SERVER_PORT': str(self.server.server_port),
                'SERVER_PROTOCOL': self.protocol_version,
                'wsgi.version': (1, 0),
                'wsgi.url_scheme': 'http',
                'wsgi.input': io.BytesIO(),
                'wsgi.errors': sys.stderr,
                'wsgi.multithread': False,
                'wsgi.multiprocess': False,
                'wsgi.run_once': False,
            }

            # Add headers to environ
            for key, value in self.headers.items():
                key = 'HTTP_' + key.upper().replace('-', '_')
                environ[key] = value

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

# Vercel requires this exact variable name
handler = VercelHandler 