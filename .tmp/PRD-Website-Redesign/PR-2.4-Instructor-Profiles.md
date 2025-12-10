# PR 2.4: Instructor Profiles Implementation

## PR Metadata

**Title:** feat: Implement dynamic instructor profiles with bio and gallery  
**Branch:** `feature/instructor-profiles`  
**Base:** `feature/contact-email`  
**Dependencies:**
- PR 1.1 (Project Setup)
- PR 1.2 (Static Assets)
- PR 2.1 (Homepage & Navigation)

## Overview

This PR implements comprehensive instructor profile pages with biography sections, photo galleries, credentials display, teaching specialties, and social media integration using semantic HTML5, CSS3, vanilla JavaScript, and Vercel Serverless Functions.

## File Structure

```
/
├── instructors.html
├── instructors/
│   ├── [instructor-slug].html
│   └── template.html
├── api/
│   ├── instructors/
│   │   ├── index.js
│   │   ├── profile.js
│   │   └── schedule.js
│   └── gallery/
│       └── photos.js
├── static/
│   ├── css/
│   │   ├── instructors.css
│   │   ├── profile.css
│   │   └── gallery.css
│   ├── js/
│   │   ├── instructors.js
│   │   ├── profile.js
│   │   ├── gallery.js
│   │   └── social-share.js
│   └── images/
│       └── instructors/
└── tests/
    ├── instructors.test.js
    └── gallery.test.js
```

## Implementation Details

### 1. Instructors Page HTML (`instructors.html`)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Meet our expert dance instructors at Sabor con Flow Dance">
    <title>Our Instructors - Sabor con Flow Dance</title>
    
    <!-- Critical CSS -->
    <style>
        :root {
            --profile-card-width: 320px;
            --profile-image-height: 380px;
        }
        
        .instructors-grid {
            display: grid;
            gap: 2rem;
            padding: 2rem 0;
        }
        
        @media (min-width: 768px) {
            .instructors-grid {
                grid-template-columns: repeat(auto-fill, minmax(var(--profile-card-width), 1fr));
            }
        }
        
        .instructor-card {
            background: var(--white);
            border-radius: var(--card-radius);
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .instructor-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        }
    </style>
    
    <!-- Async CSS -->
    <link rel="preload" href="/static/css/instructors.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
    <noscript>
        <link rel="stylesheet" href="/static/css/instructors.css">
    </noscript>
    
    <!-- Structured Data for SEO -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "DanceSchool",
        "name": "Sabor con Flow Dance",
        "instructor": [
            {
                "@type": "Person",
                "name": "Maria Rodriguez",
                "jobTitle": "Lead Salsa Instructor",
                "image": "/static/images/instructors/maria-rodriguez.jpg"
            }
        ]
    }
    </script>
