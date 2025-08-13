#!/usr/bin/env python3
"""
Development Server Manager - Platform Engineering Tool
Optimized Django development server with hot reload and debugging features
"""

import os
import sys
import subprocess
import signal
import time
import threading
from pathlib import Path

# Add the project directory to Python path
PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))

# Set Django settings module for development
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sabor_con_flow.settings_dev')

class DevelopmentServer:
    def __init__(self):
        self.server_process = None
        self.running = False
        
    def check_requirements(self):
        """Check if development requirements are met"""
        print("🔍 Checking development environment...")
        
        # Check if virtual environment is activated
        if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("⚠️  Warning: Virtual environment not detected. Recommend activating venv first.")
        else:
            print("✅ Virtual environment active")
            
        # Check Django installation
        try:
            import django
            print(f"✅ Django {django.get_version()} installed")
        except ImportError:
            print("❌ Django not installed. Run: pip install -r requirements.txt")
            return False
            
        # Check if .env file exists
        env_file = PROJECT_DIR / '.env'
        if env_file.exists():
            print("✅ Environment configuration found")
        else:
            print("⚠️  Warning: .env file not found. Using default settings.")
            
        return True
    
    def setup_database(self):
        """Set up development database with migrations"""
        print("\n📊 Setting up development database...")
        
        try:
            # Import Django and configure settings
            import django
            django.setup()
            
            from django.core.management import execute_from_command_line
            from django.db import connection
            
            # Check if database exists and has tables
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
            if not tables:
                print("🔨 Running initial migrations...")
                execute_from_command_line(['manage.py', 'migrate'])
                
                # Create superuser if none exists
                from django.contrib.auth.models import User
                if not User.objects.filter(is_superuser=True).exists():
                    print("👤 Creating development superuser...")
                    print("   Username: admin")
                    print("   Password: admin123")
                    print("   Email: admin@localhost")
                    User.objects.create_superuser('admin', 'admin@localhost', 'admin123')
                    print("✅ Development superuser created")
            else:
                print("✅ Database already configured")
                
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            return False
            
        return True
    
    def collect_static_files(self):
        """Collect static files for development"""
        print("\n📁 Collecting static files...")
        
        try:
            import django
            django.setup()
            
            from django.core.management import execute_from_command_line
            execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
            print("✅ Static files collected")
            
        except Exception as e:
            print(f"❌ Static file collection failed: {e}")
            return False
            
        return True
    
    def start_server(self, host='127.0.0.1', port='8000', auto_reload=True):
        """Start the Django development server"""
        print(f"\n🚀 Starting Django development server on {host}:{port}")
        
        # Prepare server command
        cmd = [
            sys.executable, 'manage.py', 'runserver', 
            f'{host}:{port}',
            '--settings=sabor_con_flow.settings_dev'
        ]
        
        if not auto_reload:
            cmd.append('--noreload')
            
        try:
            # Start the server process
            self.server_process = subprocess.Popen(
                cmd,
                cwd=PROJECT_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.running = True
            
            # Print server startup info
            print(f"""
🌟 Development Server Started Successfully!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 Server URL:     http://{host}:{port}/
🔧 Admin Panel:    http://{host}:{port}/admin/
👤 Admin Login:    admin / admin123
🗄️  Database:      db_dev.sqlite3
📧 Email Backend:  Console (check terminal)
🔄 Auto-reload:    {'Enabled' if auto_reload else 'Disabled'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Press Ctrl+C to stop the server
""")
            
            # Stream server output
            while self.running and self.server_process.poll() is None:
                line = self.server_process.stdout.readline()
                if line:
                    print(line.rstrip())
                    
        except KeyboardInterrupt:
            self.stop_server()
        except Exception as e:
            print(f"❌ Server failed to start: {e}")
            return False
            
        return True
    
    def stop_server(self):
        """Stop the development server"""
        if self.server_process:
            print("\n🛑 Stopping development server...")
            self.server_process.terminate()
            self.server_process.wait()
            self.running = False
            print("✅ Server stopped")
    
    def run_development_checks(self):
        """Run development-specific checks"""
        print("\n🔍 Running development checks...")
        
        try:
            import django
            django.setup()
            
            from django.core.management import execute_from_command_line
            execute_from_command_line(['manage.py', 'check', '--deploy'])
            print("✅ Development checks passed")
            
        except Exception as e:
            print(f"⚠️  Some checks failed: {e}")
    
    def show_urls(self):
        """Show available URLs for development"""
        print("\n🗺️  Available URLs:")
        
        urls = [
            ("Home Page", "/"),
            ("Admin Panel", "/admin/"),
            ("Contact Form", "/contact/"),
            ("Pricing", "/pricing/"),
            ("Private Lessons", "/private-lessons/"),
            ("Events", "/events/"),
            ("Health Check", "/health/"),
            ("Monitoring Dashboard", "/admin/monitoring/"),
            ("Database Performance", "/admin/db-performance/"),
        ]
        
        for name, path in urls:
            print(f"   {name:<20} http://127.0.0.1:8000{path}")

def main():
    """Main development server entry point"""
    server = DevelopmentServer()
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--setup-only':
            server.check_requirements()
            server.setup_database()
            server.collect_static_files()
            return
        elif sys.argv[1] == '--check':
            server.run_development_checks()
            return
        elif sys.argv[1] == '--urls':
            server.show_urls()
            return
        elif sys.argv[1] == '--help':
            print("""
Django Development Server Manager

Usage:
    python dev.py                 Start development server
    python dev.py --setup-only    Setup database and static files only
    python dev.py --check         Run development checks
    python dev.py --urls          Show available URLs
    python dev.py --help          Show this help

Environment Variables:
    DEV_HOST=127.0.0.1           Development server host
    DEV_PORT=8000                Development server port
    DEV_AUTO_RELOAD=true         Enable auto-reload
""")
            return
    
    # Get configuration from environment
    host = os.environ.get('DEV_HOST', '127.0.0.1')
    port = os.environ.get('DEV_PORT', '8000')
    auto_reload = os.environ.get('DEV_AUTO_RELOAD', 'true').lower() in ('true', '1', 't')
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        server.stop_server()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run development server
    if not server.check_requirements():
        sys.exit(1)
        
    if not server.setup_database():
        sys.exit(1)
        
    if not server.collect_static_files():
        sys.exit(1)
        
    server.show_urls()
    server.start_server(host, port, auto_reload)

if __name__ == '__main__':
    main()