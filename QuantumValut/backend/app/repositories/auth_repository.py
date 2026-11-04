from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User, RefreshToken

class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: dict) -> User:
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = self.db.execute(stmt).scalar_one_or_none()
        return result

    def create_refresh_token(self, token_data: dict) -> RefreshToken:
        token = RefreshToken(**token_data)
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    def get_refresh_token(self, token_hash: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = self.db.execute(stmt).scalar_one_or_none()
        return result

    def revoke_refresh_token(self, token_hash: str) -> None:
        token = self.get_refresh_token(token_hash)
        if token:
            token.revoked = True
            self.db.commit()
