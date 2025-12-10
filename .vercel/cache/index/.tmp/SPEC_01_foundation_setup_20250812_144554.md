# SPEC 01: Foundation & Setup
**Component:** Project Foundation and Database Setup
**Priority:** P0 - Critical
**Parallel Execution:** Can run tasks 1-3 in parallel, then 4-6 in parallel

## High-Level Context
Set up the foundational infrastructure for the Sabor con Flow Dance website redesign. This includes configuring the Django project to work with Turso SQLite database, setting up the development environment, and establishing the base project structure that all other components will build upon.

## Mid-Level Objectives
- Configure Django to use Turso SQLite for data persistence
- Set up environment variables for Vercel deployment
- Establish base templates and static file structure
- Create Django admin interface for content management
- Set up development workflow with hot reloading

## Implementation Notes
- Use Django 5.2.1 with Python 3.12+
- Configure Turso SQLite with libSQL client
- Maintain existing Vercel deployment structure
- Keep WhiteNoise for static file compression
- Follow Django best practices for project organization
- Ensure all configurations work both locally and on Vercel

## Required Context
- Existing Django project at `/Users/damilola/Documents/Projects/sabor-con-flow-dance/`
- Vercel deployment configuration in `vercel.json`
- Current static site running without database
- Environment variables needed: TURSO_DATABASE_URL, TURSO_AUTH_TOKEN, SECRET_KEY
- Turso free tier account (9GB storage, 1B reads/month)

## Beginning Context (Prerequisites)
### Available Files
- `manage.py` - Django management script
- `sabor_con_flow/settings.py` - Django settings
- `requirements.txt` - Python dependencies
- `vercel.json` - Deployment configuration
- `api/index.py` - Vercel WSGI handler

### System State
- Python 3.12+ installed
- Node.js 18+ installed
- Git repository initialized
- Vercel CLI available (optional)

## Ending Context (Deliverables)
### Files to Create/Modify
- `sabor_con_flow/settings.py` - Updated with database configuration
- `.env` - Local environment variables
- `.env.example` - Template for environment variables
- `core/models.py` - Database models
- `core/admin.py` - Admin interface configuration
- Database migrations in `core/migrations/`

### System State
- Django project connected to Turso SQLite
- Admin interface accessible at `/admin/`
- Static files properly configured
- Development server running successfully
- Database tables created and migrated

## Low-Level Tasks (Implementation Prompts)

### Task 1: Install Database Dependencies
**Prompt**: "Add the libsql-client and python-dotenv packages to requirements.txt for Turso SQLite support and environment variable management. Run pip install to install the new dependencies."

**Acceptance Criteria**:
- [ ] libsql-client added to requirements.txt
- [ ] python-dotenv added to requirements.txt
- [ ] Dependencies installed successfully
- [ ] No version conflicts

### Task 2: Create Environment Configuration
**Prompt**: "Create a .env file in the project root with placeholders for TURSO_DATABASE_URL, TURSO_AUTH_TOKEN, and SECRET_KEY. Also create a .env.example file with the same structure but dummy values for version control."

**Acceptance Criteria**:
- [ ] .env file created with actual values
- [ ] .env.example created with placeholder values
- [ ] .env added to .gitignore
- [ ] Environment variables loadable in Django

### Task 3: Update Django Settings for Database
**Prompt**: "Modify sabor_con_flow/settings.py to configure Turso SQLite database connection. Import os and load environment variables using python-dotenv. Update DATABASES configuration to use Turso SQLite with the connection URL and auth token from environment variables. Re-enable necessary Django apps: admin, auth, contenttypes, sessions."

**Acceptance Criteria**:
- [ ] Database configuration using Turso SQLite
- [ ] Environment variables properly loaded
- [ ] Django apps re-enabled for database functionality
- [ ] Settings work in both dev and production

### Task 4: Create Database Models
**Prompt**: "In core/models.py, create Django models for Instructor, Class, Testimonial, and Resource based on the PRD schema. Use CharField, TextField, URLField, IntegerField, DateTimeField, and ForeignKey as appropriate. For SQLite compatibility, store JSON data as TextField. Include proper validators and default values."

**Acceptance Criteria**:
- [ ] All four models created with correct fields
- [ ] Proper field types and validators
- [ ] ForeignKey relationships established
- [ ] Model string representations defined

### Task 5: Configure Django Admin
**Prompt**: "In core/admin.py, register all models with the Django admin interface. Create ModelAdmin classes with list_display, list_filter, and search_fields for easy content management. For Testimonial model, add actions for bulk approval/rejection."

**Acceptance Criteria**:
- [ ] All models registered in admin
- [ ] Useful list displays configured
- [ ] Search and filtering enabled
- [ ] Bulk actions for testimonial moderation

### Task 6: Run Database Migrations
**Prompt**: "Execute Django migrations to create database tables. Run 'python manage.py makemigrations' to create migration files, then 'python manage.py migrate' to apply them. Create a superuser account with 'python manage.py createsuperuser' for admin access."

**Acceptance Criteria**:
- [ ] Migration files created successfully
- [ ] Database tables created in Turso
- [ ] Superuser account created
- [ ] Admin interface accessible

### Task 7: Update Vercel Configuration
**Prompt**: "Update vercel.json to include environment variables for production. Add build command to run migrations automatically on deployment. Ensure static files are properly handled."

**Acceptance Criteria**:
- [ ] Environment variables configured in Vercel
- [ ] Build command runs migrations
- [ ] Static files served correctly
- [ ] Deployment successful

### Task 8: Create Base Templates Structure
**Prompt**: "Create templates/base.html with the foundational HTML structure including viewport meta, CSS/JS links, navigation placeholder, and footer. Use Django template blocks for content, extra_css, and extra_js. Include the gold/black color scheme variables."

**Acceptance Criteria**:
- [ ] Base template with proper HTML5 structure
- [ ] Django template blocks defined
- [ ] CSS variables for brand colors
- [ ] Mobile viewport configured

### Task 9: Configure Static Files
**Prompt**: "Organize static files into static/css/, static/js/, and static/images/ directories. Create static/css/base.css with CSS custom properties for colors, spacing, and typography. Configure Django to collect static files to staticfiles/ directory."

**Acceptance Criteria**:
- [ ] Static directories properly organized
- [ ] Base CSS with design tokens
- [ ] Static file collection working
- [ ] WhiteNoise compression active

### Task 10: Verify Local Development
**Prompt**: "Start the Django development server with 'python manage.py runserver'. Test that the admin interface works at /admin/, static files load correctly, and database operations function. Document any issues found."

**Acceptance Criteria**:
- [ ] Development server starts without errors
- [ ] Admin interface fully functional
- [ ] Static files loading
- [ ] Database CRUD operations working

## Parallel Execution Groups

**Group A (Parallel):**
- Task 1: Install dependencies
- Task 2: Environment configuration  
- Task 3: Django settings update

**Group B (Parallel):**
- Task 4: Create models
- Task 5: Configure admin
- Task 8: Base templates

**Group C (Sequential):**
- Task 6: Run migrations (requires Group B)
- Task 7: Vercel configuration
- Task 9: Static files
- Task 10: Verification

## Success Metrics
- All database models created and migrated
- Admin interface operational with all models
- Environment properly configured for dev and production
- Static files serving correctly
- No errors in Django checks or deployment

## Risk Mitigation
- Keep backup of current working settings.py
- Test Turso connection before full implementation
- Maintain ability to rollback to static site
- Document all environment variables needed