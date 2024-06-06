# Django REST Framework (DRF) Project Setup

This repository contains a basic setup for a Django project using Django REST Framework (DRF) to create a RESTful API. Follow the steps below to get started.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Setup](#project-setup)
- [Running the Server](#running-the-server)
- [Running Celery](#running-celery)

## Prerequisites

- Python 3.8+
- pip (Python package installer)
- Virtualenv (recommended for creating isolated environments)

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/sengxingstx-haltech/hotel_management_system_backend.git
   ```
## Project Setup

1. **Create a virtual environment**

   ```bash
   virtualenv .venv
   ```

2. **Install dependecies**

   ```bash
   pip install -r requirements.txt
   ```
3. **Setup environment variables**

   ```bash
   # for windows
   copy .env.example .env

   # for linux
   cp .env.exmaple .env
   ```

## Running the Server
1. **Start the development server**

   ```bash
   python manage.py runserver
   ```

## Running Celery
1. **Start the celery worker**

   ```bash
   # for windows
   celery -A myproject worker --pool=solo -l info

   # for linux
   celery -A myproject worker -l info
   ```
2. **Start the celery beat**

   ```bash
   celery -A myproject beat -l info
   ```