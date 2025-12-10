# GitHub Environment Setup

## Required GitHub Environments

Create the following environments in your GitHub repository settings:

### 1. Production Environment
- **Name**: `production`
- **URL**: `https://saborconflowdance.com`
- **Protection Rules**:
  - Required reviewers: 2 (DevOps team members)
  - Wait timer: 0 minutes
  - Restrict deployments to main branch only

**Environment Secrets:**
```
DJANGO_SECRET_KEY=your-production-secret
TURSO_DATABASE_URL=libsql://production.turso.io
TURSO_AUTH_TOKEN=production-auth-token
REDIS_URL=redis://production:6379/0
VERCEL_TOKEN=vercel-deployment-token
VERCEL_ORG_ID=vercel-org-id
VERCEL_PROJECT_ID=vercel-project-id
```

### 2. Production Database Environment
- **Name**: `production-db`
- **Protection Rules**:
  - Required reviewers: 2 (DBA/Senior Dev)
  - Wait timer: 5 minutes
  - Allow only main branch deployments

**Environment Secrets:**
```
TURSO_DATABASE_URL=libsql://production.turso.io
TURSO_AUTH_TOKEN=production-auth-token
DJANGO_SECRET_KEY=your-production-secret
```

### 3. Production Rollback Environment
- **Name**: `production-rollback`
- **Protection Rules**:
  - Required reviewers: 1 (Emergency access)
  - Wait timer: 0 minutes
  - Allow emergency rollbacks

**Environment Secrets:**
```
VERCEL_TOKEN=vercel-deployment-token
VERCEL_ORG_ID=vercel-org-id
VERCEL_PROJECT_ID=vercel-project-id
```

## Repository Secrets

Add these secrets at the repository level (accessible to all workflows):

```
# Deployment
VERCEL_TOKEN=your-vercel-token
VERCEL_ORG_ID=your-vercel-org-id
VERCEL_PROJECT_ID=your-vercel-project-id

# Database
TURSO_DATABASE_URL=your-database-url
TURSO_AUTH_TOKEN=your-auth-token

# Application
DJANGO_SECRET_KEY=your-secret-key
REDIS_URL=your-redis-url

# External APIs (optional)
GOOGLE_MAPS_API_KEY=your-maps-key
FACEBOOK_APP_SECRET=your-facebook-secret
INSTAGRAM_ACCESS_TOKEN=your-instagram-token
SPOTIFY_CLIENT_SECRET=your-spotify-secret
```

## Branch Protection Rules

Configure these branch protection rules:

### Main Branch (`main`)
- **Require pull request reviews**: 2 reviews required
- **Dismiss stale reviews**: Enabled
- **Require review from code owners**: Enabled
- **Require status checks**: All CI checks must pass
- **Require up-to-date branches**: Enabled
- **Include administrators**: Enabled
- **Restrict pushes**: Only admins and CI/CD service account

### Develop Branch (`develop`) 
- **Require pull request reviews**: 1 review required
- **Require status checks**: All tests must pass
- **Allow force pushes**: Disabled
- **Allow deletions**: Disabled

## Required Status Checks

Add these status checks as required for main branch:

```
- Code Quality / code-quality
- Test Suite / test-matrix
- Frontend Tests / frontend-tests  
- Build Verification / build-check
- Migration Safety Check / migration-check
```

## Webhook Configuration

### Vercel Integration
- **Events**: Push, Pull Request
- **URL**: Provided by Vercel
- **Secret**: Vercel webhook secret

### Monitoring Integration (Optional)
- **Events**: Deployment Status
- **URL**: Your monitoring service webhook
- **Secret**: Monitoring service secret

## Team Permissions

### DevOps Team
- **Repository**: Admin access
- **Environments**: Can approve production deployments
- **Secrets**: Can manage deployment secrets

### Development Team  
- **Repository**: Write access
- **Environments**: Can view environment status
- **Secrets**: Cannot access production secrets

### QA Team
- **Repository**: Write access
- **Environments**: Can approve staging deployments
- **Secrets**: Limited access to test environments

## Security Configuration

### Required Two-Factor Authentication
- Enable 2FA for all team members
- Require 2FA for organization access
- Regular 2FA compliance audits

### Access Reviews
- **Monthly**: Review team access levels
- **Quarterly**: Audit environment permissions
- **Annually**: Complete security assessment

## Deployment Approval Process

### Standard Deployment (Main Branch)
1. **Developer**: Creates PR to main
2. **Code Review**: 2 approvals required
3. **CI/CD**: All tests must pass
4. **Auto-Deploy**: Triggers on merge to main
5. **Post-Deploy**: Health checks and monitoring

### Emergency Deployment
1. **Incident**: Production issue identified
2. **Assessment**: Team lead approves emergency process
3. **Hotfix**: Direct commit to main (with justification)
4. **Deploy**: Expedited deployment process
5. **Post-Mortem**: Required within 24 hours

### Database Migration Deployment
1. **Migration PR**: Include detailed migration plan
2. **DBA Review**: Database admin approval required
3. **Backup**: Automatic pre-migration backup
4. **Deploy**: Execute with rollback capability
5. **Verify**: Post-migration integrity checks

## Monitoring and Alerting

### GitHub Actions Monitoring
- **Failed Workflows**: Immediate Slack notification
- **Long-Running Jobs**: Alert after 30 minutes
- **Resource Usage**: Monitor runner usage

### Environment Monitoring
- **Health Checks**: Every 5 minutes
- **Performance**: Core Web Vitals tracking
- **Error Rates**: Application error monitoring

## Compliance Requirements

### Audit Trail
- All deployments logged
- Approval history maintained
- Environment changes tracked
- Secret access audited

### Data Protection
- Secrets encrypted at rest
- Limited secret access
- Regular secret rotation
- Secure secret transmission

### Change Management
- All changes via pull requests
- Required approvals documented
- Deployment windows defined
- Rollback procedures tested

---

*Configure these settings in your GitHub repository to enable the CI/CD pipeline.*