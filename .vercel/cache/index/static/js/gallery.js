/**
 * Gallery JavaScript - Lightbox and Media Viewer
 * Handles photo lightbox, video modal, navigation, and touch gestures
 */

(function() {
    'use strict';

    // Gallery state
    let currentMediaItems = [];
    let currentIndex = 0;
    let lightboxOpen = false;
    let touchStartX = 0;
    let touchEndX = 0;

    // DOM elements (will be created dynamically)
    let lightboxOverlay = null;
    let lightboxContent = null;
    let lightboxImage = null;
    let lightboxVideo = null;
    let lightboxTitle = null;
    let lightboxDescription = null;
    let prevButton = null;
    let nextButton = null;
    let closeButton = null;
    let loadingSpinner = null;

    /**
     * Initialize gallery on page load
     */
    document.addEventListener('DOMContentLoaded', function() {
        initializeGallery();
        setupKeyboardNavigation();
        setupTouchGestures();
        collectMediaItems();
        initializeLazyLoading();
    });

    /**
     * Create lightbox DOM structure
     */
    function initializeGallery() {
        // Create lightbox overlay
        lightboxOverlay = document.createElement('div');
        lightboxOverlay.id = 'lightbox-overlay';
        lightboxOverlay.className = 'lightbox-overlay';
        lightboxOverlay.style.display = 'none';
        
        // Create lightbox content container
        lightboxContent = document.createElement('div');
        lightboxContent.className = 'lightbox-content';
        
        // Create close button
        closeButton = document.createElement('button');
        closeButton.className = 'lightbox-close';
        closeButton.innerHTML = '&times;';
        closeButton.onclick = closeLightbox;
        
        // Create navigation buttons
        prevButton = document.createElement('button');
        prevButton.className = 'lightbox-nav lightbox-prev';
        prevButton.innerHTML = '&#8249;';
        prevButton.onclick = showPrevious;
        
        nextButton = document.createElement('button');
        nextButton.className = 'lightbox-nav lightbox-next';
        nextButton.innerHTML = '&#8250;';
        nextButton.onclick = showNext;
        
        // Create media container
        const mediaContainer = document.createElement('div');
        mediaContainer.className = 'lightbox-media-container';
        
        // Create image element
        lightboxImage = document.createElement('img');
        lightboxImage.className = 'lightbox-image';
        lightboxImage.style.display = 'none';
        
        // Create video iframe
        lightboxVideo = document.createElement('iframe');
        lightboxVideo.className = 'lightbox-video';
        lightboxVideo.style.display = 'none';
        lightboxVideo.frameBorder = '0';
        lightboxVideo.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
        lightboxVideo.allowFullscreen = true;
        
        // Create info container
        const infoContainer = document.createElement('div');
        infoContainer.className = 'lightbox-info';
        
        lightboxTitle = document.createElement('h3');
        lightboxTitle.className = 'lightbox-title';
        
        lightboxDescription = document.createElement('p');
        lightboxDescription.className = 'lightbox-description';
        
        // Create loading spinner
        loadingSpinner = document.createElement('div');
        loadingSpinner.className = 'lightbox-spinner';
        loadingSpinner.innerHTML = '<div class="spinner"></div>';
        
        // Assemble the lightbox
        mediaContainer.appendChild(lightboxImage);
        mediaContainer.appendChild(lightboxVideo);
        mediaContainer.appendChild(loadingSpinner);
        
        infoContainer.appendChild(lightboxTitle);
        infoContainer.appendChild(lightboxDescription);
        
        lightboxContent.appendChild(closeButton);
        lightboxContent.appendChild(prevButton);
        lightboxContent.appendChild(nextButton);
        lightboxContent.appendChild(mediaContainer);
        lightboxContent.appendChild(infoContainer);
        
        lightboxOverlay.appendChild(lightboxContent);
        
        // Add to body
        document.body.appendChild(lightboxOverlay);
        
        // Add click outside to close
        lightboxOverlay.addEventListener('click', function(e) {
            if (e.target === lightboxOverlay) {
                closeLightbox();
            }
        });
        
        // Add styles
        addLightboxStyles();
    }

    /**
     * Add lightbox CSS styles
     */
    function addLightboxStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .lightbox-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.95);
                z-index: 9999;
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            .lightbox-overlay.active {
                opacity: 1;
            }

            .lightbox-content {
                position: relative;
                max-width: 90%;
                max-height: 90%;
                display: flex;
                flex-direction: column;
                align-items: center;
            }

            .lightbox-media-container {
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 200px;
            }

            .lightbox-image {
                max-width: 100%;
                max-height: 80vh;
                object-fit: contain;
                border-radius: 8px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            }

            .lightbox-video {
                width: 80vw;
                height: 45vw;
                max-width: 1200px;
                max-height: 675px;
                border-radius: 8px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            }

            .lightbox-close {
                position: absolute;
                top: -40px;
                right: -40px;
                width: 40px;
                height: 40px;
                background: transparent;
                border: none;
                color: white;
                font-size: 40px;
                cursor: pointer;
                z-index: 10001;
                transition: transform 0.3s ease;
            }

            .lightbox-close:hover {
                transform: scale(1.1);
            }

            .lightbox-nav {
                position: absolute;
                top: 50%;
                transform: translateY(-50%);
                background: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(255, 255, 255, 0.3);
                color: white;
                font-size: 40px;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                cursor: pointer;
                transition: all 0.3s ease;
                z-index: 10000;
            }

            .lightbox-nav:hover {
                background: rgba(255, 255, 255, 0.2);
                border-color: rgba(255, 255, 255, 0.5);
            }

            .lightbox-prev {
                left: -80px;
            }

            .lightbox-next {
                right: -80px;
            }

            .lightbox-info {
                margin-top: 20px;
                text-align: center;
                color: white;
                max-width: 600px;
            }

            .lightbox-title {
                font-size: 1.5rem;
                margin-bottom: 10px;
                font-weight: 600;
            }

            .lightbox-description {
                font-size: 1rem;
                opacity: 0.9;
                line-height: 1.5;
            }

            .lightbox-spinner {
                position: absolute;
                display: none;
            }

            .lightbox-spinner.active {
                display: block;
            }

            .spinner {
                border: 3px solid rgba(255, 255, 255, 0.3);
                border-top: 3px solid white;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            /* Mobile styles */
            @media (max-width: 768px) {
                .lightbox-close {
                    top: 10px;
                    right: 10px;
                    width: 35px;
                    height: 35px;
                    font-size: 35px;
                }

                .lightbox-nav {
                    width: 45px;
                    height: 45px;
                    font-size: 30px;
                }

                .lightbox-prev {
                    left: 10px;
                }

                .lightbox-next {
                    right: 10px;
                }

                .lightbox-video {
                    width: 90vw;
                    height: 50vw;
                }

                .lightbox-title {
                    font-size: 1.2rem;
                }

                .lightbox-description {
                    font-size: 0.9rem;
                }
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Collect all media items from the gallery
     */
    function collectMediaItems() {
        const items = document.querySelectorAll('.media-item');
        currentMediaItems = Array.from(items).map((item, index) => {
            let src = '';
            let description = '';
            
            // Get source URL based on media type
            if (item.dataset.type === 'video') {
                // For video items, get from video player component
                const videoContainer = item.querySelector('.video-player-container');
                src = videoContainer ? videoContainer.dataset.videoUrl : '';
                // Get description from video player component
                const videoDesc = item.querySelector('.video-description');
                description = videoDesc ? videoDesc.textContent : '';
            } else {
                // For photo items, get from media-thumbnail
                const thumbnail = item.querySelector('.media-thumbnail');
                src = thumbnail ? thumbnail.dataset.src : '';
                // Get description from media-info
                const mediaDesc = item.querySelector('.media-info p');
                description = mediaDesc ? mediaDesc.textContent : '';
            }
            
            return {
                element: item,
                type: item.dataset.type,
                src: src,
                title: item.dataset.title || '',
                description: description,
                index: index
            };
        });
    }

    /**
     * Open lightbox with specific media
     */
    window.openLightbox = function(type, src, title, description) {
        if (!lightboxOverlay) return;

        // Find current index
        currentIndex = currentMediaItems.findIndex(item => item.src === src);
        
        // Show lightbox
        lightboxOverlay.style.display = 'flex';
        setTimeout(() => {
            lightboxOverlay.classList.add('active');
        }, 10);
        
        lightboxOpen = true;
        document.body.style.overflow = 'hidden';
        
        // Display media
        displayMedia(type, src, title, description);
        
        // Update navigation buttons
        updateNavigationButtons();
        
        // Preload adjacent images
        preloadAdjacentImages();
    };

    /**
     * Display media in lightbox
     */
    function displayMedia(type, src, title, description) {
        // Show loading spinner
        loadingSpinner.classList.add('active');
        
        // Hide both media elements
        lightboxImage.style.display = 'none';
        lightboxVideo.style.display = 'none';
        
        // Update info
        lightboxTitle.textContent = title || '';
        lightboxDescription.textContent = description || '';
        
        if (type === 'photo') {
            // Preload image
            const tempImg = new Image();
            tempImg.onload = function() {
                lightboxImage.src = src;
                lightboxImage.style.display = 'block';
                loadingSpinner.classList.remove('active');
            };
            tempImg.onerror = function() {
                loadingSpinner.classList.remove('active');
                lightboxTitle.textContent = 'Error loading image';
            };
            tempImg.src = src;
        } else if (type === 'video') {
            // Parse video URL and convert to embed URL
            const embedUrl = parseVideoUrlForEmbed(src);
            if (embedUrl) {
                lightboxVideo.src = embedUrl;
                lightboxVideo.style.display = 'block';
                loadingSpinner.classList.remove('active');
            } else {
                loadingSpinner.classList.remove('active');
                lightboxTitle.textContent = 'Unsupported video format';
            }
        }
    }
    
    /**
     * Parse video URL and convert to embed format
     */
    function parseVideoUrlForEmbed(url) {
        const providers = {
            youtube: {
                regex: /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]+)/,
                embedUrl: 'https://www.youtube.com/embed/',
                params: '?autoplay=1&rel=0&modestbranding=1'
            },
            vimeo: {
                regex: /(?:vimeo\.com\/)([0-9]+)/,
                embedUrl: 'https://player.vimeo.com/video/',
                params: '?autoplay=1&title=0&byline=0&portrait=0'
            }
        };
        
        for (const [provider, config] of Object.entries(providers)) {
            const match = url.match(config.regex);
            if (match) {
                return config.embedUrl + match[1] + config.params;
            }
        }
        
        // If already an embed URL, return as is
        if (url.includes('youtube.com/embed/') || url.includes('player.vimeo.com/video/')) {
            return url;
        }
        
        return null;
    }

    /**
     * Close lightbox
     */
    function closeLightbox() {
        if (!lightboxOverlay) return;
        
        lightboxOverlay.classList.remove('active');
        setTimeout(() => {
            lightboxOverlay.style.display = 'none';
            lightboxVideo.src = ''; // Stop video
        }, 300);
        
        lightboxOpen = false;
        document.body.style.overflow = '';
    }

    /**
     * Show previous media item
     */
    function showPrevious() {
        if (currentIndex > 0) {
            currentIndex--;
            const item = currentMediaItems[currentIndex];
            displayMedia(item.type, item.src, item.title, item.description);
            updateNavigationButtons();
            preloadAdjacentImages();
        }
    }

    /**
     * Show next media item
     */
    function showNext() {
        if (currentIndex < currentMediaItems.length - 1) {
            currentIndex++;
            const item = currentMediaItems[currentIndex];
            displayMedia(item.type, item.src, item.title, item.description);
            updateNavigationButtons();
            preloadAdjacentImages();
        }
    }

    /**
     * Update navigation button visibility
     */
    function updateNavigationButtons() {
        if (prevButton) {
            prevButton.style.display = currentIndex > 0 ? 'block' : 'none';
        }
        if (nextButton) {
            nextButton.style.display = currentIndex < currentMediaItems.length - 1 ? 'block' : 'none';
        }
    }

    /**
     * Preload adjacent images for smooth transitions
     */
    function preloadAdjacentImages() {
        // Preload next image
        if (currentIndex < currentMediaItems.length - 1) {
            const nextItem = currentMediaItems[currentIndex + 1];
            if (nextItem.type === 'photo') {
                const img = new Image();
                img.src = nextItem.src;
            }
        }
        
        // Preload previous image
        if (currentIndex > 0) {
            const prevItem = currentMediaItems[currentIndex - 1];
            if (prevItem.type === 'photo') {
                const img = new Image();
                img.src = prevItem.src;
            }
        }
    }

    /**
     * Setup keyboard navigation
     */
    function setupKeyboardNavigation() {
        document.addEventListener('keydown', function(e) {
            if (!lightboxOpen) return;
            
            switch(e.key) {
                case 'Escape':
                    closeLightbox();
                    break;
                case 'ArrowLeft':
                    showPrevious();
                    break;
                case 'ArrowRight':
                    showNext();
                    break;
            }
        });
    }

    /**
     * Setup touch gestures for mobile
     */
    function setupTouchGestures() {
        if (!lightboxOverlay) return;
        
        lightboxOverlay.addEventListener('touchstart', handleTouchStart, {passive: true});
        lightboxOverlay.addEventListener('touchend', handleTouchEnd, {passive: true});
    }

    function handleTouchStart(e) {
        touchStartX = e.changedTouches[0].screenX;
    }

    function handleTouchEnd(e) {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    }

    function handleSwipe() {
        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;
        
        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                // Swipe left - show next
                showNext();
            } else {
                // Swipe right - show previous
                showPrevious();
            }
        }
    }

    /**
     * Initialize lazy loading for gallery images
     */
    window.initializeLazyLoading = function() {
        const lazyImages = document.querySelectorAll('.lazy-load:not(.loaded)');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.onload = function() {
                            img.classList.add('loaded');
                        };
                        observer.unobserve(img);
                    }
                });
            }, {
                rootMargin: '50px 0px',
                threshold: 0.01
            });
            
            lazyImages.forEach(img => imageObserver.observe(img));
        } else {
            // Fallback for browsers without IntersectionObserver
            lazyImages.forEach(img => {
                img.src = img.dataset.src;
                img.classList.add('loaded');
            });
        }
    };

})();