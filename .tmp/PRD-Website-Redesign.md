# Product Requirements Document: Sabor con Flow Dance Website Redesign

## Document Version
- **Version:** 2.0
- **Date:** January 2025
- **Status:** Updated Draft
- **Author:** Product Team
- **Changes:** Added Testimonials Portal with Google Business integration, removed Student Portal, updated Resources section

---

## 1. Executive Summary

### Project Overview
Complete redesign of the Sabor con Flow Dance website to transform it from a basic informational site into a dynamic, conversion-focused platform that embodies the energy and passion of Cuban salsa dance.

### Core Value Proposition
**"Sabor in every step, flow in every move 💫"** - A digital experience that captures the rhythm, energy, and community of Sabor con Flow Dance studio.

### Business Impact
- **Target:** Increase student enrollment by 40% within 3 months
- **Conversion Goal:** Improve homepage visitor-to-trial conversion from 2% to 8%
- **Retention Goal:** Increase student retention from 60% to 80%

---

## 2. Problem Statement

### Current State Issues
1. **Empty Homepage:** No content beyond logo, resulting in ~90% bounce rate
2. **Poor Mobile Experience:** Non-responsive design losing 65% of mobile visitors
3. **Weak Conversion Funnel:** No clear path from interest to enrollment
4. **Limited Engagement:** Static content fails to convey studio energy
5. **Accessibility Barriers:** Multiple WCAG violations limiting audience reach

### Business Challenges
- Losing potential students to competitors with better web presence
- Unable to showcase instructor expertise and studio atmosphere
- Manual booking process creating friction in enrollment
- No data collection for marketing optimization

---

## 3. Goals and Objectives

### Primary Goals
1. **Increase Conversions:** Design user journeys that guide visitors to book trial classes
2. **Showcase Studio Energy:** Use multimedia to convey the vibrant dance experience
3. **Streamline Enrollment:** Reduce friction from interest to first class
4. **Build Community:** Create touchpoints for ongoing student engagement

### Specific Objectives
- Achieve 8% trial class conversion rate
- Reduce booking abandonment by 50%
- Increase average session duration from 1:30 to 4:00 minutes
- Generate 100+ email subscribers monthly
- Achieve 90+ Google PageSpeed score

---

## 4. User Personas

### Persona 1: Dance Explorer (Maria, 28)
**Demographics:** Young professional, disposable income, active lifestyle
**Goals:** Find fun fitness alternative, meet new people, learn Latin culture
**Pain Points:** Intimidated by dance, unsure about commitment, schedule conflicts
**Needs:** Clear pricing, beginner-friendly messaging, flexible scheduling

### Persona 2: Experienced Dancer (Carlos, 35)
**Demographics:** Dance background, looking for advanced classes
**Goals:** Improve technique, join performance team, compete
**Pain Points:** Finding qualified instructors, advanced curriculum
**Needs:** Instructor credentials, video demonstrations, competition info

### Persona 3: Social Connector (Ashley, 42)
**Demographics:** Empty nester, seeking social activities
**Goals:** New hobby, social circle, stay active
**Pain Points:** Age concerns, finding welcoming environment
**Needs:** Community testimonials, social events, beginner support

---

## 5. User Stories & Requirements

### Epic 1: First-Time Visitor Experience
```
AS A potential student
I WANT TO understand what Sabor con Flow offers
SO THAT I can decide if it's right for me
```

**Requirements:**
- Hero section with headline "Sabor in every step, flow in every move 💫"
- Video background showing actual classes
- Clear value propositions (fun, fitness, community)
- Prominent "Book Your Class" CTA
- Social proof (student count, testimonials)

### Epic 2: Class Discovery & Booking
```
AS A interested visitor
I WANT TO explore class options and book easily
SO THAT I can start dancing quickly
```

**Requirements:**
- Interactive class schedule with filtering
- Class level indicators (Beginner/Intermediate/Advanced)
- Instructor profiles with videos
- One-click Calendly integration
- Package pricing calculator

### Epic 3: Student Engagement
```
AS A current student
I WANT TO stay connected with the studio
SO THAT I remain engaged and motivated
```

