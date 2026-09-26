from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.user import User

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def count_users(self) -> int:
        return self.db.query(User).count()

    def count_customers(self) -> int:
        return self.db.query(User).filter(User.role == "customer").count()

    def create_user(self, full_name: str, email: str, hashed_password: str, phone: Optional[str], role: str, loyalty_points: int) -> User:
        user = User(
            full_name=full_name,
            email=email,
            hashed_password=hashed_password,
            phone=phone,
            role=role,
            loyalty_points=loyalty_points,
            is_active=True
        )
        return self.add(user)

    def update_loyalty_points(self, user: User, points_to_add: int) -> User:
        user.loyalty_points += points_to_add
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_admins(self) -> List[User]:
        return self.db.query(User).filter(User.role == "admin", User.is_active == True).all()
