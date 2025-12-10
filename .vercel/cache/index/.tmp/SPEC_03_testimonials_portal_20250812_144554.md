# SPEC 03: Testimonials Portal
**Component:** Testimonial Collection and Display System
**Priority:** P1 - Important
**Parallel Execution:** Tasks 1-3 parallel, 4-6 parallel, 7-8 parallel

## High-Level Context
Build a comprehensive testimonials system that collects reviews from students, integrates with Google Business Profile for SEO benefits, and displays social proof throughout the site. This system addresses trust-building and reputation management while automating the review collection process.

## Mid-Level Objectives
- Create dedicated testimonial submission page (/leave-review)
- Implement moderation workflow for quality control
- Integrate with Google Business Profile API
- Display testimonials on homepage and dedicated page
- Enable easy sharing of review link via SMS/email
- Build admin interface for testimonial management

## Implementation Notes
- Use Django forms for secure submission
- Implement CSRF protection
- Store photos in cloud storage (Google Drive/Vercel Blob)
- Cache approved testimonials for performance
- Follow GDPR compliance for data collection
- Mobile-optimized submission form

## Required Context
- Database models from SPEC_01 (Testimonial model)
- Base templates and styling from SPEC_02
- Google Business Profile API credentials
- Email configuration for notifications
- Admin interface access

## Beginning Context (Prerequisites)
### Available Files
- `core/models.py` - Testimonial model defined
- `templates/base.html` - Base template
- `static/css/base.css` - Base styles
- Admin interface configured

### System State
- Database with Testimonial table
- Static file serving configured
- Email backend configured (or ready to configure)
- Google API credentials available

## Ending Context (Deliverables)
### Files to Create/Modify
- `templates/testimonials/submit.html` - Submission form page
- `templates/testimonials/success.html` - Success confirmation
- `templates/testimonials/display.html` - Testimonials page
- `templates/components/testimonial_carousel.html` - Reusable carousel
- `core/forms.py` - Testimonial submission form
- `core/views.py` - Testimonial views
- `static/css/testimonials.css` - Testimonial styles
- `static/js/testimonial-form.js` - Form enhancements
- `core/utils/google_reviews.py` - Google API integration

### System State
- Testimonial submission page live at /leave-review
- Reviews automatically sent to Google Business
- Admin moderation workflow functional
- Testimonials displaying on homepage
- Email notifications working

## Low-Level Tasks (Implementation Prompts)

### Task 1: Create Testimonial Form
**Prompt**: "In core/forms.py, create a TestimonialForm using Django ModelForm for the Testimonial model. Include fields: student_name, email, class_type (as dropdown), rating (as radio buttons 1-5), content (as textarea), and photo upload. Add form validation to ensure rating is between 1-5 and content is at least 50 characters. Use Bootstrap classes for styling compatibility."

**Acceptance Criteria**:
- [ ] ModelForm created with specified fields
- [ ] Rating displayed as star radio buttons
- [ ] Class type dropdown populated
- [ ] Minimum content length validation
- [ ] Bootstrap form classes applied

### Task 2: Build Submission View
**Prompt**: "In core/views.py, create submit_testimonial view that handles GET (display form) and POST (process submission). On successful submission, save with status='pending', send admin notification email, trigger Google Business API integration (placeholder for now), and redirect to success page. Include CSRF protection and form validation error handling."

**Acceptance Criteria**:
- [ ] GET request shows form
- [ ] POST processes submission
- [ ] Status set to 'pending' by default
- [ ] Admin email notification sent
- [ ] Success page redirect

### Task 3: Design Submission Page
**Prompt**: "Create templates/testimonials/submit.html extending base.html. Design a clean, inviting form with heading 'Share Your Dance Journey', subheading explaining the review helps others, star rating selector with visual feedback, class type dropdown, textarea for review with character counter, optional photo upload, and submit button. Make fully mobile responsive."

**Acceptance Criteria**:
- [ ] Welcoming page design
- [ ] Visual star rating selector
- [ ] Character counter for review text
- [ ] Photo upload preview
- [ ] Mobile-optimized layout

### Task 4: Implement Star Rating UI
**Prompt**: "Create static/js/testimonial-form.js to enhance the rating input with interactive stars. When user hovers over stars, highlight them up to cursor position. On click, set the rating value. Show selected rating with filled stars (gold #C7B375) and empty stars (gray). Add accessibility with keyboard navigation."

**Acceptance Criteria**:
- [ ] Interactive star hover effect
- [ ] Click to set rating
- [ ] Visual feedback with gold stars
- [ ] Keyboard accessible (arrow keys)
- [ ] Screen reader compatible

