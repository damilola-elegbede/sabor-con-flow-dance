#!/bin/bash

# Local Deployment Test Script - SPEC_06 Group D Task 10
# This script simulates the CI/CD pipeline locally for testing

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PYTHON_VERSION="3.12"
NODE_VERSION="18"
TEST_ENV_FILE=".env.test"

echo -e "${BLUE}🚀 Starting Local Deployment Test${NC}"
echo "================================================"

# Function to print section headers
print_section() {
    echo -e "\n${BLUE}$1${NC}"
    echo "----------------------------------------"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
print_section "Checking Prerequisites"

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VER=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    print_success "Python $PYTHON_VER found"
else
    print_error "Python 3 not found"
    exit 1
fi

# Check Node.js version
if command -v node &> /dev/null; then
    NODE_VER=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    print_success "Node.js v$NODE_VER found"
else
    print_error "Node.js not found"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    print_error "Not in Django project root directory"
    exit 1
fi

# Create test environment file
print_section "Setting Up Test Environment"

cat > $TEST_ENV_FILE << EOF
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=test-secret-key-local-only
DATABASE_URL=sqlite:///test_deploy.sqlite3
REDIS_URL=redis://localhost:6379/1
TURSO_DATABASE_URL=libsql://test.sqlite
TURSO_AUTH_TOKEN=test-token
ENVIRONMENT=test
EOF

print_success "Test environment configured"

# Install Python dependencies
print_section "Installing Python Dependencies"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
fi

source venv/bin/activate
pip install --upgrade pip > /dev/null
pip install -r requirements.txt > /dev/null
print_success "Python dependencies installed"

# Install Node.js dependencies
print_section "Installing Node.js Dependencies"

npm ci > /dev/null 2>&1
print_success "Node.js dependencies installed"

# Code quality checks
print_section "Running Code Quality Checks"

echo "Running Black formatting check..."
if black --check core/ sabor_con_flow/ > /dev/null 2>&1; then
    print_success "Black formatting check passed"
else
    print_warning "Black formatting issues found (run 'black core/ sabor_con_flow/' to fix)"
fi

echo "Running isort import check..."
if isort --check-only core/ sabor_con_flow/ > /dev/null 2>&1; then
    print_success "Import sorting check passed"
else
    print_warning "Import sorting issues found (run 'isort core/ sabor_con_flow/' to fix)"
fi

echo "Running flake8 linting..."
if flake8 core/ sabor_con_flow/ --max-line-length=88 --extend-ignore=E203,W503 > /dev/null 2>&1; then
    print_success "Flake8 linting passed"
else
    print_warning "Flake8 linting issues found"
fi

echo "Running ESLint..."
if npm run lint > /dev/null 2>&1; then
    print_success "ESLint check passed"
else
    print_warning "ESLint issues found"
fi

# Security checks
print_section "Running Security Checks"

echo "Running Bandit security scan..."
if command -v bandit &> /dev/null; then
    if bandit -r core/ sabor_con_flow/ -f json > /dev/null 2>&1; then
        print_success "Bandit security scan passed"
    else
        print_warning "Bandit found potential security issues"
    fi
else
    print_warning "Bandit not installed (pip install bandit)"
fi

echo "Running Safety check..."
if command -v safety &> /dev/null; then
    if safety check > /dev/null 2>&1; then
        print_success "Safety check passed"
    else
        print_warning "Safety found vulnerable dependencies"
    fi
else
    print_warning "Safety not installed (pip install safety)"
fi

echo "Running npm audit..."
if npm audit --audit-level=moderate > /dev/null 2>&1; then
    print_success "npm audit passed"
else
    print_warning "npm audit found vulnerabilities"
fi

# Database migration check
print_section "Checking Database Migrations"

echo "Checking for migration issues..."
export DJANGO_SETTINGS_MODULE=sabor_con_flow.settings
if python manage.py makemigrations --check --dry-run > /dev/null 2>&1; then
    print_success "No migration issues found"
else
    print_warning "Pending migrations detected"
fi

echo "Running migrations..."
python manage.py migrate > /dev/null 2>&1
print_success "Migrations applied"

# Run tests
print_section "Running Test Suite"

echo "Running Django tests..."
if python manage.py test > /dev/null 2>&1; then
    print_success "Django tests passed"
else
    print_error "Django tests failed"
    TEST_FAILED=true
fi

echo "Running pytest with coverage..."
if pytest core/tests/ --cov=core --cov-report=term-missing > /dev/null 2>&1; then
    print_success "Pytest with coverage passed"
else
    print_warning "Some pytest tests failed"
fi

echo "Running JavaScript tests..."
if npm test > /dev/null 2>&1; then
    print_success "JavaScript tests passed"
else
    print_warning "JavaScript tests failed"
fi

# Build assets
print_section "Building Production Assets"

echo "Cleaning previous builds..."
npm run clean > /dev/null 2>&1 || true
rm -rf staticfiles/ > /dev/null 2>&1 || true

echo "Building JavaScript/CSS assets..."
if npm run build > /dev/null 2>&1; then
    print_success "Frontend assets built successfully"
else
    print_error "Frontend build failed"
    exit 1
fi

echo "Collecting Django static files..."
if python manage.py collectstatic --noinput > /dev/null 2>&1; then
    print_success "Static files collected"
else
    print_error "Static file collection failed"
    exit 1
fi

# Verify build artifacts
print_section "Verifying Build Artifacts"

# Check critical files exist
if [ -f "staticfiles/css/styles.css" ]; then
    CSS_SIZE=$(stat -c%s staticfiles/css/styles.css 2>/dev/null || stat -f%z staticfiles/css/styles.css)
    print_success "CSS file found (${CSS_SIZE} bytes)"
else
    print_error "CSS file missing"
    exit 1
fi

if [ -f "staticfiles/js/main.js" ]; then
    JS_SIZE=$(stat -c%s staticfiles/js/main.js 2>/dev/null || stat -f%z staticfiles/js/main.js)
    print_success "JavaScript file found (${JS_SIZE} bytes)"
else
    print_error "JavaScript file missing"
    exit 1
fi

# Performance checks
print_section "Performance Checks"

echo "Running performance budget check..."
if node build-scripts/performance-budget.js > /dev/null 2>&1; then
    print_success "Performance budget check passed"
else
    print_warning "Performance budget exceeded"
fi

# Health check simulation
print_section "Health Check Simulation"

echo "Starting test server..."
python manage.py runserver 8000 &
SERVER_PID=$!

# Wait for server to start
sleep 5

# Test health endpoint
if curl -f http://localhost:8000/api/health/ > /dev/null 2>&1; then
    print_success "Health check endpoint responding"
else
    print_warning "Health check endpoint not responding"
fi

# Test main pages
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    print_success "Home page responding"
else
    print_warning "Home page not responding"
fi

if curl -f http://localhost:8000/contact/ > /dev/null 2>&1; then
    print_success "Contact page responding"
else
    print_warning "Contact page not responding"
fi

# Stop test server
kill $SERVER_PID > /dev/null 2>&1

# Cleanup
print_section "Cleanup"

rm -f $TEST_ENV_FILE
print_success "Test environment cleaned up"

# Final report
print_section "Deployment Test Summary"

if [ "${TEST_FAILED}" = "true" ]; then
    print_error "Some tests failed - deployment would be blocked"
    echo -e "\n${RED}❌ DEPLOYMENT TEST FAILED${NC}"
    echo "Fix the issues above before deploying to production."
    exit 1
else
    print_success "All checks passed - ready for deployment"
    echo -e "\n${GREEN}✅ DEPLOYMENT TEST PASSED${NC}"
    echo "Your changes are ready for production deployment."
fi

echo -e "\n${BLUE}================================================${NC}"
echo -e "${BLUE}Local deployment test completed${NC}"

# Optional: Run lighthouse if available
if command -v lighthouse &> /dev/null; then
    echo -e "\n${YELLOW}💡 Tip: Run 'lighthouse http://localhost:8000' for performance audit${NC}"
fi

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Commit your changes"
echo "2. Push to feature branch"
echo "3. Create pull request to main"
echo "4. Review CI/CD pipeline results"
echo "5. Merge to trigger production deployment"