</head>
<body>
    <!-- Navigation -->
    <nav class="main-nav"><!-- ... --></nav>
    
    <main id="main-content">
        <!-- Page Header -->
        <header class="page-header">
            <div class="container">
                <h1>Meet Our Instructors</h1>
                <p>Learn from passionate, experienced dance professionals</p>
            </div>
        </header>
        
        <!-- Filters -->
        <section class="instructor-filters" aria-label="Filter instructors">
            <div class="container">
                <div class="filter-pills">
                    <button class="filter-pill active" data-filter="all">
                        All Instructors
                    </button>
                    <button class="filter-pill" data-filter="salsa">
                        Salsa
                    </button>
                    <button class="filter-pill" data-filter="bachata">
                        Bachata
                    </button>
                    <button class="filter-pill" data-filter="latin">
                        Latin Mix
                    </button>
                    <button class="filter-pill" data-filter="private">
                        Private Lessons
                    </button>
                </div>
            </div>
        </section>
        
        <!-- Instructors Grid -->
        <section class="instructors-section">
            <div class="container">
                <!-- Loading State -->
                <div class="loading-state" aria-live="polite" aria-busy="true">
                    <div class="spinner"></div>
                    <p>Loading instructors...</p>
                </div>
                
                <!-- Instructors Grid -->
                <div class="instructors-grid" role="list">
                    <!-- Instructor cards will be inserted here -->
                </div>
                
                <!-- Instructor Card Template -->
                <template id="instructor-card-template">
                    <article class="instructor-card" role="listitem">
                        <div class="instructor-image-wrapper">
                            <img class="instructor-image" 
                                 src="" 
                                 alt=""
                                 width="320"
                                 height="380"
                                 loading="lazy">
                            <div class="instructor-overlay">
                                <a href="#" class="view-profile-btn" aria-label="View profile">
                                    View Profile
                                </a>
                            </div>
                        </div>
                        
                        <div class="instructor-content">
                            <h2 class="instructor-name"></h2>
                            <p class="instructor-title"></p>
                            
                            <div class="instructor-specialties">
                                <!-- Specialty badges will be inserted here -->
                            </div>
                            
                            <p class="instructor-bio"></p>
                            
                            <div class="instructor-stats">
                                <div class="stat">
                                    <span class="stat-value"></span>
                                    <span class="stat-label">Years Experience</span>
                                </div>
                                <div class="stat">
                                    <span class="stat-value"></span>
                                    <span class="stat-label">Classes/Week</span>
                                </div>
                                <div class="stat">
                                    <span class="stat-value"></span>
                                    <span class="stat-label">Rating</span>
                                </div>
                            </div>
                            
                            <div class="instructor-actions">
                                <a href="#" class="btn btn-primary btn-small">
                                    View Classes
                                </a>
                                <button class="btn btn-secondary btn-small book-private-btn">
                                    Book Private Lesson
                                </button>
                            </div>
                        </div>
                    </article>
                </template>
            </div>
        </section>
        
        <!-- Featured Instructor -->
        <section class="featured-instructor">
            <div class="container">
                <h2>Instructor Spotlight</h2>
                <div class="featured-content">
                    <div class="featured-video">
                        <video poster="/static/images/instructors/featured-poster.jpg"
                               controls
                               width="100%"
                               height="auto">
                            <source src="/static/videos/featured-instructor.mp4" type="video/mp4">
                            <source src="/static/videos/featured-instructor.webm" type="video/webm">
                            Your browser doesn't support video playback.
                        </video>
                    </div>
                    <div class="featured-info">
                        <h3 id="featured-name">Maria Rodriguez</h3>
                        <p class="featured-title">Lead Salsa Instructor</p>
                        <blockquote class="featured-quote">
                            "Dance is not just movement, it's a conversation between body and soul. 
                            I love helping students discover their own unique expression through Latin dance."
                        </blockquote>
                        <div class="featured-achievements">
                            <h4>Achievements</h4>
                            <ul>
                                <li>World Salsa Championship Finalist 2019</li>
                                <li>15+ years of teaching experience</li>
                                <li>Certified by International Dance Council</li>
                                <li>Performed in 20+ countries</li>
                            </ul>
                        </div>
                        <a href="/instructors/maria-rodriguez" class="btn btn-primary">
                            Full Profile
                        </a>
                    </div>
                </div>
            </div>
        </section>
    </main>
    
    <!-- Footer -->
    <footer class="site-footer"><!-- ... --></footer>
    
    <!-- JavaScript Modules -->
    <script type="module" src="/static/js/instructors.js"></script>
