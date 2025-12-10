/**
 * Testimonial Form Interactive Star Rating System
 * Implements accessible star rating with keyboard navigation and screen reader support
 */

(function() {
    'use strict';

    class StarRating {
        constructor(container) {
            this.container = container;
            this.stars = container.querySelectorAll('.star');
            this.input = container.querySelector('input[type="hidden"]');
            this.currentRating = parseInt(this.input?.value) || 0;
            this.hoveredRating = 0;
            
            // Color configuration
            this.activeColor = '#C7B375'; // Gold color for selected stars
            this.inactiveColor = '#D3D3D3'; // Gray for empty stars
            this.hoverColor = '#E0D4A3'; // Lighter gold for hover
            
            this.init();
        }

        init() {
            if (!this.stars.length) return;
            
            // Set initial state
            this.updateDisplay(this.currentRating);
            
            // Add event listeners
            this.stars.forEach((star, index) => {
                const rating = index + 1;
                
                // Mouse events
                star.addEventListener('mouseenter', () => this.handleHover(rating));
                star.addEventListener('mouseleave', () => this.handleMouseLeave());
                star.addEventListener('click', () => this.handleClick(rating));
                
                // Keyboard events
                star.addEventListener('keydown', (e) => this.handleKeyDown(e, rating));
                
                // Touch events for mobile
                star.addEventListener('touchstart', (e) => {
                    e.preventDefault();
                    this.handleClick(rating);
                });
                
                // Set ARIA attributes
                this.setAriaAttributes(star, rating);
            });
            
            // Container-level keyboard navigation
            this.container.addEventListener('keydown', (e) => this.handleContainerKeyDown(e));
        }

        setAriaAttributes(star, rating) {
            star.setAttribute('role', 'radio');
            star.setAttribute('aria-label', `${rating} star${rating > 1 ? 's' : ''}`);
            star.setAttribute('aria-checked', rating <= this.currentRating ? 'true' : 'false');
            star.setAttribute('tabindex', rating === 1 || rating === this.currentRating ? '0' : '-1');
        }

        handleHover(rating) {
            this.hoveredRating = rating;
            this.updateDisplay(rating, true);
            this.announceToScreenReader(`Hovering ${rating} star${rating > 1 ? 's' : ''}`);
        }

        handleMouseLeave() {
            this.hoveredRating = 0;
            this.updateDisplay(this.currentRating);
        }

        handleClick(rating) {
            this.currentRating = rating;
            if (this.input) {
                this.input.value = rating;
                // Trigger change event for form validation
                this.input.dispatchEvent(new Event('change', { bubbles: true }));
            }
            
            this.updateDisplay(rating);
            this.updateAriaStates();
            this.provideFeedback(rating);
            this.announceToScreenReader(`Selected ${rating} star${rating > 1 ? 's' : ''}`);
        }

        handleKeyDown(e, rating) {
            switch(e.key) {
                case 'Enter':
                case ' ':
                    e.preventDefault();
                    this.handleClick(rating);
                    break;
            }
        }

        handleContainerKeyDown(e) {
            let newRating = this.currentRating;
            
            switch(e.key) {
                case 'ArrowRight':
                case 'ArrowUp':
                    e.preventDefault();
                    newRating = Math.min(5, this.currentRating + 1);
                    break;
                case 'ArrowLeft':
                case 'ArrowDown':
                    e.preventDefault();
                    newRating = Math.max(1, this.currentRating - 1);
                    break;
                case 'Home':
                    e.preventDefault();
                    newRating = 1;
                    break;
                case 'End':
                    e.preventDefault();
                    newRating = 5;
                    break;
                default:
                    return;
            }
            
            if (newRating !== this.currentRating) {
                this.handleClick(newRating);
                // Focus the newly selected star
                if (this.stars[newRating - 1]) {
                    this.stars[newRating - 1].focus();
                }
            }
        }

        updateDisplay(rating, isHover = false) {
            this.stars.forEach((star, index) => {
                const starRating = index + 1;
                const icon = star.querySelector('i') || star;
                
                if (starRating <= rating) {
                    // Filled star
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                    star.style.color = isHover ? this.hoverColor : this.activeColor;
                    star.style.transform = isHover ? 'scale(1.1)' : 'scale(1)';
                } else {
                    // Empty star
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                    star.style.color = this.inactiveColor;
                    star.style.transform = 'scale(1)';
                }
                
                // Add transition for smooth effect
                star.style.transition = 'all 0.2s ease';
            });
        }

        updateAriaStates() {
            this.stars.forEach((star, index) => {
                const rating = index + 1;
                star.setAttribute('aria-checked', rating <= this.currentRating ? 'true' : 'false');
                star.setAttribute('tabindex', rating === this.currentRating ? '0' : '-1');
            });
        }

        provideFeedback(rating) {
            // Visual feedback animation
            const selectedStar = this.stars[rating - 1];
            if (selectedStar) {
                selectedStar.style.transform = 'scale(1.3)';
                setTimeout(() => {
                    selectedStar.style.transform = 'scale(1)';
                }, 200);
            }
            
            // Optional: Add success message
            const feedbackMessages = {
                1: 'We appreciate your feedback',
                2: 'Thank you for your rating',
                3: 'Thanks for your feedback',
                4: 'Great! Thanks for rating us',
                5: 'Awesome! Thank you so much!'
            };
            
            const messageEl = this.container.querySelector('.rating-feedback');
            if (messageEl) {
                messageEl.textContent = feedbackMessages[rating];
                messageEl.style.opacity = '1';
                setTimeout(() => {
                    messageEl.style.opacity = '0';
                }, 3000);
            }
        }

        announceToScreenReader(message) {
            // Create or update live region for screen reader announcements
            let liveRegion = document.getElementById('star-rating-live-region');
            if (!liveRegion) {
                liveRegion = document.createElement('div');
                liveRegion.id = 'star-rating-live-region';
                liveRegion.setAttribute('aria-live', 'polite');
                liveRegion.setAttribute('aria-atomic', 'true');
                liveRegion.className = 'sr-only';
                document.body.appendChild(liveRegion);
            }
            liveRegion.textContent = message;
        }
    }

    // Initialize all star rating components on page load
    document.addEventListener('DOMContentLoaded', function() {
        const ratingContainers = document.querySelectorAll('.star-rating-container');
        ratingContainers.forEach(container => {
            new StarRating(container);
        });
    });

    // Form validation integration
    const testimonialForm = document.getElementById('testimonial-form');
    if (testimonialForm) {
        testimonialForm.addEventListener('submit', function(e) {
            const ratingInput = this.querySelector('input[name="rating"]');
            if (!ratingInput || !ratingInput.value) {
                e.preventDefault();
                const ratingContainer = this.querySelector('.star-rating-container');
                if (ratingContainer) {
                    ratingContainer.classList.add('error');
                    const errorMsg = ratingContainer.querySelector('.error-message') || 
                                   document.createElement('div');
                    errorMsg.className = 'error-message text-danger mt-1';
                    errorMsg.textContent = 'Please select a rating';
                    if (!ratingContainer.querySelector('.error-message')) {
                        ratingContainer.appendChild(errorMsg);
                    }
                    
                    // Focus first star for accessibility
                    const firstStar = ratingContainer.querySelector('.star');
                    if (firstStar) firstStar.focus();
                }
                return false;
            }
        });
    }

    // Mobile touch optimization
    if ('ontouchstart' in window) {
        document.body.classList.add('touch-device');
        
        // Add CSS for better touch targets
        const style = document.createElement('style');
        style.textContent = `
            .touch-device .star {
                padding: 10px;
                margin: 0 2px;
            }
            
            .touch-device .star-rating-container {
                display: flex;
                align-items: center;
                justify-content: center;
            }
        `;
        document.head.appendChild(style);
    }

    // Expose StarRating class globally if needed
    window.StarRating = StarRating;

})();

