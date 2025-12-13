# Sabor con Flow Dance

A Django-based website for Sabor con Flow Dance, featuring class information, registration, and private lesson booking.

## Features

- Class information display
- Private lessons page with Calendly booking integration
- Responsive design
- Direct booking system for private lessons
- Static content website (no database required)

## Pages

- **Home** - Landing page with Sabor Con Flow logo
- **Events** - Shows all dance classes with pricing and schedules
- **Pricing** - Standard class pricing information
- **Private Lessons** - Dedicated page for private lesson information and booking
- **Contact** - Contact form with email notification, plus social media links

## Private Lessons

The private lessons system includes:
- Detailed pricing table (per hour rates)
- Benefits of private instruction
- Direct Calendly booking integration
- Customized lesson plans
- Flexible scheduling options

### Booking System

Private lessons can be booked directly through the Calendly widget on the Private Lessons page:
- Floating booking button (bottom right)
- Integrated with Calendly scheduling system
- Customized with website theme colors
- Available on the dedicated Private Lessons page

## Contact Form

The contact page includes a fully functional contact form with:

### Features
- **Client-side validation**: Real-time field validation with error messages
- **Server-side validation**: Django form validation matching client rules
- **AJAX submission**: Form submits without page reload via JSON API
- **CSRF protection**: Django CSRF token integration
- **Honeypot spam protection**: Hidden field traps bots (silently succeeds without sending email)
- **Email notification**: Sends email to configured address when form is submitted
- **Character counter**: Live count for message field (max 2000 characters)
- **Loading state**: Spinner animation during form submission
- **Success/error messages**: Clear feedback after submission

### Form Fields
- **Name** (required): 2-100 characters
- **Email** (required): Valid email format
- **Subject** (dropdown): General Inquiry, Class Information, Private Lessons, Events & Workshops, Other
- **Message** (required): 10-2000 characters

### Email Configuration

For production, set the following environment variables:
```bash
EMAIL_HOST=smtp.gmail.com          # SMTP server
EMAIL_PORT=587                      # SMTP port
EMAIL_USE_TLS=True                  # Use TLS encryption
EMAIL_HOST_USER=your-email          # SMTP username
EMAIL_HOST_PASSWORD=your-password   # SMTP password (use app password for Gmail)
DEFAULT_FROM_EMAIL=noreply@domain   # From address for emails
CONTACT_EMAIL=contact@domain        # Where to receive contact form submissions
```

In development (when EMAIL_HOST is not set), emails are printed to the console.

## Project Structure

```
sabor-con-flow-dance/
├── api/                    # Vercel serverless functions
│   └── index.py           # Main API entry point
├── core/                   # Django app
│   ├── views.py           # View logic (static content)
│   ├── urls.py            # URL routing
│   └── models.py          # Placeholder file (no models used)
│   └── forms.py           # Contact form with validation
├── static/                 # Static assets
│   ├── css/               # Modular CSS architecture
│   │   ├── base/          # Foundation styles
│   │   │   ├── variables.css   # CSS design tokens + animation tokens
│   │   │   ├── reset.css       # Box model reset, accessibility, reduced motion
│   │   │   ├── typography.css  # Text styles, utilities
│   │   │   └── animations.css  # Scroll animation styles, keyframes, utilities
│   │   ├── components/    # UI components
│   │   │   ├── buttons.css     # Button styles + ripple effect
│   │   │   ├── cards.css       # Card-based UI + hover effects
│   │   │   ├── forms.css       # Input focus animations + contact form styles
│   │   │   ├── gallery.css     # Media components
│   │   │   └── navigation.css  # Nav, header, footer, social icons
│   │   ├── layouts/       # Page structures
│   │   │   ├── grid.css        # Grid systems
│   │   │   └── sections.css    # Page sections
│   │   └── main.css       # Import orchestrator
│   └── js/
│       ├── main.js        # RippleEffect, ButtonLoader, lazy loading
│       ├── animations.js  # Scroll animations, parallax, text reveal
│       └── contact.js     # Contact form validation and AJAX submission
├── staticfiles/            # Collected static files
├── templates/              # Base templates
├── vercel.json            # Vercel deployment configuration
└── requirements.txt       # Python dependencies
```

## CSS Architecture

The project uses a modular CSS architecture with CSS custom properties (design tokens) for consistent styling.

### Directory Structure