**Requirements:**
- Social media feed integration (Instagram)
- Event calendar with RSVP
- WhatsApp group quick join
- Performance video galleries
- Music playlists and resources

### Epic 4: Testimonial Collection & Reputation
```
AS A business owner
I WANT TO collect and showcase testimonials
SO THAT I can build trust and improve online reputation
```

**Requirements:**
- Dedicated testimonial submission portal
- Rating system (1-5 stars)
- Automatic Google Business Profile integration
- Photo/video testimonial support
- Moderation workflow before publishing

---

## 6. Functional Requirements

### P0 - Critical Features (Launch Required)

#### FR1: Hero Section
- **Headline:** "Sabor in every step, flow in every move 💫"
- **Video Background:** 15-second loop of class highlights
- **CTAs:** "Book Your Class" (primary), "View Schedule" (secondary)
- **Trust Indicators:** "200+ Happy Dancers", "Professional Instructors"

#### FR2: Class Schedule System
- **Display:** Simple static schedule (Sundays 12-3PM)
- **Classes:** SCF Choreo Team, Pasos Básicos, Casino Royale
- **External Events:** Links to Facebook Events and Pastio.fun for updates
- **Details:** Class description, instructor, level, duration
- **Booking:** Direct Calendly integration for private lessons

#### FR3: Pricing Display
- **Format:** Card-based layout replacing tables
- **Options:** Drop-in, packages, private lessons
- **Calculator:** Interactive savings calculator

#### FR4: Mobile Navigation
- **Type:** Hamburger menu with smooth animations
- **Touch Targets:** Minimum 44px height
- **Accessibility:** ARIA labels, keyboard navigation

### P1 - Important Features (Post-Launch)

#### FR5: Instructor Profiles
- **Content:** Bio, experience, specialties, photo
- **Video:** 30-second introduction
- **Social:** Instagram links
- **Booking:** Direct private lesson booking

#### FR6: Testimonials Portal
- **Submission Page:** Dedicated URL for testimonial collection (/leave-review)
- **Form Fields:** Name, email, class attended, rating (1-5 stars), written review, photo upload
- **Google Integration:** Automatic submission to Google Business Profile via API
- **Display:** Homepage carousel, dedicated testimonials page
- **Moderation:** Admin approval before publishing
- **Share Links:** Easy sharing via email/SMS to students

#### FR7: Media Gallery
- **Photos:** Class photos, events, performances
- **Videos:** Technique tutorials, recaps
- **Organization:** By event, class type, date

### P2 - Nice-to-Have Features

#### FR8: Resources Hub
- **Music Playlists:** Spotify/Apple Music embeds for class music
- **Video Content:** Dance tutorials, performance videos
- **Instagram Feed:** Embedded Instagram posts and stories
- **Social Sharing:** Direct share to Instagram, Facebook, WhatsApp
- **Download Materials:** Practice guides, rhythm sheets

---

## 7. Non-Functional Requirements

### Performance
- **Page Load:** < 2 seconds on 3G connection
- **Time to Interactive:** < 3 seconds
- **PageSpeed Score:** 90+ mobile, 95+ desktop
- **Core Web Vitals:** Pass all metrics

### Accessibility
- **WCAG Compliance:** Level AA
- **Screen Readers:** Full compatibility
- **Keyboard Navigation:** Complete functionality
- **Color Contrast:** 4.5:1 minimum

### Browser Support
- **Desktop:** Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Mobile:** iOS Safari 14+, Chrome Mobile 90+
- **Responsive:** 320px to 2560px width

### Security
- **HTTPS:** Enforced across all pages
- **Headers:** HSTS, CSP, X-Frame-Options
- **Data Protection:** GDPR compliant forms
- **Authentication:** Secure session management

---

## 8. Design Requirements