</body>
</html>
```

### 2. Individual Profile Page Template (`instructors/template.html`)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{instructor_name} - {instructor_title} at Sabor con Flow Dance">
    <title>{instructor_name} - Sabor con Flow Dance</title>
    
    <!-- Open Graph Tags -->
    <meta property="og:title" content="{instructor_name} - Dance Instructor">
    <meta property="og:description" content="{instructor_bio_short}">
    <meta property="og:image" content="{instructor_image}">
    <meta property="og:type" content="profile">
    
    <!-- CSS -->
    <link rel="stylesheet" href="/static/css/profile.css">
    <link rel="stylesheet" href="/static/css/gallery.css">
</head>
<body>
    <!-- Navigation -->
    <nav class="main-nav"><!-- ... --></nav>
    
    <main id="main-content">
        <!-- Profile Header -->
        <section class="profile-header">
            <div class="container">
                <div class="profile-header-content">
                    <div class="profile-image-container">
                        <img src="{instructor_image}" 
                             alt="{instructor_name}"
                             class="profile-image"
                             width="400"
                             height="400">
                        <div class="profile-badges">
                            <span class="badge badge-verified" title="Verified Instructor">
                                <svg><use href="#icon-verified"></use></svg>
                            </span>
                            <span class="badge badge-featured" title="Featured Instructor">
                                <svg><use href="#icon-star"></use></svg>
                            </span>
                        </div>
                    </div>
                    
                    <div class="profile-info">
                        <h1 class="profile-name">{instructor_name}</h1>
                        <p class="profile-title">{instructor_title}</p>
                        
                        <div class="profile-rating">
                            <div class="stars" aria-label="{rating} star rating">
                                ★★★★★
                            </div>
                            <span class="rating-text">{rating} ({review_count} reviews)</span>
                        </div>
                        
                        <div class="profile-specialties">
                            <h3>Specialties</h3>
                            <div class="specialty-tags">
                                <!-- Dynamic specialty tags -->
                            </div>
                        </div>
                        
                        <div class="profile-actions">
                            <button class="btn btn-primary" id="book-class-btn">
                                Book a Class
                            </button>
                            <button class="btn btn-secondary" id="book-private-btn">
                                Private Lesson
                            </button>
                            <button class="btn btn-icon" id="share-profile-btn" aria-label="Share profile">
                                <svg><use href="#icon-share"></use></svg>
                            </button>
                        </div>
                        
                        <div class="profile-social">
                            <a href="#" aria-label="Instagram" class="social-link">
                                <svg><use href="#icon-instagram"></use></svg>
                            </a>
                            <a href="#" aria-label="Facebook" class="social-link">
                                <svg><use href="#icon-facebook"></use></svg>
                            </a>
                            <a href="#" aria-label="YouTube" class="social-link">
                                <svg><use href="#icon-youtube"></use></svg>
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- Profile Navigation -->
        <nav class="profile-nav" aria-label="Profile sections">
            <div class="container">
                <ul class="profile-nav-list">
                    <li><a href="#about" class="profile-nav-link active">About</a></li>
                    <li><a href="#experience" class="profile-nav-link">Experience</a></li>
                    <li><a href="#classes" class="profile-nav-link">Classes</a></li>
                    <li><a href="#gallery" class="profile-nav-link">Gallery</a></li>
                    <li><a href="#reviews" class="profile-nav-link">Reviews</a></li>
                    <li><a href="#contact" class="profile-nav-link">Contact</a></li>
                </ul>
            </div>
        </nav>
        
        <!-- Profile Content -->
        <div class="profile-content">
            <div class="container">
                <!-- About Section -->
                <section id="about" class="profile-section">
                    <h2>About {instructor_name}</h2>
                    <div class="about-content">
                        <div class="bio">
                            <p>{instructor_bio_full}</p>
                        </div>
                        
                        <aside class="quick-facts">
                            <h3>Quick Facts</h3>
                            <dl class="facts-list">
                                <dt>Teaching Since</dt>
                                <dd>{teaching_since}</dd>
                                
                                <dt>Languages</dt>
                                <dd>{languages}</dd>
                                
                                <dt>Home Studio</dt>
                                <dd>{home_studio}</dd>
                                
                                <dt>Availability</dt>
                                <dd>{availability}</dd>
                            </dl>
                        </aside>
                    </div>
                    
                    <div class="philosophy">
                        <h3>Teaching Philosophy</h3>
                        <blockquote>
                            {teaching_philosophy}
                        </blockquote>
                    </div>
                </section>
                
                <!-- Experience Section -->
                <section id="experience" class="profile-section">
                    <h2>Experience & Credentials</h2>
                    
                    <div class="credentials-grid">
                        <div class="credential-card">
                            <svg class="credential-icon"><use href="#icon-certificate"></use></svg>
                            <h3>Certifications</h3>
                            <ul class="credential-list">
                                <!-- Dynamic certifications -->
                            </ul>
                        </div>
                        
                        <div class="credential-card">
                            <svg class="credential-icon"><use href="#icon-trophy"></use></svg>
                            <h3>Awards & Achievements</h3>
                            <ul class="credential-list">
                                <!-- Dynamic awards -->
                            </ul>
                        </div>
                        
                        <div class="credential-card">
                            <svg class="credential-icon"><use href="#icon-performance"></use></svg>
                            <h3>Performance History</h3>
                            <ul class="credential-list">
                                <!-- Dynamic performances -->
                            </ul>
                        </div>
                        
                        <div class="credential-card">
                            <svg class="credential-icon"><use href="#icon-workshop"></use></svg>
                            <h3>Workshops & Masterclasses</h3>
                            <ul class="credential-list">
                                <!-- Dynamic workshops -->
                            </ul>
                        </div>
                    </div>
                </section>
                
                <!-- Classes Section -->
                <section id="classes" class="profile-section">
                    <h2>Current Classes</h2>
                    <div class="classes-schedule">
                        <!-- Class cards will be inserted here -->
                    </div>
                    <a href="/schedule?instructor={instructor_slug}" class="btn btn-secondary">
                        View Full Schedule
                    </a>
                </section>
                
                <!-- Gallery Section -->
                <section id="gallery" class="profile-section">
                    <h2>Photo & Video Gallery</h2>
                    
                    <div class="gallery-tabs">
                        <button class="gallery-tab active" data-tab="photos">Photos</button>
                        <button class="gallery-tab" data-tab="videos">Videos</button>
                    </div>
                    
                    <div class="gallery-content">
                        <!-- Photos Tab -->
                        <div class="gallery-panel active" id="photos-panel">
                            <div class="photo-grid">
                                <!-- Dynamic photo grid -->
                            </div>
                        </div>
                        
                        <!-- Videos Tab -->
                        <div class="gallery-panel" id="videos-panel">
                            <div class="video-grid">
                                <!-- Dynamic video grid -->
                            </div>
                        </div>
                    </div>
                    
                    <!-- Lightbox -->
                    <div id="lightbox" class="lightbox" hidden>
                        <button class="lightbox-close" aria-label="Close">&times;</button>
                        <button class="lightbox-prev" aria-label="Previous">‹</button>
                        <button class="lightbox-next" aria-label="Next">›</button>
                        <div class="lightbox-content">
                            <img src="" alt="" id="lightbox-image">
                            <div class="lightbox-caption"></div>
                        </div>
                    </div>
                </section>
                
                <!-- Reviews Section -->
                <section id="reviews" class="profile-section">
                    <h2>Student Reviews</h2>
                    
                    <div class="reviews-summary">
                        <div class="rating-breakdown">
                            <div class="overall-rating">
                                <span class="rating-number">{rating}</span>
                                <div class="stars">★★★★★</div>
                                <span class="review-count">{review_count} reviews</span>
                            </div>
                            
                            <div class="rating-bars">
                                <div class="rating-bar">
                                    <span>5 stars</span>
                                    <div class="bar">
                                        <div class="fill" style="width: 80%"></div>
                                    </div>
                                    <span>80%</span>
                                </div>
                                <!-- More rating bars -->
                            </div>
                        </div>
                        
                        <div class="review-highlights">
                            <h3>What students love</h3>
                            <div class="highlight-tags">
                                <span class="tag">Patient</span>
                                <span class="tag">Encouraging</span>
                                <span class="tag">Fun</span>
                                <span class="tag">Professional</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="reviews-list">
                        <!-- Review cards will be inserted here -->
                    </div>
                    
                    <button class="btn btn-secondary" id="load-more-reviews">
                        Load More Reviews
                    </button>
                </section>
                
                <!-- Contact Section -->
                <section id="contact" class="profile-section">
                    <h2>Get in Touch</h2>
                    <div class="contact-options">
                        <div class="contact-card">
                            <h3>Book a Class</h3>
                            <p>Join one of {instructor_name}'s group classes</p>
                            <a href="/schedule?instructor={instructor_slug}" class="btn btn-primary">
                                View Schedule
                            </a>
                        </div>
                        
                        <div class="contact-card">
                            <h3>Private Lessons</h3>
                            <p>One-on-one personalized instruction</p>
                            <button class="btn btn-primary" id="request-private">
                                Request Lesson
                            </button>
                        </div>
                        
                        <div class="contact-card">
                            <h3>Send Message</h3>
                            <p>Have a question? Send a direct message</p>
                            <button class="btn btn-secondary" id="send-message">
                                Message
                            </button>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    </main>
    
    <!-- Share Modal -->
    <dialog id="share-modal" class="modal">
        <div class="modal-content">
            <header class="modal-header">
                <h2>Share Profile</h2>
                <button class="modal-close" aria-label="Close">&times;</button>
            </header>
            <div class="modal-body">
                <div class="share-options">
                    <button class="share-option" data-platform="facebook">
                        <svg><use href="#icon-facebook"></use></svg>
                        Facebook
                    </button>
                    <button class="share-option" data-platform="twitter">
                        <svg><use href="#icon-twitter"></use></svg>
                        Twitter
                    </button>
                    <button class="share-option" data-platform="whatsapp">
                        <svg><use href="#icon-whatsapp"></use></svg>
                        WhatsApp
                    </button>
                    <button class="share-option" data-platform="email">
                        <svg><use href="#icon-email"></use></svg>
                        Email
                    </button>
                </div>
                <div class="share-link">
                    <input type="text" 
                           id="share-url" 
                           readonly 
                           value="https://saborconflowdance.com/instructors/{instructor_slug}">
                    <button id="copy-link" class="btn btn-secondary">Copy Link</button>
                </div>
            </div>
        </div>
    </dialog>
    
    <!-- JavaScript Modules -->
    <script type="module" src="/static/js/profile.js"></script>
    <script type="module" src="/static/js/gallery.js"></script>
    <script type="module" src="/static/js/social-share.js"></script>
</body>
</html>
```

