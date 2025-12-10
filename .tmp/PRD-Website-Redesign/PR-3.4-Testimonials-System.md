# PR 3.4: Testimonials System

## PR Metadata
- **Title**: Implement Advanced Testimonials System with Social Integration
- **Type**: Feature Implementation
- **Priority**: High
- **Dependencies**: 
  - PR 1.1: Core Navigation & Header (base layout)
  - PR 2.2: Contact System (form validation patterns)
  - PR 3.2: Media Gallery (media management patterns)
- **Target Branch**: `feature/testimonials-system`
- **Estimated Effort**: 16 hours
- **Testing Requirements**: Form validation, media upload testing, moderation workflow testing

## Implementation Overview

### Core Features
1. **Multi-format Testimonials** (text, video, audio, photo)
2. **Social Media Import** (Google Reviews, Facebook, Instagram)
3. **Interactive Testimonial Forms** with rich media upload
4. **Moderation System** with approval workflow
5. **Dynamic Display System** with filtering and search
6. **SEO-optimized Structured Data** for rich snippets
7. **Analytics Tracking** for testimonial performance

### Technical Architecture

```
Frontend (Vanilla JS)
├── TestimonialDisplay.js    // Display component with filters
├── TestimonialForm.js       // Submission form with media
├── TestimonialCarousel.js   // Rotating testimonial widget
├── TestimonialModeration.js // Admin moderation interface
└── SocialTestimonials.js    // Social media integration

Backend (Vercel Functions)
├── /api/testimonials        // CRUD operations
├── /api/testimonials/submit // Public submission endpoint
├── /api/testimonials/moderate // Admin moderation
├── /api/testimonials/import // Social media import
└── /api/testimonials/analytics // Performance tracking
```

## File Structure

```
api/
├── testimonials/
│   ├── index.js            // Main CRUD API
│   ├── submit.js           // Public submission
│   ├── moderate.js         // Moderation workflow
│   ├── import-social.js    // Social media import
│   └── analytics.js        // Analytics endpoint
├── media/
│   ├── upload-testimonial.js // Media upload handler
│   └── process-video.js    // Video processing

static/js/
├── testimonial-display.js  // Main display component
├── testimonial-form.js     // Submission form
├── testimonial-carousel.js // Carousel widget
├── testimonial-moderation.js // Admin interface
├── social-testimonials.js  // Social integration
└── testimonial-analytics.js // Analytics tracking

static/css/
├── testimonials.css        // Main testimonials styles
├── testimonial-form.css    // Form-specific styles
├── testimonial-carousel.css // Carousel styles
└── testimonial-admin.css   // Admin interface styles

templates/
├── testimonials/
│   ├── testimonials-main.html
│   ├── testimonial-form.html
│   ├── testimonial-single.html
│   └── testimonial-widget.html
└── admin/
    └── testimonial-moderation.html
```

## Implementation Details

### 1. Advanced Testimonial Display System

