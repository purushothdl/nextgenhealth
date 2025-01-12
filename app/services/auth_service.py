from datetime import timedelta
from app.core.security import verify_password, create_access_token
from app.services.user_service import UserService
from app.core.exceptions import InvalidCredentialsException, UserNotFoundException
from app.schemas.token_schemas import Token

class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def authenticate_user(self, username: str, password: str) -> Token:
        """
        Authenticate a user by verifying their username and password.
        If valid, return an access token.
        """
        try:
            user = await self.user_service.get_user_by_username(username)
        except UserNotFoundException:
            # Raise a generic error to avoid revealing whether the username exists
            raise InvalidCredentialsException("Invalid username or password")

        if not verify_password(password, user["hashed_password"]):
            raise InvalidCredentialsException("Invalid username or password")

        access_token_expires = timedelta(minutes=6000)
        access_token = create_access_token(
            data={"sub": str(user["_id"])},  # Use user_id instead of username
            expires_delta=access_token_expires,
        )
        return {"access_token": access_token, "token_type": "bearer"}