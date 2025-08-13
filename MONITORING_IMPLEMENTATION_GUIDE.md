# Comprehensive Monitoring and Alerting System
## SPEC_06 Group C Task 9 - Implementation Guide

This document provides a complete guide for the monitoring and alerting system implemented for Sabor Con Flow Dance website.

## 🎯 Overview

Our monitoring system provides:
- **Real-time health checks** for all system components
- **Performance monitoring** with custom metrics and thresholds
- **Error tracking** through Sentry integration
- **Uptime monitoring** via UptimeRobot
- **Intelligent alerting** across multiple channels
- **Comprehensive dashboard** for administrators
- **Proactive incident response** capabilities

## 📊 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Application   │    │    Monitoring   │    │   External      │
│   Middleware    │───▶│   Collectors    │───▶│   Services      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Health Checks  │    │   Metrics API   │    │   UptimeRobot   │
│   Endpoints     │    │   Dashboard     │    │     Sentry      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Required for basic monitoring
ENABLE_MONITORING=True
SENTRY_DSN=your-sentry-dsn

# Optional for enhanced monitoring
UPTIMEROBOT_API_KEY=your-api-key
SLACK_WEBHOOK_URL=your-webhook-url
MONITORING_ALERT_EMAIL=alerts@yourdomain.com
```

### 3. Run Setup Command

```bash
python manage.py setup_monitoring --setup-all
```

### 4. Verify Installation

Visit your monitoring dashboard:
- **Admin Dashboard**: `/admin/monitoring/`
- **Health Check**: `/health/`
- **Metrics API**: `/api/metrics/`

## 🔧 Configuration

### Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `SENTRY_DSN` | Error tracking | `https://...@sentry.io/...` |
| `UPTIMEROBOT_API_KEY` | Uptime monitoring | `u123456-abc...` |
| `SLACK_WEBHOOK_URL` | Slack alerts | `https://hooks.slack.com/...` |
| `MONITORING_ALERT_EMAIL` | Email alerts | `alerts@domain.com` |
| `PERF_RESPONSE_TIME_WARNING` | Response time threshold | `1000` (ms) |
| `PERF_ERROR_RATE_WARNING` | Error rate threshold | `5.0` (%) |

### Performance Thresholds

Configure monitoring thresholds in your environment:

```bash
# Response Time Thresholds (milliseconds)
PERF_RESPONSE_TIME_WARNING=1000
PERF_RESPONSE_TIME_CRITICAL=3000

# Error Rate Thresholds (percentage)
PERF_ERROR_RATE_WARNING=5.0
PERF_ERROR_RATE_CRITICAL=10.0

# System Resource Thresholds (percentage)
PERF_CPU_WARNING=80
PERF_MEMORY_WARNING=85
PERF_DISK_WARNING=90
```

## 📡 Health Check Endpoints

### Primary Health Check
- **URL**: `/health/`
- **Purpose**: Comprehensive system health
- **Response**: Detailed JSON with all component status
- **Use Case**: Monitoring dashboards, detailed diagnostics

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "response_time_ms": 45.23,
  "checks": {
    "database": {"healthy": true, "response_time_ms": 12.34},
    "cache": {"healthy": true, "response_time_ms": 2.1},
    "external_apis": {"healthy": true, "apis": {...}},
    "system_resources": {"healthy": true, "cpu": {...}}
  }
}
```

### Simple Health Check
- **URL**: `/health/simple/`
- **Purpose**: Fast uptime check
- **Response**: Minimal JSON
- **Use Case**: Load balancers, quick status checks

```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Uptime Status
- **URL**: `/uptime/`
- **Purpose**: UptimeRobot integration
- **Response**: Optimized for external monitoring
- **Cache**: 1-minute TTL

## 📊 Metrics and Performance

### Metrics Endpoint
- **URL**: `/api/metrics/`
- **Purpose**: Performance metrics collection
- **Authentication**: None (public endpoint)

Available metrics:
- Request counts and error rates
- Response time statistics
- System resource usage
- Database performance
- Cache hit/miss rates
- External API status

### Performance Dashboard
- **URL**: `/api/monitoring/status/`
- **Purpose**: High-level status overview
- **Response**: Key performance indicators

## 🎛️ Admin Dashboard

### Access
- **URL**: `/admin/monitoring/`
- **Authentication**: Staff/superuser required
- **Features**: Real-time monitoring, alert management

### Dashboard Features

1. **System Health Overview**
   - Overall health status
   - Response time trends
   - Error rate monitoring

