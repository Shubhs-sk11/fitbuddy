import os
from typing import Generator

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, relationship, sessionmaker


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, "templates")
STATIC_DIR = os.path.join(PROJECT_ROOT, "static")
DB_PATH = os.path.join(PROJECT_ROOT, "fitbuddy.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    goal = Column(String(80), nullable=False)
    intensity = Column(String(40), nullable=False)

    workout_plan = relationship(
        "WorkoutPlan",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    original_plan = Column(Text, nullable=False)
    updated_plan = Column(Text, nullable=True)

    user = relationship("User", back_populates="workout_plan")


Base.metadata.create_all(bind=engine)

app = FastAPI(title="FitBuddy AI")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATE_DIR)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_workout_plan(goal: str, intensity: str) -> str:
    days = [
        ("Day 1", "Upper Body Strength"),
        ("Day 2", "Lower Body Power"),
        ("Day 3", "Cardio + Core"),
        ("Day 4", "Active Recovery"),
        ("Day 5", "Push-Pull Split"),
        ("Day 6", "Endurance Circuit"),
        ("Day 7", "Mobility + Stretch"),
    ]
    plan_lines = []
    for day, focus in days:
        plan_lines.extend(
            [
                f"{day}:",
                f"Warm-up: 5-10 min brisk walk + dynamic mobility",
                (
                    f"Main Workout: {focus} tuned for {goal} "
                    f"with {intensity.lower()} intensity effort"
                ),
                "Cooldown: 8 min breathing + full-body stretching",
                "",
            ]
        )
    return "\n".join(plan_lines).strip()


def generate_nutrition_tip(goal: str) -> str:
    goal_key = goal.strip().lower()
    tips = {
        "weight loss": "Keep meals protein-forward and include fiber in every plate to stay full longer.",
        "muscle gain": "Aim for 25-35g protein per meal and add one carb-rich meal after training.",
        "general fitness": "Build balanced plates: lean protein, whole grains, healthy fats, and colorful vegetables.",
    }
    return tips.get(
        goal_key,
        "Hydrate consistently and keep your meals balanced around lean protein and whole foods.",
    )


def update_plan_with_feedback(original_plan: str, feedback: str) -> str:
    return (
        f"{original_plan}\n\n"
        "Updated based on your feedback:\n"
        f"- Feedback noted: {feedback}\n"
        "- Adjustment: lower volume for high-fatigue days and add one extra mobility block."
    )


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: int = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    if age <= 0 or weight <= 0:
        raise HTTPException(status_code=400, detail="Age and weight must be greater than zero.")

    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.name = username
        user.age = age
        user.weight = weight
        user.goal = goal
        user.intensity = intensity
    else:
        user = User(
            id=user_id,
            name=username,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )
        db.add(user)

    workout_plan = generate_workout_plan(goal=goal, intensity=intensity)
    nutrition_tip = generate_nutrition_tip(goal=goal)

    existing_plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()
    if existing_plan:
        existing_plan.original_plan = workout_plan
        existing_plan.updated_plan = None
    else:
        db.add(WorkoutPlan(user_id=user_id, original_plan=workout_plan))

    db.commit()

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "username": username,
            "user_id": user_id,
            "age": age,
            "weight": weight,
            "goal": goal,
            "intensity": intensity,
            "workout_plan": workout_plan,
            "nutrition_tip": nutrition_tip,
            "updated_plan": None,
            "feedback_message": None,
        },
    )


@app.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: int = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()

    if not user or not plan:
        raise HTTPException(status_code=404, detail="User or plan not found.")

    updated_plan = update_plan_with_feedback(plan.original_plan, feedback)
    plan.updated_plan = updated_plan
    db.commit()

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "username": user.name,
            "user_id": user.id,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "workout_plan": plan.original_plan,
            "nutrition_tip": generate_nutrition_tip(user.goal),
            "updated_plan": updated_plan,
            "feedback_message": "Feedback saved. Your workout plan has been updated.",
        },
    )


@app.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id.asc()).all()
    user_data = []
    for user in users:
        plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user.id).first()
        user_data.append(
            {
                "id": user.id,
                "name": user.name,
                "age": user.age,
                "weight": user.weight,
                "goal": user.goal,
                "intensity": user.intensity,
                "original_plan": plan.original_plan if plan else "N/A",
                "updated_plan": plan.updated_plan if plan and plan.updated_plan else "Not updated",
            }
        )
    return templates.TemplateResponse("all_users.html", {"request": request, "users": user_data})


@app.post("/delete-user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return RedirectResponse(url="/view-all-users", status_code=303)
