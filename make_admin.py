from app.database import SessionLocal
from app.models import User


def main():
    email = input("Admin account email: ").strip().lower()
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.email == email).first()

        if not user:
            print("Account not found")
            return

        user.role = "admin"
        db.commit()
        print(f"{user.email} admin account")
    finally:
        db.close()


if __name__ == "__main__":
    main()