from app.db.postgres import Base, engine
from app.db.session import SessionLocal
from app.models.user import User

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

user = db.query(User).filter(
    User.email == "praveen@nexus.local"
).first()

if not user:
    user = User(
        email="praveen@nexus.local",
        full_name="Praveen Singh",
        role="employee",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    print(f"Created user with ID: {user.id}")
else:
    print(f"User already exists with ID: {user.id}")

db.close()