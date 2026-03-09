# FitBuddy AI - Project Documentation

## 1. Overview

FitBuddy AI is a web application built with FastAPI and Jinja2.  
It provides a complete UI-driven flow for collecting user fitness data, generating a 7-day workout plan, adding nutrition guidance, and updating the plan based on feedback.

Primary goals:
- Clean and responsive user interface
- Dynamic template rendering with backend data binding
- Simple persistence layer with SQLite + SQLAlchemy
- Admin visibility into all users and plans

## 2. Architecture

### 2.1 Application Layer

- Framework: FastAPI
- Entry point: `app/main.py`
- Templating: `Jinja2Templates(directory="templates")`
- Static assets: mounted from `/static`

### 2.2 Presentation Layer

Templates:
- `templates/index.html` - input form
- `templates/result.html` - generated result + feedback
- `templates/all_users.html` - admin table

All templates are rendered using:
- `templates.TemplateResponse(template_name, context)`

### 2.3 Data Layer

- Database: SQLite (`fitbuddy.db`)
- ORM: SQLAlchemy
- Session management via `SessionLocal`

Models in `app/main.py`:
- `User`
- `WorkoutPlan`

Relationship:
- One `User` -> one `WorkoutPlan` (`uselist=False`)

## 3. Activity 4.1 Implementation (UI Design and Development)

### 3.1 Base HTML Structure

Implemented in `templates/index.html`:
- Semantic grouped form sections with `fieldset` and `legend`
- Proper labels for every input
- Fields:
  - `username`
  - `user_id`
  - `age`
  - `weight`
  - `goal`
  - `intensity`
- Form submission to `POST /generate-workout`

### 3.2 Responsive CSS Layout

Applied embedded CSS in each template:
- Flexbox-based page centering
- Responsive grid for form inputs
- Mobile behavior via media queries
- Consistent button styles with hover effects
- Rounded cards, shadows, and dark overlay for readability
- Gym-themed background image from `static/images/gym-bg.jpg`
- Roboto font via Google Fonts

### 3.3 Separate Pages for Core Functionality

Implemented pages:
- `index.html` - user input
- `result.html` - workout output + nutrition tip + feedback form
- `all_users.html` - admin table, plan review, and user deletion

User flow:
1. Fill form on `/`
2. Submit to `/generate-workout`
3. Review result on `result.html`
4. Submit feedback to `/submit-feedback`
5. Optional admin view `/view-all-users`

## 4. Activity 4.2 Implementation (Dynamic Templates with FastAPI Jinja2)

### 4.1 Jinja2 Integration

Configured in `app/main.py`:

```python
PROJECT_ROOT = os.path.dirname(BASE_DIR)
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)
```

Template rendering pattern:

```python
return templates.TemplateResponse("result.html", {"request": request, ...})
```

### 4.2 Backend-to-Template Data Binding

#### index.html

- Form field `name` attributes map directly to FastAPI `Form(...)` parameters in `generate_workout`.
- Action endpoint: `/generate-workout`

#### result.html

Dynamic fields rendered:
- `{{ username }}`
- `{{ user_id }}`
- `{{ age }}`
- `{{ weight }}`
- `{{ goal }}`
- `{{ intensity }}`
- `{{ workout_plan }}`
- `{{ nutrition_tip }}`
- `{{ updated_plan }}`

Feedback form posts:
- `POST /submit-feedback`

#### all_users.html

Loops user rows with:

```jinja2
{% for user in users %}
```

Displays:
- basic user data
- original plan
- updated plan

Also provides per-user delete form:
- `POST /delete-user/{user_id}`

## 5. API and Route Documentation

### `GET /`

Purpose:
- Render main user input form.

Response:
- HTML (`index.html`)

### `POST /generate-workout`

Purpose:
- Save/update user data
- Generate original workout plan
- Generate nutrition tip
- Save plan in database
- Render result page

Form Inputs:
- `username: str`
- `user_id: int`
- `age: int`
- `weight: float`
- `goal: str`
- `intensity: str`

Response:
- HTML (`result.html`)

Validation:
- `age > 0`, `weight > 0`

### `POST /submit-feedback`

Purpose:
- Retrieve original plan by `user_id`
- Update plan using feedback
- Persist updated plan
- Re-render result page with update confirmation

Form Inputs:
- `user_id: int`
- `feedback: str`

Response:
- HTML (`result.html`)

### `GET /view-all-users`

Purpose:
- Admin page listing all users and plans.

Response:
- HTML (`all_users.html`)

### `POST /delete-user/{user_id}`

Purpose:
- Delete a user (and related plan via cascade).

Response:
- Redirect to `/view-all-users`

## 6. Database Schema

### users

- `id` (Integer, PK)
- `name` (String)
- `age` (Integer)
- `weight` (Float)
- `goal` (String)
- `intensity` (String)

### workout_plans

- `id` (Integer, PK)
- `user_id` (Integer, FK -> users.id, unique)
- `original_plan` (Text)
- `updated_plan` (Text, nullable)

## 7. Local Development

## Prerequisites

- Python 3.10+ (tested with Python 3.13 environment)

## Install

```bash
pip install fastapi uvicorn sqlalchemy jinja2 python-multipart
```

## Run

```bash
uvicorn app.main:app --reload
```

## Access

- App: `http://127.0.0.1:8000/`
- API docs: `http://127.0.0.1:8000/docs`

## 8. Testing Checklist

- Submit valid form and verify result page renders.
- Submit feedback and verify updated plan appears.
- Open admin page and verify rows display.
- Delete a user and verify removal from table.
- Validate mobile layout in browser dev tools.

## 9. Future Improvements

- Replace local plan generators with LLM provider integration.
- Add authentication for admin routes.
- Add structured logging and error pages.
- Add automated tests for routes and DB behavior.
- Add alembic migrations for schema versioning.
