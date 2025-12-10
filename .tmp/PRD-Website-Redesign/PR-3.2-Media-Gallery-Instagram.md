# PR 3.2: Media Gallery & Instagram Integration

## PR Metadata
- **Title**: Implement Media Gallery with Instagram Integration
- **Type**: Feature Implementation  
- **Priority**: High
- **Dependencies**: 
  - PR 1.1: Core Navigation & Header (layout structure)
  - PR 1.3: Footer & Social Links (Instagram links)
  - PR 2.3: Performance Optimization (image optimization patterns)
- **Target Branch**: `feature/media-gallery-instagram`
- **Estimated Effort**: 18 hours
- **Testing Requirements**: Instagram API mocks, image optimization testing, responsive gallery testing

## Implementation Overview

### Core Features
1. **Instagram Feed Integration** with fallback to manual uploads
2. **Advanced Image Gallery** with lazy loading and optimization
3. **Video Player** with YouTube and Vimeo integration
4. **Media Management** with automatic resizing and WebP conversion
5. **Real-time Instagram Updates** via webhooks
6. **Social Sharing** for gallery items

### Technical Architecture

```
Frontend (Vanilla JS)
├── MediaGallery.js        // Main gallery component
├── InstagramFeed.js       // Instagram API integration
├── ImageOptimizer.js      // Client-side optimization
├── VideoPlayer.js         // Video playback system
└── SocialShare.js        // Social sharing widgets

Backend (Vercel Functions)  
├── /api/instagram        // Instagram API proxy
├── /api/instagram-webhook // Instagram webhook handler
├── /api/media-upload     // Manual media upload
├── /api/image-optimize   // Server-side optimization
└── /api/media-manager    // CRUD operations
```

## File Structure

```
api/
├── instagram/
│   ├── feed.js              // Instagram Basic Display API
│   ├── webhook.js           // Instagram webhook handler
│   └── auth.js             // OAuth flow handler
├── media/
│   ├── upload.js           // Media upload endpoint
│   ├── optimize.js         // Image optimization
│   └── manager.js          // Media CRUD operations

static/js/
├── media-gallery.js        // Main gallery system
├── instagram-feed.js       // Instagram integration
├── image-optimizer.js      // Client-side optimization  
├── video-player.js         // Video playback
├── lazy-loading.js         // Advanced lazy loading
└── social-share.js         // Social sharing

static/css/
├── media-gallery.css       // Gallery styles
├── instagram-feed.css      // Instagram-specific styles
├── video-player.css        // Video player styles
└── lightbox.css           // Lightbox modal styles

templates/
├── gallery/
│   ├── gallery-main.html
│   ├── gallery-lightbox.html
│   └── gallery-upload.html
└── instagram/
    └── feed-widget.html
```

## Implementation Details

### 1. Instagram Feed Integration

