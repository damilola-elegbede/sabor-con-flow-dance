/**
 * Spotify Playlists Integration - SPEC_05 Group C Task 8
 * Handles Spotify embed loading, error handling, and user interactions
 */

class SpotifyPlaylistManager {
    constructor() {
        this.loadedEmbeds = new Set();
        this.errorRetries = new Map();
        this.maxRetries = 3;
        this.retryDelay = 2000;
        
        this.init();
    }
    
    init() {
        // Initialize all playlist embeds on page load
        this.initializeEmbeds();
        
        // Set up intersection observer for lazy loading
        this.setupIntersectionObserver();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Performance monitoring
        this.monitorEmbedPerformance();
    }
    
    initializeEmbeds() {
        const embedContainers = document.querySelectorAll('.playlist-embed-container');
        
        embedContainers.forEach(container => {
            this.loadEmbed(container);
        });
    }
    
    setupIntersectionObserver() {
        if (!('IntersectionObserver' in window)) {
            return; // Fallback for older browsers
        }
        
        const options = {
            root: null,
            rootMargin: '100px',
            threshold: 0.1
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const container = entry.target;
                    const embedId = container.dataset.embedId;
                    
                    if (!this.loadedEmbeds.has(embedId)) {
                        this.loadEmbed(container);
                    }
                    
                    observer.unobserve(container);
                }
            });
        }, options);
        
        // Observe all embed containers
        document.querySelectorAll('.playlist-embed-container').forEach(container => {
            observer.observe(container);
        });
    }
    
    loadEmbed(container) {
        const embedUrl = container.dataset.embedUrl;
        const embedId = container.dataset.embedId;
        const loadingElement = container.querySelector('.playlist-loading');
        
        if (!embedUrl || this.loadedEmbeds.has(embedId)) {
            return;
        }
        
        // Show loading state
        if (loadingElement) {
            loadingElement.style.display = 'block';
        }
        
        // Create iframe element
        const iframe = document.createElement('iframe');
        iframe.className = 'playlist-embed';
        iframe.src = embedUrl;
        iframe.allow = 'autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture';
        iframe.loading = 'lazy';
        iframe.title = `Spotify playlist: ${container.dataset.playlistTitle || 'Dance Music'}`;
        
        // Handle successful load
        iframe.onload = () => {
            this.handleEmbedLoad(container, iframe, embedId);
        };
        
        // Handle error
        iframe.onerror = () => {
            this.handleEmbedError(container, embedId);
        };
        
        // Timeout fallback
        setTimeout(() => {
            if (!this.loadedEmbeds.has(embedId) && iframe.src) {
                this.handleEmbedError(container, embedId);
            }
        }, 10000); // 10 second timeout
        
        // Add iframe to container
        container.appendChild(iframe);
    }
    
    handleEmbedLoad(container, iframe, embedId) {
        const loadingElement = container.querySelector('.playlist-loading');
        const errorElement = container.querySelector('.playlist-error');
        
        // Hide loading and error states
        if (loadingElement) loadingElement.style.display = 'none';
        if (errorElement) errorElement.style.display = 'none';
        
        // Show iframe
        iframe.style.opacity = '1';
        iframe.style.transition = 'opacity 0.3s ease';
        
        // Mark as loaded
        this.loadedEmbeds.add(embedId);
        
        // Track successful load
        this.trackEmbedEvent('load_success', embedId);
        
        console.log(`Spotify embed loaded successfully: ${embedId}`);
    }
    
    handleEmbedError(container, embedId) {
        const loadingElement = container.querySelector('.playlist-loading');
        const errorElement = container.querySelector('.playlist-error');
        const iframe = container.querySelector('.playlist-embed');
        
        // Hide loading state
        if (loadingElement) loadingElement.style.display = 'none';
        
        // Remove failed iframe
        if (iframe) iframe.remove();
        
        // Check retry count
        const retryCount = this.errorRetries.get(embedId) || 0;
        
        if (retryCount < this.maxRetries) {
            // Attempt retry
            this.errorRetries.set(embedId, retryCount + 1);
            
            setTimeout(() => {
                console.log(`Retrying Spotify embed load: ${embedId} (attempt ${retryCount + 1})`);
                this.loadEmbed(container);
            }, this.retryDelay * (retryCount + 1));
            
        } else {
            // Show error state
            if (errorElement) {
                errorElement.style.display = 'block';
            } else {
                this.createErrorMessage(container);
            }
            
            // Track error
            this.trackEmbedEvent('load_error', embedId);
            
            console.error(`Failed to load Spotify embed after ${this.maxRetries} attempts: ${embedId}`);
        }
    }
    
    createErrorMessage(container) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'playlist-error';
        errorDiv.innerHTML = `
            <p><i class="fas fa-exclamation-triangle"></i> Unable to load playlist</p>
            <p>Please try opening directly in Spotify</p>
        `;
        container.appendChild(errorDiv);
    }
    
    setupEventListeners() {
        // Handle share button clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('.playlist-share') || e.target.closest('.playlist-share')) {
                e.preventDefault();
                this.handleShare(e.target.closest('.playlist-card'));
            }
        });
        
        // Handle Spotify open button clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('.playlist-open-spotify') || e.target.closest('.playlist-open-spotify')) {
                this.trackEmbedEvent('external_open', e.target.dataset.playlistId);
            }
        });
        
        // Handle card hover for analytics
        document.addEventListener('mouseenter', (e) => {
            if (e.target.matches('.playlist-card')) {
                this.trackEmbedEvent('card_hover', e.target.dataset.playlistId);
            }
        }, true);
    }
    
    handleShare(playlistCard) {
        const playlistTitle = playlistCard.querySelector('.playlist-title')?.textContent || 'Dance Playlist';
        const spotifyUrl = playlistCard.querySelector('.playlist-open-spotify')?.href;
        
        if (!spotifyUrl) {
            this.showNotification('Share link not available', 'error');
            return;
        }
        
        // Try native Web Share API first
        if (navigator.share) {
            navigator.share({
                title: `${playlistTitle} - Sabor con Flow Dance`,
                text: `Check out this dance playlist: ${playlistTitle}`,
                url: spotifyUrl
            }).then(() => {
                this.trackEmbedEvent('share_success', playlistCard.dataset.playlistId);
                this.showNotification('Playlist shared successfully!', 'success');
            }).catch((error) => {
                if (error.name !== 'AbortError') {
                    this.fallbackShare(spotifyUrl, playlistTitle);
                }
            });
        } else {
            this.fallbackShare(spotifyUrl, playlistTitle);
        }
    }
    
    fallbackShare(url, title) {
        // Fallback: Copy to clipboard
        if (navigator.clipboard) {
            navigator.clipboard.writeText(url).then(() => {
                this.showNotification('Playlist link copied to clipboard!', 'success');
                this.trackEmbedEvent('share_clipboard', null);
            }).catch(() => {
                this.showShareModal(url, title);
            });
        } else {
            this.showShareModal(url, title);
        }
    }
    
    showShareModal(url, title) {
        // Create share modal
        const modal = document.createElement('div');
        modal.className = 'share-modal';
        modal.innerHTML = `
            <div class="share-modal-content">
                <div class="share-modal-header">
                    <h3>Share Playlist</h3>
                    <button class="share-modal-close">&times;</button>
                </div>
                <div class="share-modal-body">
                    <p>Share "${title}" with friends:</p>
                    <div class="share-url-container">
                        <input type="text" class="share-url-input" value="${url}" readonly>
                        <button class="share-copy-btn">Copy</button>
                    </div>
                    <div class="share-social-buttons">
                        <a href="https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}" target="_blank" class="share-btn facebook">
                            <i class="fab fa-facebook-f"></i> Facebook
                        </a>
                        <a href="https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}" target="_blank" class="share-btn twitter">
                            <i class="fab fa-twitter"></i> Twitter
                        </a>
                        <a href="https://wa.me/?text=${encodeURIComponent(title + ' - ' + url)}" target="_blank" class="share-btn whatsapp">
                            <i class="fab fa-whatsapp"></i> WhatsApp
                        </a>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Modal event listeners
        modal.querySelector('.share-modal-close').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        
        modal.querySelector('.share-copy-btn').addEventListener('click', () => {
            const input = modal.querySelector('.share-url-input');
            input.select();
            document.execCommand('copy');
            this.showNotification('Link copied!', 'success');
        });
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `playlist-notification ${type}`;
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '1rem 1.5rem',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '500',
            zIndex: '10000',
            opacity: '0',
            transform: 'translateY(-20px)',
            transition: 'all 0.3s ease'
        });
        
        // Set background color based on type
        const colors = {
            success: '#1DB954',
            error: '#ff6b6b',
            info: '#C7B375'
        };
        notification.style.backgroundColor = colors[type] || colors.info;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateY(0)';
        }, 100);
        
        // Remove after delay
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
    
    trackEmbedEvent(eventType, playlistId) {
        // Track events for analytics
        if (typeof gtag !== 'undefined') {
            gtag('event', 'spotify_playlist_interaction', {
                event_category: 'Spotify Playlists',
                event_label: eventType,
                playlist_id: playlistId
            });
        }
        
        // Performance API tracking
        if (performance && performance.mark) {
            performance.mark(`spotify-${eventType}-${Date.now()}`);
        }
        
        console.log(`Spotify event tracked: ${eventType}`, { playlistId });
    }
    
    monitorEmbedPerformance() {
        // Monitor embed loading performance
        const observer = new PerformanceObserver((list) => {
            list.getEntries().forEach((entry) => {
                if (entry.name.includes('spotify.com')) {
                    console.log('Spotify embed performance:', {
                        name: entry.name,
                        duration: entry.duration,
                        startTime: entry.startTime
                    });
                    
                    // Track slow loading embeds
                    if (entry.duration > 5000) {
                        this.trackEmbedEvent('slow_load', null);
                    }
                }
            });
        });
        
        try {
            observer.observe({ entryTypes: ['resource'] });
        } catch (e) {
            console.log('Performance monitoring not available');
        }
    }
    
    // Public methods for external use
    refreshEmbed(embedId) {
        const container = document.querySelector(`[data-embed-id="${embedId}"]`);
        if (container) {
            this.loadedEmbeds.delete(embedId);
            this.errorRetries.delete(embedId);
            
            // Clear container
            const iframe = container.querySelector('.playlist-embed');
            if (iframe) iframe.remove();
            
            // Reload
            this.loadEmbed(container);
        }
    }
    
    getLoadedEmbeds() {
        return Array.from(this.loadedEmbeds);
    }
    
    getEmbedStats() {
        return {
            loaded: this.loadedEmbeds.size,
            errors: this.errorRetries.size,
            total: document.querySelectorAll('.playlist-embed-container').length
        };
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Check if there are any playlist embeds on the page
    if (document.querySelector('.playlist-embed-container')) {
        window.spotifyPlaylistManager = new SpotifyPlaylistManager();
        
        // Expose manager for debugging
        if (window.location.hostname === 'localhost' || window.location.hostname.includes('127.0.0.1')) {
            console.log('Spotify Playlist Manager initialized:', window.spotifyPlaylistManager);
        }
    }
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && window.spotifyPlaylistManager) {
        // Refresh any failed embeds when page becomes visible again
        const stats = window.spotifyPlaylistManager.getEmbedStats();
        if (stats.errors > 0) {
            console.log('Page visible again, refreshing failed embeds');
            // Could implement auto-refresh logic here
        }
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SpotifyPlaylistManager;
}