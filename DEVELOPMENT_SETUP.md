# Local Development Setup Guide
## Platform Engineering - Optimized Django Development Environment

This guide provides a comprehensive local development setup with platform engineering best practices for the Sabor Con Flow Dance project.

## 🚀 Quick Start

```bash
# 1. Activate virtual environment (already created)
source venv/bin/activate

# 2. Quick setup and run (using Make)
make dev

# OR manual setup
python dev.py
```

## 📋 Environment Configuration

### Development Environment (.env)
The `.env` file is pre-configured for optimal local development:

- **Django Debug Mode**: Enabled for development
- **Database**: Local SQLite (`db_dev.sqlite3`)
- **Email Backend**: Console output (no SMTP needed)
- **Caching**: Disabled for faster development
- **Static Files**: Local serving with hot reload
- **Security**: Relaxed settings for localhost

### Environment Variables Overview
```bash
DJANGO_DEBUG=True                    # Enable debug mode
ENVIRONMENT=local                    # Development environment
DJANGO_LOG_LEVEL=DEBUG              # Verbose logging
DEBUG_SQL_QUERIES=True              # Log SQL queries
ENABLE_DEBUG_TOOLBAR=True           # Django Debug Toolbar
```

## 🛠️ Development Tools

### 1. Development Server Script (`dev.py`)
Optimized development server with enhanced features:
```bash
python dev.py                       # Full development server
python dev.py --setup-only          # Database and static files setup only
python dev.py --check              # Run Django system checks
python dev.py --urls               # Show available URLs
```

**Features:**
- Automatic database setup and migrations
- Superuser creation (admin/admin123)
- Static file collection
- Colored logging output
- Health checks
- URL overview

### 2. Makefile Commands
Comprehensive development workflow automation:

```bash
# Setup and Installation
make help                           # Show all available commands
make setup                          # Full development setup
make install-dev                    # Install development dependencies

# Development Server
make run                           # Start optimized development server
make run-simple                    # Basic Django runserver

# Database Management
make migrate                       # Run migrations
make makemigrations               # Create new migrations
make reset-db                     # Reset development database

# Testing and Quality
make test                         # Run tests
make test-coverage               # Run tests with coverage
make check                       # Django system checks
make lint                        # Code linting
make format                      # Code formatting

# Maintenance
make clean                       # Clean temporary files
make reset                       # Complete environment reset
```

### 3. Development Settings (`settings_dev.py`)
Specialized Django settings for development:

- **Database**: Separate development SQLite database
- **Logging**: Enhanced colored console output
- **Middleware**: Reduced stack for faster development
- **Templates**: Hot reload enabled
- **Static Files**: Direct serving without compression
- **Debug Features**: Query count logging, performance monitoring

## 🗄️ Database Configuration

### Development Database
- **File**: `db_dev.sqlite3` (separate from production)
- **Configuration**: Optimized for development with WAL mode
- **Migrations**: Auto-applied on first run
- **Superuser**: Automatically created (admin/admin123)

### Database Management
```bash
make migrate                      # Apply migrations
make makemigrations              # Create new migrations
make dbshell                     # Open database shell
make reset-db                    # Reset database (clean slate)
```

## 📁 Static Files and Assets

### Development Static Files
- **Source**: `static/` directory
- **Collected**: `staticfiles/` directory
- **Serving**: Django development server (no CDN)
- **Hot Reload**: Enabled for CSS/JS changes

### Asset Pipeline
```bash
make collectstatic               # Collect all static files
npm run build                    # Build JavaScript/CSS (if configured)
```

## 🔧 Development Features

### 1. Debug Information
- **SQL Query Logging**: All database queries logged
- **Performance Monitoring**: Request timing and database performance
- **Error Details**: Full stack traces and context
- **Template Debug**: Template rendering information

### 2. Hot Reload
- **Templates**: Automatic reload on changes
- **Static Files**: Live CSS/JS updates
- **Python Code**: Auto-restart on model/view changes

### 3. Developer Tools Integration
- **Django Debug Toolbar**: Install with `pip install django-debug-toolbar`
- **iPython Shell**: Enhanced Django shell
- **Rich Output**: Colored terminal output

## 🧪 Testing and Quality

### Running Tests
```bash
make test                        # Standard test run
make test-fast                   # Parallel test execution
make test-coverage              # Coverage reporting
```