2. **Component Status**
   - Database connectivity
   - Cache performance
   - External API health
   - System resources

3. **Alert Management**
   - Recent alerts display
   - Alert configuration status
   - Test alert functionality

4. **Performance Metrics**
   - Request statistics
   - Response time analytics
   - Resource utilization

### Dashboard Actions

- **Refresh**: Update all metrics
- **Test Alerts**: Send test notifications
- **Clear Cache**: Reset monitoring data
- **Export Metrics**: Download performance data

## 🚨 Alert System

### Alert Channels

1. **Sentry Integration**
   - Error and performance alerts
   - Stack trace capture
   - Release tracking

2. **Email Notifications**
   - Critical alerts
   - Daily/weekly summaries
   - Configuration: `ALERT_CHANNELS['email']`

3. **Slack Integration**
   - Real-time alerts
   - Team notifications
   - Channel: configurable

### Alert Types

| Alert Type | Severity | Trigger |
|------------|----------|---------|
| `response_time_critical` | Critical | >3000ms |
| `response_time_warning` | Warning | >1000ms |
| `error_rate_critical` | Critical | >10% |
| `error_rate_warning` | Warning | >5% |
| `cpu_high` | Warning | >80% |
| `memory_high` | Warning | >85% |
| `disk_high` | Critical | >90% |
| `health_check_failed` | Critical | Service down |

### Alert Cooldown

- **Purpose**: Prevent alert spam
- **Duration**: 5 minutes (configurable)
- **Logic**: Same alert type won't trigger again within cooldown period

## 🔍 Monitoring Components

### 1. Health Check Manager
- **Purpose**: Comprehensive system health assessment
- **Components**: Database, cache, APIs, resources, application
- **Location**: `core/monitoring.py`

### 2. Performance Monitor
- **Purpose**: Real-time performance metrics collection
- **Metrics**: Response times, resource usage, application stats
- **Cache**: 5-minute TTL

### 3. Alert Manager
- **Purpose**: Intelligent alert routing and management
- **Features**: Threshold checking, cooldown periods, multi-channel delivery
- **History**: Last 100 alerts retained

### 4. Monitoring Middleware
- **Purpose**: Request/response tracking
- **Features**: Automatic instrumentation, error tracking, performance profiling
- **Location**: `core/middleware/monitoring.py`

## 📈 UptimeRobot Integration

### Setup
1. Create UptimeRobot account
2. Get API key from dashboard
3. Configure `UPTIMEROBOT_API_KEY`
4. Run setup command:

```bash
python manage.py setup_monitoring --setup-uptimerobot
```

### Monitor Configuration
- **Type**: HTTP(S)
- **URL**: `/health/` endpoint
- **Interval**: 5 minutes
- **Timeout**: 30 seconds
- **Method**: GET

### Automatic Setup
The setup command will:
- Check for existing monitors
- Create new monitor if needed
- Update existing monitor configuration
- Verify monitor status

## 🛠️ Management Commands

### Setup Monitoring
```bash
# Complete setup
python manage.py setup_monitoring --setup-all

# Individual components
python manage.py setup_monitoring --setup-uptimerobot
python manage.py setup_monitoring --test-alerts
python manage.py setup_monitoring --verify-health
```

### Verify Health
```bash
# Test all health endpoints
python manage.py setup_monitoring --verify-health
```

### Test Alerts
```bash
# Send test alerts through all channels
python manage.py setup_monitoring --test-alerts
```

## 🔧 Troubleshooting

### Common Issues

1. **Health Check Fails**
   ```bash
   # Check database connection
   python manage.py dbshell
   
   # Verify cache
   python manage.py shell -c "from django.core.cache import cache; print(cache.get('test'))"
   ```

2. **Sentry Not Working**
   ```bash
   # Verify DSN
   python manage.py shell -c "from django.conf import settings; print(settings.SENTRY_DSN)"
   
   # Test Sentry
   python manage.py setup_monitoring --test-alerts
   ```

3. **UptimeRobot Setup Fails**
   ```bash
   # Check API key
   curl -X POST https://api.uptimerobot.com/v2/getMonitors \
        -d "api_key=YOUR_API_KEY&format=json"
   ```

4. **High Memory Usage**
   ```bash
   # Clear monitoring cache
   python manage.py shell -c "from django.core.cache import cache; cache.clear()"
   ```

### Debug Mode

Enable debug logging:
```python
LOGGING = {
    'loggers': {
        'core.monitoring': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}
```

