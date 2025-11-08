# Simple ERMS

A role-based Employee Record Management System built with Django and Djongo (MongoDB) featuring themed dashboards, admin CRUD workflows, and an employee self-service portal. Recent UI work focused on stabilising Chart.js analytics across light/dark themes with crisp typography and reliable tooltips. The project is optimized for deployment to Vercel and uses MongoDB Atlas as the backing database.

## Features
- **Role-aware authentication**: Separate admin and employee login flows with automatic dashboard redirects.
- **Admin dashboard**: Searchable employee directory, aggregate stats, and full CRUD (create, view, edit, delete) interfaces.
- **Employee dashboard**: Read-only profile overview, compensation summary, and emergency contact details.
- **MongoDB integration**: Stores employee records in MongoDB via Djongo; includes import script to seed data from an existing collection.
- **Responsive UI & theming**: Modern layout, light/dark theme toggle with synchronized chart styling, corporate accents, and mobile-friendly design.
- **Deployment ready**: Configuration, scripts, and guidance for running on Vercel serverless infrastructure with MongoDB Atlas.

## Tech Stack
- Python 3.11+
- Django 4.1
- Djongo + PyMongo (MongoDB Atlas)
- HTML/CSS with custom styling (no frontend frameworks)
- Gunicorn/Whitenoise for production WSGI & static serving

## Getting Started

### 1. Clone & create virtual environment
```bash
git clone https://github.com/<you>/simple_erms.git
cd simple_erms
python -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Environment variables
Create a `.env` file in the project root (or configure your shell) with:
```
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>/<database>?retryWrites=true&w=majority&appName=<app>
```
> For production set `DJANGO_DEBUG=0` and include your deployed host (e.g., `.vercel.app`).

### 3. Apply migrations
```bash
.\.venv\Scripts\python manage.py migrate
```

### 4. Seed data (optional)
If you have an `employee_data` collection in MongoDB that matches the expected schema, run:
```bash
.\.venv\Scripts\python scripts\import_empdata.py
```
This script will create Django auth users for each employee (default password `Employee123!`).

### 5. Create an admin user
```bash
.\.venv\Scripts\python manage.py createsuperuser
```
> Alternatively, use `scripts/create_admin.py` to bootstrap the `admin` account with a default password.

### 6. Run the development server
```bash
.\.venv\Scripts\python manage.py runserver
```
Navigate to:
- Admin login: `http://127.0.0.1:8000/auth/admin/`
- Employee login: `http://127.0.0.1:8000/auth/employee/`

## Project Structure
```
├── employees/
│   ├── forms.py           # Admin/employee auth forms & dropdown options
│   ├── models.py          # Employee model linked to Django user
│   ├── views.py           # Auth views, dashboards, CRUD handlers
│   └── ...
├── templates/
│   ├── base.html          # Shared layout with theme toggle & messages
│   ├── home.html          # Landing page with login CTAs
│   └── employees/
│       ├── admin_dashboard.html
│       ├── employee_dashboard.html
│       ├── employee_form.html
│       ├── employee_detail.html
│       └── employee_confirm_delete.html
├── static/
│   └── employees/
│       ├── css/styles.css
│       └── js/
│           ├── admin_dashboard.js  # Chart.js configuration with dynamic theming
│           └── theme.js            # Theme toggle + event dispatch
├── scripts/
│   ├── import_empdata.py  # Imports documents from MongoDB into Django
│   └── create_admin.py    # Creates or updates the admin superuser
├── erms_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── README.md
```

## Running Tests
```bash
.\.venv\Scripts\python manage.py test
```
(Currently no automated tests are defined; command confirms Django setup.)

## Deployment (Vercel)
1. **Add production dependencies**: Ensure `gunicorn`, `whitenoise`, `djongo`, and `pymongo` are listed in `requirements.txt`.
2. **Create `vercel_handler.py`**:
    ```python
    import os
    from django.core.wsgi import get_wsgi_application

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "erms_project.settings")
    app = get_wsgi_application()
    ```
3. **Add `vercel.json`**:
    ```json
    {
      "builds": [
        {
          "src": "vercel_handler.py",
          "use": "@vercel/python",
          "config": {
            "runtime": "python3.11",
            "installCommand": "pip install -r requirements.txt",
            "buildCommand": "python manage.py collectstatic --noinput"
          }
        }
      ],
      "routes": [
        {
          "src": "/(.*)",
          "dest": "vercel_handler.py"
        }
      ]
    }
    ```
4. **Configure environment variables** in the Vercel dashboard (`DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS=.vercel.app`, `MONGODB_URI`).
5. **Push to GitHub/GitLab** and import the repository in Vercel. Deploy via UI or `vercel deploy --prod`.

## Default Credentials
- Admin (if created via script): `admin / AdminPass123!`
- Imported employees: username is the email prefix, password `Employee123!` (prompt users to change on first login).

## Version Control Notes
- Project root: repository base (`manage.py`, `requirements.txt`, etc.). Run all `git` commands here.
- Do **not** commit local virtual environments (`.venv/`), `staticfiles/`, or `.env`. A starter `.env.example` is recommended.
- Before pushing, run `python manage.py check` and consider `python manage.py test` to validate Django is healthy.
- Update `requirements.txt` via `pip freeze > requirements.txt` when dependencies change.

## License
Specify your preferred license here (e.g., MIT, Apache 2.0). Replace this section if needed before publishing.