- **base/**: Foundation styles loaded first (variables, reset, typography)
- **layouts/**: Page structure and grid systems
- **components/**: Reusable UI components (buttons, cards, navigation, gallery)
- **main.css**: Import orchestrator that loads all modules in correct order

### Design Tokens

Design tokens in `static/css/base/variables.css` include:

- **Colors**: Brand palette (gold, black, white) with semantic aliases
- **Typography**: Font families (Inter for body, Playfair Display for headings), sizes, weights, and line heights
- **Spacing**: 4px base unit scale (xs through 3xl)
- **Shadows**: Layered elevation system (5 levels) and gold glow effects
- **Glassmorphism**: Semi-transparent backgrounds, backdrop blur, and glass borders
- **Transitions**: Standardized durations and easing functions
- **Z-Index**: Layering scale for dropdowns, modals, etc.

### Card System

The card components in `static/css/components/cards.css` provide modern UI patterns:

- **Glassmorphism Base** (`.card-glass`): Semi-transparent cards with backdrop blur effect
- **Elevation Utilities** (`.elevation-1` to `.elevation-5`): Layered shadow depth system
- **Interactive Elevation** (`.elevation-interactive`): Cards that rise on hover with gold glow
- **Gradient Borders** (`.card-gradient-border`): Animated diagonal gradient border effect
- **Top Accent** (`.card-top-accent`): Expanding gold top border on hover

Existing cards (`.event-card`, `.mission-item`, `.class-preview`) use glassmorphism with:
- Backdrop blur for depth
- Gold accent borders/gradients
- Hover lift animations
- Proper fallbacks for older browsers

### Gallery and Media System

The gallery components in `static/css/components/gallery.css` provide rich media presentation:

- **Video Container** (`.dual-video-container`): Side-by-side video layout with responsive stacking
- **Video Overlay** (`.video-overlay`): Fade-in caption overlay with backdrop blur on hover
- **Gallery Grid** (`.gallery-grid`): Responsive 3→2→1 column grid for images
- **Gallery Overlay** (`.gallery-overlay`): Slide-up overlay with staggered content animation
- **Grain Texture** (`.hero-grain`): SVG-based film grain overlay for premium aesthetic
- **Lazy Loading**: Native `loading="lazy"` with CSS fade-in transitions

Media features include:
- Video poster frames for immediate visual feedback
- Lazy loading with Intersection Observer fallback for older browsers
- Touch-friendly overlays (always visible on mobile)
- Expand icon indicator on gallery hover
- Aspect ratio preservation (3:2 for gallery, 16:10 on mobile)

### Button System

The button components in `static/css/components/buttons.css` include:

- **Base Button** (`.btn`): Consistent styling with gap support for icons
- **Primary** (`.btn-primary`): Gold fill, inverts on hover with lift effect
- **Secondary** (`.btn-secondary`): Outline style, fills on hover
- **Ripple Effect**: Material Design-inspired click ripple originating from click position
- **Loading State** (`.btn--loading`): CSS spinner animation with screen reader support
- **Icon Buttons** (`.btn-icon`): Circular icon-only buttons (44px touch target)
- **Icon with Text** (`.btn-with-icon`): Buttons combining icons and text
- **Size Variants**: `.btn-icon-sm` (36px) and `.btn-icon-lg` (56px)

JavaScript utilities in `static/js/main.js`:

```javascript
// Button loading state control
ButtonLoader.start(button, 'Submitting...');  // Show loading spinner
ButtonLoader.stop(button);                     // Remove loading state

// Ripple effect (auto-initialized on all .btn elements)
RippleEffect.init();                          // Initialize on page load
RippleEffect.attachRipple(button);            // Manually attach to new buttons
```

### Micro-Interactions

The site includes polished micro-interactions for a premium user experience:

#### Button Ripple Effect
- Click ripple animation originates from exact click position
- Different ripple colors for primary (dark) and secondary (gold) buttons
- Press feedback with scale transform on active state
- Implemented via CSS `::before` pseudo-element and `@keyframes ripple-expand`

#### Card Hover Effects
- Progressive shadow system with multi-layered shadows
- Cards lift on hover with smooth `ease-out-cubic` easing
- Gold glow effect using `::after` pseudo-element
- `will-change` optimization for 60fps animations

#### Menu Animations
- Enhanced slide-in with spring easing and scale transform
- Staggered entrance delays (50ms increments)
- Faster exit animation (no stagger, 200ms duration)
- Hover state shifts items 8px right

#### Link Underline Reveals
- Navigation links: gradient underline expands on hover
- Content links: underline scales from right-to-left origin, reverses on hover
- Smooth `ease-out-expo` easing for premium feel

#### Social Icon Interactions
- Background glow effect on hover (scales from 0.8 to 1)
- Lift effect (translateY -3px)
- Icon scales to 1.15 with 5deg rotation
- Press feedback scales icon to 0.95

#### Input Focus Animations
- Focus glow with 3px gold ring and subtle shadow
- Hover state transitions background opacity
- Floating label animation support
- 16px font-size on mobile prevents iOS zoom

### Scroll Animations

The site includes performant scroll-triggered animations using Intersection Observer:

#### Animation System (`static/js/animations.js`)
- **ScrollAnimations**: Intersection Observer-based reveal animations
- **ParallaxEffect**: Smooth parallax scrolling for hero elements
- **TextReveal**: Word-by-word and line-by-line text animations

#### Animation Presets
Elements use `data-animate` attributes to specify animation type:

| Preset | Effect | Use Case |
|--------|--------|----------|
| `fade-up` | Fade in from below | Default for most content |
| `fade-down` | Fade in from above | Page headers |
| `fade-left` | Fade in from right | Side content |
| `fade-right` | Fade in from left | Side content |
| `scale-up` | Scale from 90% | Cards, images |
| `scale-fade` | Scale + fade up | Hero videos |

#### Data Attributes
```html
<!-- Basic scroll animation -->
<div data-animate="fade-up">Content</div>

<!-- With custom duration and delay -->
<div data-animate="fade-up" data-duration="800" data-delay="200">Content</div>

<!-- Parallax effect -->
<div data-parallax data-parallax-factor="0.15">Parallax content</div>

<!-- Text reveal (word-by-word) -->
<h2 data-text-reveal="words">Animated heading</h2>
```

#### Staggered Animations
Grid items automatically receive staggered delays (100ms increments, max 500ms):
- Gallery items in `.gallery-grid`
- Mission items in `.mission-grid`
- Class previews in `.classes-grid`
- Event cards in `.event-container`
- Video items in `.dual-video-container`

#### Reduced Motion Support
All scroll animations respect `prefers-reduced-motion`:
- Animations disabled instantly when preference detected
- Elements shown immediately without motion
- No performance impact when reduced motion enabled

#### JavaScript API
```javascript
// Access animation modules
window.SaborAnimations.ScrollAnimations;
window.SaborAnimations.ParallaxEffect;
window.SaborAnimations.TextReveal;

// Reinitialize after dynamic content load
window.SaborAnimations.reinit();
```

### Animation Design Tokens

Animation timing and easing values in `static/css/base/variables.css`:

| Token | Value | Use Case |
|-------|-------|----------|
| `--duration-instant` | 100ms | Micro-feedback |
| `--duration-fast` | 200ms | Quick state changes |
| `--duration-normal` | 300ms | Standard transitions |
| `--duration-slow` | 400ms | Complex transforms |
| `--duration-slower` | 600ms | Scroll reveals |
| `--duration-slowest` | 800ms | Page load animations |

Easing functions:
- `--ease-out-cubic`: Smooth deceleration (default)
- `--ease-out-expo`: Dramatic deceleration
- `--ease-spring`: Overshoot bounce effect
- `--ease-in-out-cubic`: Symmetric acceleration

### Import Order

The `main.css` file imports modules in dependency order:

1. Base layer (variables → reset → typography → animations)
2. Layout layer (grid → sections)
3. Component layer (buttons → navigation → cards → gallery → forms)

### Responsive Breakpoints

The project uses a consistent breakpoint system across all CSS modules:

| Breakpoint | Description | Typical Usage |
|------------|-------------|---------------|
| `1200px` | Large desktop → Standard desktop | Reserved for future use |
| `1000px` | Desktop → Tablet landscape | Grid columns (3→2) |
| `768px` | Tablet → Mobile | Layout stacking, spacing adjustments |
| `600px` | Mobile → Small mobile | Single column layouts |
| `480px` | Small mobile refinements | Compact spacing, smaller fonts |

**Testing Viewports:** 320px, 480px, 600px, 768px, 1000px, 1200px, 1920px

### Touch Target Compliance

All interactive elements follow WCAG 2.1 Level AAA guidelines with minimum 44x44px touch targets:

- Navigation links (`.nav a`)
- Buttons (`.btn`, `.whatsapp-button`)
- Menu toggle (`.menu-toggle`)
- Social links (`.social-link`)

## Accessibility Features

The site includes built-in accessibility support:

- **Skip-to-content link**: Keyboard users can skip navigation and jump directly to main content
- **Focus-visible states**: Gold outline indicators for keyboard navigation (3px solid with 2-4px offset)
- **ARIA attributes**: Proper labeling for navigation, social links, and interactive elements
- **Screen reader utilities**: `.sr-only` class for visually hidden but accessible content
- **Focus trap**: Mobile menu traps focus within when open, preventing background interaction
- **Screen reader announcements**: Live region announces menu state changes
- **Escape key support**: Mobile menu closes on Escape key press
- **Reduced motion support**: Animations disabled when user prefers reduced motion
- **Semantic HTML**: Proper heading hierarchy, landmarks, and button/link roles

### Keyboard Navigation

- Press `Tab` to reveal skip-link at top of page
- Press `Enter` on skip-link to jump to main content
- Press `Escape` to close mobile navigation menu
- `Tab` cycles through menu items when open (focus trap)
- `Shift+Tab` cycles backwards through menu items
- All interactive elements have visible focus indicators

### Navigation Enhancements

- **Close button (X)**: Visible close button in mobile menu with 44px touch target
- **Active page indicator**: Current page highlighted with underline and glowing dot
- **Header scroll blur**: Glassmorphism effect on header when scrolling (backdrop-filter)
- **ARIA current page**: `aria-current="page"` attribute on active navigation link

## Prerequisites

- Python 3.12+
- Virtual environment (recommended)
- No database required (static content site)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sabor-con-flow-dance.git
cd sabor-con-flow-dance
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key-here
```

5. Collect static files:
```bash
python manage.py collectstatic --noinput
```

Note: This is a static content website and does not require database setup or migrations.

## Running the Development Server

```bash
python manage.py runserver
```

Visit http://localhost:8000 to see the website.

## Class Information

The website displays:
1. Upcoming classes and events with schedules
2. Class pricing information
3. Private lesson booking through Calendly integration

## Dance Classes Offered

- **SCF Choreo Team** - Advanced Cuban salsa techniques (Sundays 12-1 PM)
- **Pasos Básicos** - Basic Cuban salsa footwork (Sundays 1-2 PM)
- **Casino Royale** - Casino dancing fundamentals (Sundays 2-3 PM)

## Private Lesson Pricing

- **1 Hour**: $120
- **3 Hours**: $100 per hour ($300 total)
- **5+ Hours**: $75 per hour ($375+ total)

## Deployment

### Vercel Deployment

This project is configured for deployment on Vercel. The configuration includes:

1. Python 3.12 runtime
2. Custom WSGI handler for Django
3. Static file serving
4. Error handling and logging
5. URL redirects for Facebook click tracking parameters (`fbclid`)

#### URL Redirects

The `vercel.json` configuration includes automatic redirects to handle Facebook click tracking parameters:

- **fbclid Parameter Removal**: URLs containing `?fbclid=` parameters are automatically redirected to clean URLs
- **Clean URL Tracking**: Redirects add a `?cleaned=true` parameter to track when fbclid cleanup occurs
- **Temporary Redirects**: Uses 302 temporary redirects for better user experience
- **Complete Parameter Removal**: All query parameters are removed when fbclid is present

Example:
- `https://www.saborconflowdance.com/?fbclid=abc123` → `https://www.saborconflowdance.com/?cleaned=true`
- `https://www.saborconflowdance.com/events?fbclid=xyz789` → `https://www.saborconflowdance.com/events?cleaned=true`
- `https://www.saborconflowdance.com/contact?fbclid=def456&other=param` → `https://www.saborconflowdance.com/contact?cleaned=true`

To deploy:

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

For production deployment:
```bash
vercel --prod
```

### Current Deployment Status

- **Live URL**: https://www.saborconflowdance.com/
- **Platform**: Vercel
- **Python Runtime**: 3.12
- **Static Files**: Served via WhiteNoise middleware
- **fbclid Redirects**: Active and functional
- **Database**: Not required (static content site)

### Troubleshooting

If you encounter issues with the deployment:

1. **Check Vercel logs** in the Vercel dashboard
2. **Verify environment variables** are set correctly
3. **Ensure static files** are collected: `python manage.py collectstatic`
4. **Check fbclid redirects** by testing URLs with `?fbclid=test`

### Traditional Deployment

For traditional hosting:

1. Set `DEBUG=False` in your `.env` file
2. Update `ALLOWED_HOSTS` in `settings.py`
3. Configure your web server (e.g., Nginx)
4. Set up SSL certificates
5. Use Gunicorn as the WSGI server

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