**File: `static/js/testimonial-display.js`**
```javascript
class TestimonialDisplay {
  constructor(container, options = {}) {
    this.container = document.querySelector(container);
    this.options = {
      layout: 'grid', // grid, carousel, masonry, list
      itemsPerPage: 9,
      enableFilters: true,
      enableSearch: true,
      enableSorting: true,
      showRatings: true,
      showDates: true,
      showSocialSource: true,
      autoPlay: false,
      filters: {
        type: ['all', 'text', 'video', 'audio', 'photo'],
        rating: [1, 2, 3, 4, 5],
        source: ['all', 'website', 'google', 'facebook', 'instagram'],
        category: ['all', 'salsa', 'bachata', 'merengue', 'private-lessons', 'events']
      },
      ...options
    };
    
    this.currentPage = 1;
    this.currentFilters = {
      type: 'all',
      rating: null,
      source: 'all',
      category: 'all',
      search: ''
    };
    this.testimonials = [];
    this.filteredTestimonials = [];
    this.isLoading = false;
  }

  async initialize() {
    try {
      await this.loadTestimonials();
      this.render();
      this.setupEventListeners();
      this.setupIntersectionObserver();
      
      // Setup structured data for SEO
      this.addStructuredData();
      
    } catch (error) {
      console.error('Failed to initialize testimonials:', error);
      this.showErrorState();
    }
  }

  async loadTestimonials(page = 1) {
    if (this.isLoading) return;
    
    this.isLoading = true;
    this.showLoadingState(page === 1);
    
    try {
      const params = new URLSearchParams({
        page,
        limit: this.options.itemsPerPage,
        status: 'approved', // Only show approved testimonials
        ...this.currentFilters
      });
      
      const response = await fetch(`/api/testimonials?${params}`);
      
      if (!response.ok) {
        throw new Error(`Testimonials API error: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (page === 1) {
        this.testimonials = data.testimonials;
      } else {
        this.testimonials.push(...data.testimonials);
      }
      
      this.hasMore = data.hasMore;
      this.totalCount = data.total;
      
      this.applyFiltersAndSort();
      
    } catch (error) {
      console.error('Error loading testimonials:', error);
      this.showErrorState();
    } finally {
      this.isLoading = false;
      this.hideLoadingState();
    }
  }

  render() {
    const testimonialHTML = `
      <div class="testimonials-container">
        ${this.renderHeader()}
        ${this.options.enableFilters ? this.renderFilters() : ''}
        ${this.renderStats()}
        
        <div class="testimonials-display ${this.options.layout}">
          <div class="testimonials-grid" id="testimonials-grid">
            ${this.renderTestimonials()}
          </div>
          
          <div class="testimonials-loading" id="testimonials-loading" style="display: none;">
            <div class="loading-spinner"></div>
            <p>Loading more testimonials...</p>
          </div>
          
          <div class="testimonials-end" id="testimonials-end" style="display: none;">
            <p>You've seen all our amazing testimonials!</p>
            <button class="btn-primary" onclick="document.querySelector('#testimonial-form').scrollIntoView()">
              Share Your Experience
            </button>
          </div>
        </div>
        
        ${this.renderSubmissionCTA()}
      </div>
    `;
    
    this.container.innerHTML = testimonialHTML;
    
    // Initialize layout-specific features
    if (this.options.layout === 'carousel') {
      this.initializeCarousel();
    } else if (this.options.layout === 'masonry') {
      this.initializeMasonry();
    }
  }

  renderHeader() {
    const averageRating = this.calculateAverageRating();
    const totalReviews = this.totalCount || this.testimonials.length;
    
    return `
      <div class="testimonials-header">
        <h2>What Our Students Say</h2>
        <div class="testimonials-summary">
          <div class="rating-summary">
            <div class="stars-display">
              ${this.renderStars(averageRating)}
              <span class="rating-number">${averageRating.toFixed(1)}</span>
            </div>
            <p>${totalReviews} reviews from our amazing dance community</p>
          </div>
          ${this.options.showSocialSource ? `
            <div class="social-badges">
              <div class="social-badge google">
                <img src="/static/images/google-logo.svg" alt="Google">
                <span>Google Reviews</span>
              </div>
              <div class="social-badge facebook">
                <img src="/static/images/facebook-logo.svg" alt="Facebook">
                <span>Facebook</span>
              </div>
            </div>
          ` : ''}
        </div>
      </div>
    `;
  }

  renderFilters() {
    return `
      <div class="testimonials-filters">
        <div class="filter-group">
          <label>Type:</label>
          <select class="filter-select" data-filter="type">
            <option value="all">All Types</option>
            <option value="text">Text Reviews</option>
            <option value="video">Video Reviews</option>
            <option value="audio">Audio Reviews</option>
            <option value="photo">Photo Reviews</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Rating:</label>
          <select class="filter-select" data-filter="rating">
            <option value="">All Ratings</option>
            <option value="5">5 Stars</option>
            <option value="4">4+ Stars</option>
            <option value="3">3+ Stars</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Class Type:</label>
          <select class="filter-select" data-filter="category">
            <option value="all">All Classes</option>
            <option value="salsa">Salsa</option>
            <option value="bachata">Bachata</option>
            <option value="merengue">Merengue</option>
            <option value="private-lessons">Private Lessons</option>
            <option value="events">Events</option>
          </select>
        </div>
        
        <div class="filter-group search-group">
          <label>Search:</label>
          <input 
            type="text" 
            class="search-input" 
            placeholder="Search testimonials..."
            value="${this.currentFilters.search}"
          >
          <button class="search-clear" style="${this.currentFilters.search ? '' : 'display: none;'}">
            ×
          </button>
        </div>
        
        <button class="filters-clear" id="clear-filters">Clear All</button>
      </div>
    `;
  }

  renderStats() {
    return `
      <div class="testimonials-stats">
        <span class="testimonials-count">
          ${this.filteredTestimonials.length} testimonial${this.filteredTestimonials.length === 1 ? '' : 's'}
        </span>
        ${Object.entries(this.currentFilters).some(([key, value]) => value && value !== 'all') ? `
          <div class="active-filters">
            ${Object.entries(this.currentFilters)
              .filter(([key, value]) => value && value !== 'all')
              .map(([key, value]) => `
                <span class="filter-tag" data-filter="${key}">
                  ${this.formatFilterValue(key, value)}
                  <button class="remove-filter" data-filter="${key}">×</button>
                </span>
              `).join('')}
          </div>
        ` : ''}
      </div>
    `;
  }

  renderTestimonials() {
    if (this.filteredTestimonials.length === 0) {
      return this.renderEmptyState();
    }
    
    return this.filteredTestimonials.map(testimonial => this.renderTestimonial(testimonial)).join('');
  }

  renderTestimonial(testimonial) {
    const testimonialClass = `testimonial-card ${testimonial.type} ${testimonial.featured ? 'featured' : ''}`;
    
    return `
      <article class="${testimonialClass}" data-id="${testimonial.id}" itemscope itemtype="https://schema.org/Review">
        <div class="testimonial-header">
          <div class="customer-info">
            <div class="customer-avatar">
              ${testimonial.customer.avatar ? 
                `<img src="${testimonial.customer.avatar}" alt="${testimonial.customer.name}" loading="lazy">` :
                `<div class="avatar-placeholder">${testimonial.customer.name.charAt(0).toUpperCase()}</div>`
              }
            </div>
            <div class="customer-details">
              <h3 class="customer-name" itemprop="author">${testimonial.customer.name}</h3>
              ${testimonial.customer.title ? `<p class="customer-title">${testimonial.customer.title}</p>` : ''}
              ${this.options.showDates ? `
                <time class="testimonial-date" datetime="${testimonial.createdAt}" itemprop="datePublished">
                  ${this.formatDate(testimonial.createdAt)}
                </time>
              ` : ''}
            </div>
          </div>
          
          <div class="testimonial-meta">
            ${this.options.showRatings && testimonial.rating ? `
              <div class="rating-display" itemprop="reviewRating" itemscope itemtype="https://schema.org/Rating">
                <div class="stars">
                  ${this.renderStars(testimonial.rating)}
                </div>
                <meta itemprop="ratingValue" content="${testimonial.rating}">
                <meta itemprop="bestRating" content="5">
              </div>
            ` : ''}
            
            ${this.options.showSocialSource && testimonial.source !== 'website' ? `
              <div class="source-badge ${testimonial.source}">
                <img src="/static/images/${testimonial.source}-logo.svg" alt="${testimonial.source}">
              </div>
            ` : ''}
          </div>
        </div>
        
        <div class="testimonial-content" itemprop="reviewBody">
          ${this.renderTestimonialContent(testimonial)}
        </div>
        
        ${testimonial.category ? `
          <div class="testimonial-category">
            <span class="category-tag">${this.formatCategory(testimonial.category)}</span>
          </div>
        ` : ''}
        
        <div class="testimonial-actions">
          <button class="action-button helpful" data-id="${testimonial.id}" title="Mark as helpful">
            <span class="icon">👍</span>
            <span class="count">${testimonial.helpfulCount || 0}</span>
          </button>
          <button class="action-button share" data-id="${testimonial.id}" title="Share testimonial">
            <span class="icon">📤</span>
            Share
          </button>
          ${testimonial.type === 'video' || testimonial.type === 'audio' ? `
            <button class="action-button play-pause" data-id="${testimonial.id}" title="Play/Pause">
              <span class="icon">▶️</span>
              <span class="duration">${this.formatDuration(testimonial.duration)}</span>
            </button>
          ` : ''}
        </div>
        
        <!-- Schema.org structured data -->
        <div itemprop="itemReviewed" itemscope itemtype="https://schema.org/LocalBusiness" style="display: none;">
          <meta itemprop="name" content="Sabor con Flow Dance Studio">
        </div>
      </article>
    `;
  }

  renderTestimonialContent(testimonial) {
    switch (testimonial.type) {
      case 'video':
        return `
          <div class="video-testimonial">
            <video 
              poster="${testimonial.thumbnail}"
              preload="metadata"
              controls
              class="testimonial-video"
              data-id="${testimonial.id}"
            >
              <source src="${testimonial.videoUrl}" type="video/mp4">
              Your browser does not support the video tag.
            </video>
            ${testimonial.transcript ? `
              <details class="video-transcript">
                <summary>View Transcript</summary>
                <p>${testimonial.transcript}</p>
              </details>
            ` : ''}
          </div>
        `;
      
      case 'audio':
        return `
          <div class="audio-testimonial">
            <div class="audio-player" data-id="${testimonial.id}">
              <button class="audio-play-button">
                <span class="play-icon">▶️</span>
                <span class="pause-icon" style="display: none;">⏸️</span>
              </button>
              <div class="audio-waveform">
                <div class="waveform-progress"></div>
              </div>
              <span class="audio-duration">${this.formatDuration(testimonial.duration)}</span>
            </div>
            <audio preload="none" data-id="${testimonial.id}">
              <source src="${testimonial.audioUrl}" type="audio/mp3">
              Your browser does not support the audio element.
            </audio>
            ${testimonial.transcript ? `<p class="audio-transcript">${testimonial.transcript}</p>` : ''}
          </div>
        `;
      
      case 'photo':
        return `
          <div class="photo-testimonial">
            <div class="photo-gallery">
              ${testimonial.photos.map(photo => `
                <img 
                  src="${photo.url}" 
                  alt="${photo.caption || 'Customer photo'}"
                  class="testimonial-photo"
                  loading="lazy"
                  onclick="this.closest('.testimonials-container').dispatchEvent(new CustomEvent('openLightbox', {detail: {photo: '${photo.url}', caption: '${photo.caption || ''}'}}))"
                >
              `).join('')}
            </div>
            ${testimonial.text ? `<p class="photo-caption">${testimonial.text}</p>` : ''}
          </div>
        `;
      
      default: // text
        return `
          <div class="text-testimonial">
            <blockquote>
              <p>${this.formatTestimonialText(testimonial.text)}</p>
            </blockquote>
          </div>
        `;
    }
  }

  renderEmptyState() {
    return `
      <div class="testimonials-empty">
        <div class="empty-icon">💭</div>
        <h3>No testimonials found</h3>
        <p>Try adjusting your filters or be the first to share your experience!</p>
        <button class="btn-primary" onclick="document.querySelector('#testimonial-form').scrollIntoView()">
          Write a Review
        </button>
      </div>
    `;
  }

  renderSubmissionCTA() {
    return `
      <div class="testimonial-cta">
        <div class="cta-content">
          <h3>Share Your Dance Journey</h3>
          <p>Help others discover the joy of dancing at Sabor con Flow!</p>
          <div class="cta-options">
            <button class="btn-primary cta-button" data-type="text">
              ✏️ Write a Review
            </button>
            <button class="btn-secondary cta-button" data-type="video">
              🎥 Record a Video
            </button>
            <button class="btn-secondary cta-button" data-type="audio">
              🎤 Leave Voice Message
            </button>
          </div>
        </div>
      </div>
    `;
  }

  setupEventListeners() {
    // Filter handling
    this.container.addEventListener('change', (e) => {
      if (e.target.classList.contains('filter-select')) {
        const filterType = e.target.dataset.filter;
        const filterValue = e.target.value;
        this.applyFilter(filterType, filterValue);
      }
    });

    // Search handling
    const searchInput = this.container.querySelector('.search-input');
    if (searchInput) {
      let searchTimeout;
      searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
          this.applyFilter('search', e.target.value.trim());
        }, 300);
      });
    }

    // Clear filters
    this.container.addEventListener('click', (e) => {
      if (e.target.id === 'clear-filters') {
        this.clearAllFilters();
      } else if (e.target.classList.contains('remove-filter')) {
        const filterType = e.target.dataset.filter;
        this.removeFilter(filterType);
      } else if (e.target.classList.contains('search-clear')) {
        searchInput.value = '';
        this.applyFilter('search', '');
      }
    });

    // Testimonial actions
    this.container.addEventListener('click', (e) => {
      if (e.target.closest('.helpful')) {
        const testimonialId = e.target.closest('.helpful').dataset.id;
        this.markAsHelpful(testimonialId);
      } else if (e.target.closest('.share')) {
        const testimonialId = e.target.closest('.share').dataset.id;
        this.shareTestimonial(testimonialId);
      } else if (e.target.closest('.cta-button')) {
        const type = e.target.closest('.cta-button').dataset.type;
        this.openTestimonialForm(type);
      }
    });

    // Audio/Video controls
    this.setupMediaControls();

    // Lightbox for photos
    this.container.addEventListener('openLightbox', (e) => {
      this.openPhotoLightbox(e.detail);
    });
  }

  setupMediaControls() {
    // Audio player controls
    this.container.addEventListener('click', (e) => {
      if (e.target.closest('.audio-play-button')) {
        const playButton = e.target.closest('.audio-play-button');
        const audioPlayer = playButton.closest('.audio-testimonial');
        const audio = audioPlayer.querySelector('audio');
        
        if (audio.paused) {
          this.playAudio(audio, playButton);
        } else {
          this.pauseAudio(audio, playButton);
        }
      }
    });

    // Video tracking
    this.container.addEventListener('play', (e) => {
      if (e.target.classList.contains('testimonial-video')) {
        this.trackMediaPlay(e.target.dataset.id, 'video');
      }
    }, true);

    this.container.addEventListener('ended', (e) => {
      if (e.target.classList.contains('testimonial-video')) {
        this.trackMediaComplete(e.target.dataset.id, 'video');
      }
    }, true);
  }

  setupIntersectionObserver() {
    // Lazy loading for infinite scroll
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && this.hasMore && !this.isLoading) {
          this.currentPage++;
          this.loadTestimonials(this.currentPage);
        }
      });
    }, { threshold: 0.1 });

    // Observe scroll trigger
    const scrollTrigger = document.createElement('div');
    scrollTrigger.className = 'scroll-trigger';
    this.container.querySelector('.testimonials-grid').appendChild(scrollTrigger);
    observer.observe(scrollTrigger);
  }

  applyFilter(filterType, filterValue) {
    this.currentFilters[filterType] = filterValue;
    this.currentPage = 1;
    
    // Update search clear button visibility
    if (filterType === 'search') {
      const clearButton = this.container.querySelector('.search-clear');
      if (clearButton) {
        clearButton.style.display = filterValue ? '' : 'none';
      }
    }
    
    this.applyFiltersAndSort();
    this.updateDisplay();
  }

  applyFiltersAndSort() {
    this.filteredTestimonials = this.testimonials.filter(testimonial => {
      // Type filter
      if (this.currentFilters.type !== 'all' && testimonial.type !== this.currentFilters.type) {
        return false;
      }
      
      // Rating filter
      if (this.currentFilters.rating && testimonial.rating < parseInt(this.currentFilters.rating)) {
        return false;
      }
      
      // Source filter
      if (this.currentFilters.source !== 'all' && testimonial.source !== this.currentFilters.source) {
        return false;
      }
      
      // Category filter
      if (this.currentFilters.category !== 'all' && testimonial.category !== this.currentFilters.category) {
        return false;
      }
      
      // Search filter
      if (this.currentFilters.search) {
        const searchTerm = this.currentFilters.search.toLowerCase();
        const searchableText = [
          testimonial.text,
          testimonial.transcript,
          testimonial.customer.name,
          testimonial.category
        ].filter(Boolean).join(' ').toLowerCase();
        
        if (!searchableText.includes(searchTerm)) {
          return false;
        }
      }
      
      return true;
    });

    // Sort testimonials (featured first, then by date)
    this.filteredTestimonials.sort((a, b) => {
      if (a.featured && !b.featured) return -1;
      if (!a.featured && b.featured) return 1;
      return new Date(b.createdAt) - new Date(a.createdAt);
    });
  }

  updateDisplay() {
    const grid = this.container.querySelector('.testimonials-grid');
    grid.innerHTML = this.renderTestimonials();
    
    // Update stats
    const stats = this.container.querySelector('.testimonials-stats');
    stats.innerHTML = this.renderStats().match(/<div class="testimonials-stats">(.*?)<\/div>/s)[1];
    
    // Reinitialize media controls for new content
    this.setupMediaControls();
  }

  async markAsHelpful(testimonialId) {
    try {
      const response = await fetch(`/api/testimonials/${testimonialId}/helpful`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const result = await response.json();
        
        // Update the count in the UI
        const button = this.container.querySelector(`[data-id="${testimonialId}"].helpful .count`);
        if (button) {
          button.textContent = result.helpfulCount;
        }
        
        // Disable the button to prevent multiple votes
        const helpfulButton = this.container.querySelector(`[data-id="${testimonialId}"].helpful`);
        helpfulButton.disabled = true;
        helpfulButton.classList.add('voted');
        
        this.trackEvent('testimonial_helpful', { testimonial_id: testimonialId });
      }
    } catch (error) {
      console.error('Error marking testimonial as helpful:', error);
    }
  }

  shareTestimonial(testimonialId) {
    const testimonial = this.testimonials.find(t => t.id === testimonialId);
    if (!testimonial) return;
    
    const shareUrl = `${window.location.origin}/testimonials/${testimonialId}`;
    const shareText = `Check out this amazing review of Sabor con Flow: "${testimonial.text.substring(0, 100)}..."`;
    
    if (navigator.share) {
      navigator.share({
        title: 'Sabor con Flow Testimonial',
        text: shareText,
        url: shareUrl
      }).then(() => {
        this.trackEvent('testimonial_shared', { 
          testimonial_id: testimonialId,
          method: 'native'
        });
      }).catch(console.error);
    } else {
      // Fallback to copying URL
      navigator.clipboard.writeText(shareUrl).then(() => {
        this.showToast('Testimonial link copied to clipboard!');
        this.trackEvent('testimonial_shared', { 
          testimonial_id: testimonialId,
          method: 'clipboard'
        });
      }).catch(() => {
        // Final fallback to social share
        const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`;
        window.open(facebookUrl, '_blank', 'width=600,height=400');
      });
    }
  }

  openTestimonialForm(type = 'text') {
    // Scroll to testimonial form and set the type
    const form = document.querySelector('#testimonial-form');
    if (form) {
      form.scrollIntoView({ behavior: 'smooth' });
      
      // Trigger form type selection
      const event = new CustomEvent('setTestimonialType', { detail: { type } });
      form.dispatchEvent(event);
    }
  }

  addStructuredData() {
    // Add JSON-LD structured data for rich snippets
    const structuredData = {
      "@context": "https://schema.org",
      "@type": "LocalBusiness",
      "name": "Sabor con Flow Dance Studio",
      "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": this.calculateAverageRating().toFixed(1),
        "reviewCount": this.totalCount || this.testimonials.length,
        "bestRating": "5",
        "worstRating": "1"
      },
      "review": this.testimonials.slice(0, 5).map(testimonial => ({
        "@type": "Review",
        "author": {
          "@type": "Person",
          "name": testimonial.customer.name
        },
        "reviewRating": {
          "@type": "Rating",
          "ratingValue": testimonial.rating,
          "bestRating": "5"
        },
        "reviewBody": testimonial.text,
        "datePublished": testimonial.createdAt
      }))
    };

    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify(structuredData);
    document.head.appendChild(script);
  }

  // Utility methods
  calculateAverageRating() {
    const ratingsSum = this.testimonials
      .filter(t => t.rating)
      .reduce((sum, t) => sum + t.rating, 0);
    const ratingsCount = this.testimonials.filter(t => t.rating).length;
    
    return ratingsCount > 0 ? ratingsSum / ratingsCount : 5.0;
  }

  renderStars(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    
    return [
      '★'.repeat(fullStars),
      hasHalfStar ? '☆' : '',
      '☆'.repeat(emptyStars)
    ].join('');
  }

  formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  formatCategory(category) {
    const categoryNames = {
      'salsa': 'Salsa Classes',
      'bachata': 'Bachata Classes',
      'merengue': 'Merengue Classes',
      'private-lessons': 'Private Lessons',
      'events': 'Events & Socials'
    };
    
    return categoryNames[category] || category.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
  }

  formatFilterValue(key, value) {
    const formatters = {
      type: value => value.charAt(0).toUpperCase() + value.slice(1),
      rating: value => `${value}+ Stars`,
      category: value => this.formatCategory(value),
      search: value => `"${value}"`
    };
    
    return formatters[key] ? formatters[key](value) : value;
  }

  formatTestimonialText(text) {
    // Convert line breaks to paragraphs
    return text.split('\n\n').map(paragraph => 
      paragraph.replace(/\n/g, '<br>')
    ).join('</p><p>');
  }

  formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => toast.remove(), 3000);
  }

  trackEvent(eventName, properties = {}) {
    if (typeof gtag !== 'undefined') {
      gtag('event', eventName, {
        event_category: 'Testimonials',
        ...properties
      });
    }
  }

  showLoadingState(clear = false) {
    if (clear) {
      const grid = this.container.querySelector('.testimonials-grid');
      if (grid) grid.innerHTML = '';
    }
    
    const loadingElement = this.container.querySelector('#testimonials-loading');
    if (loadingElement) {
      loadingElement.style.display = 'block';
    }
  }

  hideLoadingState() {
    const loadingElement = this.container.querySelector('#testimonials-loading');
    if (loadingElement) {
      loadingElement.style.display = 'none';
    }
  }

  showErrorState() {
    this.container.innerHTML = `
      <div class="testimonials-error">
        <div class="error-icon">⚠️</div>
        <h3>Unable to load testimonials</h3>
        <p>Please try again later</p>
        <button class="btn-primary retry-button">Retry</button>
      </div>
    `;
    
    this.container.querySelector('.retry-button').addEventListener('click', () => {
      this.initialize();
    });
  }
}

// Initialize testimonials display
document.addEventListener('DOMContentLoaded', () => {
  const testimonialsContainer = document.querySelector('#testimonials-display');
  if (testimonialsContainer) {
    const testimonials = new TestimonialDisplay('#testimonials-display', {
      layout: 'grid',
      itemsPerPage: 12,
      enableFilters: true,
      enableSearch: true,
      showSocialSource: true
    });
    
    testimonials.initialize();
  }
});
```

### 2. Advanced Testimonial Form

**File: `static/js/testimonial-form.js`**
```javascript
class TestimonialForm {
  constructor(container, options = {}) {
    this.container = document.querySelector(container);
    this.options = {
      enableMediaUpload: true,
      maxVideoSize: 50 * 1024 * 1024, // 50MB
      maxAudioSize: 10 * 1024 * 1024, // 10MB
      maxPhotoSize: 5 * 1024 * 1024,  // 5MB
      allowedVideoTypes: ['video/mp4', 'video/webm', 'video/quicktime'],
      allowedAudioTypes: ['audio/mp3', 'audio/wav', 'audio/m4a'],
      allowedPhotoTypes: ['image/jpeg', 'image/png', 'image/webp'],
      requireModeration: true,
      ...options
    };
    
    this.currentStep = 1;
    this.totalSteps = 4;
    this.formData = {
      type: 'text',
      customer: {},
      content: {},
      rating: null,
      category: null,
      media: []
    };
    this.mediaRecorder = null;
    this.recordingStream = null;
  }

  initialize() {
    this.render();
    this.setupEventListeners();
    this.setupMediaRecording();
  }

  render() {
    const formHTML = `
      <form class="testimonial-form" id="testimonial-form">
        <div class="form-header">
          <h2>Share Your Experience</h2>
          <p>Help others discover the joy of dancing at Sabor con Flow!</p>
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${(this.currentStep / this.totalSteps) * 100}%"></div>
          </div>
          <div class="step-indicator">
            Step ${this.currentStep} of ${this.totalSteps}
          </div>
        </div>

        <!-- Step 1: Choose Review Type -->
        <div class="form-step ${this.currentStep === 1 ? 'active' : ''}" data-step="1">
          <h3>How would you like to share your experience?</h3>
          <div class="review-type-options">
            <label class="type-option ${this.formData.type === 'text' ? 'selected' : ''}" data-type="text">
              <input type="radio" name="reviewType" value="text" ${this.formData.type === 'text' ? 'checked' : ''}>
              <div class="option-card">
                <div class="option-icon">✏️</div>
                <h4>Written Review</h4>
                <p>Share your thoughts in writing</p>
              </div>
            </label>
            
            <label class="type-option ${this.formData.type === 'video' ? 'selected' : ''}" data-type="video">
              <input type="radio" name="reviewType" value="video" ${this.formData.type === 'video' ? 'checked' : ''}>
              <div class="option-card">
                <div class="option-icon">🎥</div>
                <h4>Video Review</h4>
                <p>Record yourself sharing your experience</p>
              </div>
            </label>
            
            <label class="type-option ${this.formData.type === 'audio' ? 'selected' : ''}" data-type="audio">
              <input type="radio" name="reviewType" value="audio" ${this.formData.type === 'audio' ? 'checked' : ''}>
              <div class="option-card">
                <div class="option-icon">🎤</div>
                <h4>Voice Message</h4>
                <p>Leave an audio testimonial</p>
              </div>
            </label>
            
            <label class="type-option ${this.formData.type === 'photo' ? 'selected' : ''}" data-type="photo">
              <input type="radio" name="reviewType" value="photo" ${this.formData.type === 'photo' ? 'checked' : ''}>
              <div class="option-card">
                <div class="option-icon">📸</div>
                <h4>Photo Review</h4>
                <p>Share photos with your story</p>
              </div>
            </label>
          </div>
        </div>

        <!-- Step 2: Content Creation -->
        <div class="form-step ${this.currentStep === 2 ? 'active' : ''}" data-step="2">
          ${this.renderContentStep()}
        </div>

        <!-- Step 3: Rating & Category -->
        <div class="form-step ${this.currentStep === 3 ? 'active' : ''}" data-step="3">
          <h3>Tell us more about your experience</h3>
          
          <div class="form-group">
            <label>How would you rate your overall experience?</label>
            <div class="star-rating" id="star-rating">
              ${[1, 2, 3, 4, 5].map(rating => `
                <button type="button" class="star ${this.formData.rating >= rating ? 'filled' : ''}" data-rating="${rating}">
                  ★
                </button>
              `).join('')}
            </div>
          </div>
          
          <div class="form-group">
            <label for="category">Which classes or services is this review about?</label>
            <select name="category" id="category" required>
              <option value="">Select a category</option>
              <option value="salsa" ${this.formData.category === 'salsa' ? 'selected' : ''}>Salsa Classes</option>
              <option value="bachata" ${this.formData.category === 'bachata' ? 'selected' : ''}>Bachata Classes</option>
              <option value="merengue" ${this.formData.category === 'merengue' ? 'selected' : ''}>Merengue Classes</option>
              <option value="private-lessons" ${this.formData.category === 'private-lessons' ? 'selected' : ''}>Private Lessons</option>
              <option value="events" ${this.formData.category === 'events' ? 'selected' : ''}>Events & Socials</option>
              <option value="general" ${this.formData.category === 'general' ? 'selected' : ''}>General Experience</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="experience-length">How long have you been dancing with us?</label>
            <select name="experienceLength" id="experience-length">
              <option value="">Select duration</option>
              <option value="first-time">First time student</option>
              <option value="1-3months">1-3 months</option>
              <option value="3-6months">3-6 months</option>
              <option value="6months-1year">6 months - 1 year</option>
              <option value="1year+">More than 1 year</option>
            </select>
          </div>
        </div>

        <!-- Step 4: Personal Information -->
        <div class="form-step ${this.currentStep === 4 ? 'active' : ''}" data-step="4">
          <h3>Your Information</h3>
          <p class="privacy-note">Your information helps us display your testimonial authentically. We respect your privacy.</p>
          
          <div class="form-row">
            <div class="form-group">
              <label for="firstName">First Name *</label>
              <input 
                type="text" 
                name="firstName" 
                id="firstName" 
                required 
                value="${this.formData.customer.firstName || ''}"
              >
            </div>
            
            <div class="form-group">
              <label for="lastName">Last Name *</label>
              <input 
                type="text" 
                name="lastName" 
                id="lastName" 
                required 
                value="${this.formData.customer.lastName || ''}"
              >
            </div>
          </div>
          
          <div class="form-group">
            <label for="email">Email Address *</label>
            <input 
              type="email" 
              name="email" 
              id="email" 
              required 
              value="${this.formData.customer.email || ''}"
            >
            <small>We'll use this to contact you if needed. Not displayed publicly.</small>
          </div>
          
          <div class="form-group">
            <label for="phone">Phone Number (Optional)</label>
            <input 
              type="tel" 
              name="phone" 
              id="phone" 
              value="${this.formData.customer.phone || ''}"
            >
          </div>
          
          <div class="form-group">
            <label>
              <input 
                type="checkbox" 
                name="displayPublicly" 
                ${this.formData.customer.displayPublicly !== false ? 'checked' : ''}
              >
              I consent to displaying this testimonial publicly on the website
            </label>
          </div>
          
          <div class="form-group">
            <label>
              <input 
                type="checkbox" 
                name="allowMarketing" 
                ${this.formData.customer.allowMarketing ? 'checked' : ''}
              >
              I'd like to receive updates about classes and events (optional)
            </label>
          </div>
        </div>

        <!-- Form Navigation -->
        <div class="form-navigation">
          <button 
            type="button" 
            class="btn-secondary" 
            id="prev-button"
            ${this.currentStep === 1 ? 'style="visibility: hidden;"' : ''}
          >
            Previous
          </button>
          
          <button 
            type="button" 
            class="btn-primary" 
            id="next-button"
            ${this.currentStep === this.totalSteps ? 'style="display: none;"' : ''}
          >
            Next Step
          </button>
          
          <button 
            type="submit" 
            class="btn-primary" 
            id="submit-button"
            ${this.currentStep !== this.totalSteps ? 'style="display: none;"' : ''}
          >
            Submit Review
          </button>
        </div>
      </form>
      
      <!-- Media Preview Modal -->
      <div class="media-preview-modal" id="media-preview" style="display: none;">
        <div class="modal-backdrop"></div>
        <div class="modal-content">
          <div class="modal-header">
            <h3>Preview Your Media</h3>
            <button class="modal-close">&times;</button>
          </div>
          <div class="modal-body" id="preview-content">
            <!-- Media preview content -->
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" id="retake-media">Retake</button>
            <button class="btn-primary" id="accept-media">Use This Recording</button>
          </div>
        </div>
      </div>
    `;
    
    this.container.innerHTML = formHTML;
  }

  renderContentStep() {
    switch (this.formData.type) {
      case 'text':
        return this.renderTextContent();
      case 'video':
        return this.renderVideoContent();
      case 'audio':
        return this.renderAudioContent();
      case 'photo':
        return this.renderPhotoContent();
      default:
        return this.renderTextContent();
    }
  }

  renderTextContent() {
    return `
      <h3>Write Your Review</h3>
      <div class="form-group">
        <label for="testimonial-text">Share your experience with Sabor con Flow</label>
        <textarea 
          name="testimonialText" 
          id="testimonial-text" 
          rows="8" 
          placeholder="Tell us about your experience... What did you love most? How did we help you achieve your dance goals? What would you tell someone considering joining our classes?"
          required
        >${this.formData.content.text || ''}</textarea>
        <div class="character-count">
          <span id="char-count">${this.formData.content.text?.length || 0}</span>/2000 characters
        </div>
      </div>
      
      <div class="writing-tips">
        <h4>💡 Writing Tips:</h4>
        <ul>
          <li>Be specific about what you enjoyed</li>
          <li>Mention instructors or specific classes if relevant</li>
          <li>Share how dancing has impacted you</li>
          <li>Be honest and authentic</li>
        </ul>
      </div>
    `;
  }

  renderVideoContent() {
    return `
      <h3>Record Your Video Review</h3>
      <div class="video-recording-container">
        <div class="recording-preview" id="video-preview">
          <video id="camera-preview" autoplay muted></video>
          <div class="recording-controls">
            <button type="button" class="record-button" id="start-video-recording">
              <span class="record-icon">🎥</span>
              Start Recording
            </button>
            <div class="recording-timer" id="video-timer" style="display: none;">
              <span class="timer-display">00:00</span>
              <button type="button" class="stop-button" id="stop-video-recording">Stop</button>
            </div>
          </div>
        </div>
        
        ${this.formData.content.videoBlob ? `
          <div class="recorded-video">
            <video controls>
              <source src="${URL.createObjectURL(this.formData.content.videoBlob)}" type="video/mp4">
            </video>
            <button type="button" class="btn-secondary" id="retake-video">Record Again</button>
          </div>
        ` : ''}
      </div>
      
      <div class="upload-alternative">
        <p>Or upload a video file:</p>
        <input 
          type="file" 
          id="video-upload" 
          accept="${this.options.allowedVideoTypes.join(',')}"
          style="display: none;"
        >
        <button type="button" class="btn-secondary" id="video-upload-button">
          📁 Choose Video File
        </button>
      </div>
      
      <div class="video-tips">
        <h4>📹 Video Tips:</h4>
        <ul>
          <li>Keep your video under 2 minutes</li>
          <li>Ensure good lighting and audio</li>
          <li>Speak clearly and at a comfortable pace</li>
          <li>Be yourself and have fun!</li>
        </ul>
      </div>
    `;
  }

  renderAudioContent() {
    return `
      <h3>Record Your Voice Message</h3>
      <div class="audio-recording-container">
        <div class="recording-visualizer" id="audio-visualizer">
          <canvas id="audio-waveform" width="400" height="100"></canvas>
        </div>
        
        <div class="recording-controls">
          <button type="button" class="record-button" id="start-audio-recording">
            <span class="record-icon">🎤</span>
            Start Recording
          </button>
          <div class="recording-timer" id="audio-timer" style="display: none;">
            <span class="timer-display">00:00</span>
            <button type="button" class="stop-button" id="stop-audio-recording">Stop</button>
          </div>
        </div>
        
        ${this.formData.content.audioBlob ? `
          <div class="recorded-audio">
            <audio controls>
              <source src="${URL.createObjectURL(this.formData.content.audioBlob)}" type="audio/mp3">
            </audio>
            <button type="button" class="btn-secondary" id="retake-audio">Record Again</button>
          </div>
        ` : ''}
      </div>
      
      <div class="upload-alternative">
        <p>Or upload an audio file:</p>
        <input 
          type="file" 
          id="audio-upload" 
          accept="${this.options.allowedAudioTypes.join(',')}"
          style="display: none;"
        >
        <button type="button" class="btn-secondary" id="audio-upload-button">
          📁 Choose Audio File
        </button>
      </div>
      
      <div class="audio-tips">
        <h4>🎤 Audio Tips:</h4>
        <ul>
          <li>Find a quiet space for recording</li>
          <li>Hold your device close to your mouth</li>
          <li>Speak clearly and enthusiastically</li>
          <li>Keep it under 60 seconds</li>
        </ul>
      </div>
    `;
  }

  renderPhotoContent() {
    return `
      <h3>Share Photos with Your Story</h3>
      <div class="photo-upload-container">
        <div class="photo-upload-zone" id="photo-drop-zone">
          <div class="upload-icon">📸</div>
          <h4>Drag photos here or click to upload</h4>
          <p>You can upload up to 5 photos</p>
          <input 
            type="file" 
            id="photo-upload" 
            accept="${this.options.allowedPhotoTypes.join(',')}"
            multiple
            style="display: none;"
          >
          <button type="button" class="btn-primary" id="photo-upload-button">
            Choose Photos
          </button>
        </div>
        
        <div class="photo-preview-grid" id="photo-preview-grid">
          ${this.formData.content.photos ? this.formData.content.photos.map((photo, index) => `
            <div class="photo-preview" data-index="${index}">
              <img src="${URL.createObjectURL(photo.file)}" alt="Photo ${index + 1}">
              <button type="button" class="remove-photo" data-index="${index}">&times;</button>
              <input 
                type="text" 
                placeholder="Add a caption (optional)"
                class="photo-caption"
                value="${photo.caption || ''}"
                data-index="${index}"
              >
            </div>
          `).join('') : ''}
        </div>
      </div>
      
      <div class="form-group">
        <label for="photo-story">Tell us about your photos</label>
        <textarea 
          name="photoStory" 
          id="photo-story" 
          rows="4" 
          placeholder="Share the story behind your photos..."
        >${this.formData.content.story || ''}</textarea>
      </div>
      
      <div class="photo-tips">
        <h4>📷 Photo Tips:</h4>
        <ul>
          <li>Show yourself dancing or at our studio</li>
          <li>Include friends or instructors (with permission)</li>
          <li>High-quality photos work best</li>
          <li>Each photo can have its own caption</li>
        </ul>
      </div>
    `;
  }

  setupEventListeners() {
    // Step navigation
    this.container.addEventListener('click', (e) => {
      if (e.target.id === 'next-button') {
        this.nextStep();
      } else if (e.target.id === 'prev-button') {
        this.previousStep();
      }
    });

    // Form submission
    this.container.addEventListener('submit', (e) => {
      e.preventDefault();
      this.submitTestimonial();
    });

    // Review type selection
    this.container.addEventListener('change', (e) => {
      if (e.target.name === 'reviewType') {
        this.formData.type = e.target.value;
        this.updateTypeSelection();
      }
    });

    // Star rating
    this.container.addEventListener('click', (e) => {
      if (e.target.classList.contains('star')) {
        const rating = parseInt(e.target.dataset.rating);
        this.setRating(rating);
      }
    });

    // Media recording controls
    this.setupMediaEventListeners();

    // Form field updates
    this.container.addEventListener('input', (e) => {
      this.saveFormData(e.target);
    });

    // External event listener for type setting
    this.container.addEventListener('setTestimonialType', (e) => {
      this.formData.type = e.detail.type;
      this.updateTypeSelection();
    });
  }

  setupMediaEventListeners() {
    // Video recording
    this.container.addEventListener('click', (e) => {
      if (e.target.id === 'start-video-recording') {
        this.startVideoRecording();
      } else if (e.target.id === 'stop-video-recording') {
        this.stopVideoRecording();
      } else if (e.target.id === 'retake-video') {
        this.retakeVideo();
      } else if (e.target.id === 'video-upload-button') {
        document.getElementById('video-upload').click();
      }
    });

    // Audio recording
    this.container.addEventListener('click', (e) => {
      if (e.target.id === 'start-audio-recording') {
        this.startAudioRecording();
      } else if (e.target.id === 'stop-audio-recording') {
        this.stopAudioRecording();
      } else if (e.target.id === 'retake-audio') {
        this.retakeAudio();
      } else if (e.target.id === 'audio-upload-button') {
        document.getElementById('audio-upload').click();
      }
    });

    // Photo upload
    this.container.addEventListener('click', (e) => {
      if (e.target.id === 'photo-upload-button') {
        document.getElementById('photo-upload').click();
      } else if (e.target.classList.contains('remove-photo')) {
        const index = parseInt(e.target.dataset.index);
        this.removePhoto(index);
      }
    });

    // File uploads
    this.container.addEventListener('change', (e) => {
      if (e.target.id === 'video-upload') {
        this.handleVideoUpload(e.target.files[0]);
      } else if (e.target.id === 'audio-upload') {
        this.handleAudioUpload(e.target.files[0]);
      } else if (e.target.id === 'photo-upload') {
        this.handlePhotoUpload(e.target.files);
      }
    });

    // Photo drag and drop
    const dropZone = this.container.querySelector('#photo-drop-zone');
    if (dropZone) {
      dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
      });

      dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
      });

      dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        this.handlePhotoUpload(e.dataTransfer.files);
      });
    }
  }

  setupMediaRecording() {
    // Check for media API support
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.warn('Media recording not supported');
      this.options.enableMediaUpload = false;
    }
  }

  async startVideoRecording() {
    try {
      this.recordingStream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720 },
        audio: true
      });

      const preview = document.getElementById('camera-preview');
      preview.srcObject = this.recordingStream;

      this.mediaRecorder = new MediaRecorder(this.recordingStream, {
        mimeType: 'video/webm;codecs=vp8,opus'
      });

      const recordedChunks = [];
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          recordedChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = () => {
        const blob = new Blob(recordedChunks, { type: 'video/webm' });
        this.formData.content.videoBlob = blob;
        this.showVideoRecordingControls(false);
        this.updateContentStep();
      };

      this.mediaRecorder.start();
      this.showVideoRecordingControls(true);
      this.startRecordingTimer('video');

    } catch (error) {
      console.error('Error starting video recording:', error);
      this.showError('Unable to access camera. Please check permissions.');
    }
  }

  stopVideoRecording() {
    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.stop();
      this.recordingStream.getTracks().forEach(track => track.stop());
      this.stopRecordingTimer();
    }
  }

  async startAudioRecording() {
    try {
      this.recordingStream = await navigator.mediaDevices.getUserMedia({
        audio: true
      });

      this.mediaRecorder = new MediaRecorder(this.recordingStream);
      const recordedChunks = [];

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          recordedChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = () => {
        const blob = new Blob(recordedChunks, { type: 'audio/webm' });
        this.formData.content.audioBlob = blob;
        this.showAudioRecordingControls(false);
        this.updateContentStep();
      };

      this.mediaRecorder.start();
      this.showAudioRecordingControls(true);
      this.startRecordingTimer('audio');
      this.startAudioVisualization();

    } catch (error) {
      console.error('Error starting audio recording:', error);
      this.showError('Unable to access microphone. Please check permissions.');
    }
  }

  stopAudioRecording() {
    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.stop();
      this.recordingStream.getTracks().forEach(track => track.stop());
      this.stopRecordingTimer();
      this.stopAudioVisualization();
    }
  }

  async submitTestimonial() {
    try {
      this.showSubmittingState(true);

      // Prepare form data
      const submitData = new FormData();
      
      // Add basic information
      submitData.append('type', this.formData.type);
      submitData.append('rating', this.formData.rating);
      submitData.append('category', this.formData.category);
      submitData.append('customer', JSON.stringify(this.formData.customer));

      // Add content based on type
      switch (this.formData.type) {
        case 'text':
          submitData.append('text', this.formData.content.text);
          break;
        
        case 'video':
          if (this.formData.content.videoBlob) {
            submitData.append('video', this.formData.content.videoBlob, 'testimonial-video.webm');
          }
          break;
        
        case 'audio':
          if (this.formData.content.audioBlob) {
            submitData.append('audio', this.formData.content.audioBlob, 'testimonial-audio.webm');
          }
          break;
        
        case 'photo':
          if (this.formData.content.photos) {
            this.formData.content.photos.forEach((photo, index) => {
              submitData.append(`photo_${index}`, photo.file);
              submitData.append(`photo_${index}_caption`, photo.caption || '');
            });
          }
          submitData.append('story', this.formData.content.story || '');
          break;
      }

      const response = await fetch('/api/testimonials/submit', {
        method: 'POST',
        body: submitData
      });

      if (response.ok) {
        const result = await response.json();
        this.showSuccessMessage(result);
        this.trackEvent('testimonial_submitted', { 
          type: this.formData.type,
          rating: this.formData.rating 
        });
      } else {
        const error = await response.json();
        throw new Error(error.message || 'Submission failed');
      }

    } catch (error) {
      console.error('Error submitting testimonial:', error);
      this.showError(error.message || 'Failed to submit testimonial. Please try again.');
    } finally {
      this.showSubmittingState(false);
    }
  }

  showSuccessMessage(result) {
    this.container.innerHTML = `
      <div class="testimonial-success">
        <div class="success-icon">🎉</div>
        <h2>Thank you for your testimonial!</h2>
        <p>Your review has been submitted successfully.</p>
        
        ${this.options.requireModeration ? `
          <div class="moderation-notice">
            <p>Your testimonial will be reviewed and published within 24 hours.</p>
            <p>We'll send you an email confirmation once it's live!</p>
          </div>
        ` : `
          <div class="published-notice">
            <p>Your testimonial is now live on our website!</p>
            <a href="/testimonials#${result.id}" class="btn-primary">View Your Review</a>
          </div>
        `}
        
        <div class="success-actions">
          <button class="btn-secondary" onclick="window.location.reload()">
            Submit Another Review
          </button>
          <a href="/" class="btn-primary">Back to Home</a>
        </div>
      </div>
    `;
  }

  // Utility methods
  nextStep() {
    if (this.validateCurrentStep()) {
      this.currentStep++;
      this.updateStepDisplay();
    }
  }

  previousStep() {
    if (this.currentStep > 1) {
      this.currentStep--;
      this.updateStepDisplay();
    }
  }

  updateStepDisplay() {
    // Hide all steps
    this.container.querySelectorAll('.form-step').forEach(step => {
      step.classList.remove('active');
    });

    // Show current step
    const currentStep = this.container.querySelector(`[data-step="${this.currentStep}"]`);
    if (currentStep) {
      currentStep.classList.add('active');
    }

    // Update progress bar
    const progressFill = this.container.querySelector('.progress-fill');
    progressFill.style.width = `${(this.currentStep / this.totalSteps) * 100}%`;

    // Update step indicator
    const stepIndicator = this.container.querySelector('.step-indicator');
    stepIndicator.textContent = `Step ${this.currentStep} of ${this.totalSteps}`;

    // Update navigation buttons
    const prevButton = document.getElementById('prev-button');
    const nextButton = document.getElementById('next-button');
    const submitButton = document.getElementById('submit-button');

    prevButton.style.visibility = this.currentStep === 1 ? 'hidden' : 'visible';
    nextButton.style.display = this.currentStep === this.totalSteps ? 'none' : 'block';
    submitButton.style.display = this.currentStep === this.totalSteps ? 'block' : 'none';

    // Re-render content step if needed
    if (this.currentStep === 2) {
      const contentStep = this.container.querySelector('[data-step="2"]');
      contentStep.innerHTML = this.renderContentStep();
      this.setupMediaEventListeners();
    }
  }

  validateCurrentStep() {
    switch (this.currentStep) {
      case 1:
        return this.formData.type !== null;
      case 2:
        return this.validateContentStep();
      case 3:
        return this.formData.rating !== null && this.formData.category !== null;
      case 4:
        return this.validatePersonalInfo();
      default:
        return true;
    }
  }

  validateContentStep() {
    switch (this.formData.type) {
      case 'text':
        return this.formData.content.text && this.formData.content.text.trim().length > 10;
      case 'video':
        return this.formData.content.videoBlob || this.formData.content.videoFile;
      case 'audio':
        return this.formData.content.audioBlob || this.formData.content.audioFile;
      case 'photo':
        return this.formData.content.photos && this.formData.content.photos.length > 0;
      default:
        return false;
    }
  }

  validatePersonalInfo() {
    const customer = this.formData.customer;
    return customer.firstName && 
           customer.lastName && 
           customer.email && 
           customer.displayPublicly !== false;
  }

  saveFormData(input) {
    const name = input.name;
    const value = input.value;

    if (name.startsWith('customer.') || ['firstName', 'lastName', 'email', 'phone'].includes(name)) {
      const customerField = name.replace('customer.', '') || name;
      this.formData.customer[customerField] = value;
    } else if (name === 'testimonialText') {
      this.formData.content.text = value;
      this.updateCharacterCount(value);
    } else if (name === 'photoStory') {
      this.formData.content.story = value;
    } else {
      this.formData[name] = value;
    }
  }

  trackEvent(eventName, properties = {}) {
    if (typeof gtag !== 'undefined') {
      gtag('event', eventName, {
        event_category: 'Testimonial Form',
        ...properties
      });
    }
  }

  showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'form-error';
    errorDiv.innerHTML = `
      <div class="error-content">
        <span class="error-icon">⚠️</span>
        <p>${message}</p>
        <button class="error-close">&times;</button>
      </div>
    `;
    
    this.container.appendChild(errorDiv);
    
    errorDiv.querySelector('.error-close').addEventListener('click', () => {
      errorDiv.remove();
    });
    
    setTimeout(() => {
      if (errorDiv.parentNode) {
        errorDiv.remove();
      }
    }, 5000);
  }

  showSubmittingState(show) {
    const submitButton = document.getElementById('submit-button');
    if (show) {
      submitButton.disabled = true;
      submitButton.innerHTML = `
        <span class="loading-spinner small"></span>
        Submitting...
      `;
    } else {
      submitButton.disabled = false;
      submitButton.innerHTML = 'Submit Review';
    }
  }
}

// Initialize testimonial form
document.addEventListener('DOMContentLoaded', () => {
  const formContainer = document.querySelector('#testimonial-form-container');
  if (formContainer) {
    const testimonialForm = new TestimonialForm('#testimonial-form-container');
    testimonialForm.initialize();
  }
});
```

### 3. Backend API Implementation

**File: `api/testimonials/submit.js`**
```javascript
import { kv } from '@vercel/kv';
import multer from 'multer';
import { v4 as uuidv4 } from 'uuid';
import { sendEmail } from '../../lib/email-service.js';

// Configure multer for file uploads
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 50 * 1024 * 1024, // 50MB max file size
    files: 10 // Max 10 files
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = [
      'video/mp4', 'video/webm', 'video/quicktime',
      'audio/mp3', 'audio/wav', 'audio/m4a', 'audio/webm',
      'image/jpeg', 'image/png', 'image/webp'
    ];
    
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error(`File type ${file.mimetype} not allowed`));
    }
  }
});

export default async function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Use multer to handle multipart/form-data
    await new Promise((resolve, reject) => {
      upload.any()(req, res, (err) => {
        if (err) {
          reject(err);
        } else {
          resolve();
        }
      });
    });

    const testimonial = await processTestimonialSubmission(req);
    
    // Store testimonial
    await storeTestimonial(testimonial);
    
    // Send confirmation email
    await sendConfirmationEmail(testimonial);
    
    // Notify moderators if moderation is required
    if (process.env.TESTIMONIAL_MODERATION === 'true') {
      await notifyModerators(testimonial);
    }
    
    return res.status(201).json({
      success: true,
      id: testimonial.id,
      message: 'Testimonial submitted successfully',
      requiresModeration: process.env.TESTIMONIAL_MODERATION === 'true'
    });
    
  } catch (error) {
    console.error('Error submitting testimonial:', error);
    return res.status(500).json({
      error: 'Submission failed',
      message: error.message
    });
  }
}

async function processTestimonialSubmission(req) {
  const testimonialId = uuidv4();
  const now = new Date().toISOString();
  
  // Parse customer data
  const customer = JSON.parse(req.body.customer || '{}');
  
  // Validate required fields
  if (!customer.firstName || !customer.lastName || !customer.email) {
    throw new Error('Missing required customer information');
  }
  
  if (!req.body.type || !req.body.rating) {
    throw new Error('Missing required testimonial information');
  }

  const testimonial = {
    id: testimonialId,
    type: req.body.type,
    rating: parseInt(req.body.rating),
    category: req.body.category || 'general',
    customer: {
      firstName: customer.firstName,
      lastName: customer.lastName,
      email: customer.email,
      phone: customer.phone || null,
      displayPublicly: customer.displayPublicly !== 'false',
      allowMarketing: customer.allowMarketing === 'true'
    },
    status: process.env.TESTIMONIAL_MODERATION === 'true' ? 'pending' : 'approved',
    createdAt: now,
    updatedAt: now,
    featured: false,
    helpfulCount: 0,
    source: 'website'
  };

  // Process content based on type
  switch (req.body.type) {
    case 'text':
      testimonial.text = req.body.text;
      if (!testimonial.text || testimonial.text.trim().length < 10) {
        throw new Error('Testimonial text must be at least 10 characters long');
      }
      break;

    case 'video':
      const videoFile = req.files.find(f => f.fieldname === 'video');
      if (videoFile) {
        testimonial.videoUrl = await uploadMedia(videoFile, 'video', testimonialId);
        testimonial.thumbnail = await generateVideoThumbnail(testimonial.videoUrl);
        testimonial.duration = await getVideoDuration(testimonial.videoUrl);
      } else {
        throw new Error('Video file is required for video testimonials');
      }
      break;

    case 'audio':
      const audioFile = req.files.find(f => f.fieldname === 'audio');
      if (audioFile) {
        testimonial.audioUrl = await uploadMedia(audioFile, 'audio', testimonialId);
        testimonial.duration = await getAudioDuration(testimonial.audioUrl);
      } else {
        throw new Error('Audio file is required for audio testimonials');
      }
      break;

    case 'photo':
      const photoFiles = req.files.filter(f => f.fieldname.startsWith('photo_'));
      if (photoFiles.length === 0) {
        throw new Error('At least one photo is required for photo testimonials');
      }
      
      testimonial.photos = await Promise.all(photoFiles.map(async (file, index) => {
        const captionKey = `photo_${index}_caption`;
        return {
          url: await uploadMedia(file, 'photo', `${testimonialId}_${index}`),
          caption: req.body[captionKey] || null,
          order: index
        };
      }));
      
      testimonial.text = req.body.story || null;
      break;

    default:
      throw new Error('Invalid testimonial type');
  }

  return testimonial;
}

async function uploadMedia(file, type, identifier) {
  // In a real implementation, this would upload to a cloud storage service
  // For now, we'll simulate the upload and return a URL
  
  const fileExtension = file.originalname.split('.').pop();
  const fileName = `${type}_${identifier}.${fileExtension}`;
  const uploadPath = `/uploads/testimonials/${fileName}`;
  
  // Here you would upload to S3, Cloudinary, or another service
  // For demonstration, we'll store the file data in KV storage (not recommended for large files)
  
  try {
    // Convert buffer to base64 for storage (temporary solution)
    const base64Data = file.buffer.toString('base64');
    await kv.set(`media:${fileName}`, {
      data: base64Data,
      mimetype: file.mimetype,
      size: file.size,
      uploadedAt: new Date().toISOString()
    });
    
    return uploadPath;
  } catch (error) {
    console.error('Error uploading media:', error);
    throw new Error('Failed to upload media file');
  }
}

async function generateVideoThumbnail(videoUrl) {
  // In a real implementation, this would generate a thumbnail from the video
  // For now, return a placeholder
  return `/static/images/video-placeholder.jpg`;
}

async function getVideoDuration(videoUrl) {
  // In a real implementation, this would analyze the video file
  // For now, return a default duration
  return 60; // 60 seconds
}

async function getAudioDuration(audioUrl) {
  // In a real implementation, this would analyze the audio file
  // For now, return a default duration
  return 45; // 45 seconds
}

async function storeTestimonial(testimonial) {
  try {
    // Store main testimonial record
    await kv.set(`testimonial:${testimonial.id}`, testimonial);
    
    // Add to category index
    await kv.sadd(`testimonials:category:${testimonial.category}`, testimonial.id);
    
    // Add to type index
    await kv.sadd(`testimonials:type:${testimonial.type}`, testimonial.id);
    
    // Add to status index
    await kv.sadd(`testimonials:status:${testimonial.status}`, testimonial.id);
    
    // Add to rating index
    await kv.sadd(`testimonials:rating:${testimonial.rating}`, testimonial.id);
    
    // Add to chronological index
    await kv.zadd('testimonials:chronological', Date.now(), testimonial.id);
    
    // Update statistics
    await updateTestimonialStats(testimonial);
    
    console.log(`Testimonial ${testimonial.id} stored successfully`);
    
  } catch (error) {
    console.error('Error storing testimonial:', error);
    throw new Error('Failed to save testimonial');
  }
}

async function updateTestimonialStats(testimonial) {
  const stats = await kv.get('testimonial_stats') || {
    total: 0,
    byType: { text: 0, video: 0, audio: 0, photo: 0 },
    byRating: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 },
    byCategory: {},
    averageRating: 0
  };
  
  stats.total++;
  stats.byType[testimonial.type]++;
  stats.byRating[testimonial.rating]++;
  
  if (!stats.byCategory[testimonial.category]) {
    stats.byCategory[testimonial.category] = 0;
  }
  stats.byCategory[testimonial.category]++;
  
  // Recalculate average rating
  const totalRatingPoints = Object.entries(stats.byRating)
    .reduce((sum, [rating, count]) => sum + (parseInt(rating) * count), 0);
  stats.averageRating = totalRatingPoints / stats.total;
  
  await kv.set('testimonial_stats', stats);
}

async function sendConfirmationEmail(testimonial) {
  try {
    const emailData = {
      to: testimonial.customer.email,
      subject: 'Thank you for your testimonial! - Sabor con Flow',
      template: 'testimonial-confirmation',
      data: {
        customerName: `${testimonial.customer.firstName} ${testimonial.customer.lastName}`,
        testimonialType: testimonial.type,
        requiresModeration: testimonial.status === 'pending',
        testimonialId: testimonial.id
      }
    };
    
    await sendEmail(emailData);
    console.log('Confirmation email sent successfully');
    
  } catch (error) {
    console.error('Failed to send confirmation email:', error);
    // Don't throw error as this is not critical for testimonial submission
  }
}

async function notifyModerators(testimonial) {
  try {
    const moderatorEmails = process.env.MODERATOR_EMAILS?.split(',') || [];
    
    for (const email of moderatorEmails) {
      const emailData = {
        to: email.trim(),
        subject: 'New Testimonial Awaiting Moderation - Sabor con Flow',
        template: 'testimonial-moderation',
        data: {
          testimonialId: testimonial.id,
          customerName: `${testimonial.customer.firstName} ${testimonial.customer.lastName}`,
          type: testimonial.type,
          rating: testimonial.rating,
          category: testimonial.category,
          moderationUrl: `${process.env.VERCEL_URL || 'http://localhost:3000'}/admin/testimonials/${testimonial.id}`
        }
      };
      
      await sendEmail(emailData);
    }
    
    console.log('Moderator notifications sent successfully');
    
  } catch (error) {
    console.error('Failed to send moderator notifications:', error);
    // Don't throw error as this is not critical
  }
}

export const config = {
  api: {
    bodyParser: false, // Disable default body parser for multer
  },
};
```

## Performance & SEO Metrics

- **Form Completion Rate**: Target 65% completion rate
- **Media Upload Success**: 95% success rate for file uploads  
- **Page Load Speed**: < 2 seconds with lazy loading
- **SEO Rich Snippets**: Structured data for all testimonials
- **Accessibility**: WCAG 2.1 AA compliance
- **Mobile Optimization**: Touch-friendly interface with responsive design

This comprehensive testimonials system provides rich media capabilities, social integration, and robust moderation tools while maintaining excellent performance and user experience.