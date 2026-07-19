import sys
import os

# Adjust Python Path to import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, Base, SessionLocal
from models import User, Notification
from core.security import get_password_hash

def init_db():
    print("Creating all tables in SQLite database...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if users already exist
        candidate = db.query(User).filter(User.email == "ananya@example.com").first()
        if not candidate:
            print("Seeding default candidate user: ananya@example.com / password123")
            candidate_user = User(
                name="Ananya",
                email="ananya@example.com",
                role="candidate",
                dob="1995-08-15",
                gender="female",
                country="India",
                state="Karnataka",
                city="Bengaluru",
                phone="9876543210",
                password=get_password_hash("password123"),
                verified=True
            )
            db.add(candidate_user)
            db.commit()
            db.refresh(candidate_user)

            # Add default notification
            db.add(Notification(
                user_id=candidate_user.id,
                title="Welcome to Career AI",
                message="Your career command center is ready. Upload your resume to start!",
                type="system"
            ))
            db.commit()
        else:
            print("Candidate user already exists.")

        recruiter = db.query(User).filter(User.email == "recruiter@example.com").first()
        if not recruiter:
            print("Seeding default recruiter user: recruiter@example.com / password123")
            recruiter_user = User(
                name="Recruiter",
                email="recruiter@example.com",
                role="recruiter",
                dob="1988-11-20",
                gender="male",
                country="India",
                state="Maharashtra",
                city="Mumbai",
                phone="9123456780",
                password=get_password_hash("password123"),
                verified=True
            )
            db.add(recruiter_user)
            db.commit()
        else:
            print("Recruiter user already exists.")

        print("Database seeded successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