### Performance Optimization

1. **Cache Health Checks**
   - Health checks cached for 60 seconds
   - Configure via `HEALTH_CHECK_CACHE_TTL`

2. **Middleware Optimization**
   - Monitoring can be disabled: `ENABLE_MONITORING=False`
   - Request sampling available

3. **Database Optimization**
   - Use connection pooling
   - Monitor slow queries

## 📊 Metrics Reference

### System Metrics
- `cpu_usage_percent`: CPU utilization
- `memory_usage_percent`: Memory utilization
- `disk_usage_percent`: Disk utilization
- `load_average`: System load (1m, 5m, 15m)

### Application Metrics
- `total_requests`: Total request count
- `total_errors`: Total error count
- `error_rate`: Error percentage
- `successful_responses`: 2xx responses
- `client_errors`: 4xx responses
- `server_errors`: 5xx responses

### Performance Metrics
- `response_time_ms`: Response time in milliseconds
- `database_query_time_ms`: Database query time
- `cache_operation_time_ms`: Cache operation time
- `external_api_response_time_ms`: External API response time

### Database Metrics
- `connection_status`: Database connectivity
- `query_count`: Number of queries
- `slow_queries`: Queries exceeding threshold
- `connection_pool_size`: Pool utilization

## 🔐 Security Considerations

### Data Privacy
- No PII in monitoring data
- Sanitized error messages
- Secure transmission only

### Access Control
- Admin dashboard requires authentication
- API endpoints have rate limiting
- Sensitive metrics protected

### Compliance
- GDPR compliant data handling
- Configurable data retention
- Audit trail for configuration changes

## 🚀 Production Deployment

### Vercel Configuration
```json
{
  "env": {
    "SENTRY_DSN": "@sentry-dsn",
    "UPTIMEROBOT_API_KEY": "@uptimerobot-key",
    "MONITORING_ALERT_EMAIL": "@alert-email"
  }
}
```

### Environment Setup
1. Set all required environment variables
2. Configure alert channels
3. Set up UptimeRobot monitoring
4. Test all endpoints
5. Verify alert delivery

### Post-Deployment Checklist
- [ ] Health checks responding correctly
- [ ] Sentry receiving error reports
- [ ] UptimeRobot monitor active
- [ ] Alert channels configured
- [ ] Dashboard accessible
- [ ] Performance metrics collecting
- [ ] Test alerts working

## 📚 API Reference

### Health Check API

#### GET /health/
Returns comprehensive health status
```json
{
  "status": "healthy|degraded|unhealthy",
  "timestamp": "ISO 8601",
  "response_time_ms": 45.23,
  "checks": {
    "database": {...},
    "cache": {...},
    "external_apis": {...},
    "system_resources": {...},
    "application": {...}
  }
}
```

#### GET /health/simple/
Returns basic health status
```json
{
  "status": "ok|error",
  "timestamp": "ISO 8601"
}
```

#### GET /uptime/
Optimized for UptimeRobot
```json
{
  "status": "ok|error",
  "response_time_ms": 12.34,
  "timestamp": "ISO 8601"
}
```

### Metrics API

#### GET /api/metrics/
Returns performance metrics
```json
{
  "timestamp": "ISO 8601",
  "application": {...},
  "database": {...},
  "cache": {...},
  "system": {...},
  "counters": {...},
  "response_time_stats": {...}
}
```

#### GET /api/monitoring/status/
Returns monitoring status
```json
{
  "status": "healthy|degraded|unhealthy",
  "monitoring_enabled": true,
  "error_rate": 2.5,
  "average_response_time_ms": 123.45,
  "total_requests": 1000,
  "total_errors": 25
}
```

### Admin API

#### POST /admin/monitoring/clear-cache/
Clear monitoring cache (requires authentication)
```json
{
  "success": true,
  "message": "Cache cleared successfully"
}
```

#### POST /admin/monitoring/test-alerts/
Send test alerts (requires authentication)
```json
{
  "success": true,
  "message": "Test alerts sent",
  "alert_channels": {...}
}
```

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs: `django.log`
3. Test individual components
4. Contact development team

## 📝 Changelog

### v1.0.0 (Current)
- Initial monitoring system implementation
- Sentry integration
- UptimeRobot setup
- Admin dashboard
- Comprehensive health checks
- Multi-channel alerting

### Future Enhancements
- Grafana dashboard integration
- Advanced analytics
- Machine learning anomaly detection
- Custom metric collectors
- API rate limiting monitoring