### 3. Instructors JavaScript Module (`static/js/instructors.js`)

```javascript
/**
 * Instructors Page Module
 * Manages instructor grid display and filtering
 */

class InstructorsManager {
    constructor() {
        this.instructors = [];
        this.filteredInstructors = [];
        this.currentFilter = 'all';
        
        this.elements = {
            grid: document.querySelector('.instructors-grid'),
            loadingState: document.querySelector('.loading-state'),
            filterPills: document.querySelectorAll('.filter-pill'),
            template: document.getElementById('instructor-card-template')
        };
        
        this.init();
    }
    
    async init() {
        // Load instructors
        await this.loadInstructors();
        
        // Set up filters
        this.setupFilters();
        
        // Set up featured instructor
        this.loadFeaturedInstructor();
        
        // Initialize animations
        this.initAnimations();
    }
    
    async loadInstructors() {
        try {
            this.showLoading(true);
            
            const response = await fetch('/api/instructors', {
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to load instructors');
            }
            
            const data = await response.json();
            this.instructors = data.instructors;
            this.filteredInstructors = [...this.instructors];
            
            this.renderInstructors();
            
        } catch (error) {
            console.error('Error loading instructors:', error);
            this.showError('Failed to load instructors. Please try again.');
        } finally {
            this.showLoading(false);
        }
    }
    
    renderInstructors() {
        if (!this.elements.grid || !this.elements.template) return;
        
        // Clear grid
        this.elements.grid.innerHTML = '';
        
        // Render each instructor
        this.filteredInstructors.forEach((instructor, index) => {
            const card = this.createInstructorCard(instructor);
            card.style.animationDelay = `${index * 0.1}s`;
            this.elements.grid.appendChild(card);
        });
        
        // Initialize lazy loading for images
        this.initLazyLoading();
    }
    
    createInstructorCard(instructor) {
        const template = this.elements.template.content.cloneNode(true);
        const card = template.querySelector('.instructor-card');
        
        // Set image
        const img = card.querySelector('.instructor-image');
        img.src = instructor.image;
        img.alt = instructor.name;
        
        // Set content
        card.querySelector('.instructor-name').textContent = instructor.name;
        card.querySelector('.instructor-title').textContent = instructor.title;
        card.querySelector('.instructor-bio').textContent = instructor.bioShort;
        
        // Set specialties
        const specialtiesContainer = card.querySelector('.instructor-specialties');
        instructor.specialties.forEach(specialty => {
            const badge = document.createElement('span');
            badge.className = `specialty-badge badge-${specialty.toLowerCase()}`;
            badge.textContent = specialty;
            specialtiesContainer.appendChild(badge);
        });
        
        // Set stats
        const stats = card.querySelectorAll('.stat-value');
        stats[0].textContent = instructor.yearsExperience;
        stats[1].textContent = instructor.classesPerWeek;
        stats[2].textContent = instructor.rating;
        
        // Set links
        card.querySelector('.view-profile-btn').href = `/instructors/${instructor.slug}`;
        card.querySelector('.instructor-actions a').href = `/schedule?instructor=${instructor.slug}`;
        
        // Set up booking button
        const bookBtn = card.querySelector('.book-private-btn');
        bookBtn.addEventListener('click', () => this.handlePrivateBooking(instructor));
        
        // Add filter data
        card.dataset.specialties = instructor.specialties.join(',').toLowerCase();
        
        return card;
    }
    
    setupFilters() {
        this.elements.filterPills.forEach(pill => {
            pill.addEventListener('click', () => {
                this.setFilter(pill.dataset.filter);
            });
        });
    }
    
    setFilter(filter) {
        this.currentFilter = filter;
        
        // Update active pill
        this.elements.filterPills.forEach(pill => {
            pill.classList.toggle('active', pill.dataset.filter === filter);
        });
        
        // Filter instructors
        if (filter === 'all') {
            this.filteredInstructors = [...this.instructors];
        } else {
            this.filteredInstructors = this.instructors.filter(instructor => {
                return instructor.specialties.some(s => s.toLowerCase() === filter);
            });
        }
        
        // Re-render
        this.renderInstructors();
    }
    
    async loadFeaturedInstructor() {
        try {
            const response = await fetch('/api/instructors/featured');
            if (!response.ok) return;
            
            const featured = await response.json();
            
            // Update featured section
            document.getElementById('featured-name').textContent = featured.name;
            // Update other featured content...
            
        } catch (error) {
            console.error('Error loading featured instructor:', error);
        }
    }
    
    async handlePrivateBooking(instructor) {
        // Could open a modal or redirect to booking page
        window.location.href = `/book/private?instructor=${instructor.slug}`;
    }
    
    initLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.add('loaded');
                        observer.unobserve(img);
                    }
                });
            });
            
            const images = this.elements.grid.querySelectorAll('.instructor-image[data-src]');
            images.forEach(img => imageObserver.observe(img));
        }
    }
    
    initAnimations() {
        // Add scroll animations
        const cards = this.elements.grid.querySelectorAll('.instructor-card');
        
        if ('IntersectionObserver' in window) {
            const animationObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-in');
                    }
                });
            }, {
                threshold: 0.1
            });
            
            cards.forEach(card => animationObserver.observe(card));
        }
    }
    
    showLoading(show) {
        if (this.elements.loadingState) {
            this.elements.loadingState.hidden = !show;
            this.elements.loadingState.setAttribute('aria-busy', show);
        }
    }
    
    showError(message) {
        const error = document.createElement('div');
        error.className = 'error-message';
        error.textContent = message;
        error.setAttribute('role', 'alert');
        
        this.elements.grid.parentNode.insertBefore(error, this.elements.grid);
        
        setTimeout(() => error.remove(), 5000);
    }
}

// Initialize
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new InstructorsManager());
} else {
    new InstructorsManager();
}

export default InstructorsManager;
```