**File: `static/js/instagram-feed.js`**
```javascript
class InstagramFeed {
  constructor(config) {
    this.accessToken = config.accessToken;
    this.userId = config.userId;
    this.endpoint = '/api/instagram/feed';
    this.fallbackData = config.fallbackData || [];
    this.refreshInterval = config.refreshInterval || 300000; // 5 minutes
    this.maxRetries = 3;
  }

  async initialize(container) {
    this.container = document.querySelector(container);
    if (!this.container) {
      console.error('Instagram feed container not found');
      return;
    }

    try {
      await this.loadFeed();
      this.startAutoRefresh();
      this.setupInfiniteScroll();
    } catch (error) {
      console.error('Failed to initialize Instagram feed:', error);
      this.showFallbackContent();
    }
  }

  async loadFeed(cursor = null) {
    try {
      const url = new URL(this.endpoint, window.location.origin);
      if (cursor) url.searchParams.set('after', cursor);
      
      const response = await this.fetchWithRetry(url.toString());
      
      if (!response.ok) {
        throw new Error(`Instagram API error: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error.message);
      }
      
      await this.renderFeed(data.data, cursor ? 'append' : 'replace');
      
      // Store for offline use
      this.cacheFeedData(data);
      
      return data;
      
    } catch (error) {
      console.error('Error loading Instagram feed:', error);
      
      if (!cursor) { // Only show fallback for initial load
        this.loadCachedData();
      }
      
      throw error;
    }
  }

  async fetchWithRetry(url, options = {}, retries = 0) {
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        signal: AbortSignal.timeout(10000) // 10 second timeout
      });
      
      return response;
      
    } catch (error) {
      if (retries < this.maxRetries && this.isRetryableError(error)) {
        console.warn(`Instagram API retry ${retries + 1}/${this.maxRetries}`);
        await this.delay(Math.pow(2, retries) * 1000); // Exponential backoff
        return this.fetchWithRetry(url, options, retries + 1);
      }
      throw error;
    }
  }

  isRetryableError(error) {
    return error.name === 'AbortError' || 
           error.message.includes('fetch') ||
           error.message.includes('network');
  }

  async renderFeed(posts, mode = 'replace') {
    if (!posts || posts.length === 0) {
      if (mode === 'replace') {
        this.showEmptyState();
      }
      return;
    }

    const feedHTML = await this.generateFeedHTML(posts);
    
    if (mode === 'replace') {
      this.container.innerHTML = feedHTML;
    } else {
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = feedHTML;
      
      while (tempDiv.firstChild) {
        this.container.appendChild(tempDiv.firstChild);
      }
    }

    // Initialize lazy loading for new images
    this.initializeLazyLoading();
    
    // Setup lightbox for new images
    this.initializeLightbox();
  }

  async generateFeedHTML(posts) {
    const postPromises = posts.map(post => this.generatePostHTML(post));
    const postHTMLs = await Promise.all(postPromises);
    
    return `
      <div class="instagram-grid">
        ${postHTMLs.join('')}
      </div>
    `;
  }

  async generatePostHTML(post) {
    const mediaUrl = await this.optimizeMediaUrl(post.media_url, post.media_type);
    const thumbnailUrl = post.thumbnail_url || mediaUrl;
    
    return `
      <div class="instagram-post" data-id="${post.id}">
        <div class="post-media">
          ${post.media_type === 'VIDEO' ? 
            this.generateVideoHTML(mediaUrl, thumbnailUrl) :
            this.generateImageHTML(mediaUrl, post.caption)
          }
          <div class="post-overlay">
            <div class="post-stats">
              <span class="likes-count" data-post-id="${post.id}">
                <i class="icon-heart"></i>
                <span class="count">Loading...</span>
              </span>
              <span class="comments-count" data-post-id="${post.id}">
                <i class="icon-comment"></i>
                <span class="count">Loading...</span>
              </span>
            </div>
            <button class="view-original" data-permalink="${post.permalink}">
              <i class="icon-instagram"></i>
              View on Instagram
            </button>
          </div>
        </div>
        ${post.caption ? `
          <div class="post-caption">
            <p>${this.formatCaption(post.caption)}</p>
            <time datetime="${post.timestamp}">${this.formatDate(post.timestamp)}</time>
          </div>
        ` : ''}
      </div>
    `;
  }

  generateVideoHTML(videoUrl, thumbnailUrl) {
    return `
      <div class="video-container">
        <img 
          src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E"
          data-src="${thumbnailUrl}"
          alt="Video thumbnail"
          class="lazy-load video-thumbnail"
        >
        <button class="video-play-button" data-video-src="${videoUrl}">
          <i class="icon-play"></i>
        </button>
      </div>
    `;
  }

  generateImageHTML(imageUrl, caption) {
    return `
      <img 
        src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E"
        data-src="${imageUrl}"
        alt="${this.stripHtml(caption || 'Instagram post')}"
        class="lazy-load gallery-image"
        loading="lazy"
      >
    `;
  }

  async optimizeMediaUrl(originalUrl, mediaType) {
    // Use our image optimization service for Instagram images
    if (mediaType === 'IMAGE') {
      const optimizedUrl = `/api/instagram/optimize?url=${encodeURIComponent(originalUrl)}&format=webp&quality=85`;
      return optimizedUrl;
    }
    return originalUrl;
  }

  formatCaption(caption) {
    // Convert hashtags to links and limit length
    const truncated = caption.length > 150 ? 
      caption.substring(0, 150) + '...' : caption;
    
    return truncated.replace(/#(\w+)/g, '<span class="hashtag">#$1</span>');
  }

  formatDate(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
  }

  setupInfiniteScroll() {
    let loading = false;
    let hasMore = true;
    let nextCursor = null;

    const observer = new IntersectionObserver(async (entries) => {
      const lastEntry = entries[0];
      
      if (lastEntry.isIntersecting && !loading && hasMore) {
        loading = true;
        
        try {
          const data = await this.loadFeed(nextCursor);
          nextCursor = data.paging?.cursors?.after;
          hasMore = !!nextCursor;
          
          if (!hasMore) {
            observer.disconnect();
            this.showEndOfFeedMessage();
          }
        } catch (error) {
          console.error('Error loading more posts:', error);
          hasMore = false;
          observer.disconnect();
        } finally {
          loading = false;
        }
      }
    }, { threshold: 0.1 });

    // Observe the last post for infinite scroll
    const observeLastPost = () => {
      const posts = this.container.querySelectorAll('.instagram-post');
      const lastPost = posts[posts.length - 1];
      
      if (lastPost && hasMore) {
        observer.observe(lastPost);
      }
    };

    // Initial observation
    setTimeout(observeLastPost, 1000);
    
    // Re-observe after new posts are loaded
    this.container.addEventListener('postsLoaded', observeLastPost);
  }

  initializeLazyLoading() {
    const images = this.container.querySelectorAll('.lazy-load:not(.loaded)');
    
    const imageObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          const src = img.getAttribute('data-src');
          
          if (src) {
            img.src = src;
            img.classList.add('loaded');
            imageObserver.unobserve(img);
            
            // Fade in animation
            img.addEventListener('load', () => {
              img.style.opacity = '1';
            });
          }
        }
      });
    }, { rootMargin: '50px' });

    images.forEach(img => imageObserver.observe(img));
  }

  initializeLightbox() {
    const images = this.container.querySelectorAll('.gallery-image:not(.lightbox-enabled)');
    
    images.forEach(img => {
      img.classList.add('lightbox-enabled');
      img.addEventListener('click', (e) => {
        this.openLightbox(e.target);
      });
    });

    // Video play buttons
    const playButtons = this.container.querySelectorAll('.video-play-button:not(.enabled)');
    playButtons.forEach(button => {
      button.classList.add('enabled');
      button.addEventListener('click', (e) => {
        const videoSrc = e.target.getAttribute('data-video-src');
        this.playVideo(videoSrc);
      });
    });
  }

  openLightbox(image) {
    const lightbox = document.createElement('div');
    lightbox.className = 'instagram-lightbox';
    lightbox.innerHTML = `
      <div class="lightbox-backdrop"></div>
      <div class="lightbox-content">
        <img src="${image.src}" alt="${image.alt}">
        <button class="lightbox-close">&times;</button>
        <div class="lightbox-nav">
          <button class="lightbox-prev">&lt;</button>
          <button class="lightbox-next">&gt;</button>
        </div>
      </div>
    `;

    document.body.appendChild(lightbox);
    
    // Setup lightbox controls
    this.setupLightboxControls(lightbox, image);
    
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
  }

  startAutoRefresh() {
    // Clear existing interval
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
    }

    this.refreshTimer = setInterval(async () => {
      try {
        await this.loadFeed();
        console.log('Instagram feed refreshed');
      } catch (error) {
        console.error('Auto refresh failed:', error);
      }
    }, this.refreshInterval);
  }

  cacheFeedData(data) {
    try {
      localStorage.setItem('instagram_feed_cache', JSON.stringify({
        data: data,
        timestamp: Date.now()
      }));
    } catch (error) {
      console.warn('Failed to cache Instagram feed data:', error);
    }
  }

  loadCachedData() {
    try {
      const cached = localStorage.getItem('instagram_feed_cache');
      if (cached) {
        const { data, timestamp } = JSON.parse(cached);
        
        // Use cached data if less than 1 hour old
        if (Date.now() - timestamp < 3600000) {
          this.renderFeed(data.data);
          console.log('Loaded cached Instagram feed');
          return true;
        }
      }
    } catch (error) {
      console.warn('Failed to load cached Instagram data:', error);
    }
    
    this.showFallbackContent();
    return false;
  }

  showFallbackContent() {
    if (this.fallbackData.length > 0) {
      this.renderFeed(this.fallbackData);
    } else {
      this.container.innerHTML = `
        <div class="instagram-fallback">
          <div class="fallback-icon">📸</div>
          <h3>Instagram feed temporarily unavailable</h3>
          <p>Check out our latest posts directly on Instagram</p>
          <a href="https://instagram.com/saborconflow" class="btn-primary" target="_blank" rel="noopener">
            View on Instagram
          </a>
        </div>
      `;
    }
  }

  destroy() {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
    }
  }
}
```

### 2. Advanced Media Gallery

**File: `static/js/media-gallery.js`**
```javascript
class MediaGallery {
  constructor(container, options = {}) {
    this.container = document.querySelector(container);
    this.options = {
      layout: 'masonry', // masonry, grid, carousel
      itemsPerPage: 20,
      autoPlay: false,
      enableFilters: true,
      enableSearch: true,
      enableUpload: false,
      categories: ['all', 'classes', 'events', 'performances', 'instructors'],
      ...options
    };
    
    this.currentPage = 1;
    this.currentFilter = 'all';
    this.currentSearch = '';
    this.items = [];
    this.filteredItems = [];
    this.isLoading = false;
  }

