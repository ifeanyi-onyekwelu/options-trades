# Django Trading Platform

A robust trading platform built with Django for managing options trades and investments.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-brightgreen)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)](https://www.postgresql.org/)

## Features

- User authentication and authorization system
- Trade management dashboard
- Real-time portfolio tracking
- Secure transaction processing
- Email notifications system
- Admin management interface
- REST API endpoints

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 15+
- pip package manager
- Virtualenv (recommended)

### Installation

1. **Clone the repository**
   ```
    bash
    git clone https://github.com/yourusername/trading-platform.git
    cd trading-platform

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

    pip install -r requirements.txt

    SECRET_KEY=your-secret-key-here

    DEBUG=True

    DB_NAME=
    DB_USER=
    DB_PASSWORD=
    DB_HOST=
    DB_PORT=

    APP_URL=

    DEFAULT_EMAIL=

    sudo -u postgres psql
    CREATE DATABASE "options-trades";
    CREATE USER postgres WITH PASSWORD 'ifyonyekeshy7';
    ALTER ROLE postgres SET client_encoding TO 'utf8';
    ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
    ALTER ROLE postgres SET timezone TO 'UTC';
    GRANT ALL PRIVILEGES ON DATABASE "options-trades" TO postgres;

    python manage.py migrate

    python manage.py migrate

    python manage.py runserver