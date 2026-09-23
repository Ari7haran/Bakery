from app.repositories.user_repository import UserRepository
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.exceptions import BusinessRuleError, ConflictError, UnauthorizedError
from app.models.user import User, RoleEnum
from app.schemas.auth import UserRegister, Token
from app.schemas.user import UserOut

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def register(self, user_in: UserRegister) -> Token:
        existing = self.user_repo.get_by_email(user_in.email)
        if existing:
            raise ConflictError("Email already registered")

        # First user is admin, else customer
        user_count = self.user_repo.count_users()
        role = RoleEnum.ADMIN.value if user_count == 0 else RoleEnum.CUSTOMER.value
        loyalty_points = 100 if role == RoleEnum.CUSTOMER.value else 0

        hashed_password = get_password_hash(user_in.password)
        user = self.user_repo.create_user(
            full_name=user_in.full_name,
            email=user_in.email,
            hashed_password=hashed_password,
            phone=user_in.phone,
            role=role,
            loyalty_points=loyalty_points
        )

        token = create_access_token(subject=user.id, role=user.role)
        return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(user))

    def authenticate(self, email: str, password: str) -> Token:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Incorrect email or password")

        if not user.is_active:
            raise UnauthorizedError("User account is inactive")

        token = create_access_token(subject=user.id, role=user.role)
        return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(user))