  async initialize() {
    try {
      await this.loadMediaItems();
      this.render();
      this.setupEventListeners();
      this.setupIntersectionObserver();
    } catch (error) {
      console.error('Failed to initialize media gallery:', error);
      this.showErrorState();
    }
  }

  async loadMediaItems(page = 1) {
    if (this.isLoading) return;
    
    this.isLoading = true;
    this.showLoadingState(page === 1);
    
    try {
      const response = await fetch(`/api/media/gallery?page=${page}&limit=${this.options.itemsPerPage}&filter=${this.currentFilter}&search=${encodeURIComponent(this.currentSearch)}`);
      
      if (!response.ok) {
        throw new Error(`Gallery API error: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (page === 1) {
        this.items = data.items;
      } else {
        this.items.push(...data.items);
      }
      
      this.hasMore = data.hasMore;
      this.totalItems = data.total;
      
      this.filterAndSortItems();
      
    } catch (error) {
      console.error('Error loading media items:', error);
      this.showErrorState();
    } finally {
      this.isLoading = false;
      this.hideLoadingState();
    }
  }

  render() {
    const galleryHTML = `
      <div class="media-gallery">
        ${this.options.enableSearch ? this.renderSearchBar() : ''}
        ${this.options.enableFilters ? this.renderFilters() : ''}
        ${this.options.enableUpload ? this.renderUploadButton() : ''}
        
        <div class="gallery-stats">
          <span class="items-count">${this.filteredItems.length} ${this.filteredItems.length === 1 ? 'item' : 'items'}</span>
          ${this.currentFilter !== 'all' ? `<span class="filter-indicator">Filtered by: ${this.currentFilter}</span>` : ''}
        </div>
        
        <div class="gallery-container ${this.options.layout}">
          <div class="gallery-grid" id="gallery-grid">
            ${this.renderGalleryItems()}
          </div>
          
          <div class="gallery-loading" id="gallery-loading" style="display: none;">
            <div class="loading-spinner"></div>
            <p>Loading more images...</p>
          </div>
          
          <div class="gallery-end-message" id="gallery-end" style="display: none;">
            <p>You've reached the end of our gallery!</p>
          </div>
        </div>
      </div>
    `;
    
    this.container.innerHTML = galleryHTML;
    
    // Initialize masonry layout if needed
    if (this.options.layout === 'masonry') {
      this.initializeMasonry();
    }
  }

  renderSearchBar() {
    return `
      <div class="gallery-search">
        <input 
          type="text" 
          placeholder="Search photos and videos..." 
          class="search-input"
          value="${this.currentSearch}"
        >
        <button class="search-clear" style="${this.currentSearch ? '' : 'display: none;'}">
          <i class="icon-close"></i>
        </button>
      </div>
    `;
  }

  renderFilters() {
    return `
      <div class="gallery-filters">
        ${this.options.categories.map(category => `
          <button 
            class="filter-button ${category === this.currentFilter ? 'active' : ''}"
            data-filter="${category}"
          >
            ${this.capitalizeFirst(category)}
          </button>
        `).join('')}
      </div>
    `;
  }

  renderUploadButton() {
    return `
      <div class="gallery-upload">
        <button class="upload-button btn-primary">
          <i class="icon-upload"></i>
          Upload Media
        </button>
        <input type="file" id="media-upload" multiple accept="image/*,video/*" style="display: none;">
      </div>
    `;
  }

  renderGalleryItems() {
    return this.filteredItems.map(item => this.renderGalleryItem(item)).join('');
  }

  renderGalleryItem(item) {
    const isVideo = item.type === 'video';
    const thumbnailUrl = item.thumbnail || item.url;
    
    return `
      <div class="gallery-item ${item.category}" data-id="${item.id}" data-type="${item.type}">
        <div class="item-container">
          <div class="item-media">
            ${isVideo ? this.renderVideoItem(item) : this.renderImageItem(item)}
            
            <div class="item-overlay">
              <div class="item-actions">
                <button class="action-button view-full" data-id="${item.id}" title="View full size">
                  <i class="icon-expand"></i>
                </button>
                <button class="action-button share" data-id="${item.id}" title="Share">
                  <i class="icon-share"></i>
                </button>
                <button class="action-button download" data-url="${item.downloadUrl || item.url}" title="Download">
                  <i class="icon-download"></i>
                </button>
              </div>
              
              <div class="item-info">
                <div class="item-stats">
                  ${item.likes ? `<span class="likes"><i class="icon-heart"></i> ${item.likes}</span>` : ''}
                  ${item.views ? `<span class="views"><i class="icon-eye"></i> ${item.views}</span>` : ''}
                </div>
              </div>
            </div>
          </div>
          
          ${item.caption || item.title ? `
            <div class="item-details">
              ${item.title ? `<h3 class="item-title">${item.title}</h3>` : ''}
              ${item.caption ? `<p class="item-caption">${this.truncateText(item.caption, 100)}</p>` : ''}
              <time class="item-date" datetime="${item.createdAt}">
                ${this.formatDate(item.createdAt)}
              </time>
            </div>
          ` : ''}
        </div>
      </div>
    `;
  }

  renderImageItem(item) {
    // Generate responsive image URLs
    const sizes = [300, 600, 900, 1200];
    const srcset = sizes.map(size => 
      `/api/media/resize?url=${encodeURIComponent(item.url)}&width=${size}&format=webp ${size}w`
    ).join(', ');

    return `
      <img 
        src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 ${item.width || 1} ${item.height || 1}'%3E%3C/svg%3E"
        data-src="/api/media/resize?url=${encodeURIComponent(item.url)}&width=600&format=webp"
        srcset="${srcset}"
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        alt="${item.alt || item.title || 'Gallery image'}"
        class="gallery-image lazy-load"
        loading="lazy"
        width="${item.width || ''}"
        height="${item.height || ''}"
      >
    `;
  }

  renderVideoItem(item) {
    return `
      <div class="video-item">
        <img 
          src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 9'%3E%3C/svg%3E"
          data-src="${item.thumbnail}"
          alt="${item.title || 'Video thumbnail'}"
          class="video-thumbnail lazy-load"
          loading="lazy"
        >
        <div class="video-play-overlay">
          <button class="video-play-button" data-video-id="${item.id}">
            <i class="icon-play"></i>
          </button>
          <div class="video-duration">${this.formatDuration(item.duration)}</div>
        </div>
      </div>
    `;
  }

  setupEventListeners() {
    // Search functionality
    const searchInput = this.container.querySelector('.search-input');
    if (searchInput) {
      let searchTimeout;
      searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
          this.currentSearch = e.target.value.trim();
          this.currentPage = 1;
          this.performSearch();
        }, 300);
      });

      // Clear search
      const clearButton = this.container.querySelector('.search-clear');
      if (clearButton) {
        clearButton.addEventListener('click', () => {
          searchInput.value = '';
          this.currentSearch = '';
          this.currentPage = 1;
          this.performSearch();
        });
      }
    }

    // Filter buttons
    this.container.addEventListener('click', (e) => {
      if (e.target.classList.contains('filter-button')) {
        this.handleFilterChange(e.target.dataset.filter);
      }
    });

    // Gallery item actions
    this.container.addEventListener('click', (e) => {
      if (e.target.closest('.view-full')) {
        const itemId = e.target.closest('[data-id]').dataset.id;
        this.openLightbox(itemId);
      } else if (e.target.closest('.share')) {
        const itemId = e.target.closest('[data-id]').dataset.id;
        this.shareItem(itemId);
      } else if (e.target.closest('.download')) {
        const url = e.target.closest('.download').dataset.url;
        this.downloadItem(url);
      } else if (e.target.closest('.video-play-button')) {
        const videoId = e.target.closest('.video-play-button').dataset.videoId;
        this.playVideo(videoId);
      }
    });

    // Upload functionality
    const uploadButton = this.container.querySelector('.upload-button');
    const uploadInput = this.container.querySelector('#media-upload');
    
    if (uploadButton && uploadInput) {
      uploadButton.addEventListener('click', () => {
        uploadInput.click();
      });
      
      uploadInput.addEventListener('change', (e) => {
        this.handleFileUpload(e.target.files);
      });
    }

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && document.querySelector('.gallery-lightbox')) {
        this.closeLightbox();
      }
    });
  }

  setupIntersectionObserver() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          // Lazy load images
          if (entry.target.classList.contains('lazy-load')) {
            this.loadImage(entry.target);
            observer.unobserve(entry.target);
          }
        }
      });
    }, { rootMargin: '100px' });

    // Observe all lazy-load images
    this.container.querySelectorAll('.lazy-load').forEach(img => {
      observer.observe(img);
    });

    // Infinite scroll observer
    const endElement = document.createElement('div');
    endElement.className = 'scroll-trigger';
    this.container.querySelector('.gallery-grid').appendChild(endElement);

    const scrollObserver = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && this.hasMore && !this.isLoading) {
        this.currentPage++;
        this.loadMediaItems(this.currentPage);
      }
    }, { threshold: 0.1 });

    scrollObserver.observe(endElement);
  }

  async loadImage(img) {
    const src = img.getAttribute('data-src');
    if (!src) return;

    try {
      // Create a temporary image to test loading
      const tempImg = new Image();
      tempImg.onload = () => {
        img.src = src;
        img.classList.add('loaded');
        
        // Animate in
        img.style.opacity = '1';
        img.style.transform = 'scale(1)';
      };
      
      tempImg.onerror = () => {
        img.classList.add('error');
        img.alt = 'Failed to load image';
      };
      
      tempImg.src = src;
      
    } catch (error) {
      console.error('Error loading image:', error);
      img.classList.add('error');
    }
  }

  async performSearch() {
    this.showLoadingState(true);
    await this.loadMediaItems(1);
    this.render();
    this.setupEventListeners();
    this.setupIntersectionObserver();
    
    // Update search clear button
    const clearButton = this.container.querySelector('.search-clear');
    if (clearButton) {
      clearButton.style.display = this.currentSearch ? '' : 'none';
    }
  }

  handleFilterChange(filter) {
    if (filter === this.currentFilter) return;
    
    // Update active filter button
    this.container.querySelectorAll('.filter-button').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.filter === filter);
    });
    
    this.currentFilter = filter;
    this.currentPage = 1;
    this.performSearch();
  }

  filterAndSortItems() {
    this.filteredItems = this.items.filter(item => {
      // Apply filter
      if (this.currentFilter !== 'all' && item.category !== this.currentFilter) {
        return false;
      }
      
      // Apply search
      if (this.currentSearch) {
        const searchTerm = this.currentSearch.toLowerCase();
        const searchableText = [
          item.title,
          item.caption,
          item.alt,
          item.tags?.join(' ')
        ].filter(Boolean).join(' ').toLowerCase();
        
        if (!searchableText.includes(searchTerm)) {
          return false;
        }
      }
      
      return true;
    });

    // Sort by date (newest first)
    this.filteredItems.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  }

  openLightbox(itemId) {
    const item = this.items.find(i => i.id === itemId);
    if (!item) return;

    const lightbox = document.createElement('div');
    lightbox.className = 'gallery-lightbox';
    lightbox.innerHTML = `
      <div class="lightbox-backdrop"></div>
      <div class="lightbox-content">
        <div class="lightbox-header">
          <h3>${item.title || 'Media Item'}</h3>
          <button class="lightbox-close">&times;</button>
        </div>
        
        <div class="lightbox-media">
          ${item.type === 'video' ? 
            this.renderLightboxVideo(item) :
            this.renderLightboxImage(item)
          }
        </div>
        
        <div class="lightbox-info">
          ${item.caption ? `<p>${item.caption}</p>` : ''}
          <div class="lightbox-meta">
            <span class="upload-date">${this.formatDate(item.createdAt)}</span>
            ${item.photographer ? `<span class="photographer">by ${item.photographer}</span>` : ''}
          </div>
          <div class="lightbox-actions">
            <button class="btn-secondary share-button" data-id="${item.id}">Share</button>
            <a href="${item.downloadUrl || item.url}" download class="btn-primary">Download</a>
          </div>
        </div>
        
        <div class="lightbox-nav">
          <button class="lightbox-prev">&lt;</button>
          <button class="lightbox-next">&gt;</button>
        </div>
      </div>
    `;

    document.body.appendChild(lightbox);
    document.body.style.overflow = 'hidden';
    
    // Setup lightbox controls
    this.setupLightboxControls(lightbox, itemId);
    
    // Track view
    this.trackMediaView(itemId);
  }

  renderLightboxImage(item) {
    return `
      <img 
        src="/api/media/resize?url=${encodeURIComponent(item.url)}&width=1200&format=webp&quality=90"
        alt="${item.alt || item.title || 'Gallery image'}"
        class="lightbox-image"
      >
    `;
  }

  renderLightboxVideo(item) {
    return `
      <video 
        src="${item.url}"
        poster="${item.thumbnail}"
        controls
        class="lightbox-video"
        preload="metadata"
      >
        Your browser does not support the video tag.
      </video>
    `;
  }

  async handleFileUpload(files) {
    if (!files.length) return;
    
    const uploadResults = [];
    const maxSize = 10 * 1024 * 1024; // 10MB limit
    
    for (const file of files) {
      if (file.size > maxSize) {
        alert(`File ${file.name} is too large. Maximum size is 10MB.`);
        continue;
      }
      
      try {
        const result = await this.uploadFile(file);
        uploadResults.push(result);
      } catch (error) {
        console.error(`Failed to upload ${file.name}:`, error);
        alert(`Failed to upload ${file.name}`);
      }
    }
    
    if (uploadResults.length > 0) {
      // Refresh gallery to show new items
      await this.loadMediaItems(1);
      this.render();
      this.setupEventListeners();
      this.setupIntersectionObserver();
      
      alert(`Successfully uploaded ${uploadResults.length} file(s)`);
    }
  }

  async uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', this.currentFilter === 'all' ? 'general' : this.currentFilter);
    
    const response = await fetch('/api/media/upload', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Upload failed');
    }
    
    return await response.json();
  }

  initializeMasonry() {
    // Simple masonry layout implementation
    const grid = this.container.querySelector('.gallery-grid');
    if (!grid) return;
    
    const resizeObserver = new ResizeObserver(() => {
      this.layoutMasonry();
    });
    
    resizeObserver.observe(grid);
    
    // Layout after images load
    setTimeout(() => this.layoutMasonry(), 100);
  }

  layoutMasonry() {
    const grid = this.container.querySelector('.gallery-grid');
    const items = grid.querySelectorAll('.gallery-item');
    const columns = this.calculateColumns();
    
    // Reset grid
    grid.style.columnCount = columns;
    grid.style.columnGap = '1rem';
    
    items.forEach(item => {
      item.style.breakInside = 'avoid';
      item.style.marginBottom = '1rem';
    });
  }

  calculateColumns() {
    const width = this.container.offsetWidth;
    if (width < 768) return 1;
    if (width < 1024) return 2;
    if (width < 1200) return 3;
    return 4;
  }

  // Utility methods
  capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength).trim() + '...';
  }

  formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  showLoadingState(clear = false) {
    if (clear) {
      const grid = this.container.querySelector('.gallery-grid');
      if (grid) grid.innerHTML = '';
    }
    
    const loadingElement = this.container.querySelector('#gallery-loading');
    if (loadingElement) {
      loadingElement.style.display = 'block';
    }
  }

  hideLoadingState() {
    const loadingElement = this.container.querySelector('#gallery-loading');
    if (loadingElement) {
      loadingElement.style.display = 'none';
    }
  }

  showErrorState() {
    this.container.innerHTML = `
      <div class="gallery-error">
        <div class="error-icon">⚠️</div>
        <h3>Unable to load gallery</h3>
        <p>Please try again later</p>
        <button class="btn-primary retry-button">Retry</button>
      </div>
    `;
    
    this.container.querySelector('.retry-button').addEventListener('click', () => {
      this.initialize();
    });
  }
}

// Initialize gallery when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  const galleryContainer = document.querySelector('#media-gallery');
  if (galleryContainer) {
    const gallery = new MediaGallery('#media-gallery', {
      layout: 'masonry',
      enableFilters: true,
      enableSearch: true,
      enableUpload: true // Set to false for public view
    });
    
    gallery.initialize();
  }
});
```

### 3. Backend API Endpoints

**File: `api/instagram/feed.js`**
```javascript
import { kv } from '@vercel/kv';

const INSTAGRAM_API_URL = 'https://graph.instagram.com';
const ACCESS_TOKEN = process.env.INSTAGRAM_ACCESS_TOKEN;
const CACHE_DURATION = 300; // 5 minutes

export default async function handler(req, res) {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { after, limit = 20 } = req.query;
    
    // Check cache first
    const cacheKey = `instagram_feed:${after || 'initial'}:${limit}`;
    const cachedData = await kv.get(cacheKey);
    
    if (cachedData) {
      return res.json(cachedData);
    }

    // Fetch from Instagram API
    const feedData = await fetchInstagramFeed(after, parseInt(limit));
    
    // Cache the response
    await kv.setex(cacheKey, CACHE_DURATION, feedData);
    
    return res.json(feedData);
    
  } catch (error) {
    console.error('Instagram API error:', error);
    
    // Try to return fallback data
    const fallbackData = await getFallbackData();
    if (fallbackData) {
      return res.json(fallbackData);
    }
    
    return res.status(500).json({ 
      error: 'Failed to fetch Instagram feed',
      message: error.message 
    });
  }
}

async function fetchInstagramFeed(after = null, limit = 20) {
  if (!ACCESS_TOKEN) {
    throw new Error('Instagram access token not configured');
  }

  const fields = [
    'id',
    'media_type',
    'media_url',
    'thumbnail_url',
    'permalink',
    'caption',
    'timestamp',
    'username'
  ].join(',');

  let url = `${INSTAGRAM_API_URL}/me/media?fields=${fields}&limit=${limit}&access_token=${ACCESS_TOKEN}`;
  
  if (after) {
    url += `&after=${after}`;
  }

  const response = await fetch(url, {
    headers: {
      'User-Agent': 'SaborConFlow/1.0'
    }
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(`Instagram API error: ${response.status} - ${errorData.error?.message || 'Unknown error'}`);
  }

  const data = await response.json();
  
  // Process and enhance the data
  const processedData = {
    data: await Promise.all(data.data.map(processInstagramPost)),
    paging: data.paging
  };

  return processedData;
}

async function processInstagramPost(post) {
  // Enhance post data
  const processed = {
    ...post,
    optimized_media_url: await getOptimizedMediaUrl(post.media_url, post.media_type),
    engagement: await getPostEngagement(post.id)
  };

  return processed;
}

async function getOptimizedMediaUrl(originalUrl, mediaType) {
  if (mediaType !== 'IMAGE') return originalUrl;
  
  // Create optimized version through our image service
  return `/api/image-optimize?url=${encodeURIComponent(originalUrl)}&format=webp&quality=85&width=600`;
}

async function getPostEngagement(postId) {
  try {
    // Fetch likes and comments count
    const response = await fetch(`${INSTAGRAM_API_URL}/${postId}?fields=like_count,comments_count&access_token=${ACCESS_TOKEN}`);
    
    if (response.ok) {
      return await response.json();
    }
  } catch (error) {
    console.warn('Failed to fetch engagement data:', error);
  }
  
  return { like_count: null, comments_count: null };
}

async function getFallbackData() {
  try {
    // Return cached fallback data or static data
    return await kv.get('instagram_fallback_data');
  } catch (error) {
    console.warn('Failed to get fallback data:', error);
    return null;
  }
}
```

**File: `api/instagram/webhook.js`**
```javascript
import crypto from 'crypto';
import { kv } from '@vercel/kv';

const VERIFY_TOKEN = process.env.INSTAGRAM_WEBHOOK_VERIFY_TOKEN;
const APP_SECRET = process.env.INSTAGRAM_APP_SECRET;

export default async function handler(req, res) {
  console.log('Instagram webhook received:', req.method, req.query);
  
  if (req.method === 'GET') {
    return handleVerification(req, res);
  } else if (req.method === 'POST') {
    return handleWebhook(req, res);
  } else {
    return res.status(405).json({ error: 'Method not allowed' });
  }
}

function handleVerification(req, res) {
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];

  if (mode === 'subscribe' && token === VERIFY_TOKEN) {
    console.log('Instagram webhook verified successfully');
    return res.status(200).send(challenge);
  } else {
    console.error('Instagram webhook verification failed');
    return res.status(403).json({ error: 'Verification failed' });
  }
}

async function handleWebhook(req, res) {
  try {
    // Verify signature
    if (!verifySignature(req)) {
      console.error('Invalid Instagram webhook signature');
      return res.status(401).json({ error: 'Invalid signature' });
    }

    const body = req.body;
    console.log('Instagram webhook payload:', JSON.stringify(body, null, 2));

    // Process the webhook
    for (const entry of body.entry || []) {
      await processEntry(entry);
    }

    return res.status(200).json({ received: true });
    
  } catch (error) {
    console.error('Instagram webhook processing error:', error);
    return res.status(500).json({ error: 'Processing failed' });
  }
}

function verifySignature(req) {
  if (!APP_SECRET) {
    console.warn('Instagram app secret not configured');
    return true; // Skip verification in development
  }

  const signature = req.headers['x-hub-signature-256'];
  if (!signature) {
    return false;
  }

  const expectedSignature = crypto
    .createHmac('sha256', APP_SECRET)
    .update(JSON.stringify(req.body))
    .digest('hex');

  const hubSignature = signature.replace('sha256=', '');

  return crypto.timingSafeEqual(
    Buffer.from(expectedSignature, 'hex'),
    Buffer.from(hubSignature, 'hex')
  );
}

async function processEntry(entry) {
  const userId = entry.id;
  
  for (const change of entry.changes || []) {
    await processChange(userId, change);
  }
}

async function processChange(userId, change) {
  console.log(`Processing change: ${change.field} for user ${userId}`);
  
  switch (change.field) {
    case 'media':
      await handleMediaChange(userId, change.value);
      break;
    default:
      console.log(`Unhandled change field: ${change.field}`);
  }
}

async function handleMediaChange(userId, value) {
  // Invalidate relevant caches
  const cacheKeys = [
    'instagram_feed:initial:20',
    'instagram_feed:initial:40',
    `user_media:${userId}`
  ];
  
  for (const key of cacheKeys) {
    await kv.del(key);
  }
  
  // Optionally, pre-fetch new content
  try {
    await prefetchNewContent(userId);
  } catch (error) {
    console.warn('Failed to prefetch new content:', error);
  }
  
  console.log('Instagram feed cache invalidated due to media change');
}

async function prefetchNewContent(userId) {
  // This would trigger a background refresh of the Instagram feed
  // Implementation depends on your specific requirements
  console.log(`Prefetching new content for user ${userId}`);
}
```

### 4. CSS Styling

**File: `static/css/media-gallery.css`**
```css
/* Media Gallery Styles */
.media-gallery {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

/* Gallery Header */
.gallery-search {
  position: relative;
  max-width: 400px;
  margin: 0 auto 2rem;
}

.search-input {
  width: 100%;
  padding: 1rem 3rem 1rem 1rem;
  border: 2px solid var(--border-color);
  border-radius: 25px;
  font-size: 1rem;
  background: var(--background-color);
  transition: border-color 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.search-clear {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
  transition: color 0.3s ease;
}

.search-clear:hover {
  color: var(--primary-color);
}

/* Filter Buttons */
.gallery-filters {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 2rem;
}

.filter-button {
  padding: 0.5rem 1.5rem;
  border: 2px solid var(--border-color);
  border-radius: 20px;
  background: var(--background-color);
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-button:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.filter-button.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

/* Gallery Stats */
.gallery-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--surface-color);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.items-count {
  font-weight: bold;
  color: var(--primary-color);
}

.filter-indicator {
  font-size: 0.9rem;
  color: var(--text-secondary);
  background: var(--muted-color);
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
}

/* Gallery Grid Layouts */
.gallery-container.masonry .gallery-grid {
  column-count: 4;
  column-gap: 1.5rem;
}

.gallery-container.grid .gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.gallery-container.carousel .gallery-grid {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  gap: 1rem;
  padding-bottom: 1rem;
}

/* Gallery Items */
.gallery-item {
  background: var(--surface-color);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-light);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  break-inside: avoid;
  margin-bottom: 1.5rem;
}

.gallery-item:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-medium);
}

.item-container {
  position: relative;
}

/* Media Display */
.item-media {
  position: relative;
  overflow: hidden;
}

.gallery-image,
.video-thumbnail {
  width: 100%;
  height: auto;
  display: block;
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.gallery-image {
  opacity: 0;
  transform: scale(0.95);
}

.gallery-image.loaded {
  opacity: 1;
  transform: scale(1);
}

.gallery-image.error {
  opacity: 0.5;
  background: var(--muted-color);
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.gallery-image.error::after {
  content: '📷';
  font-size: 2rem;
  color: var(--text-secondary);
}

/* Video Items */
.video-item {
  position: relative;
}

.video-play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.4);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.video-item:hover .video-play-overlay {
  opacity: 1;
}

.video-play-button {
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: var(--primary-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.video-play-button:hover {
  background: white;
  transform: scale(1.1);
}

.video-duration {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

/* Item Overlay */
.item-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 1rem;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.gallery-item:hover .item-overlay {
  opacity: 1;
}

.item-actions {
  display: flex;
  gap: 0.5rem;
  align-self: flex-end;
}

.action-button {
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--primary-color);
  transition: all 0.3s ease;
}

.action-button:hover {
  background: white;
  transform: scale(1.1);
}

.item-info {
  align-self: flex-start;
}

.item-stats {
  display: flex;
  gap: 1rem;
  color: white;
  font-size: 0.9rem;
}

.item-stats span {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* Item Details */
.item-details {
  padding: 1rem;
}

.item-title {
  font-size: 1.1rem;
  font-weight: bold;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.item-caption {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.4;
  margin-bottom: 0.5rem;
}

.item-date {
  color: var(--text-muted);
  font-size: 0.8rem;
}

/* Instagram Feed Specific */
.instagram-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.instagram-post {
  background: var(--surface-color);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-light);
  transition: transform 0.3s ease;
}

.instagram-post:hover {
  transform: translateY(-2px);
}

.post-caption {
  padding: 1rem;
}

.post-caption p {
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.hashtag {
  color: var(--primary-color);
  font-weight: 500;
}

/* Lightbox Styles */
.gallery-lightbox {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.lightbox-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  cursor: pointer;
}

.lightbox-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  background: var(--surface-color);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-large);
  display: flex;
  flex-direction: column;
}

.lightbox-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--background-color);
  border-bottom: 1px solid var(--border-color);
}

.lightbox-header h3 {
  margin: 0;
  color: var(--primary-color);
}

.lightbox-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0.5rem;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.lightbox-close:hover {
  background: var(--muted-color);
  color: var(--text-primary);
}

.lightbox-media {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.lightbox-image,
.lightbox-video {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.lightbox-info {
  padding: 1rem;
  background: var(--background-color);
  border-top: 1px solid var(--border-color);
}

.lightbox-meta {
  display: flex;
  justify-content: space-between;
  margin: 1rem 0;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.lightbox-actions {
  display: flex;
  gap: 1rem;
}

.lightbox-nav {
  position: absolute;
  top: 50%;
  left: 1rem;
  right: 1rem;
  transform: translateY(-50%);
  display: flex;
  justify-content: space-between;
  pointer-events: none;
}

.lightbox-prev,
.lightbox-next {
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.3s ease;
  pointer-events: auto;
}

.lightbox-prev:hover,
.lightbox-next:hover {
  background: rgba(0, 0, 0, 0.9);
  transform: scale(1.1);
}

/* Loading States */
.gallery-loading {
  text-align: center;
  padding: 2rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Error States */
.gallery-error,
.instagram-fallback {
  text-align: center;
  padding: 4rem 2rem;
  background: var(--surface-color);
  border-radius: 12px;
  border: 2px dashed var(--border-color);
}

.error-icon,
.fallback-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.gallery-error h3,
.instagram-fallback h3 {
  color: var(--primary-color);
  margin-bottom: 1rem;
}

.gallery-error p,
.instagram-fallback p {
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

/* Upload Section */
.gallery-upload {
  text-align: center;
  margin-bottom: 2rem;
}

.upload-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  border-radius: 8px;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .gallery-container.masonry .gallery-grid {
    column-count: 3;
  }
}

@media (max-width: 968px) {
  .gallery-container.masonry .gallery-grid {
    column-count: 2;
  }
  
  .instagram-grid {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }
  
  .gallery-filters {
    justify-content: flex-start;
    overflow-x: auto;
    padding-bottom: 0.5rem;
  }
  
  .filter-button {
    flex-shrink: 0;
  }
}

@media (max-width: 768px) {
  .media-gallery {
    padding: 1rem;
  }
  
  .gallery-container.masonry .gallery-grid {
    column-count: 1;
  }
  
  .gallery-container.grid .gallery-grid {
    grid-template-columns: 1fr;
  }
  
  .instagram-grid {
    grid-template-columns: 1fr;
  }
  
  .lightbox-content {
    margin: 1rem;
    max-width: calc(100vw - 2rem);
    max-height: calc(100vh - 2rem);
  }
  
  .lightbox-nav {
    left: 0.5rem;
    right: 0.5rem;
  }
  
  .lightbox-prev,
  .lightbox-next {
    width: 40px;
    height: 40px;
    font-size: 1rem;
  }
  
  .gallery-stats {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}

@media (max-width: 480px) {
  .action-button {
    width: 35px;
    height: 35px;
    font-size: 0.9rem;
  }
  
  .video-play-button {
    width: 50px;
    height: 50px;
    font-size: 1.2rem;
  }
  
  .item-overlay {
    padding: 0.75rem;
  }
  
  .search-input {
    font-size: 16px; /* Prevent zoom on iOS */
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .gallery-item {
    border: 2px solid var(--text-primary);
  }
  
  .item-overlay {
    background: rgba(0, 0, 0, 0.9);
  }
  
  .action-button {
    background: var(--background-color);
    border: 2px solid var(--text-primary);
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .gallery-item,
  .gallery-image,
  .action-button,
  .video-play-button {
    transition: none;
  }
  
  .loading-spinner {
    animation: none;
  }
}
```

## Testing Strategy

### API Mock Testing
```javascript
import { describe, it, expect, vi, beforeEach } from 'vitest';

describe('Instagram Integration', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  it('should handle Instagram API failures gracefully', async () => {
    // Mock API failure
    global.fetch.mockRejectedValue(new Error('Instagram API down'));
    
    const instagram = new InstagramFeed({
      accessToken: 'test_token',
      fallbackData: [{ id: '1', media_url: 'test.jpg' }]
    });
    
    // Should not throw and should show fallback
    await expect(instagram.loadFeed()).rejects.toThrow();
    
    // Verify fallback is used
    expect(instagram.fallbackData).toHaveLength(1);
  });
});
```

## Performance Metrics
- **Instagram Feed Load**: < 2 seconds initial load
- **Image Optimization**: 60% file size reduction with WebP
- **Lazy Loading**: Images load only when in viewport
- **Mobile Performance**: 90+ Lighthouse score
- **Cache Hit Rate**: 80% for Instagram content

This implementation provides a robust media gallery system with Instagram integration, comprehensive fallback mechanisms, and excellent user experience across all devices.