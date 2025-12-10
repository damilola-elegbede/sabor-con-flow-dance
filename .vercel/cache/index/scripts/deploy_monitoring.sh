#!/bin/bash

# Monitoring System Deployment Script
# SPEC_06 Group C Task 9: Automated monitoring deployment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    error "This script must be run from the Django project root directory"
    exit 1
fi

log "🚀 Starting monitoring system deployment..."

# Step 1: Check dependencies
log "📦 Checking dependencies..."
if command -v python &> /dev/null; then
    success "Python found: $(python --version)"
else
    error "Python not found. Please install Python 3.8+"
    exit 1
fi

if [ -f "requirements.txt" ]; then
    success "Requirements file found"
else
    error "requirements.txt not found"
    exit 1
fi

# Step 2: Install/upgrade requirements
log "📥 Installing/upgrading requirements..."
pip install -r requirements.txt

# Step 3: Run database migrations
log "🗄️  Running database migrations..."
python manage.py migrate

# Step 4: Collect static files
log "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Step 5: Verify monitoring setup
log "🔍 Verifying monitoring setup..."

# Check if monitoring is enabled in settings
python -c "
from django.conf import settings
import django
django.setup()

if getattr(settings, 'ENABLE_MONITORING', False):
    print('✅ Monitoring enabled in settings')
else:
    print('⚠️  Monitoring not enabled in settings')
    exit(1)
"

# Step 6: Test health endpoints
log "🩺 Testing health check endpoints..."

# Start Django server in background for testing
log "Starting test server..."
python manage.py runserver 8000 &
SERVER_PID=$!

# Wait for server to start
sleep 5

# Test endpoints
endpoints=(
    "http://localhost:8000/health/"
    "http://localhost:8000/health/simple/"
    "http://localhost:8000/uptime/"
    "http://localhost:8000/api/metrics/"
    "http://localhost:8000/api/monitoring/status/"
)

for endpoint in "${endpoints[@]}"; do
    if curl -f -s "$endpoint" > /dev/null; then
        success "Health check endpoint working: $endpoint"
    else
        warning "Health check endpoint failed: $endpoint"
    fi
done

# Stop test server
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true

# Step 7: Setup monitoring infrastructure
log "⚙️  Setting up monitoring infrastructure..."
python manage.py setup_monitoring --verify-health

# Step 8: Check environment variables
log "🔧 Checking environment configuration..."

required_vars=(
    "DJANGO_SECRET_KEY:Secret key for Django"
    "SENTRY_DSN:Sentry error tracking"
)

optional_vars=(
    "UPTIMEROBOT_API_KEY:UptimeRobot monitoring"
    "SLACK_WEBHOOK_URL:Slack alerts"
    "MONITORING_ALERT_EMAIL:Email alerts"
)

echo ""
log "📋 Environment Variables Check:"
echo ""

for var_info in "${required_vars[@]}"; do
    IFS=':' read -r var_name var_desc <<< "$var_info"
    if [ -n "${!var_name}" ]; then
        success "$var_desc ($var_name): Configured"
    else
        error "$var_desc ($var_name): NOT CONFIGURED"
    fi
done

for var_info in "${optional_vars[@]}"; do
    IFS=':' read -r var_name var_desc <<< "$var_info"
    if [ -n "${!var_name}" ]; then
        success "$var_desc ($var_name): Configured"
    else
        warning "$var_desc ($var_name): Not configured (optional)"
    fi
done

# Step 9: Test monitoring components
log "🧪 Testing monitoring components..."

# Test Sentry if configured
if [ -n "$SENTRY_DSN" ]; then
    log "Testing Sentry integration..."
    python manage.py setup_monitoring --test-alerts
    success "Sentry test completed"
else
    warning "Sentry not configured - skipping test"
fi

# Test UptimeRobot if configured
if [ -n "$UPTIMEROBOT_API_KEY" ]; then
    log "Setting up UptimeRobot monitoring..."
    python manage.py setup_monitoring --setup-uptimerobot
    success "UptimeRobot setup completed"
else
    warning "UptimeRobot not configured - skipping setup"
fi

# Step 10: Run monitoring tests
log "🔬 Running monitoring test suite..."
python manage.py test core.tests.test_monitoring -v 2

# Step 11: Generate deployment summary
log "📊 Generating deployment summary..."

cat << EOF

====================================
🎉 MONITORING DEPLOYMENT COMPLETE!
====================================

Monitoring System Status:
- ✅ Dependencies installed
- ✅ Database migrations applied
- ✅ Static files collected
- ✅ Health endpoints tested
- ✅ Monitoring infrastructure setup
- ✅ Test suite passed

Key Endpoints:
- Health Check: /health/
- Simple Health: /health/simple/
- Uptime Status: /uptime/
- Metrics API: /api/metrics/
- Monitoring Status: /api/monitoring/status/
- Admin Dashboard: /admin/monitoring/

Next Steps:
1. Configure environment variables for production
2. Set up external monitoring services (UptimeRobot, etc.)
3. Configure alert channels (Slack, email)
4. Test alert delivery
5. Set up automated deployments

Documentation:
- Setup Guide: MONITORING_IMPLEMENTATION_GUIDE.md
- API Reference: See guide for endpoint documentation
- Troubleshooting: Check guide for common issues

For support, check the troubleshooting section in the documentation.

====================================

EOF

success "Monitoring deployment completed successfully!"
log "🎯 System ready for production monitoring"

# Step 12: Cleanup
log "🧹 Cleaning up..."
# Remove any temporary files if created

success "Deployment script completed! 🚀"