// Additional utility styles
const starRatingStyles = `
<style>
.star-rating-container {
    display: inline-flex;
    gap: 8px;
    padding: 10px 0;
}

.star {
    font-size: 28px;
    cursor: pointer;
    transition: all 0.2s ease;
    color: #D3D3D3;
}

.star:hover {
    transform: scale(1.1);
}

.star:focus {
    outline: 2px solid #C7B375;
    outline-offset: 2px;
    border-radius: 4px;
}

.star.active {
    color: #C7B375;
}

.rating-feedback {
    margin-left: 15px;
    color: #C7B375;
    font-weight: 500;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.star-rating-container.error {
    animation: shake 0.5s;
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}

.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}

/* Mobile responsive styles */
@media (max-width: 576px) {
    .star {
        font-size: 32px;
        padding: 8px;
    }
    
    .star-rating-container {
        gap: 12px;
    }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
    .star:focus {
        outline-width: 3px;
    }
    
    .star.active {
        text-shadow: 0 0 2px #000;
    }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
    .star,
    .rating-feedback {
        transition: none;
    }
    
    .star-rating-container.error {
        animation: none;
        border: 2px solid red;
    }
}
</style>
`;

// Auto-inject styles if not already present
if (!document.querySelector('#star-rating-styles')) {
    const styleElement = document.createElement('div');
    styleElement.id = 'star-rating-styles';
    styleElement.innerHTML = starRatingStyles;
    document.head.appendChild(styleElement.firstElementChild);
}