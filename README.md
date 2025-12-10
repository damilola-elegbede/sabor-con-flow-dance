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
- **Contact** - Contact information and social media links

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

## Project Structure

```
sabor-con-flow-dance/
├── api/                    # Vercel serverless functions
│   └── index.py           # Main API entry point
├── core/                   # Django app
│   ├── views.py           # View logic (static content)
│   ├── urls.py            # URL routing
│   └── models.py          # Placeholder file (no models used)
│   └── forms.py           # Placeholder file (no forms used)
├── public/                 # Public static assets
│   └── css/
│       └── base/
│           └── variables.css  # CSS design tokens
├── static/                 # Static assets (CSS, JS, images)
├── staticfiles/            # Collected static files
├── templates/              # Base templates
├── vercel.json            # Vercel deployment configuration
└── requirements.txt       # Python dependencies
```

## CSS Design System

The project uses CSS custom properties (design tokens) for consistent styling:

- **Colors**: Brand palette (gold, black, white) with semantic aliases
- **Typography**: Font families (Inter for body, Playfair Display for headings), sizes, weights, and line heights
- **Spacing**: 4px base unit scale (0-24 increments)
- **Shadows**: Elevation and hover state shadows
- **Transitions**: Standardized durations and easing functions

Design tokens are defined in `public/css/base/variables.css`.

## Accessibility Features

The site includes built-in accessibility support:

- **Skip-to-content link**: Keyboard users can skip navigation and jump directly to main content
- **Focus-visible states**: Gold outline indicators for keyboard navigation (3px solid with 2-4px offset)
- **ARIA attributes**: Proper labeling for navigation, social links, and interactive elements
- **Screen reader utilities**: `.sr-only` class for visually hidden but accessible content
- **Escape key support**: Mobile menu closes on Escape key press
- **Semantic HTML**: Proper heading hierarchy, landmarks, and button/link roles

### Keyboard Navigation

- Press `Tab` to reveal skip-link at top of page
- Press `Enter` on skip-link to jump to main content
- Press `Escape` to close mobile navigation menu
- All interactive elements have visible focus indicators

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