### 4. Gallery Module (`static/js/gallery.js`)

```javascript
/**
 * Photo Gallery Module
 * Handles image gallery with lightbox functionality
 */

class Gallery {
    constructor(container) {
        this.container = container;
        this.images = [];
        this.currentIndex = 0;
        
        this.lightbox = document.getElementById('lightbox');
        this.lightboxImage = document.getElementById('lightbox-image');
        this.lightboxCaption = document.querySelector('.lightbox-caption');
        
        this.init();
    }
    
    init() {
        if (!this.container) return;
        
        // Get all gallery images
        this.images = Array.from(this.container.querySelectorAll('.gallery-image'));
        
        // Set up click handlers
        this.images.forEach((img, index) => {
            img.addEventListener('click', () => this.openLightbox(index));
        });
        
        // Set up lightbox controls
        this.setupLightboxControls();
        
        // Set up keyboard navigation
        this.setupKeyboardNavigation();
        
        // Initialize lazy loading
        this.initLazyLoading();
    }
    
    openLightbox(index) {
        this.currentIndex = index;
        const image = this.images[index];
        
        // Set image source and caption
        this.lightboxImage.src = image.dataset.fullSrc || image.src;
        this.lightboxImage.alt = image.alt;
        this.lightboxCaption.textContent = image.dataset.caption || image.alt;
        
        // Show lightbox
        this.lightbox.hidden = false;
        this.lightbox.classList.add('active');
        
        // Trap focus
        this.trapFocus();
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
    }
    
    closeLightbox() {
        this.lightbox.classList.remove('active');
        
        setTimeout(() => {
            this.lightbox.hidden = true;
            this.lightboxImage.src = '';
        }, 300);
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        // Return focus to trigger element
        this.images[this.currentIndex].focus();
    }
    
    nextImage() {
        this.currentIndex = (this.currentIndex + 1) % this.images.length;
        this.updateLightboxImage();
    }
    
    prevImage() {
        this.currentIndex = (this.currentIndex - 1 + this.images.length) % this.images.length;
        this.updateLightboxImage();
    }
    
    updateLightboxImage() {
        const image = this.images[this.currentIndex];
        
        // Fade out
        this.lightboxImage.style.opacity = '0';
        
        setTimeout(() => {
            // Update image
            this.lightboxImage.src = image.dataset.fullSrc || image.src;
            this.lightboxImage.alt = image.alt;
            this.lightboxCaption.textContent = image.dataset.caption || image.alt;
            
            // Fade in
            this.lightboxImage.style.opacity = '1';
        }, 200);
    }
    
    setupLightboxControls() {
        // Close button
        const closeBtn = this.lightbox.querySelector('.lightbox-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closeLightbox());
        }
        
        // Previous button
        const prevBtn = this.lightbox.querySelector('.lightbox-prev');
        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.prevImage());
        }
        
        // Next button
        const nextBtn = this.lightbox.querySelector('.lightbox-next');
        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.nextImage());
        }
        
        // Click outside to close
        this.lightbox.addEventListener('click', (e) => {
            if (e.target === this.lightbox) {
                this.closeLightbox();
            }
        });
    }
    
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            if (this.lightbox.hidden) return;
            
            switch (e.key) {
                case 'Escape':
                    this.closeLightbox();
                    break;
                case 'ArrowLeft':
                    this.prevImage();
                    break;
                case 'ArrowRight':
                    this.nextImage();
                    break;
            }
        });
    }
    
    trapFocus() {
        const focusableElements = this.lightbox.querySelectorAll(
            'button, [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements.length === 0) return;
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        firstElement.focus();
        
        this.handleTabKey = (e) => {
            if (e.key !== 'Tab') return;
            
            if (e.shiftKey) {
                if (document.activeElement === firstElement) {
                    e.preventDefault();
                    lastElement.focus();
                }
            } else {
                if (document.activeElement === lastElement) {
                    e.preventDefault();
                    firstElement.focus();
                }
            }
        };
        
        document.addEventListener('keydown', this.handleTabKey);
    }
    
    initLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.removeAttribute('data-src');
                        }
                        img.classList.add('loaded');
                        observer.unobserve(img);
                    }
                });
            }, {
                rootMargin: '50px'
            });
            
            this.images.forEach(img => {
                if (img.dataset.src) {
                    imageObserver.observe(img);
                }
            });
        }
    }
}

// Auto-initialize galleries
document.addEventListener('DOMContentLoaded', () => {
    const galleries = document.querySelectorAll('.photo-grid, .video-grid');
    galleries.forEach(gallery => new Gallery(gallery));
});

export default Gallery;
```