### Code Quality
```bash
make format                      # Auto-format with Black + isort
make lint                       # Flake8 linting
make check                      # Django system checks
make quality                    # All quality checks
```

## 🔍 Monitoring and Debugging

### Available URLs (Development Server Running)
```
Home Page:           http://127.0.0.1:8000/
Admin Panel:         http://127.0.0.1:8000/admin/
Health Check:        http://127.0.0.1:8000/health/
Monitoring:          http://127.0.0.1:8000/admin/monitoring/
DB Performance:      http://127.0.0.1:8000/admin/db-performance/
```

### Logging
- **Console**: Colored development logs
- **File**: `django_dev.log` for persistent logging
- **SQL Queries**: Logged when `DEBUG_SQL_QUERIES=True`

### Health Monitoring
```bash
make health                      # Check server health
make monitor                     # Show monitoring URLs
make logs                       # Tail log files
```

## 🚀 Performance Optimization

### Development Optimizations
- **Dummy Cache**: No caching overhead during development
- **No Compression**: Faster static file serving
- **Separate Database**: No production data conflicts
- **Reduced Middleware**: Minimal processing overhead

### Performance Monitoring
- Database query analysis with threshold alerts
- Response time monitoring
- Memory usage tracking
- Slow query identification

## 🔐 Security Configuration

### Development Security Settings
- **DEBUG Mode**: Enabled (shows detailed error pages)
- **ALLOWED_HOSTS**: Localhost and 127.0.0.1
- **CSRF**: Relaxed for development
- **HTTPS**: Disabled for local development
- **Security Headers**: Minimal for development

## 📦 Dependency Management

### Production Dependencies
```bash
pip install -r requirements.txt
```

### Development Dependencies (Enhanced)
```bash
pip install -r requirements-dev.txt
```

**Development Tools Include:**
- `django-debug-toolbar`: SQL profiling
- `ipython`: Enhanced REPL
- `black`, `isort`: Code formatting
- `flake8`: Linting
- `pytest`: Advanced testing
- `coverage`: Test coverage

## 🔄 Development Workflow

### Daily Development Cycle
1. **Start Development**:
   ```bash
   source venv/bin/activate
   make run
   ```

2. **Make Changes**:
   - Edit code (auto-reload active)
   - Add/modify templates (hot reload)
   - Update static files (auto-served)

3. **Test Changes**:
   ```bash
   make test
   make check
   ```

4. **Database Changes**:
   ```bash
   make makemigrations
   make migrate
   ```

5. **Code Quality**:
   ```bash
   make format
   make lint
   ```

### Fresh Start (Reset Everything)
```bash
make reset                       # Clean database and setup
make fresh                       # Reset and run
```

## 🎯 Platform Engineering Features

### 1. Automated Setup
- One-command environment setup
- Automatic dependency installation
- Database initialization with sample data
- Static file optimization

### 2. Developer Experience
- Fast server startup (< 5 seconds)
- Hot reload for all file types
- Comprehensive error reporting
- Integrated debugging tools

### 3. Consistency
- Standardized development environment
- Consistent tool configuration
- Unified command interface (Makefile)
- Version-controlled configuration

### 4. Productivity Tools
- Pre-commit hooks for code quality
- Automated testing pipeline
- Performance monitoring
- Health checks and diagnostics

## 🆘 Troubleshooting

### Common Issues

1. **Server Won't Start**
   ```bash
   make check                   # Check for configuration issues
   python dev.py --check       # Detailed checks
   ```

2. **Database Issues**
   ```bash
   make reset-db               # Reset database
   python manage.py shell      # Debug in shell
   ```

3. **Static Files Not Loading**
   ```bash
   make collectstatic          # Recollect static files
   ```

4. **Import Errors**
   ```bash
   source venv/bin/activate    # Ensure venv is active
   make install-dev            # Reinstall dependencies
   ```

### Performance Issues
- Check `django_dev.log` for slow queries
- Monitor console output for timing information
- Use Django Debug Toolbar for detailed profiling

## 📞 Support and Resources

### Development Resources
- Django Documentation: https://docs.djangoproject.com/
- Platform Engineering Best Practices
- Local development optimizations
- Performance monitoring guides

### Quick Reference
```bash
make help                       # All available commands
python dev.py --help          # Development server options
make urls                      # Show all URLs
```

---

**Happy Coding! 🎉**

This development setup is optimized for productivity, performance, and developer experience. All tools and configurations follow platform engineering best practices for Django development.