# FitBuddy AI

FitBuddy AI is a FastAPI + Jinja2 web app that generates a personalized 7-day workout plan, provides a nutrition tip, accepts user feedback, and lets admins review all users and plans.

## Features

- User input form with:
  - `username`
  - `user_id`
  - `age`
  - `weight`
  - `goal`
  - `intensity`
- AI-style 7-day workout plan generation
- Nutrition tip based on fitness goal
- Feedback-based plan update flow
- Admin dashboard to:
  - view all users
  - view original and updated plans
  - delete users
- Responsive, gym-themed UI with Jinja2 templates

## Tech Stack

- Python 3.13
- FastAPI
- Jinja2 Templates
- SQLAlchemy ORM
- SQLite
- HTML/CSS (embedded template styling)

## Project Structure

```text
FitBUddy/
|-- app/
|   `-- main.py
|-- templates/
|   |-- index.html
|   |-- result.html
|   `-- all_users.html
|-- static/
|   `-- images/
|       `-- gym-bg.jpg
|-- fitbuddy.db
`-- README.md
```

## Setup and Run

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install fastapi uvicorn sqlalchemy jinja2 python-multipart
```

4. Start the app:

```bash
uvicorn app.main:app --reload
```

5. Open:

- App UI: `http://127.0.0.1:8000/`
- Swagger Docs: `http://127.0.0.1:8000/docs`

## Main Routes

- `GET /` - User input form
- `POST /generate-workout` - Generate workout and show result page
- `POST /submit-feedback` - Update plan from feedback
- `GET /view-all-users` - Admin dashboard
- `POST /delete-user/{user_id}` - Delete a user

## UI Pages

- `templates/index.html` - Form page (input collection)
- `templates/result.html` - Workout result + nutrition tip + feedback form
- `templates/all_users.html` - Admin user/plan table

## Database

SQLite database file: `fitbuddy.db`

Tables:
- `users`
- `workout_plans`

The app auto-creates tables on startup using SQLAlchemy.

## Notes

- Current logic uses deterministic plan generation functions in `app/main.py`.
- The codebase includes additional Gemini helper files (`gemini_generator.py`, etc.), but the active web flow is implemented in `app/main.py`.

## License

Use an appropriate license before publishing (for example MIT).
