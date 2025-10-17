"""
Seed Initial Data
Create initial users including admin accounts
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import User
from auth import get_password_hash
from datetime import datetime


def create_initial_users(db: Session):
    """
    Create initial users for testing and administration
    """
    # Check if users already exist
    existing_users = db.query(User).count()
    if existing_users > 0:
        print(f"⚠️  Database already has {existing_users} users. Skipping seed data.")
        return

    print("🌱 Seeding initial users...")

    # Initial users to create
    initial_users = [
        {
            "user_id": "admin",
            "email": "admin@secondarymarket.com",
            "name": "Super Admin",
            "password": "admin123",
            "role": "super_admin"
        },
        {
            "user_id": "manager",
            "email": "manager@secondarymarket.com",
            "name": "Manager User",
            "password": "manager123",
            "role": "admin"
        },
        {
            "user_id": "test",
            "email": "test@secondarymarket.com",
            "name": "Test User",
            "password": "test123",
            "role": "user"
        },
        {
            "user_id": "demo",
            "email": "demo@secondarymarket.com",
            "name": "Demo User",
            "password": "demo123",
            "role": "user"
        }
    ]

    created_count = 0

    for user_data in initial_users:
        try:
            # Create new user
            new_user = User(
                user_id=user_data["user_id"],
                email=user_data["email"],
                name=user_data["name"],
                password_hash=get_password_hash(user_data["password"]),
                role=user_data["role"],
                is_active=True,
                created_at=datetime.now()
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            print(f"✅ Created {user_data['role']:12} | {user_data['user_id']:10} | {user_data['email']}")
            created_count += 1

        except Exception as e:
            print(f"❌ Failed to create user '{user_data['user_id']}': {e}")
            db.rollback()

    print(f"\n🎉 Successfully created {created_count}/{len(initial_users)} users!")
    print("\n📋 Login credentials:")
    print("=" * 60)
    for user_data in initial_users:
        print(f"User ID: {user_data['user_id']:10} | Password: {user_data['password']:10} | Role: {user_data['role']}")
    print("=" * 60)


def main():
    """Main function to seed database"""
    print("🚀 Starting database seeding...")

    # Create database session
    db = SessionLocal()

    try:
        # Create initial users
        create_initial_users(db)

        print("\n✅ Database seeding completed!")

    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    main()
