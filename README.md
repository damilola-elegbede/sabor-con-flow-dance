# Sabor con Flow Dance

A Django-based website for Sabor con Flow Dance, featuring class information and registration.

## Features

- Class information display
- Simple registration form
- Newsletter subscription
- Responsive design

## Prerequisites

- Python 3.8+
- Virtual environment (recommended)

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
python manage.py collectstatic
```

## Running the Development Server

```bash
python manage.py runserver
```

Visit http://localhost:8000 to see the website.

## Class Registration

The registration system allows users to:
1. View upcoming classes and events
2. Register for classes
3. Receive confirmation with payment instructions

## Deployment

### Vercel Deployment

This project is configured for deployment on Vercel. The configuration includes:

1. Python 3.11 runtime
2. Custom WSGI handler for Django
3. Static file serving
4. Error handling and logging

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
