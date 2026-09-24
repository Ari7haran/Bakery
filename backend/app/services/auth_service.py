from app.repositories.user_repository import UserRepository
from app.core.security import get_password_hash, verify_password, create_access_token, dummy_verify_password
from app.core.exceptions import BusinessRuleError, ConflictError, UnauthorizedError
from app.models.user import User, RoleEnum
from app.schemas.auth import UserRegister, Token
from app.schemas.user import UserOut

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def register(self, user_in: UserRegister) -> Token:
        normalized_email = str(user_in.email).strip().lower()
        existing = self.user_repo.get_by_email(normalized_email)
        if existing:
            raise ConflictError("Email already registered")

        # First user is admin, else customer
        user_count = self.user_repo.count_users()
        role = RoleEnum.ADMIN.value if user_count == 0 else RoleEnum.CUSTOMER.value
        loyalty_points = 100 if role == RoleEnum.CUSTOMER.value else 0

        hashed_password = get_password_hash(user_in.password)
        user = self.user_repo.create_user(
            full_name=user_in.full_name.strip(),
            email=normalized_email,
            hashed_password=hashed_password,
            phone=user_in.phone.strip() if user_in.phone else None,
            role=role,
            loyalty_points=loyalty_points
        )

        token = create_access_token(subject=user.id, role=user.role)
        return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(user))

    def authenticate(self, email: str, password: str) -> Token:
        normalized_email = email.strip().lower()
        user = self.user_repo.get_by_email(normalized_email)
        if not user:
            # Perform dummy verify to equalize response timing and mitigate email enumeration
            dummy_verify_password(password)
            raise UnauthorizedError("Incorrect email or password")

        if not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Incorrect email or password")

        if not user.is_active:
            raise UnauthorizedError("User account is inactive")

        token = create_access_token(subject=user.id, role=user.role)
        return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(user))
