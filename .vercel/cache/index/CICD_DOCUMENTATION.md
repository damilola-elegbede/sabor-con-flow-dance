# CI/CD Pipeline Documentation

## Overview

This document describes the comprehensive CI/CD pipeline implementation for the Sabor Con Flow Dance website, designed to ensure reliable, automated deployments with zero downtime and robust quality gates.

## Pipeline Architecture

### Workflow Components

1. **Test Workflow** (`.github/workflows/test.yml`)
   - Runs on pull requests and feature branches
   - Comprehensive quality gates and testing
   - Multi-matrix testing approach

2. **CI/CD Pipeline** (`.github/workflows/ci.yml`)
   - Main integration and deployment workflow
   - Handles production deployments
   - Includes rollback mechanisms

3. **Production Deployment** (`.github/workflows/deploy.yml`)
   - Dedicated production deployment workflow
   - Database migration handling
   - Health checks and verification

## Workflow Triggers

### Test Workflow
- **Pull Requests**: `main`, `develop` branches
- **Push Events**: `feature/*`, `develop` branches
- **Draft PRs**: Automatically skipped

### CI/CD Pipeline
- **Push to Main**: Full deployment pipeline
- **Pull Requests**: Test and quality checks only
- **Manual Trigger**: Emergency deployments

### Production Deployment
- **Workflow Completion**: Triggered after successful CI
- **Manual Dispatch**: Force deployments with options
- **Failure Recovery**: Automatic rollback mechanisms

## Quality Gates

### Code Quality Checks
```yaml
- Black formatting (Python)
- isort import sorting
- flake8 linting
- ESLint (JavaScript)
- Security scanning (Bandit, Safety)
```

### Testing Matrix
```yaml
- Unit Tests (isolated components)
- Integration Tests (system interactions)
- Security Tests (vulnerability checks)
- Performance Tests (load and speed)
- Frontend Tests (JavaScript/UI)
- Accessibility Tests (WCAG compliance)
```

### Build Verification
```yaml
- Asset compilation
- Static file collection
- Bundle size validation
- Performance budget checks
- Migration safety verification
```

## Environment Configuration

### Required Secrets

#### GitHub Repository Secrets
```bash
# Django Configuration
DJANGO_SECRET_KEY=your-production-secret-key

# Database (Turso/LibSQL)
TURSO_DATABASE_URL=libsql://your-database.turso.io
TURSO_AUTH_TOKEN=your-auth-token

# Cache (Redis)
REDIS_URL=redis://your-redis-instance:6379/0

# Vercel Deployment
VERCEL_TOKEN=your-vercel-deployment-token
VERCEL_ORG_ID=your-vercel-organization-id
VERCEL_PROJECT_ID=your-vercel-project-id

# External APIs (Optional)
GOOGLE_MAPS_API_KEY=your-maps-key
FACEBOOK_APP_SECRET=your-facebook-secret
INSTAGRAM_ACCESS_TOKEN=your-instagram-token
SPOTIFY_CLIENT_SECRET=your-spotify-secret
```

#### Environment Variables
```bash
# Set in GitHub Actions environment
PYTHON_VERSION=3.12
NODE_VERSION=18
COVERAGE_THRESHOLD=80
```

### Local Development Setup
```bash
# 1. Copy environment template
cp .env.example .env

# 2. Install pre-commit hooks
pip install pre-commit
pre-commit install

# 3. Install dependencies
pip install -r requirements.txt
npm install

# 4. Run local tests
python manage.py test
npm test
```

## Deployment Process

### Automatic Deployment (Push to Main)

1. **Pre-deployment Checks**
   ```yaml
   - Code quality validation
   - Security scanning
   - Test suite execution
   - Build verification
   ```

2. **Database Migration**
   ```yaml
   - Pre-migration backup
   - Migration safety analysis
   - Execution with rollback capability
   - Post-migration verification
   ```

3. **Asset Build and Deploy**
   ```yaml
   - Production asset compilation
   - Static file optimization
   - Vercel deployment
   - Health check verification
   ```

4. **Post-deployment Validation**
   ```yaml
   - Endpoint health checks
   - Performance monitoring
   - Core Web Vitals measurement
   - Error rate monitoring
   ```

### Manual Deployment Options

#### Force Deployment
```bash
# Via GitHub Actions UI
Workflow: "Production Deployment"
Inputs:
  - force_deploy: true
  - skip_migrations: false
```

#### Skip Migrations
```bash
# For non-database changes
Workflow: "Production Deployment"
Inputs:
  - force_deploy: false
  - skip_migrations: true
```

## Rollback Mechanisms

### Automatic Rollback Triggers
- Health check failures
- Database migration errors
- Critical application errors
- Performance degradation

### Manual Rollback Process
```bash
# 1. Identify last stable commit
git log --oneline -10

# 2. Trigger rollback workflow
# (Automatically triggered on deployment failures)

# 3. Verify rollback success
curl -f https://saborconflowdance.com/api/health/
```