### Brand Guidelines
- **Primary Colors:** Gold (#C7B375), Black (#000000)
- **Accent Colors:** Secondary Gold (#BFAA65), White (#FFFFFF)
- **Typography:** Playfair Display (headings), System fonts (body)
- **Imagery:** High-energy, diverse, authentic studio shots

### Component Library
- **Framework:** shadcn/ui components (customized)
- **Icons:** Font Awesome 6.0
- **Animations:** Framer Motion or CSS transitions
- **Grid System:** CSS Grid with flexbox fallbacks

### Key Design Patterns
- **Cards:** For pricing, classes, instructors
- **Carousel:** Testimonials, gallery
- **Modal:** Quick booking, video players
- **Toast:** Success notifications
- **Skeleton:** Loading states

---

## 9. Technical Specifications

### Architecture
- **Backend:** Django 5.2+ with Turso SQLite (edge-hosted)
- **Frontend:** Django templates with modern JavaScript
- **Hosting:** Vercel with CDN
- **Database:** Turso SQLite (libSQL) for read/write operations
- **Static Files:** WhiteNoise with compression
- **Event Management:** Facebook Events + Pastio.fun (external)

### Database Strategy

**Turso SQLite Configuration:**
- **Service:** Turso (edge-hosted SQLite)
- **Free Tier:** 9GB storage, 1B row reads/month (more than sufficient)
- **Latency:** <50ms globally via edge replicas
- **Cost:** $0/month for expected usage

**Data Management Approach:**
- **Static Content:** Class schedules remain mostly fixed (Sundays 12-3PM)
- **Dynamic Content:** Testimonials, instructor updates via admin panel
- **Event Updates:** Handled externally via Facebook Events and Pastio.fun
- **Media:** Videos/photos stored in Google Drive or Vercel Blob

### Database Schema
```python
# Simplified models for SQLite/Turso
class Instructor(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()
    photo_url = models.URLField()  # Store URL only
    video_url = models.URLField(blank=True)
    instagram = models.CharField(max_length=50, blank=True)
    specialties = models.TextField()  # JSON string for SQLite

class Class(models.Model):
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')])
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, default='Sunday')
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.TextField()
    capacity = models.IntegerField(default=20)

class Testimonial(models.Model):
    student_name = CharField(max_length=100)
    email = EmailField()
    rating = IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    content = TextField()
    class_type = CharField(max_length=50)
    photo = ImageField(blank=True, null=True)
    video_url = URLField(blank=True, null=True)
    google_review_id = CharField(max_length=255, blank=True)
    status = CharField(choices=['pending', 'approved', 'rejected'], default='pending')
    featured = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    published_at = DateTimeField(null=True, blank=True)

class Resource(models.Model):
    title = CharField(max_length=200)
    type = CharField(choices=['playlist', 'video', 'guide'])
    embed_url = URLField()
    instagram_post_id = CharField(max_length=100, blank=True)
    description = TextField()
    order = IntegerField(default=0)
    created_at = DateTimeField(auto_now_add=True)
```

### API Integrations
- **Calendly:** Embedded widget for private lesson booking
- **Instagram:** Basic Display API for feed and embedded posts
- **WhatsApp:** Click-to-chat integration
- **Google Analytics:** GA4 with custom events
- **Google Business Profile API:** Automated review submission
- **Spotify/Apple Music:** Embedded playlists for class music
- **Google Drive:** Video embedding and storage
- **Facebook Events:** Event listing integration (read-only)
- **Pastio.fun:** RSVP tracking for special events

### Database Connection
```python
# Turso SQLite configuration for Django
import libsql_client

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get('TURSO_DATABASE_URL'),
        'OPTIONS': {
            'auth_token': os.environ.get('TURSO_AUTH_TOKEN'),
            'sync_url': os.environ.get('TURSO_SYNC_URL'),
        }
    }
}

# Environment variables in Vercel
TURSO_DATABASE_URL=libsql://your-db.turso.io
TURSO_AUTH_TOKEN=your-auth-token
TURSO_SYNC_URL=https://your-db.turso.io
```

### Performance Optimizations
- **Images:** WebP with fallbacks, lazy loading
- **CSS:** Critical CSS inline, async load rest
- **JavaScript:** Code splitting, tree shaking
- **Caching:** Browser caching, CDN caching

---

## 10. Success Metrics

### Primary KPIs
| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Visitor → Trial Conversion | 2.1% | 8.0% | 3 months |
| Trial → Paid Conversion | 35% | 50% | 3 months |
| Average Session Duration | 1:30 | 4:00 | 1 month |
| Bounce Rate | 65% | 35% | 1 month |
| Page Load Time | 4.5s | <2s | Launch |

### Secondary Metrics
- Mobile traffic percentage: 45% → 65%
- Social media referrals: +200%
- Email subscribers: 100+/month
- Student retention: 60% → 80%

### Tracking Implementation
- Google Analytics 4 with custom events
- Hotjar for heatmaps and recordings
- Calendly webhook for booking tracking
- Custom dashboard for instructor metrics

---

## 11. Implementation Timeline

### Phase 1: Foundation (Weeks 1-4)
**Week 1-2:** Design System & Components
- Set up component library
- Create design tokens
- Build core components (buttons, cards, navigation)

**Week 3-4:** Core Pages
- Hero section with video
- Class schedule page
- Pricing page with calculator
- Mobile navigation

### Phase 2: Content & Social Proof (Weeks 5-7)
**Week 5:** Dynamic Content
- Instructor profiles
- Class descriptions
- Gallery system

**Week 6-7:** Engagement Features
- Testimonials portal with Google Business integration
- Instagram feed and post embedding
- WhatsApp integration
- Contact forms
- Resources hub with playlists

### Phase 3: Optimization & Polish (Weeks 8-9)
**Week 8:** Performance
- Image optimization
- Caching strategy
- Loading states
- Error handling

**Week 9:** Quality Assurance
- Cross-browser testing
- Accessibility audit
- Performance testing
- User acceptance testing

### Phase 4: Launch & Monitor (Week 10)
- Soft launch with existing students
- Gather feedback
- Bug fixes
- Full launch
- Monitor metrics

---

## 12. Risks & Mitigations

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Video performance issues | Medium | High | Optimize video files, implement lazy loading, provide image fallback |
| Calendly integration breaks | Low | High | Build fallback contact form, monitor API status |
| Mobile responsiveness bugs | Medium | Medium | Extensive device testing, progressive enhancement |
| SEO ranking drop | Low | Medium | 301 redirects, maintain URL structure, submit sitemap |

### Business Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Low trial conversion | Medium | High | A/B test CTAs, offer incentives, optimize user journey |
| Content creation delays | High | Medium | Start content creation early, hire photographer/videographer |
| Instructor resistance | Low | Low | Include instructors in design process, provide training |

---

## 13. Future Enhancements (Post-MVP)

### Quarter 2
- Online class streaming capability
- Automated email marketing
- Loyalty rewards program
- Mobile app development

### Quarter 3
- Multi-language support (Spanish)
- Advanced booking system with waitlists
- Payment processing integration
- Community forum

### Quarter 4
- Virtual reality dance lessons
- AI-powered class recommendations
- Franchise location support
- B2B corporate wellness program

---

## 14. Appendices

### A. Competitive Analysis
- Arthur Murray Dance Studio: Traditional, expensive, formal
- Salsa con Todo: Good web presence, lacks personality
- Local gym dance classes: Convenient but not specialized

### B. Technical Dependencies
- Django 5.2.1
- Python 3.12+
- Turso SQLite (libSQL client)
- Node.js 18+ (for build tools)
- Vercel hosting
- Google Drive API (for video storage)
- Facebook Events API (for event management)
- Pastio.fun (for RSVP tracking)

### C. Content Requirements
- 20+ high-quality class photos
- 5+ instructor introduction videos
- 10+ student testimonials
- 3+ class highlight videos
- Updated class descriptions

### D. Legal Considerations
- Photo/video release forms
- Privacy policy update
- Terms of service
- Cookie policy
- GDPR compliance

---

## Approval Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Product Owner | | | |
| Technical Lead | | | |
| Design Lead | | | |
| Business Stakeholder | | | |

---

*This PRD is a living document and will be updated as requirements evolve.*