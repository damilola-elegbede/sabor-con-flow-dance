# Sabor con Flow Dance

A Django-based website for Sabor con Flow Dance, featuring event management and class registration.

## Features

- Event management and display
- Class registration with manual payment processing
- Newsletter subscription
- Responsive design
- Admin interface for managing events and registrations

## Prerequisites

- Python 3.8+
- PostgreSQL
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
DATABASE_URL=postgres://username:password@localhost:5432/sabor_con_flow
```

5. Create the PostgreSQL database:
```bash
createdb sabor_con_flow
```

6. Run migrations:
```bash
python manage.py migrate
```

7. Create a superuser:
```bash
python manage.py createsuperuser
```

8. Collect static files:
```bash
python manage.py collectstatic
```

## Running the Development Server

```bash
python manage.py runserver
```

Visit http://localhost:8000 to see the website.

## Admin Interface

Access the admin interface at http://localhost:8000/admin to:
- Manage events
- View registrations
- Manage newsletter subscribers

## Class Registration

The registration system allows users to:
1. View upcoming classes and events
2. Register for classes
3. Receive confirmation with payment instructions
4. Admin can track registrations and payment status

## Deployment

1. Set `DEBUG=False` in your `.env` file
2. Update `ALLOWED_HOSTS` in `settings.py`
3. Set up a production database with a valid PostgreSQL URL (e.g., `postgres://username:password@host:5432/dbname`)
4. Configure your web server (e.g., Nginx)
5. Set up SSL certificates
6. Use Gunicorn as the WSGI server

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