### Rollback Components
- Previous version deployment
- Database state restoration
- Cache invalidation
- DNS/CDN cache clearing
- Incident notification

## Monitoring and Alerting

### Health Check Endpoint
```
GET /api/health/
```

**Response Format:**
```json
{
  "status": "healthy|degraded|unhealthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "v2024.01.15-abc123",
  "environment": "production",
  "checks": {
    "database": {
      "status": "healthy",
      "response_time_ms": 45.2
    },
    "cache": {
      "status": "healthy", 
      "response_time_ms": 12.8
    },
    "application": {
      "status": "healthy",
      "response_time_ms": 23.5,
      "metrics": {
        "testimonials": 156,
        "instructors": 8
      }
    },
    "static_files": {
      "status": "healthy",
      "response_time_ms": 5.1,
      "found_files": {
        "css": true,
        "js": true
      }
    }
  },
  "total_response_time_ms": 86.6
}
```

### Performance Monitoring
- **Lighthouse Audits**: Automated performance scoring
- **Core Web Vitals**: LCP, FID, CLS tracking
- **Bundle Analysis**: JavaScript/CSS size monitoring
- **Error Tracking**: Application error monitoring

### Notification Channels
- **GitHub Issues**: Automatic incident creation
- **PR Comments**: Test result summaries
- **Workflow Annotations**: Build status updates

## Security Features

### Code Security
- **Secret Detection**: Prevents credential commits
- **Dependency Scanning**: Vulnerability assessment
- **Static Analysis**: Security issue identification
- **Access Control**: Branch protection rules

### Deployment Security
- **Environment Isolation**: Separate staging/production
- **Secret Management**: Encrypted environment variables
- **Audit Trail**: Complete deployment history
- **Rollback Protection**: Safe failure recovery

## Performance Optimization

### Build Optimization
```yaml
- Parallel job execution
- Dependency caching
- Artifact optimization
- Incremental builds
```

### Asset Optimization
```yaml
- CSS/JS minification
- Image compression
- Bundle splitting
- Cache optimization
```

### Database Optimization
```yaml
- Migration safety checks
- Index optimization
- Query performance monitoring
- Connection pooling
```

## Troubleshooting

### Common Issues

#### Test Failures
```bash
# Check specific test output
pytest core/tests/ -v --tb=long

# Run specific test category
pytest core/tests/ -m "unit" -v
```

#### Build Failures
```bash
# Check asset compilation
npm run build

# Verify static files
python manage.py collectstatic --dry-run
```

#### Deployment Failures
```bash
# Check health endpoint
curl -f https://saborconflowdance.com/api/health/

# Review deployment logs
gh run view <run-id> --log
```

#### Migration Issues
```bash
# Check migration status
python manage.py showmigrations

# Test migration safety
python manage.py migrate --dry-run
```

### Debug Commands

#### Local Testing
```bash
# Run full test suite
pytest core/tests/ --cov=core

# Security scan
bandit -r core/ sabor_con_flow/

# Code quality
black --check core/ sabor_con_flow/
flake8 core/ sabor_con_flow/
```

#### Performance Testing
```bash
# Frontend performance
npm run performance

# Lighthouse audit
lighthouse https://saborconflowdance.com

# Bundle analysis
npm run analyze
```

## Maintenance

### Regular Tasks
- **Weekly**: Review failed deployments
- **Monthly**: Update dependencies
- **Quarterly**: Security audit
- **Annually**: Performance optimization review

### Dependency Updates
```bash
# Python dependencies
pip-audit
safety check

# Node.js dependencies  
npm audit
npm update
```

### Backup Management
- **Database**: Automated pre-migration backups
- **Code**: Git repository with full history
- **Assets**: Vercel deployment snapshots
- **Configuration**: Environment variable backups

## Best Practices

### Development Workflow
1. **Feature Branches**: Create from `develop`
2. **Pull Requests**: Required for `main` branch
3. **Code Review**: Minimum two approvals
4. **Testing**: All tests must pass
5. **Documentation**: Update relevant docs

### Deployment Guidelines
1. **Small Changes**: Deploy frequently
2. **Testing**: Thorough QA before merge
3. **Monitoring**: Watch metrics post-deploy
4. **Rollback**: Quick decision on issues
5. **Communication**: Notify team of deployments

### Security Practices
1. **Secrets**: Never commit credentials
2. **Dependencies**: Regular security updates
3. **Access**: Principle of least privilege
4. **Monitoring**: Continuous security scanning
5. **Incident Response**: Documented procedures

## Contact and Support

### Team Responsibilities
- **DevOps Lead**: CI/CD pipeline maintenance
- **Backend Team**: Database migrations and API health
- **Frontend Team**: Asset builds and performance
- **QA Team**: Test suite maintenance

### Emergency Contacts
- **Production Issues**: Create GitHub issue with "production" label
- **Security Incidents**: Create GitHub issue with "security" label
- **Performance Degradation**: Monitor via health endpoint

---

*Last Updated: 2024-01-15*
*Version: 1.0.0*
*SPEC_06 Group D Task 10 Implementation*