### 5. Vercel Serverless API (`api/instructors/index.js`)

```javascript
/**
 * Instructors API Endpoint
 * Returns list of all instructors with filtering
 */

export default async function handler(req, res) {
    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate');
    
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }
    
    if (req.method !== 'GET') {
        res.status(405).json({ error: 'Method not allowed' });
        return;
    }
    
    try {
        // Mock data - replace with database query
        const instructors = [
            {
                id: 'inst_001',
                slug: 'maria-rodriguez',
                name: 'Maria Rodriguez',
                title: 'Lead Salsa Instructor',
                image: '/static/images/instructors/maria-rodriguez.jpg',
                bioShort: 'World-class salsa instructor with 15+ years of experience teaching and performing internationally.',
                bioFull: 'Maria Rodriguez is a passionate salsa instructor who has dedicated her life to sharing the joy of Latin dance. With over 15 years of teaching experience and performances in more than 20 countries, Maria brings a unique blend of technical expertise and infectious enthusiasm to every class.',
                specialties: ['Salsa', 'Bachata', 'Latin Mix'],
                yearsExperience: 15,
                classesPerWeek: 8,
                rating: 4.9,
                reviewCount: 156,
                certifications: [
                    'International Dance Council Certified',
                    'World Salsa Federation Instructor',
                    'CPR & First Aid Certified'
                ],
                awards: [
                    'World Salsa Championship Finalist 2019',
                    'Best Instructor Award - SF Dance Festival 2020',
                    'Excellence in Teaching - Latin Dance Association 2021'
                ],
                languages: ['English', 'Spanish', 'Portuguese'],
                social: {
                    instagram: '@maria_salsa_sf',
                    facebook: 'mariarodriguezdance',
                    youtube: 'MariaRodriguezDance'
                }
            },
            {
                id: 'inst_002',
                slug: 'carlos-mendez',
                name: 'Carlos Mendez',
                title: 'Bachata & Salsa Instructor',
                image: '/static/images/instructors/carlos-mendez.jpg',
                bioShort: 'Specializing in sensual bachata and Cuban salsa with a focus on musicality and connection.',
                bioFull: 'Carlos Mendez brings the authentic flavors of Dominican bachata and Cuban salsa to San Francisco. His teaching style emphasizes the importance of connection, musicality, and the cultural roots of Latin dance.',
                specialties: ['Bachata', 'Salsa', 'Private Lessons'],
                yearsExperience: 10,
                classesPerWeek: 6,
                rating: 4.8,
                reviewCount: 98,
                certifications: [
                    'Bachata Sensual Certified Instructor',
                    'Cuban Salsa Specialist',
                    'Dance Kinesiology Certificate'
                ],
                awards: [
                    'Bachata Championship Winner 2018',
                    'Rising Star Instructor 2019'
                ],
                languages: ['English', 'Spanish'],
                social: {
                    instagram: '@carlos_bachata',
                    facebook: 'carlosmendezdance'
                }
            },
            {
                id: 'inst_003',
                slug: 'lisa-chen',
                name: 'Lisa Chen',
                title: 'Latin Fusion Instructor',
                image: '/static/images/instructors/lisa-chen.jpg',
                bioShort: 'Innovative instructor blending traditional Latin styles with modern dance techniques.',
                bioFull: 'Lisa Chen is known for her creative approach to Latin dance, seamlessly blending traditional styles with contemporary movement. Her classes are energetic, inclusive, and perfect for dancers looking to expand their horizons.',
                specialties: ['Latin Mix', 'Salsa', 'Contemporary Latin'],
                yearsExperience: 8,
                classesPerWeek: 5,
                rating: 4.7,
                reviewCount: 72,
                certifications: [
                    'Contemporary Dance MFA',
                    'Latin Dance Instructor Certification',
                    'Yoga Alliance 200-hour RYT'
                ],
                awards: [
                    'Innovative Choreography Award 2020',
                    'Best Fusion Performance 2021'
                ],
                languages: ['English', 'Mandarin', 'Spanish'],
                social: {
                    instagram: '@lisa_latin_fusion',
                    youtube: 'LisaChenDance'
                }
            }
        ];
        
        // Apply filters if provided
        let filteredInstructors = instructors;
        
        const { specialty, availability } = req.query;
        
        if (specialty) {
            filteredInstructors = filteredInstructors.filter(inst => 
                inst.specialties.some(s => s.toLowerCase() === specialty.toLowerCase())
            );
        }
        
        // Sort by rating
        filteredInstructors.sort((a, b) => b.rating - a.rating);
        
        res.status(200).json({
            success: true,
            instructors: filteredInstructors,
            meta: {
                total: filteredInstructors.length
            }
        });
        
    } catch (error) {
        console.error('Error fetching instructors:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to fetch instructors'
        });
    }
}
```

