def save_user(user_id: int, name: str, age: int, weight: float, goal: str, intensity: str):
    db = SessionLocal()
    existing = db.query(User).filter_by(id=user_id) . first()
    if existing:
        # Update existing user info
        existing. name = name
        existing.age = age
        existing.weight = weight
        existing.goal = goal
        existing. intensity = intensity
    else:
    # Create a new user
        user = User(
            id=user_id,
            name=name,

            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
            schedule=7 # default schedule or logic
        )
        db.add(user)
    db.commit()
    db.close()

#stores the plan in the database
def save_plan(user_id: int, plan: str):
    db = SessionLocal()
    workout = WorkoutPlan(user_id=user_id, original_plan=plan)
    db.add(workout)
    db. commit ()
    db.close()

# Update the plan based on feedback
def update_plan(user_id: int, updated_text: str):
    db = SessionLocal()
    workout = db.query(WorkoutPlan). filter_by(user_id=user_id) . first()
    if workout:
        workout. updated_plan = updated_text
        db.commit()
    db.close()

# Fetch the original plan for a user
def get_original_plan(user_id: int):
    db = SessionLocal()
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id). first()
    return plan.original_plan if plan else None

def get_user(user_id: int):
    db = SessionLocal()
    return db.query(User).filter(User.id == user_id). first()