### Task 5: Create Success Page
**Prompt**: "Create templates/testimonials/success.html with a thank you message, confirmation that review is being processed, note about Google Business Profile submission, social sharing buttons to share their experience, and a CTA to return to homepage or book another class."

**Acceptance Criteria**:
- [ ] Clear thank you message
- [ ] Explanation of what happens next
- [ ] Social sharing buttons
- [ ] Navigation options

### Task 6: Build Admin Moderation Interface
**Prompt**: "Enhance core/admin.py TestimonialAdmin to add custom actions: 'Approve selected testimonials' and 'Reject selected testimonials'. Approved testimonials should set status='approved' and published_at=now(). Add list filters for status, rating, and date. Include preview of testimonial content in list view."

**Acceptance Criteria**:
- [ ] Bulk approve/reject actions
- [ ] Status and date filters
- [ ] Content preview in list
- [ ] Published date auto-set on approval

### Task 7: Create Testimonial Display View
**Prompt**: "Create display_testimonials view in core/views.py that fetches all approved testimonials ordered by published_at descending. Create templates/testimonials/display.html showing testimonials in a masonry grid layout with student name, rating stars, review text, class type badge, and photo if available. Add filtering by rating and class type."

**Acceptance Criteria**:
- [ ] Only approved testimonials shown
- [ ] Masonry grid layout
- [ ] Rating and class filters
- [ ] Responsive design
- [ ] Photo display handling

### Task 8: Build Homepage Carousel Component
**Prompt**: "Create templates/components/testimonial_carousel.html as an include template that displays featured testimonials in a carousel. Show 3 testimonials at a time on desktop, 1 on mobile. Include student name, star rating, truncated review (150 chars), and 'Read more' link. Add smooth transitions and auto-play with pause on hover."

**Acceptance Criteria**:
- [ ] Reusable carousel component
- [ ] Responsive (3 desktop, 1 mobile)
- [ ] Auto-play with pause
- [ ] Smooth transitions
- [ ] Read more links

### Task 9: Style Testimonial Components
**Prompt**: "Create static/css/testimonials.css with styles for testimonial cards using soft shadows and rounded corners, star ratings with gold color (#C7B375), masonry grid layout using CSS Grid, carousel with smooth transitions, and hover effects that slightly lift cards. Ensure consistent styling across all testimonial displays."

**Acceptance Criteria**:
- [ ] Card-based design with shadows
- [ ] Gold star ratings
- [ ] Masonry grid on display page
- [ ] Smooth carousel animations
- [ ] Consistent hover effects

### Task 10: Add Google Business Integration
**Prompt**: "Create core/utils/google_reviews.py with function to submit reviews to Google Business Profile API. Function should authenticate with API, format testimonial data for Google's requirements, submit review with rating and text, handle API errors gracefully, and return success/failure status. Use environment variables for API credentials."

**Acceptance Criteria**:
- [ ] Google API authentication
- [ ] Review submission function
- [ ] Error handling
- [ ] Logging of submissions
- [ ] Async task queue ready

### Task 11: Create Share Link Generator
**Prompt**: "Add a management command core/management/commands/generate_review_link.py that creates shareable links for review collection. Generate unique URL with optional parameters (instructor, class), create shortened URL if needed, and provide template for SMS/email messages. Add view to handle these parameterized links."

**Acceptance Criteria**:
- [ ] Unique link generation
- [ ] Parameter handling
- [ ] SMS/email templates
- [ ] Pre-filled form data
- [ ] Tracking capability

### Task 12: Implement Email Notifications
**Prompt**: "Set up email notifications for testimonial workflow: admin notification on new submission, thank you email to submitter, notification when testimonial is approved, and weekly summary of new testimonials. Use Django's email framework with HTML templates."

**Acceptance Criteria**:
- [ ] Admin notification on submission
- [ ] Thank you email to student
- [ ] Approval notification
- [ ] Weekly summary email
- [ ] HTML email templates

## Parallel Execution Groups

**Group A (Parallel):**
- Task 1: Create form
- Task 2: Build submission view
- Task 3: Design submission page

**Group B (Parallel):**
- Task 4: Star rating UI
- Task 5: Success page
- Task 6: Admin moderation

**Group C (Parallel):**
- Task 7: Display view
- Task 8: Homepage carousel

**Group D (Sequential):**
- Task 9: Styling
- Task 10: Google integration
- Task 11: Share links
- Task 12: Email notifications

## Success Metrics
- 20+ testimonials collected in first month
- 80% of testimonials receive 4-5 stars
- Google Business Profile reviews increase by 50%
- Homepage carousel CTR > 3%
- Submission form completion rate > 60%

## Risk Mitigation
- Implement spam protection (honeypot, rate limiting)
- Regular backups of testimonial data
- Fallback if Google API fails
- Content moderation for inappropriate reviews
- GDPR compliance with data handling