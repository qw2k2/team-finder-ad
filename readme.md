# TeamFinder

TeamFinder is a Django web application for finding collaborators for pet projects. Users can create profiles, describe their skills, publish projects, and discover projects that need their expertise.

The current implementation uses **project skill requirements and skill-based project filtering** (variant 3).

## Features

- User registration, authentication, and profile management
- User profiles with searchable skills
- Create, edit, and complete projects
- Join and leave projects
- Browse platform members
- Define required skills for each project
- Search and filter projects by required skills
- Add and remove project skills without a full page reload
- PostgreSQL-backed persistence
- Demo data generation with a Django management command

## Tech stack

- Python 3.11+
- Django 5.2
- PostgreSQL 16
- psycopg 3
- Pillow
- python-decouple
- Docker Compose

## Getting started

### Prerequisites

- Python 3.11 or newer
- pip
- Docker and Docker Compose
- Git

### 1. Clone the repository

```bash
git clone https://github.com/qw2k2/team-finder-ad.git
cd team-finder-ad
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file by copying `.env_example`:

Windows PowerShell:

```powershell
Copy-Item .env_example .env
```

Linux / macOS:

```bash
cp .env_example .env
```

Set `TASK_VERSION=3` in `.env`. Replace the example `DJANGO_SECRET_KEY` and database password with local values before starting the application. The application requires `DJANGO_SECRET_KEY` to be set. Do not commit your real `.env` file.

### 5. Start PostgreSQL

```bash
docker compose up -d
```

### 6. Apply migrations and load demo data

```bash
python manage.py migrate
python manage.py seed_data
```

### 7. Start the development server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## Main routes

| Route | Description |
| --- | --- |
| `/projects/list/` | Browse projects and filter by required skills |
| `/projects/create-project/` | Create a project |
| `/projects/<id>/` | View project details |
| `/users/list/` | Browse platform members |
| `/users/<id>/` | View a user profile |
| `/users/skills/` | Search skills for a profile |
| `/users/register/` | Register an account |
| `/users/login/` | Sign in |
| `/users/change-password/` | Change password |

## Project skill workflow

Project owners can manage the skills required for their projects. Skill suggestions are searched through:

```text
/projects/skills/?q=<query>
```

The project skill endpoints are:

- `POST /projects/<id>/skills/add/` — add a required skill
- `POST /projects/<id>/skills/<skill_id>/remove/` — remove a required skill

The project list supports filtering with the `skill` query parameter.

## Useful development commands

Run automated tests:

```bash
python manage.py test
```

Run Django's system checks:

```bash
python manage.py check
```

Stop the database container:

```bash
docker compose down
```

## Configuration and security

The repository includes `.env_example` with development defaults. Use a unique `DJANGO_SECRET_KEY`, disable debug mode, configure allowed hosts, and set strong database credentials before deploying anywhere beyond local development.

## Project status

TeamFinder is an educational full-stack Django project. It demonstrates user and project workflows, relational data modelling, skill-based discovery, and local containerized database setup.