### 6. Instructors CSS (`static/css/instructors.css`)

```css
/* Instructors Page Styles */

.page-header {
    background: linear-gradient(135deg, var(--primary-color), var(--dark-color));
    color: var(--white);
    padding: 4rem 0 2rem;
    margin-top: var(--nav-height);
    text-align: center;
}

.page-header h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}

/* Filter Pills */
.instructor-filters {
    background: var(--white);
    padding: 2rem 0;
    border-bottom: 1px solid var(--secondary-color);
    position: sticky;
    top: var(--nav-height);
    z-index: 100;
}

.filter-pills {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.filter-pill {
    padding: 0.5rem 1.5rem;
    background: transparent;
    border: 2px solid var(--secondary-color);
    border-radius: 25px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 500;
}

.filter-pill:hover {
    border-color: var(--primary-color);
    background: var(--secondary-color);
}

.filter-pill.active {
    background: var(--primary-color);
    color: var(--white);
    border-color: var(--primary-color);
}

/* Instructors Grid */
.instructors-section {
    padding: 3rem 0;
    background: #f9f9f9;
}

.instructors-grid {
    display: grid;
    gap: 2rem;
    animation: fadeIn 0.5s ease;
}

@media (min-width: 768px) {
    .instructors-grid {
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    }
}

/* Instructor Card */
.instructor-card {
    background: var(--white);
    border-radius: var(--card-radius);
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    transition: all 0.3s ease;
    animation: slideUp 0.4s ease backwards;
}

.instructor-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.12);
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Image Wrapper */
.instructor-image-wrapper {
    position: relative;
    height: var(--profile-image-height);
    overflow: hidden;
}

.instructor-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
}

.instructor-card:hover .instructor-image {
    transform: scale(1.05);
}

.instructor-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to bottom, transparent 50%, rgba(0,0,0,0.7));
    display: flex;
    align-items: flex-end;
    justify-content: center;
    padding: 1.5rem;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.instructor-card:hover .instructor-overlay {
    opacity: 1;
}

.view-profile-btn {
    background: var(--primary-color);
    color: var(--white);
    padding: 0.75rem 2rem;
    border-radius: 25px;
    text-decoration: none;
    font-weight: 500;
    transform: translateY(20px);
    transition: all 0.3s ease;
}

.instructor-card:hover .view-profile-btn {
    transform: translateY(0);
}

/* Content */
.instructor-content {
    padding: 1.5rem;
}

.instructor-name {
    font-size: 1.5rem;
    color: var(--dark-color);
    margin-bottom: 0.25rem;
}

.instructor-title {
    color: var(--primary-color);
    font-weight: 500;
    margin-bottom: 1rem;
}

/* Specialties */
.instructor-specialties {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.specialty-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 15px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}

.badge-salsa {
    background: #FFE5E5;
    color: #D32F2F;
}

.badge-bachata {
    background: #E8F5E9;
    color: #388E3C;
}

.badge-latin {
    background: #FFF3E0;
    color: #F57C00;
}

.badge-private {
    background: #F3E5F5;
    color: #7B1FA2;
}

/* Bio */
.instructor-bio {
    color: #666;
    line-height: 1.6;
    margin-bottom: 1.5rem;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* Stats */
.instructor-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    padding: 1rem 0;
    border-top: 1px solid var(--secondary-color);
    border-bottom: 1px solid var(--secondary-color);
    margin-bottom: 1.5rem;
}

.stat {
    text-align: center;
}

.stat-value {
    display: block;
    font-size: 1.25rem;
    font-weight: bold;
    color: var(--dark-color);
}

.stat-label {
    font-size: 0.75rem;
    color: #666;
    text-transform: uppercase;
}

/* Actions */
.instructor-actions {
    display: flex;
    gap: 0.5rem;
}

.instructor-actions .btn {
    flex: 1;
}

/* Featured Instructor */
.featured-instructor {
    background: var(--white);
    padding: 4rem 0;
}

.featured-instructor h2 {
    text-align: center;
    font-size: 2rem;
    margin-bottom: 3rem;
    color: var(--dark-color);
}

.featured-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 3rem;
    align-items: center;
}

.featured-video {
    border-radius: var(--card-radius);
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.featured-video video {
    width: 100%;
    height: auto;
    display: block;
}

.featured-info h3 {
    font-size: 1.75rem;
    color: var(--dark-color);
    margin-bottom: 0.5rem;
}

.featured-title {
    color: var(--primary-color);
    font-weight: 500;
    margin-bottom: 1.5rem;
}

.featured-quote {
    font-size: 1.1rem;
    font-style: italic;
    color: #666;
    padding: 1.5rem;
    background: var(--secondary-color);
    border-left: 4px solid var(--primary-color);
    margin-bottom: 2rem;
}

.featured-achievements h4 {
    font-size: 1.25rem;
    margin-bottom: 1rem;
    color: var(--dark-color);
}

.featured-achievements ul {
    list-style: none;
    padding: 0;
}

.featured-achievements li {
    padding: 0.5rem 0;
    padding-left: 1.5rem;
    position: relative;
}

.featured-achievements li::before {
    content: '✓';
    position: absolute;
    left: 0;
    color: var(--primary-color);
    font-weight: bold;
}

/* Loading State */
.loading-state {
    text-align: center;
    padding: 4rem;
}

.spinner {
    width: 50px;
    height: 50px;
    border: 3px solid var(--secondary-color);
    border-top-color: var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Responsive Design */
@media (max-width: 768px) {
    .page-header h1 {
        font-size: 2rem;
    }
    
    .filter-pills {
        justify-content: flex-start;
        overflow-x: auto;
        padding-bottom: 0.5rem;
    }
    
    .featured-content {
        grid-template-columns: 1fr;
    }
    
    .instructor-stats {
        font-size: 0.9rem;
    }
    
    .stat-value {
        font-size: 1rem;
    }
}

/* Print Styles */
@media print {
    .instructor-filters {
        display: none;
    }
    
    .instructor-overlay {
        display: none;
    }
    
    .instructor-actions {
        display: none;
    }
    
    .instructor-card {
        break-inside: avoid;
    }
}